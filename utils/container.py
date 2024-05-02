import os

from dotenv import find_dotenv, load_dotenv
from project import DockerConfig

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Define the Docker configuration
container_args = {
    "deployment": {
        "image_name": "deployment",
        "image_tag": "latest",
        "dockerfile_path": "pipelines/deployment/Dockerfile",
        # Repository_id match the bucket name for consistency
        "repository_id": os.environ.get("BUCKET_NAME"),
        "project_id": os.environ.get("PROJECT_ID"),
        "region": os.environ.get("REGION"),
    },
    "training": {
        "image_name": "training",
        "image_tag": "latest",
        "dockerfile_path": "pipelines/training/Dockerfile",
        # Repository_id match the bucket name for consistency
        "repository_id": os.environ.get("BUCKET_NAME"),
        "project_id": os.environ.get("PROJECT_ID"),
        "region": os.environ.get("REGION"),
    },
}


# Create a DockerConfig instance
docker_config_deployment = DockerConfig(config=container_args["deployment"])
docker_config_training = DockerConfig(config=container_args["training"])

# Create the Docker container process
docker_config_deployment.create_container()
docker_config_training.create_container()
