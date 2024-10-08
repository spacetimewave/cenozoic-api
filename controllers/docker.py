import docker
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Create a new FastAPI router for docker operations
docker_router = APIRouter()

# Initialize Docker client
client = docker.from_env()

class StartContainerRequest(BaseModel):
    image_name: str

@docker_router.post("/start-container")
def start_container(req: StartContainerRequest):
    """
    Start a Docker container with the specified image.
    :param image_name: The name of the Docker image to use (e.g., "nginx", "ubuntu")
    """
    try:
        print(f"Starting container with image: {req.image_name}")
        # Pull the image if not available locally
        client.images.pull(req.image_name)
        # Start a container with the image
        container = client.containers.run(req.image_name, detach=True)
        return {"message": "Container started", "container_id": container.id, "status": container.status}
    
    except docker.errors.ImageNotFound:
        raise HTTPException(status_code=404, detail=f"Docker image {req.image_name} not found.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting container: {str(e)}")
