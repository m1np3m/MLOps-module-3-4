import kfp
from kfp.components import InputPath, OutputPath
from kfp.components import func_to_container_op
import sys, os


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.config import *
from utils.model_utils import Recommender


def model_training(
    df: InputPath("PKL"),
    matrix_path: OutputPath("PKL"),
    movie2idx_path: OutputPath("PKL"),
):
    import os, sys
    import pandas as pd
    import joblib
    from sklearn.feature_extraction.text import TfidfVectorizer

    ENVIRONMENT = os.getenv("ENVIRONMENT")
    print(f"Running on {ENVIRONMENT}")
    # load data
    df = joblib.load(df)

    recommender = Recommender(df, 2000)

    matrix = recommender.init_matrix()

    movie2idx = recommender.map_movie_title_to_idx()
    print("Done training model")
    joblib.dump(matrix, matrix_path)
    joblib.dump(movie2idx, movie2idx_path)


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
