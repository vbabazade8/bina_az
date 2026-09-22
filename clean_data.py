import pandas as pd
import sys

sys.stdout.reconfigure(encoding="utf-8")

df = pd.read_csv("items.csv")

df_clean = df[df["rooms"].notna()]
df_clean = df_clean[df_clean["price"] >= 5000]
df_clean["price_per_m2"] = df_clean["price"] / df_clean["area"]
df_clean = df_clean[df_clean["price_per_m2"] >= 300]
df_clean["rooms"] = df_clean["rooms"].astype(int)
df_clean = df_clean[df_clean["location"].notna()]
print(df_clean.shape)
# print(df_clean["location"].isna().sum())
# print(df_clean.dtypes)
# print(df_clean.shape)
# print(df_clean.sort_values("price_per_m2").head(10))
