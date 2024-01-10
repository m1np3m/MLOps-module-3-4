import kfp
from kfp.components import InputPath, OutputPath
from kfp.components import func_to_container_op
import sys, os


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.config import *


def data_downloading(url: str, data_path: OutputPath("PKL")):
    import os, sys
    import pandas as pd
    import joblib

    ENVIRONMENT = os.getenv("ENVIRONMENT")
    print(f"Running on {ENVIRONMENT}")

    df = pd.read_csv(DATA_URL.format(MOVIES_CSV))

    print(f"Successfully download data shape: {df.shape}")

    joblib.dump(df, data_path)


if __name__ == "__main__":
    print("building data downloading component...")
    data_downloading_op = func_to_container_op(
        func=data_downloading,
        output_component_file=__file__.replace(".py", ".yaml"),
        modules_to_capture=[
            "config.config",
        ],
        packages_to_install=["joblib", "cloudpickle", "pandas", "kfp==1.8.22"],
        use_code_pickling=True,
        base_image=COMPONENT_BASE_IMAGE,
    )
