import pandas as pd
import feast
from joblib import load
from utils.feast_utils import FEAST


class DriverRankingModel:
    def __init__(self, model_path):
        # Initialize Feast
        fs = FEAST()
        self.store = fs.store
        # Load model
        self.model = load(model_path)

    def predict(self, driver_ids):
        # Read features from Feast
        driver_features = self.store.get_online_features(
            entity_rows=[{"driver_id": driver_id} for driver_id in driver_ids],
            features=[
                "driver_hourly_stats:conv_rate",
                "driver_hourly_stats:acc_rate",
                "driver_hourly_stats:avg_daily_trips",
            ],
        )
        df = pd.DataFrame.from_dict(driver_features.to_dict())

        # Make prediction
        df["prediction"] = self.model.predict(df[sorted(df)])

        # Choose best driver
        best_driver_id = df["driver_id"].iloc[df["prediction"].argmax()]

        # return best driver
        return best_driver_id
