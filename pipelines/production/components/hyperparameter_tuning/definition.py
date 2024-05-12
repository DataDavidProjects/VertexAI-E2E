import os
from typing import Dict
from kfp import dsl
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from kfp import compiler


load_dotenv(find_dotenv())


# Define the details component
PROJECT_ID = os.environ.get("PROJECT_ID")
REGION = os.environ.get("REGION")
REPOSITORY = os.environ.get("BUCKET_NAME")  # Match the Bucket name on Artifact Registry

PIPELINE_NAME = (
    Path(__file__).resolve().parents[2].name
)  # Match the directory name of pipeline
COMPONENT_NAME = os.path.basename(os.path.dirname(__file__))  # Match the directory name
BASE_IMAGE = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/{REPOSITORY}/{PIPELINE_NAME}:latest"


@dsl.component(
    base_image=BASE_IMAGE,
)
def hyperparameter_tuning_component():

    from src.features.selection import FeatureEliminationShap
    from sklearn.model_selection import RandomizedSearchCV
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification

    # Create a classification problem
    X, y = make_classification(
        n_samples=1000, n_features=20, n_informative=5, n_redundant=15, random_state=1
    )

    # Define the parameter grid for the random search
    param_grid = {
        "n_estimators": [50, 100, 200],
        "max_depth": [10, 20, 30],
        "min_samples_split": [2, 5, 10],
    }

    # Initialize the base model
    base_model = RandomForestClassifier()

    # Initialize the random search model
    model = RandomizedSearchCV(
        estimator=base_model,
        param_distributions=param_grid,
    )

    # Initialize the feature elimination object
    fe = FeatureEliminationShap(
        model=model,
        step=0.2,
        cv=5,
        scoring="roc_auc",
        standard_error_threshold=0.5,
        return_type="feature_names",
        num_features="best_coherent",
    )

    import time

    time_start = time.time()

    # Run the feature elimination process
    reduced_features = fe.run(X, y)

    print(reduced_features)

    print(f"Time taken: {time.time() - time_start} seconds")


# Compile the component
COMPONENT_FILE = f"pipelines/{PIPELINE_NAME}/components/{COMPONENT_NAME}.yaml"
print(f"Compiling {COMPONENT_FILE}")
compiler.Compiler().compile(hyperparameter_tuning_component, COMPONENT_FILE)
