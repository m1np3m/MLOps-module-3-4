import sys, os
import subprocess
from datetime import datetime
from pathlib import Path
import wget
import pandas as pd
from feast import FeatureStore


class FEAST:
    def __init__(self) -> None:
        # Initiate Feast Store
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

        self.store = FeatureStore(repo_path=".")
        pass

    def fetch_historical_features_entity_df(self, for_batch_scoring: bool):
        # Note: see https://docs.feast.dev/getting-started/concepts/feature-retrieval for more details on how to retrieve
        # for all entities in the offline store instead
        entity_df = pd.DataFrame.from_dict(
            {
                # entity's join key -> entity values
                "driver_id": [1001, 1002, 1003],
                # "event_timestamp" (reserved key) -> timestamps
                "event_timestamp": [
                    datetime(2021, 4, 12, 10, 59, 42),
                    datetime(2021, 4, 12, 8, 12, 10),
                    datetime(2021, 4, 12, 16, 40, 26),
                ],
                # (optional) label name -> label values. Feast does not process these
                "label_driver_reported_satisfaction": [1, 5, 3],
                # values we're using for an on-demand transformation
                "val_to_add": [1, 2, 3],
                "val_to_add_2": [10, 20, 30],
            }
        )
        # For batch scoring, we want the latest timestamps
        if for_batch_scoring:
            entity_df["event_timestamp"] = pd.to_datetime("now", utc=True)

        training_df = self.store.get_historical_features(
            entity_df=entity_df,
            features=[
                "driver_hourly_stats:conv_rate",
                "driver_hourly_stats:acc_rate",
                "driver_hourly_stats:avg_daily_trips",
                "transformed_conv_rate:conv_rate_plus_val1",
                "transformed_conv_rate:conv_rate_plus_val2",
            ],
        )
        return training_df


# def fetch_online_features(store, source: str = ""):
#     entity_rows = [
#         # {join_key: entity_value}
#         {
#             "driver_id": 1001,
#             "val_to_add": 1000,
#             "val_to_add_2": 2000,
#         },
#         {
#             "driver_id": 1002,
#             "val_to_add": 1001,
#             "val_to_add_2": 2002,
#         },
#     ]
#     if source == "feature_service":
#         features_to_fetch = store.get_feature_service("driver_activity_v1")
#     elif source == "push":
#         features_to_fetch = store.get_feature_service("driver_activity_v3")
#     else:
#         features_to_fetch = [
#             "driver_hourly_stats:acc_rate",
#             "transformed_conv_rate:conv_rate_plus_val1",
#             "transformed_conv_rate:conv_rate_plus_val2",
#         ]
#     returned_features = store.get_online_features(
#         features=features_to_fetch,
#         entity_rows=entity_rows,
#     ).to_dict()
#     for key, value in sorted(returned_features.items()):
#         print(key, " : ", value)


# def get_offline_store_from_config(
#     offline_store_config: OfflineStoreConfig,
# ) -> OfflineStore:
#     """Get the offline store from offline store config"""

#     if isinstance(offline_store_config, FileOfflineStoreConfig):
#         from feast.infra.offline_stores.file import FileOfflineStore

#         return FileOfflineStore()
#     elif isinstance(offline_store_config, BigQueryOfflineStoreConfig):
#         from feast.infra.offline_stores.bigquery import BigQueryOfflineStore

#         return BigQueryOfflineStore()

#     raise ValueError(f"Unsupported offline store config '{offline_store_config}'")


# # def assert_offline_store_supports_data_source(
# #     offline_store_config: OfflineStoreConfig, data_source: DataSource
# # ):
# #     if (
# #         isinstance(offline_store_config, FileOfflineStoreConfig)
# #         and isinstance(data_source, FileSource)
# #     ) or (
# #         isinstance(offline_store_config, BigQueryOfflineStoreConfig)
# #         and isinstance(data_source, BigQuerySource)
# #     ):
# #         return
# #     raise FeastOfflineStoreUnsupportedDataSource(
# #         offline_store_config.type, data_source.__class__.__name__
# #     )
