import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


# Define the details component
PROJECT_ID = os.environ.get("PROJECT_ID")
REGION = os.environ.get("REGION")
REPOSITORY = os.environ.get("BUCKET_NAME")  # Match the Bucket name on Artifact Registry

PIPELINE_NAME = os.path.basename(os.path.dirname(__file__))  # Match the directory name
COMPONENT_NAME = os.path.basename(__file__).split(".")[0]  # Match the file name
BASE_IMAGE = (
    f"{REGION}-docker.pkg.dev/{PROJECT_ID}/{REPOSITORY}/{PIPELINE_NAME}-image:latest"
)
