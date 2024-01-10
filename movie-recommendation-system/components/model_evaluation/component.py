import kfp
from kfp.components import InputPath, OutputPath
from kfp.components import func_to_container_op
import sys, os


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.config import *


def model_evaluation(
    df: InputPath("PKL"),
    matrix: InputPath("PKL"),
    movie2idx: InputPath("PKL"),
):
    import os, sys
    import pandas as pd
    import joblib
    from sklearn.metrics.pairwise import cosine_similarity
    import matplotlib.pyplot as plt

    ENVIRONMENT = os.getenv("ENVIRONMENT")
    print(f"Running on {ENVIRONMENT}")

    # load data
    df = joblib.load(df)
    X = joblib.load(matrix)
    movie2idx = joblib.load(movie2idx)

    idx = movie2idx["Avatar"]

    query = X[idx]

    # compute similarity between query and every vector in X
    scores = cosine_similarity(query, X)
    scores = scores.flatten()

    plt.plot(scores)

    # get the indexes of the highest scoring movies
    # get the first K recommendations
    # don't return itself!
    recommended_idx = (-scores).argsort()[1:6]

    # return the titles of the recommendations
    recommended_file = df["title"].iloc[recommended_idx]
    print("Recommendations for 'Avatar':" + recommended_file)


if __name__ == "__main__":
    print("building data evaluation component...")
    model_evaluation_op = func_to_container_op(
        func=model_evaluation,
        output_component_file=__file__.replace(".py", ".yaml"),
        modules_to_capture=[
            "config.config",
        ],
        packages_to_install=[
            "joblib",
            "cloudpickle",
            "pandas",
            "kfp==1.8.22",
            "matplotlib==3.8.2",
            "scikit-learn==1.3.2",
            "SciPy==1.11.4",
        ],
        use_code_pickling=True,
        base_image=COMPONENT_BASE_IMAGE,
    )
