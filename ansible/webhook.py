from fastapi import FastAPI, HTTPException
import subprocess

app = FastAPI()

@app.post("/webhook")
async def handle_alert(alert: dict):
    # print("Received alert:", alert)

    # Extract alert details (modify this based on your alertmanager config)
    for alert_item in alert.get("alerts", []):
        instance = alert_item.get("labels", {}).get("instance", "unknown")
        print(f"Instance down: {instance}")

    # Run Ansible playbook to restart Nginx
    try:
        result = subprocess.run(
            ["ansible-playbook", "-i", "/app/config/inventory.ini", "/app/config/restart_nginx.yml"], capture_output=True, text=True)
        print(result)
        return {"status": "success", "message": "Ansible playbook executed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))