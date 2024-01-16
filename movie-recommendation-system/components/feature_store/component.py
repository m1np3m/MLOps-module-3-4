import kfp
from kfp.components import InputPath, OutputPath
from kfp.components import func_to_container_op
import sys, os


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.config import *
from utils.feast_utils import fetch_historical_features_entity_df


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

    # Load driver order data
    orders = pd.read_csv(DATA_URL.format(DRIVER_ORDERS_CSV), sep="\t")
    orders["event_timestamp"] = pd.to_datetime(orders["event_timestamp"])
    data_path = "./data"

    # Download the feast repo
    registry_db_url = "https://github.com/m1np3m/MLOps-module-3-4/raw/main/movie-recommendation-system/feast/feature_repo/data/registry.db"
    driver_stats_parquet_url = "https://github.com/m1np3m/MLOps-module-3-4/raw/main/movie-recommendation-system/feast/feature_repo/data/driver_stats.parquet"
    feature_store_url = "https://raw.githubusercontent.com/m1np3m/MLOps-module-3-4/main/movie-recommendation-system/feast/feature_repo/feature_store.yaml"
    online_db_url = "https://github.com/m1np3m/MLOps-module-3-4/raw/main/movie-recommendation-system/feast/feature_repo/data/online_store.db"
    test_fill_flow_url = "https://raw.githubusercontent.com/m1np3m/MLOps-module-3-4/main/movie-recommendation-system/feast/feature_repo/test_workflow.py"
    Path("./data").mkdir(parents=True, exist_ok=True)
    registry_db = wget.download(registry_db_url, out=data_path)
    print(f"registry_db existed: { os.path.exists(registry_db)}")
    driver_stats_parquet = wget.download(driver_stats_parquet_url, out=data_path)
    print(f"driver_stats_parquet existed: { os.path.exists(driver_stats_parquet)}")
    feature_store_parquet = wget.download(feature_store_url)
    print(f"feature_store.yaml existed: { os.path.exists(feature_store_parquet)}")
    online_db = wget.download(online_db_url, out=data_path)
    print(f"online.db existed: { os.path.exists(online_db)}")
    example_feature_repo = wget.download(
        "https://raw.githubusercontent.com/m1np3m/MLOps-module-3-4/main/movie-recommendation-system/feast/feature_repo/example_repo.py"
    )
    print(f"example_feature_repo existed: {os.path.exists(example_feature_repo)}")
    test_fill_flow_py = wget.download(test_fill_flow_url)
    print(f"test_fill_flow.py existed: {os.path.exists(test_fill_flow_py)}")

    # Initiate Feast Store
    store = FeatureStore(repo_path=".")
    # Apply feature repo
    print("\n--- Run feast apply ---")
    subprocess.run(["feast", "apply"])

    # Fetch historical data for training
    try:
        # feature_service = store.get_feature_service("driver_activity_v1")
        # training_df = store.get_historical_features(
        #     features=feature_service, entity_df=orders
        # )
        training_df = fetch_historical_features_entity_df(store, False).to_df()
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
