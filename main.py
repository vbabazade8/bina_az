from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import pandas as pd
import joblib

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

model = joblib.load("models/model.pkl")

def build_features(rooms, area, floor, has_repair, location):
    row = pd.DataFrame(0, index=[0], columns=model.feature_names_in_)
    row["rooms"] = rooms
    row["area"] = area
    row["floor"] = floor
    row["hasRepair"] = int(has_repair)

    location_col = f"location_{location}"
    if location_col in row.columns:
        row[location_col] = 1
    else:
        row["location_Other"] = 1

    return row

@app.get("/")
def read_root():
    return RedirectResponse(url="/static/index.html")

@app.get("/predict")
def predict(rooms: int, area: float, floor: int, has_repair: bool, location: str):
    row = build_features(rooms, area, floor, has_repair, location)
    prediction = model.predict(row)
    return {"predicted_price": round(float(prediction[0]))}

