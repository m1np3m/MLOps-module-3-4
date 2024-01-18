import kfp
from kfp.components import InputPath, OutputPath
from kfp.components import func_to_container_op
import sys, os


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.config import *
from utils.feast_utils import FEAST


def feature_store(url: str):
    import os, sys
    import pandas as pd
    import joblib
    import feast
    from feast import FeatureStore
    import subprocess
    import wget
    import time
    from sklearn.linear_model import LinearRegression

    store = FEAST()
    # Apply feature repo
    print("\n--- Run feast apply ---")
    subprocess.run(["feast", "apply"])

    # Fetch historical data for training
    try:
        training_df = store.fetch_historical_features_entity_df(store, False).to_df()
        print(f"columns: {training_df.columns}")
        print("training_df: ", training_df.head())
    except Exception as e:
        print(f"Error While convert historical data to df: {e}")

    # Train model
    target = "label_driver_reported_satisfaction"

    print("\n--- Training model ---")
    reg = LinearRegression()
    train_X = training_df[training_df.columns.drop(target).drop("event_timestamp")]
    train_Y = training_df.loc[:, target]
    reg.fit(train_X[sorted(train_X)], train_Y)


if __name__ == "__main__":
    print("building feature store component...")
    feature_store_op = func_to_container_op(
        func=feature_store,
        output_component_file=__file__.replace(".py", ".yaml"),
        modules_to_capture=[
            "config.config",
            "utils.feast_utils",
        ],
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
