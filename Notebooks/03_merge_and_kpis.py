import pandas as pd
import numpy as np

# -----------------------------
# Load cleaned datasets
# -----------------------------
used = pd.read_csv("Datasets/used_cars_clean.csv")
co2 = pd.read_csv("Datasets/co2_clean.csv")

# -----------------------------
# Merge (Left join: keep all used car listings)
# -----------------------------
merged = used.merge(
    co2[["brand", "model", "year", "co2_g_km", "engine_size_l", "motor_kw", "fuel_consumption_l_100km"]],
    on=["brand", "model", "year"],
    how="left"
)

# -----------------------------
# Create useful business features
# -----------------------------

# Car age (relative to listing year)
# Not perfect but good for analysis
merged["car_age"] = (pd.Timestamp.now().year - merged["year"]).astype("Int64")

# Price bands (good for Power BI filters)
merged["price_band"] = pd.cut(
    merged["price_in_euro"],
    bins=[0, 5000, 10000, 20000, 30000, 50000, 100000, 300000],
    labels=["0-5k", "5-10k", "10-20k", "20-30k", "30-50k", "50-100k", "100k+"]
)

# Mileage bands
merged["mileage_band"] = pd.cut(
    merged["mileage_in_km"],
    bins=[-1, 20000, 50000, 100000, 150000, 200000, 5000000],
    labels=["0-20k", "20-50k", "50-100k", "100-150k", "150-200k", "200k+"]
)

# Power bands (kW)
merged["power_band_kw"] = pd.cut(
    merged["power_kw"],
    bins=[0, 50, 75, 100, 150, 250, 2000],
    labels=["0-50", "50-75", "75-100", "100-150", "150-250", "250+"]
)

# CO2 availability flag
merged["has_co2_data"] = np.where(merged["co2_g_km"].notna(), 1, 0)

# -----------------------------
# Create KPI summary tables (for reporting)
# -----------------------------

# 1) Average price by fuel type
kpi_price_fuel = (
    merged.groupby("fuel_type_clean", dropna=False)
    .agg(listings=("price_in_euro", "count"),
         avg_price=("price_in_euro", "mean"),
         median_price=("price_in_euro", "median"))
    .reset_index()
    .sort_values("listings", ascending=False)
)

# 2) EV share by year
kpi_ev_share = (
    merged.assign(is_ev=merged["fuel_type_clean"].eq("electric").astype(int))
    .groupby("year", dropna=False)
    .agg(total_listings=("is_ev", "size"),
         ev_listings=("is_ev", "sum"))
    .reset_index()
)
kpi_ev_share["ev_share_pct"] = (kpi_ev_share["ev_listings"] / kpi_ev_share["total_listings"] * 100).round(2)

# 3) Average CO2 by fuel type (only where CO2 exists)
kpi_co2_fuel = (
    merged[merged["co2_g_km"].notna()]
    .groupby("fuel_type_clean", dropna=False)
    .agg(vehicles_with_co2=("co2_g_km", "count"),
         avg_co2=("co2_g_km", "mean"),
         median_co2=("co2_g_km", "median"))
    .reset_index()
    .sort_values("vehicles_with_co2", ascending=False)
)

# 4) Top brands by listings and average price
kpi_brand = (
    merged.groupby("brand", dropna=False)
    .agg(listings=("price_in_euro", "count"),
         avg_price=("price_in_euro", "mean"))
    .reset_index()
    .sort_values("listings", ascending=False)
    .head(15)
)

# -----------------------------
# Save outputs for Power BI / Excel
# -----------------------------
merged.to_csv("Datasets/merged_powerbi_ready.csv", index=False)

kpi_price_fuel.to_csv("Datasets/kpi_price_by_fuel.csv", index=False)
kpi_ev_share.to_csv("Datasets/kpi_ev_share_by_year.csv", index=False)
kpi_co2_fuel.to_csv("Datasets/kpi_co2_by_fuel.csv", index=False)
kpi_brand.to_csv("Datasets/kpi_top_brands.csv", index=False)

print("✅ Saved Power BI ready dataset:")
print(" - Datasets/merged_powerbi_ready.csv")

print("\n✅ Saved KPI tables:")
print(" - Datasets/kpi_price_by_fuel.csv")
print(" - Datasets/kpi_ev_share_by_year.csv")
print(" - Datasets/kpi_co2_by_fuel.csv")
print(" - Datasets/kpi_top_brands.csv")

print("\n--- Quick Checks ---")
print("Merged shape:", merged.shape)
print("CO2 match rate (% rows with CO2):", round(merged['has_co2_data'].mean() * 100, 2))

print("\nTop 5 fuel types (listings):")
print(merged["fuel_type_clean"].value_counts().head(5))

print("\nTop 10 brands (listings):")
print(merged["brand"].value_counts().head(10))
