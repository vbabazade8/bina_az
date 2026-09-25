import pandas as pd
import sys

sys.stdout.reconfigure(encoding="utf-8")

df = pd.read_csv("data/items.csv")

# Drop listings with no rooms value — these are land plots or commercial
# properties, not apartments, and don't fit this residential price model.
df_clean = df[df["rooms"].notna()]

# Drop very cheap rows — anything this low isn't a real sale price, it's
# either bad data or a rental listing mixed into the sale data.
df_clean = df_clean[df_clean["price"] >= 5000]

# price_per_m2 catches the rest of the rental contamination: real sale
# prices in Baku run in the thousands per m², rentals in the tens/hundreds.
df_clean["price_per_m2"] = df_clean["price"] / df_clean["area"]
df_clean = df_clean[df_clean["price_per_m2"] >= 300]
df_clean["rooms"] = df_clean["rooms"].astype(int)  # safe now that NaNs are gone

# Drop listings with no location — needed as a feature for the model.
df_clean = df_clean[df_clean["location"].notna()]
df_clean["price_per_m2"] = df_clean["price_per_m2"].round(2)

df_clean.to_csv("data/item_clean.csv", index=False, encoding="utf-8")