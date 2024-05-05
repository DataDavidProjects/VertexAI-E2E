from google.cloud.aiplatform import pipeline_jobs
from pathlib import Path
from datetime import datetime
from dotenv import find_dotenv, load_dotenv
import os

# Load environment variables from .env file
load_dotenv(find_dotenv())


# Define the pipeline
PIPELINE_NAME = Path(__file__).resolve().parents[0].name


PROJECT_ID = os.environ.get("PROJECT_ID")
REGION = os.environ.get("REGION")
TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")
# Define the pipeline
PIPELINE_NAME = Path(__file__).resolve().parents[0].name

start_pipeline = pipeline_jobs.PipelineJob(
    display_name=PIPELINE_NAME,
    template_path=f"pipelines/{PIPELINE_NAME}/{PIPELINE_NAME}_pipeline.json",
    enable_caching=False,
    location=REGION,
    project=PROJECT_ID,
    job_id=f"{PIPELINE_NAME}-{TIMESTAMP}",
)


# Run the pipeline
# Note : Update Containter if new changes are made in src
start_pipeline.run()
