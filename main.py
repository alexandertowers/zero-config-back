from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import zipfile
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DeployRequest(BaseModel):
    message: str

def deploy_function(message: str):
    terraform_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../terraform"))
    print(f"Terraform directory: {terraform_dir}")
    try:
        contents = os.listdir(terraform_dir)
        print(f"Directory contents: {contents}")
        main_tf_path = os.path.join(terraform_dir, "main.tf")
        print(f"main.tf exists: {os.path.exists(main_tf_path)}")
        if not os.path.exists(main_tf_path):
            print("main.tf not found—check file location or OneDrive sync")
    except Exception as e:
        print(f"Error listing directory: {e}")

    source_dir = os.path.join(terraform_dir, "function-source")
    os.makedirs(source_dir, exist_ok=True)

    source_file = os.path.join(source_dir, "main.py")
    with open(source_file, "w") as f:
        f.write(f'def hello_world(request):\n    return "Hello World: {message}"')

    zip_path = os.path.join(terraform_dir, "function-source.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(source_file, os.path.relpath(source_file, terraform_dir))

    env = dict(os.environ)
    env["TF_VAR_gcp_project_id"] = os.getenv("TF_VAR_gcp_project_id", "")
    env["TF_VAR_gcp_region"] = os.getenv("TF_VAR_gcp_region", "us-central1")

    try:
        init_result = subprocess.run(
            ["terraform", "init", "-upgrade"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            env=env
        )
        print(f"Init stdout: {init_result.stdout}")
        print(f"Init stderr: {init_result.stderr}")
        init_result.check_returncode()

        apply_result = subprocess.run(
            ["terraform", "apply", "-auto-approve"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            env=env
        )
        print(f"Apply stdout: {apply_result.stdout}")
        print(f"Apply stderr: {apply_result.stderr}")
        apply_result.check_returncode()

        output_result = subprocess.run(
            ["terraform", "output", "function_url"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            env=env
        )
        print(f"Output stdout: {output_result.stdout}")
        print(f"Output stderr: {output_result.stderr}")
        output_result.check_returncode()

        return output_result.stdout.strip().replace('"', '')
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Terraform failed at {e.cmd}: {e.stderr}")

@app.post("/api/deploy")
async def deploy(request: DeployRequest):
    url = deploy_function(request.message)
    return {"url": url}