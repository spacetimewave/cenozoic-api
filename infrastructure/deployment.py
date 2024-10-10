import os
import subprocess
import sys

# Configuration Variables
IMAGE_NAME = "javierhersan/code-ai"
TAG = "latest"  # Or specify your version
DOCKERFILE_PATH = "."  # Assuming the Dockerfile is in the current directory

# Functions
def build_image():
    """Build Docker image"""
    try:
        print(f"Building Docker image '{IMAGE_NAME}:{TAG}'...")
        subprocess.run(["docker", "build", "-t", f"{IMAGE_NAME}:{TAG}", DOCKERFILE_PATH], check=True)
        print("Docker image built successfully!")
    except subprocess.CalledProcessError:
        sys.exit("Error occurred while building the Docker image.")

def login_docker():
    """Login to Docker Hub"""
    try:
        print("Logging into Docker Hub...")
        subprocess.run(["docker", "login"], check=True)
        print("Logged in successfully!")
    except subprocess.CalledProcessError:
        sys.exit("Failed to log in to Docker Hub.")

def push_image():
    """Push the image to Docker Hub"""
    try:
        print(f"Pushing image '{IMAGE_NAME}:{TAG}' to Docker Hub...")
        subprocess.run(["docker", "push", f"{IMAGE_NAME}:{TAG}"], check=True)
        print("Image pushed to Docker Hub successfully!")
    except subprocess.CalledProcessError:
        sys.exit("Failed to push the Docker image.")

def deploy_container():
    """Run the container locally (deployment step)"""
    try:
        print(f"Running Docker container from image '{IMAGE_NAME}:{TAG}'...")
        subprocess.run(["docker", "run", "-d", f"{IMAGE_NAME}:{TAG}"], check=True)
        print("Docker container deployed successfully!")
    except subprocess.CalledProcessError:
        sys.exit("Failed to deploy Docker container.")

# Main process
if __name__ == "__main__":
    # 1. Build Docker image
    build_image()
    # 2. Log in to Docker Hub (if necessary)
    login_docker()
    # 3. Push the Docker image to Docker Hub
    push_image()
    # 4. Deploy the Docker image locally
    # deploy_container()

