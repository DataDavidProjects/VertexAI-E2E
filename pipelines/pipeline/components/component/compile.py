from typing import NamedTuple, List, Dict
from kfp import dsl
import yaml
import pandas as pd
import os
from queries.query import generate_query


CONFIG_PATH = "config/pipeline.yaml"
with open(CONFIG_PATH, "r") as f:
    pipeline_config = yaml.safe_load(f)



COMPONENT_NAME = os.path.basename(__file__).split('.')[0]
BASE_IMAGE = pipeline_config["train"]


