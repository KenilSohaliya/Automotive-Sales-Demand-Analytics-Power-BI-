import pandas as pd
import re

# -----------------------------
# Load datasets
# -----------------------------
used_cars_path = "Datasets/used_cars_germany_2023.csv"
co2_path = "Datasets/co2_emission_train.csv"

used = pd.read_csv(used_cars_path)
co2 = pd.read_csv(co2_path)

# -----------------------------
# Helper functions
# -----------------------------
def clean_text(x):
    """Lowercase + strip + remove extra spaces."""
    if pd.isna(x):
        return x
    x = str(x).strip().lower()
    x = re.sub(r"\s+", " ", x)
    return x

def standardize_fuel(x):
    """
    Map many fuel labels into clean buckets:
    petrol, diesel, electric, hybrid, other
    """
    if pd.isna(x):
        return x
    x = clean_text(x)

    # common variants
    if any(k in x for k in ["electric", "ev", "strom", "battery", "elektro"]):
        return "electric"
    if any(k in x for k in ["hybrid", "plug-in", "plugin", "phev"]):
        return "hybrid"
    if any(k in x for k in ["diesel"]):
        return "diesel"
    if any(k in x for k in ["petrol", "gasoline", "benzin", "benzin"]):
        return "petrol"

    # some datasets use letters or codes
    if x in ["x", "e"]:
        return "electric"
    if x in ["d"]:
        return "diesel"
    if x in ["p", "g"]:
        return "petrol"

    return "other"

# -----------------------------
# CLEAN: Used Cars dataset
# -----------------------------
# Drop index-like column if present
if "no" in used.columns:
    used = used.drop(columns=["no"])

# Clean brand/model text for joining later
used["brand"] = used["brand"].apply(clean_text)
used["model"] = used["model"].apply(clean_text)

# Convert types
used["year"] = pd.to_numeric(used["year"], errors="coerce")
used["price_in_euro"] = pd.to_numeric(used["price_in_euro"], errors="coerce")
used["power_kw"] = pd.to_numeric(used["power_kw"], errors="coerce")
used["mileage_in_km"] = pd.to_numeric(used["mileage_in_km"], errors="coerce")

# Parse registration date
used["registration_date"] = pd.to_datetime(used["registration_date"], errors="coerce")

# Standardize fuel and transmission
used["fuel_type_clean"] = used["fuel_type"].apply(standardize_fuel)
used["transmission_type_clean"] = used["transmission_type"].apply(clean_text)

# Remove rows that are unusable for analysis
used = used.dropna(subset=["year", "price_in_euro", "fuel_type_clean"])

# Basic sanity filters (optional but good)
used = used[(used["price_in_euro"] > 0) & (used["price_in_euro"] < 300000)]
used = used[(used["mileage_in_km"].isna()) | (used["mileage_in_km"] >= 0)]

# -----------------------------
# CLEAN: CO2 dataset
# -----------------------------
# Rename columns to match used cars dataset
rename_map = {
    "Year": "year",
    "Make": "brand",
    "Model": "model",
    "Fuel Type": "fuel_type",
    "Engine Size (L)": "engine_size_l",
    "Motor (kW)": "motor_kw",
    "Fuel Consumption [Comb (L/100 km)]": "fuel_consumption_l_100km",
    "CO2 Emissions (g/km)": "co2_g_km",
}
co2 = co2.rename(columns={k: v for k, v in rename_map.items() if k in co2.columns})

# Keep only key columns if they exist
keep_cols = [c for c in [
    "year", "brand", "model", "fuel_type",
    "engine_size_l", "motor_kw", "fuel_consumption_l_100km", "co2_g_km"
] if c in co2.columns]
co2 = co2[keep_cols].copy()

# Clean text columns
co2["brand"] = co2["brand"].apply(clean_text)
co2["model"] = co2["model"].apply(clean_text)
co2["fuel_type_clean"] = co2["fuel_type"].apply(standardize_fuel)

# Convert numeric columns
for col in ["year", "engine_size_l", "motor_kw", "fuel_consumption_l_100km", "co2_g_km"]:
    if col in co2.columns:
        co2[col] = pd.to_numeric(co2[col], errors="coerce")

# Drop rows missing essentials
co2 = co2.dropna(subset=["year", "brand", "model", "fuel_type_clean", "co2_g_km"])

# Remove duplicates for stable joins later
co2 = co2.drop_duplicates(subset=["brand", "model", "year"], keep="first")

# -----------------------------
# Save cleaned outputs
# -----------------------------
used.to_csv("Datasets/used_cars_clean.csv", index=False)
co2.to_csv("Datasets/co2_clean.csv", index=False)

print("✅ Saved cleaned datasets:")
print(" - Datasets/used_cars_clean.csv")
print(" - Datasets/co2_clean.csv")

print("\nUsed Cars cleaned shape:", used.shape)
print("CO2 cleaned shape:", co2.shape)

print("\nFuel type distribution (Used Cars):")
print(used["fuel_type_clean"].value_counts(dropna=False))

print("\nFuel type distribution (CO2):")
print(co2["fuel_type_clean"].value_counts(dropna=False))
