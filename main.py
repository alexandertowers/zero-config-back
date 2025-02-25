from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class DeployRequest(BaseModel):
    message: str

@app.post("/api/deploy")
async def deploy(request: DeployRequest):
    # Placeholder for Pulumi
    return {"message": f"Hello World: {request.message}"}