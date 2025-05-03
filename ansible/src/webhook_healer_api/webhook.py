from fastapi import FastAPI, HTTPException
import subprocess
import boto3
from jenkinsapi.jenkins import Jenkins
import requests
from loguru import logger
import time
from functools import wraps
import redis
import os
import socket


app = FastAPI()
jenkins_url = "https://jenkins.digitalsteve.net/"
prometheus_url = "http://monitor.digitalsteve.net/prometheus/api/v1/query"
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)
MAX_HEALTH_CHECKS = 15
DELAY = 15


# -------------------- Retry Decorator --------------------
def retry(max_retries=3, delay=10):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                result = func(*args, **kwargs)
                if result:
                    return True
                logger.warning(f"Attempt {attempt} failed for {func.__name__}, retrying...")
                time.sleep(delay)
            return False
        return wrapper
    return decorator

# -------------------- Prometheus Check --------------------
def nginx_health_checks(instance_ip: str) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        print(f'Metric: HTTP port 80 check. Value: {sock.connect_ex((instance_ip, 80))}')
        # print(sock.connect_ex((instance_ip, 80)))
        if sock.connect_ex((instance_ip, 80)) != 0:
            logger.error(f"HTTP port 80 not reachable on {instance_ip}")
            return False
        sock.close()

        # 2. Check nginx_up == 1
        nginx_up_query = f'nginx_up{{instance="{instance_ip}:9113"}}'
        response = requests.get(prometheus_url, params={"query": nginx_up_query}, timeout=10)
        response.raise_for_status()
        result = response.json()["data"]["result"]
        print(f'Metric: {result[0]["metric"]["__name__"]}. Value: {result[0]["value"]}')
        if not result or result[0]["value"][1] != "1":
            logger.error(f"nginx_up metric is not 1 for {instance_ip}")
            return False

        # 3. Check node_exporter is up
        node_exporter_query = f'up{{job="node_exporter",instance="{instance_ip}:9100"}}'
        response = requests.get(prometheus_url, params={"query": node_exporter_query}, timeout=10)
        response.raise_for_status()
        result = response.json()["data"]["result"]
        print(f'Metric: {result[0]["metric"]["__name__"]}. Value: {result[0]["value"]}')
        if not result or result[0]["value"][1] != "1":
            logger.error(f"node_exporter is down or unreachable for {instance_ip}")
            return False

        logger.info(f"All health checks passed for {instance_ip}")
        return True

    except Exception as e:
        logger.error(f"Health check failed for {instance_ip}: {e}")
        return False

def get_nginx_ip_from_inventory(file="/app/config/inventory.ini"):
    try:
        with open(file) as f:
            for line in f:
                if line.startswith("nginx"):
                    return line.split("=")[1].strip()
    except Exception as e:
        logger.error(f"Error reading inventory file: {e}")
        return None

# -------------------- Jenkins Trigger --------------------
def get_jenkins_credentials():
    ssm = boto3.client("ssm", region_name="us-east-1")
    username = ssm.get_parameter(Name="/jenkins/user", WithDecryption=True)["Parameter"]["Value"]
    token = ssm.get_parameter(Name="/jenkins/token", WithDecryption=True)["Parameter"]["Value"]
    return username, token

def get_jenkins_session():
    username, token = get_jenkins_credentials()
    session = Jenkins(
        jenkins_url,
        username=username,
        password=token
    )
    return session

def trigger_jenkins_job(job_name: str, params: dict):
    server = get_jenkins_session()
    try:
        server.build_job(job_name, params=params)
        return "Job started successfully"
    except Exception as e:
        return "Error starting job: " + str(e)

@retry()
def reboot_nginx_instance_with_jenkins():
    job_name = "nginx_healer"
    parameters = {
        "Options": "RebootNginx",
        "Branch": "origin/main"
    }
    response = trigger_jenkins_job(job_name, parameters)
    logger.info(response)
    if "Error" in response:
        logger.error(f"Failed to trigger Jenkins job: {response}")
        return False
    return True

# -------------------- AWS EC2 Instance Management --------------------
def instance_exists(instance_id):
    ec2 = boto3.client("ec2", region_name="us-east-1")
    try:
        ec2.describe_instances(InstanceIds=[instance_id])
        return True
    except:
        return False

