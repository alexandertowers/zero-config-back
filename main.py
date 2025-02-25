from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",  # adjust as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # allow front-end domain(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DeployRequest(BaseModel):
    message: str


@app.post("/api/deploy")
async def deploy(request: DeployRequest):
    # Placeholder for Pulumi
    return {"message": f"Hello World: {request.message}"}
