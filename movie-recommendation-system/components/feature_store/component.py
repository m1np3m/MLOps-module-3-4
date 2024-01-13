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

    # from sklearn.linear_model import LinearRegression

    # Load driver order data
    orders = pd.read_csv(DATA_URL.format(DRIVER_ORDERS_CSV), sep="\t")
    orders["event_timestamp"] = pd.to_datetime(orders["event_timestamp"])

    # Connect to your feature store provider
    ENVIRONMENT = os.getenv("ENVIRONMENT")
    print(f"Running on {ENVIRONMENT}")

    repo_config = RepoConfig(
        registry=RegistryConfig(
            # registry_type="PostgreSQLRegistry",
            # registry_store_type="PostgreSQLRegistryStore",
            path="gs://kend_feature_store_bucket/registry.pb",
        ),
        # registry="./data/registry.db",
        project="feature_store",
        provider="local",
        offline_store=PostgreSQLOfflineStoreConfig(
            host="postgres.postgres.svc.cluster.local",
            database="postgres",
            user="admin",
            password="12341234",
        ),  # Could also be the OfflineStoreConfig e.g. FileOfflineStoreConfig
        online_store=RedisOnlineStoreConfig(
            type="redis",
            redis_type="redis_cluster",
            connection_string="redis-master:6379,redis-replicas:6379,ssl=true,password=HZxUwXSusY",
        ),  # Could also be the OnlineStoreConfig e.g. RedisOnlineStoreConfig
    )
    store = FeatureStore(config=repo_config)
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
            "feast[redis, postgres]",
            "scikit-learn==1.3.2",
            "SciPy==1.11.4",
        ],
        use_code_pickling=True,
        base_image=COMPONENT_BASE_IMAGE,
    )
