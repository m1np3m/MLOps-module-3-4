import kfp
from kfp.components import InputPath, OutputPath
from kfp.components import func_to_container_op
import sys, os


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.config import *
from utils.data_utils import genres_and_keywords_to_string


def data_processing(input_df: InputPath("PKL"), df_path: OutputPath("PKL")):
    import os, sys
    import pandas as pd
    import joblib

    ENVIRONMENT = os.getenv("ENVIRONMENT")
    print(f"Running on {ENVIRONMENT}")

    # load data
    df = joblib.load(input_df)

    df["string"] = df.apply(genres_and_keywords_to_string, axis=1)

    joblib.dump(df, df_path)


if __name__ == "__main__":
    print("building data processing component...")
    data_processing_op = func_to_container_op(
        func=data_processing,
        output_component_file=__file__.replace(".py", ".yaml"),
        modules_to_capture=["config.config", "utils.data_utils"],
        packages_to_install=["joblib", "cloudpickle", "pandas", "kfp==1.8.22"],
        use_code_pickling=True,
        base_image=COMPONENT_BASE_IMAGE,
    )
