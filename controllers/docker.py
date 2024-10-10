import docker
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models.container import Container
from repositories.database_repository import get_db, get_user_by_email
from controllers.auth import oauth2_scheme

from repositories.auth_repository import verify_token

docker_router = APIRouter()

client = docker.from_env()

class StartContainerRequest(BaseModel):
    user_mail: str
    token: str

@docker_router.post("/docker/create-container")
def create_container(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Start a Docker container with the specified image.
    :param image_name: The name of the Docker image to use (e.g., "nginx", "ubuntu")
    """
    try:
        print(token)
        payload = verify_token(token)

        if payload == None: 
            return {"message": "Invalid credentials"}

        IMAGE_NAME = "javierhersan/code-ai"
        print(f"Starting container with image: {IMAGE_NAME}")
        # Pull the image if not available locally
        client.images.pull(IMAGE_NAME)
        # Start a container with the image
        container = client.containers.create(IMAGE_NAME)
        # container = client.containers.run(IMAGE_NAME, detach=True)

        user = get_user_by_email(db, payload.get('sub'))
        if user:
            new_container = Container(
                container_id=container.id, 
                container_name=IMAGE_NAME, 
                user_id=user.id,
                status=container.status
            )
            db.add(new_container)
            db.commit()
            db.refresh(new_container)

        return {"id":new_container.id, "container_id": new_container.id, "container_id": container.id, "container_name": IMAGE_NAME, "user_id":user.id, "status": container.status}
    
    except docker.errors.ImageNotFound:
        raise HTTPException(status_code=404, detail=f"Docker image {IMAGE_NAME} not found.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting container: {str(e)}")

@docker_router.get("/docker/user-containers")
def list_user_containers(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    List all containers associated with a user.
    """
    token_payload = verify_token(token)
    
    if token_payload == None: 
        return {"message": "Invalid credentials"}
    
    user = token_payload.get('sub')
    
    user = get_user_by_email(db, user)
    if user:
        containers = db.query(Container).filter(Container.user_id == user.id).all()
        return {"containers": containers}
    else:
        raise HTTPException(status_code=404, detail="User not found.")

@docker_router.put("/docker/stop-container/{container_id}")
def stop_user_container(container_id: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    token_payload = verify_token(token)
    
    if token_payload is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = token_payload.get('sub')
    user = get_user_by_email(db, user)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    container = db.query(Container).filter(Container.container_id == container_id, Container.user_id == user.id).first()
    if not container:
        raise HTTPException(status_code=404, detail="Container not found or does not belong to the user")
    
    try:
        docker_container = client.containers.get(container.container_id)
        docker_container.stop()
        
        container.status = 'exited'
        db.commit()
        db.refresh(container)
        
        return {"message": "Container deleted successfully"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Docker container not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting container: {str(e)}")
    
@docker_router.put("/docker/start-container/{container_id}")
def start_user_container(container_id: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    token_payload = verify_token(token)
    
    if token_payload is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = token_payload.get('sub')
    user = get_user_by_email(db, user)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    container = db.query(Container).filter(Container.container_id == container_id, Container.user_id == user.id).first()
    if not container:
        raise HTTPException(status_code=404, detail="Container not found or does not belong to the user")
    
    try:
        docker_container = client.containers.get(container.container_id)
        docker_container.start()
        
        container.status = 'running'
        db.commit()
        db.refresh(container)
        
        return {"message": "Container deleted successfully"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Docker container not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting container: {str(e)}")

@docker_router.delete("/docker/delete-container/{container_id}")
def delete_user_container(container_id: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Delete a Docker container associated with a user.
    """
    token_payload = verify_token(token)
    
    if token_payload is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = token_payload.get('sub')
    user = get_user_by_email(db, user)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    container = db.query(Container).filter(Container.container_id == container_id, Container.user_id == user.id).first()
    if not container:
        raise HTTPException(status_code=404, detail="Container not found or does not belong to the user")
    
    try:
        docker_container = client.containers.get(container.container_id)
        docker_container.stop()
        docker_container.remove()
        
        db.delete(container)
        db.commit()
        
        return {"message": "Container deleted successfully"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Docker container not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting container: {str(e)}")

class ExecCommandRequest(BaseModel):
    command: str  # Command to be executed in the container

@docker_router.post("/docker/exec-command/{container_id}")
def exec_command(container_id: str, exec_request: ExecCommandRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Execute a command inside a running Docker container.
    """
    token_payload = verify_token(token)

    if token_payload is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = token_payload.get('sub')
    user = get_user_by_email(db, user)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    container = db.query(Container).filter(Container.container_id == container_id, Container.user_id == user.id).first()
    if not container:
        raise HTTPException(status_code=404, detail="Container not found or does not belong to the user")
    
    try:
        docker_container = client.containers.get(container.container_id)
        
        if docker_container.status != 'running':
            raise HTTPException(status_code=400, detail="Container is not running")
        
        # Execute the command inside the container
        exec_result = docker_container.exec_run(exec_request.command, tty=True)
        
        if exec_result.exit_code == 0:
            return {"message": "Command executed successfully", "output": exec_result.output.decode("utf-8")}
        else:
            return {"message": "Command failed", "output": exec_result.output.decode("utf-8"), "exit_code": exec_result.exit_code}

    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Docker container not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing command: {str(e)}")
