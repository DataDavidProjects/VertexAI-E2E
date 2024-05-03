import os
from pathlib import Path
from kfp import compiler, dsl

from utils.vertexai import vertex_authenticate

# Import components
from components.hyperparameter_tuning.definition import hyperparameter_tuning_component


# Authenticate with Google Cloud SDK for Vertex AI
aiplatform_client = vertex_authenticate()

# Define the pipeline
PIPELINE_NAME = Path(__file__).resolve().parents[0].name


# Define pipeline arguments for components configs
pipeline_args = {
    # Component Configs
    "hyperparameter_tuning_component": {
        "component_args": {
            "project_id": os.environ.get("PROJECT_ID"),
            "region": os.environ.get("REGION"),
            "bucket_name": os.environ.get("BUCKET_NAME"),
            "pipeline_name": PIPELINE_NAME,
        },
    }
}


@dsl.pipeline(
    pipeline_root=f"gs://{os.environ.get('BUCKET_NAME')}/{PIPELINE_NAME}/run/",
    name=PIPELINE_NAME,
    description=f"Pipeline on Vertex AI for {PIPELINE_NAME}",
)
def pipeline():
    # Define pipeline steps using components
    hyperparameter_tuning_component()
    pass


# Compile the pipeline
compiler.Compiler().compile(
    pipeline_func=pipeline,
    package_path=f"pipelines/{PIPELINE_NAME}/{PIPELINE_NAME}_pipeline.json",
)
