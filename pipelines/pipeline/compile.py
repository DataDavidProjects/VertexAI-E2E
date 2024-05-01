import os
from datetime import datetime
from kfp import dsl
from kfp import compiler
import yaml
from google.auth import exceptions, default
from google.cloud import aiplatform
from typing import Dict
from components.data_fetching.component import data_fetching
from components.processing.component import processing
from components.features.component import features
from components.feature_selection.component import feature_selection
from components.hyperparameter_tuning.component import hyperparameter_tuning
from components.training.component import training
from components.evaluation.component import evaluation

# Load the pipeline configuration file
CONFIG_PATH = "conf/components/config.yaml"
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


# Authenticate with Google Cloud SDK for Vertex AI
aiplatform_client = vertex_authenticate(pipeline_config)


# Define the pipeline
PIPELINE_NAME = os.path.basename(__file__).split('.')[0]


# Define pipeline arguments for steps
pipeline_args = {
    "data_fetching": {
        "files": ["X_train"],
        "input_path": pipeline_config["01_raw"],
    },
    "processing": {
        "files": ["X_train"],
        "input_path": pipeline_config["03_primary"],
    },
    "features": {
        "files": ["X_train"],
        "input_path": pipeline_config["04_processing"],
    },
    "features_selection": {
        "files": ["X_train"],
        "input_path": pipeline_config["05_features"],
    },
    "hyperparameter_tuning": {
        "files": ["X_train"],
        "input_path": pipeline_config["06_scoring"],
    },
    "training": {
        "files": ["X_train"],
        "input_path": pipeline_config["06_scoring"],
    },
    "evaluation": {
        "files": ["X_train"],
        "input_path": pipeline_config["06_scoring"],
    },
    "deployment": {
        "files": ["X_train"],
        "input_path": pipeline_config["06_scoring"],
        "clients": aiplatform_client,
        "pipeline_config": pipeline_config,
    },
}


@dsl.pipeline(
    pipeline_root=pipeline_config["pipeline_root"],
    name=PIPELINE_NAME,
    description="Custom Pipeline for MLOps",
)
def pipeline():

    # Data fetching
    data_fetching_task = data_fetching(
        files=pipeline_args["data_fetching"]["files"],
        input_path=pipeline_args["data_fetching"]["input_path"],
        pipeline_config=pipeline_config,
    )
    # Processing
    processing_task = processing(
        files=pipeline_args["processing"]["files"],
        input_path=pipeline_args["processing"]["input_path"],
        pipeline_config=pipeline_config,
    )
    processing_task.after(data_fetching_task)

    # Features engineering
    features_task = features(
        files=pipeline_args["processing"]["files"],
        input_path=pipeline_args["processing"]["input_path"],
        pipeline_config=pipeline_config,
    )
    features_task.after(processing_task)

    # Feature selection
    features_selection_task = feature_selection(
        files=pipeline_args["processing"]["files"],
        input_path=pipeline_args["processing"]["input_path"],
        pipeline_config=pipeline_config,
    )
    features_selection_task.after(features_task)

    # Hyperparameter tuning
    hyperparameter_tuning_task = hyperparameter_tuning(
        files=pipeline_args["processing"]["files"],
        input_path=pipeline_args["processing"]["input_path"],
        pipeline_config=pipeline_config,
    )
    hyperparameter_tuning_task.after(features_selection_task)

    # Training
    training_task = training(
        files=pipeline_args["processing"]["files"],
        input_path=pipeline_args["processing"]["input_path"],
        pipeline_config=pipeline_config,
    )
    training_task.after(features_selection_task)

    # Evaluation
    evaluation_task = evaluation(
        files=pipeline_args["processing"]["files"],
        input_path=pipeline_args["processing"]["input_path"],
        pipeline_config=pipeline_config,
        model=training_task.outputs["model"],
    )
    evaluation_task.after(training_task)


# Compile the pipeline
compiler.Compiler().compile(
    pipeline_func=pipeline, package_path="pipeline/pipeline-mlops.json"
)
