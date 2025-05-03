import requests
import socket
from loguru import logger

prometheus_url = "http://monitor.digitalsteve.net/prometheus/api/v1/query"

def is_nginx_healthy(instance_ip: str) -> bool:
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

response = is_nginx_healthy("18.215.163.164")

print(response)