from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import pandas as pd
import joblib

app = FastAPI()

# Serve the frontend (static/index.html + assets) at /static/*
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load the trained Random Forest model once at startup, not per-request,
# so predictions stay fast. Trained in scripts/train.ipynb.
model = joblib.load("models/model.pkl")


def build_features(rooms, area, floor, has_repair, location):
    """
    Build a single-row DataFrame matching the exact columns the model
    was trained on (model.feature_names_in_), so column order/names
    always line up with what the model expects.
    """
    # Start with a zero-filled row: 4 numeric columns + one column per
    # known location (one-hot encoded), all initialized to 0.
    row = pd.DataFrame(0, index=[0], columns=model.feature_names_in_)

    row["rooms"] = rooms
    row["area"] = area
    row["floor"] = floor
    row["hasRepair"] = int(has_repair)  # bool -> 0/1 for the model

    # One-hot encode location: set the matching column to 1.
    # Unknown/rare locations fall back to "Other", the same bucket
    # used during training for locations with < 5 listings.
    location_col = f"location_{location}"
    if location_col in row.columns:
        row[location_col] = 1
    else:
        row["location_Other"] = 1

    return row


@app.get("/")
def read_root():
    # Redirect the root URL straight to the prediction form.
    return RedirectResponse(url="/static/index.html")


@app.get("/predict")
def predict(rooms: int, area: float, floor: int, has_repair: bool, location: str):
    # FastAPI parses and validates these query params automatically
    # based on the type hints (int/float/bool/str).
    row = build_features(rooms, area, floor, has_repair, location)
    prediction = model.predict(row)
    # prediction is a numpy array with one value; convert to a plain
    # Python float and round it for a cleaner response.
    return {"predicted_price": round(float(prediction[0]))}