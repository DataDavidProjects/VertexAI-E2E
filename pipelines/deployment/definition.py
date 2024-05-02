import os

from kfp import compiler, dsl

from utils.config import vertex_authenticate

# Import components


# Authenticate with Google Cloud SDK for Vertex AI
aiplatform_client = vertex_authenticate()

# Define the pipeline
PIPELINE_NAME = os.path.basename(__file__).split(".")[0]


# Define pipeline arguments for components
pipeline_args = {}


@dsl.pipeline(
    pipeline_root=f"gs://{os.environ.get('BUCKET_NAME')}/{PIPELINE_NAME}/run/",
    name=PIPELINE_NAME,
    description=f"Pipeline on Vertex AI for {PIPELINE_NAME}",
)
def pipeline():
    # Define pipeline steps
    pass


# Compile the pipeline
compiler.Compiler().compile(
    pipeline_func=pipeline, package_path=f"{PIPELINE_NAME}_pipeline.json"
)
