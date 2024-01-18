import kfp
from kfp.components import InputPath, OutputPath
from kfp.components import func_to_container_op
import sys, os


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.config import *
from utils.feast_utils import FEAST


def data_downloading(training_df_path: OutputPath("PKL")):
    import os, sys
    import pandas as pd
    import joblib
    from feast import FeatureStore
    import subprocess
    import wget
    import time
    from sklearn.linear_model import LinearRegression

    feature_store = FEAST()

    # Fetch historical data for training
    try:
        training_df = feature_store.fetch_historical_features_entity_df(
            for_batch_scoring=False
        ).to_df()
        print(f"columns: {training_df.columns}")
        print("training_df: ", training_df.head())
        joblib.dump(training_df, training_df_path)
    except Exception as e:
        print(f"Error While convert historical data to df: {e}")


if __name__ == "__main__":
    print("building data downloading component...")
    data_downloading_op = func_to_container_op(
        func=data_downloading,
        output_component_file=__file__.replace(".py", ".yaml"),
        modules_to_capture=["config.config", "utils.feast_utils"],
        packages_to_install=[
            "joblib",
            "cloudpickle",
            "pandas",
            "kfp==1.8.22",
            "scikit-learn==1.3.2",
            "SciPy==1.11.4",
            "wget==3.2",
            "feast",
        ],
        use_code_pickling=True,
        base_image=COMPONENT_BASE_IMAGE,
    )
