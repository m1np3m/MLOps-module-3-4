import kfp
from kfp.components import InputPath, OutputPath
from kfp.components import func_to_container_op
import sys, os


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.config import *
from utils.data_utils import genres_and_keywords_to_string


def data_processing(
    training_df: InputPath("PKL"),
    train_X_path: OutputPath("PKL"),
    train_Y_path: OutputPath("PKL"),
):
    import os, sys
    import pandas as pd
    import joblib
    from sklearn.linear_model import LinearRegression

    ENVIRONMENT = os.getenv("ENVIRONMENT")
    print(f"Running on {ENVIRONMENT}")

    # load data
    training_df = joblib.load(training_df)

    target = "label_driver_reported_satisfaction"

    train_X = training_df[training_df.columns.drop(target).drop("event_timestamp")]
    train_X = train_X[sorted(train_X)]
    train_Y = training_df.loc[:, target]

    joblib.dump(train_X, train_X_path)
    joblib.dump(train_Y, train_Y_path)


if __name__ == "__main__":
    print("building data processing component...")
    data_processing_op = func_to_container_op(
        func=data_processing,
        output_component_file=__file__.replace(".py", ".yaml"),
        modules_to_capture=["config.config", "utils.data_utils"],
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