def get_instance_id_from_ip(ip):
    ec2 = boto3.client("ec2", region_name="us-east-1")
    try:
        response = ec2.describe_instances(
            Filters = [
                {
                    "Name": "network-interface.association.public-ip",
                    "Values": [ip]
                }
            ]
        )
        if response["Reservations"]:
            return response["Reservations"][0]["Instances"][0]["InstanceId"]
        else:
            return None
    except Exception as e:
        print(f"Error retrieving instance ID: {e}")
        return None
    
def delete_instance(instance_id):
    ec2 = boto3.client("ec2", region_name="us-east-1")
    try:
        response = ec2.terminate_instances(
            InstanceIds=[instance_id],
            DryRun=True
        )
        return response
    except Exception as e:
        print(f"Error terminating instance: {e}")
        return None

# -------------------- Ansible Playbook Execution --------------------
@retry()
def restart_nginx_with_ansible():
    try:
        result = subprocess.run(["ansible-playbook", "-i", "/app/config/inventory.ini", "/app/config/restart_nginx.yml"], capture_output=True, text=True)
        logger.info(result.stdout)
        if result.stderr:
            logger.error(result.stderr)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Ansible playbook execution failed: {e}")
        return False
    




# -------------------- FastAPI Endpoint --------------------
@app.post("/webhook")
async def handle_alert(alert: dict):

    if redis_client.exists("webhook_firing"):
        logger.warning("Another webhook is already firing. Ignoring latest alert.")
        return {"status": "locked", "message": "Another escalation is in progress."}

    redis_client.set("webhook_firing", "1")
    redis_client.expire("webhook_firing", 1200) # Set expiration to 20 minutes

    try:
        logger.info("Received alert:", alert)
        nginx_ip = get_nginx_ip_from_inventory()
        instance_id = get_instance_id_from_ip(nginx_ip)
        if not nginx_ip:
            logger.error("NGINX host not found in inventory.")
            raise HTTPException(status_code=500, detail="NGINX host not found in inventory.")
        logger.info(f"NGINX host from inventory: {nginx_ip}")

        for alert_item in alert.get("alerts", []):
            instance = alert_item.get("labels", {}).get("instance", "unknown")
            logger.trace(f"Instance down: {instance}")

        # Check if instance exists
        if not instance_id:
            logger.warning("Instance was deleted. Redeploying...")
            trigger_jenkins_job("nginx_healer", {"Options": "Update", "Branch": "origin/main"})
            return {"status": "Instance deleted. Redeployment triggered."}

        # If instance exists, restart nginx and exporters with ansible
        if restart_nginx_with_ansible():
            logger.info("NGINX restarted successfully.")
        else:
            logger.error("NGINX restart failed.")
            raise HTTPException(status_code=500, detail="NGINX restart failed.")
        logger.info("Waiting for health check...")
        for i in range(MAX_HEALTH_CHECKS):
            if nginx_health_checks(nginx_ip):
                logger.success("Instance is healthy after restart")
                return {"status": "Restart fixed the issue."}
            logger.info(f"Health check {i+1}/15 failed, retrying...")
            time.sleep(DELAY)
        logger.error("Restart failed. Triggering reboot...")

        # If restart failed, trigger jenkins reboot job
        if reboot_nginx_instance_with_jenkins():
            logger.info("Reboot triggered, waiting for health check...")
        else:
            logger.error("Reboot failed to trigger.")
        
        for i in range(MAX_HEALTH_CHECKS):
            if nginx_health_checks(nginx_ip):
                logger.success("Instance is healthy after reboot")
                return {"status": "Reboot fixed the issue."}
            logger.info(f"Health check {i+1}/15 failed, retrying...")
            time.sleep(DELAY)

        # If reboot failed, delete instance and trigger redeployment
        logger.error("Reboot failed. Deleting instance and redeploying...")
        delete_instance(instance_id)
        trigger_jenkins_job("nginx_healer", {"Options": "Update", "Branch": "origin/main"})
        return {"status": "Reboot failed. Instance replaced."}
    
    finally:
        redis_client.delete("webhook_firing")