import pandas as pd
import sys
# import os
# print(os.getcwd())

sys.stdout.reconfigure(encoding="utf-8")

df = pd.read_csv("data/items.csv")

df_clean = df[df["rooms"].notna()]
df_clean = df_clean[df_clean["price"] >= 5000]
df_clean["price_per_m2"] = df_clean["price"] / df_clean["area"]
df_clean = df_clean[df_clean["price_per_m2"] >= 300]
df_clean["rooms"] = df_clean["rooms"].astype(int)
df_clean = df_clean[df_clean["location"].notna()]
df_clean["price_per_m2"] = df_clean["price_per_m2"].round(2)


df_clean.to_csv("data/item_clean.csv", index=False, encoding="utf-8")