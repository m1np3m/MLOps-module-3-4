import kfp
from kfp.components import InputPath, OutputPath
from kfp.components import func_to_container_op
import sys, os


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.config import *
from utils.feast_utils import FEAST
from common.git_common import Git


def data_downloading(training_df_path: OutputPath("PKL")):
    import os, sys
    import pandas as pd
    import joblib
    from feast import FeatureStore
    import subprocess
    import wget
    import time
    from sklearn.linear_model import LinearRegression

    # Download the feast repo
    # repo_url = "git@github.com:m1np3m/MLOps-module-3-4.git"
    # work_dir = "./MLOps-module-3-4"
    # git = Git()
    # git.clone(repo_url, work_dir)
    # os.chdir(work_dir + "/movie-recommendation-system/feast/feature_repo")
    # print(f"Current working directory: {os.listdir(os.getcwd())}")
    feature_store = FEAST()
    # Fetch historical data for training
    try:
        training_df = feature_store.fetch_historical_features_entity_df(
            for_batch_scoring=False
        ).to_df()
        print(f"columns: {training_df.columns}")
        print("training_df: ", training_df.head())
        while True:
            time.sleep(1)
        joblib.dump(training_df, training_df_path)
    except Exception as e:
        print(f"Error While convert historical data to df: {e}")


if __name__ == "__main__":
    print("building data downloading component...")
    data_downloading_op = func_to_container_op(
        func=data_downloading,
        output_component_file=__file__.replace(".py", ".yaml"),
        modules_to_capture=["config.config", "utils.feast_utils", "common.git_common"],
        packages_to_install=[
            "joblib",
            "cloudpickle",
            "pandas",
            "kfp==1.8.22",
            "scikit-learn==1.3.2",
            "SciPy==1.11.4",
            "wget==3.2",
            "feast",
            "psycopg2",
            "GitPython",
        ],
        use_code_pickling=True,
        base_image=COMPONENT_BASE_IMAGE,
    )
