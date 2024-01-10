from pathlib import Path
import datetime
from uuid import uuid4

# https://www.kaggle.com/tmdb/tmdb-movie-metadata
DATA_URL = "https://raw.githubusercontent.com/CTopham/TophamRepo/master/Movie%20Project/Resources/{}"
MOVIES_CSV = "tmdb_5000_movies.csv"

BASE_DIR = Path(__file__).parent.parent.absolute()
CONFIG_DIR = Path(BASE_DIR, "config")
COMPONENTS_DIR = Path(BASE_DIR, "components")

# Kubeflow
KF_USERNAME = "user"
KF_PASSWORD = "Mxthg3uShI"
NAMESPACE = "kubeflow-user"
HOST = "http://10.10.10.10:8080"

# Directories
BASE_DIR = Path(__file__).parent.parent.absolute()
CONFIG_DIR = Path(BASE_DIR, "config")
COMPONENTS_DIR = Path(BASE_DIR, "components")

# Pipeline
PIPELINE_NAME = "film-recommendation"
PIPELINE_DESCRIPTION = "Batch training pipeline for file recommender"
PIPELINE_VERSION = datetime.datetime.now().strftime("%Y%m-%d%H-%M%S-") + str(uuid4())
EXPERIMENT_NAME = "film-recommendation-exp"
NUM_PODS_PARALLEL = 2

# cron job
JOB_NAME = "cron_film-recommendation"
JOB_DESCRIPTION = "cron job for daily training pipeline."
JOB_EXPRESSION = "0 00 11 * * *"

# component's base image
COMPONENT_BASE_IMAGE = "python:3.10"
