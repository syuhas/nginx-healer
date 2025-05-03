import uvicorn


def run():
    uvicorn.run("webhook_healer_api.webhook:app", host="0.0.0.0", port=8000, reload=False)