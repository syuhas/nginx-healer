import uvicorn


def run():
    uvicorn.run("webhook:app", host="0.0.0.0", port=8000, reload=False)