import os
from datetime import datetime
from kfp import dsl
from kfp import compiler
import yaml
from google.auth import exceptions, default
from google.cloud import aiplatform
from typing import Dict

# Load the pipeline configuration file
CONFIG_PATH = "config/pipeline.yaml"
with open(CONFIG_PATH, "r") as f:
    pipeline_config = yaml.safe_load(f)


def vertex_authenticate(pipeline_config: Dict[str, str]):
    """Authenticate with Google Cloud SDK."""
    # Authenticate with Google Cloud SDK
    try:
        credentials, _ = default()
        aiplatform.init(
            project=pipeline_config.get("project_id"),
            credentials=credentials,
            location=pipeline_config.get("region"),
            staging_bucket=pipeline_config.get("bucket_uri"),
        )
        return aiplatform
        # print("Authenticated with Google Cloud SDK successfully.")
        # print(f"Project ID: {project} \nRegion: {self.config.get('region')}")
    except exceptions.DefaultCredentialsError:
        print("Please authenticate with Google Cloud SDK.")

