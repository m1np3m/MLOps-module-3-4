import kfp
from kfp.components import InputPath, OutputPath
from kfp.components import func_to_container_op
import sys, os


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.config import *


def model_training(
    train_X: InputPath("PKL"),
    train_Y: InputPath("PKL"),
):
    import os, sys
    import pandas as pd
    import joblib
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LinearRegression

    ENVIRONMENT = os.getenv("ENVIRONMENT")
    print(f"Running on {ENVIRONMENT}")
    # load data
    train_X = joblib.load(train_X)
    train_Y = joblib.load(train_Y)

    print("\n--- Training model ---")
    reg = LinearRegression()
    reg.fit(train_X, train_Y)

    print("Done training model")


if __name__ == "__main__":
    print("building model training component...")
    model_training_op = func_to_container_op(
        func=model_training,
        output_component_file=__file__.replace(".py", ".yaml"),
        modules_to_capture=[
            "config.config",
            "utils.model_utils",
        ],
        packages_to_install=[
            "joblib",
            "cloudpickle",
            "pandas",
            "kfp==1.8.22",
            "scikit-learn==1.3.2",
            "SciPy==1.11.4",
        ],
        use_code_pickling=True,
        base_image=COMPONENT_BASE_IMAGE,
    )
