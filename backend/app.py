from fastapi import FastAPI

app = FastAPI(title="FIXORA")

@app.get("/")
def home():
    return {
        "message": "FIXORA Troubleshooting Engine is running!"
    }
