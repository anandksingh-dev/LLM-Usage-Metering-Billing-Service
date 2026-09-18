from fastapi import FastAPI

app = FastAPI(
    title="Usage Metering & Billing Engine",
    description="FlyRank Backend Capstone",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Usage Metering & Billing Engine API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }