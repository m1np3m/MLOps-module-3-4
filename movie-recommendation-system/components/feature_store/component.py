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
    from feast import RepoConfig, FeatureStore
    from feast.repo_config import RegistryConfig
    from feast.infra.offline_stores.contrib.postgres_offline_store.postgres import (
        PostgreSQLOfflineStoreConfig,
    )
    from feast.infra.online_stores.redis import RedisOnlineStoreConfig
    from joblib import dump
    import subprocess
    import wget
    from datetime import timedelta
    from feast import (
        Entity,
        FeatureService,
        FeatureView,
        Field,
        FileSource,
        PushSource,
        RequestSource,
    )

    from feast.on_demand_feature_view import on_demand_feature_view
    from feast.types import Float32, Float64, Int64

    # from sklearn.linear_model import LinearRegression

    # Load driver order data
    orders = pd.read_csv(DATA_URL.format(DRIVER_ORDERS_CSV), sep="\t")
    orders["event_timestamp"] = pd.to_datetime(orders["event_timestamp"])
    data_path = "./data"

    # Down load the registry
    registry_db_url = "https://github.com/m1np3m/MLOps-module-3-4/raw/main/movie-recommendation-system/feast/feature_repo/data/registry.db"
    driver_stats_parquet_url = "https://github.com/m1np3m/MLOps-module-3-4/raw/main/movie-recommendation-system/feast/feature_repo/data/driver_stats.parquet"
    feature_store_url = "https://raw.githubusercontent.com/m1np3m/MLOps-module-3-4/main/movie-recommendation-system/feast/feature_repo/feature_store.yaml"
    Path("./data").mkdir(parents=True, exist_ok=True)
    registry_db = wget.download(registry_db_url, out=data_path)
    print(f"registry_db existed: { os.path.exists(registry_db)}")
    driver_stats_parquet = wget.download(driver_stats_parquet_url, out=data_path)
    print(f"driver_stats_parquet existed: { os.path.exists(driver_stats_parquet)}")
    feature_store_parquet = wget.download(feature_store_url)
    print(f"feature_store.yaml existed: { os.path.exists(feature_store_parquet)}")

    example_feature_repo = wget.download(
        "https://raw.githubusercontent.com/m1np3m/MLOps-module-3-4/main/movie-recommendation-system/feast/feature_repo/example_repo.py"
    )
    print(f"example_feature_repo existed: {os.path.exists(example_feature_repo)}")

    subprocess.run(["ls", "-l", "./data"])

    store = FeatureStore(repo_path=".")
    print("\n--- Run feast apply ---")
    subprocess.run(["feast", "apply"])

    fetch_historical_features_entity_df(store, False)


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
            "feast",
            "scikit-learn==1.3.2",
            "SciPy==1.11.4",
            "wget==3.2",
            "psycopg2",
            "feast[redis]",
        ],
        use_code_pickling=True,
        base_image=COMPONENT_BASE_IMAGE,
    )
