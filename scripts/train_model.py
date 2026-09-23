import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib
import sys

sys.stdout.reconfigure(encoding="utf-8")

df = pd.read_csv("data/item_clean.csv")

location_counts = df["location"].value_counts()
common_locations = location_counts[location_counts >= 5].index
df["location"] = df["location"].where(df["location"].isin(common_locations), "Other")

df_encoded = pd.get_dummies(df, columns=["location"])

features = df_encoded.drop(columns=["id", "price", "city", "currency", "price_per_m2"])
target = df_encoded["price"]

features_train, features_test, target_train, target_test = train_test_split(
    features, target, test_size=0.2, random_state=42
)

rf_model = RandomForestRegressor()
rf_model.fit(features_train, target_train)

predictions = rf_model.predict(features_test)

rf_mae = mean_absolute_error(target_test, predictions)

joblib.dump(rf_model, "models/model.pkl")