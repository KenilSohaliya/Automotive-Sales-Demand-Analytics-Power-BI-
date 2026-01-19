import pandas as pd
import re

# Load cleaned datasets
used = pd.read_csv("Datasets/used_cars_clean.csv")
co2 = pd.read_csv("Datasets/co2_clean.csv")

def normalize_text(x):
    if pd.isna(x):
        return x
    x = str(x).lower().strip()
    x = re.sub(r"[^a-z0-9\s]", " ", x)  # remove special chars
    x = re.sub(r"\s+", " ", x)         # collapse spaces
    return x

def get_model_base(m):
    """
    Create a base model name for joining.
    Examples:
      "golf vii 1.6 tdi" -> "golf"
      "3 series 320d" -> "3 series"
      "a class 180" -> "a class"
    """
    if pd.isna(m):
        return m
    tokens = m.split()

    # cases like "3 series", "5 series"
    if len(tokens) >= 2 and tokens[0].isdigit():
        return " ".join(tokens[:2])

    # cases like "a class", "c class", "e class"
    if len(tokens) >= 2 and tokens[1] == "class":
        return " ".join(tokens[:2])

    # default: first word only
    return tokens[0]

# Normalize join keys
used["brand_n"] = used["brand"].apply(normalize_text)
used["model_n"] = used["model"].apply(normalize_text)

co2["brand_n"] = co2["brand"].apply(normalize_text)
co2["model_n"] = co2["model"].apply(normalize_text)

# Create model_base for better matching
used["model_base"] = used["model_n"].apply(get_model_base)
co2["model_base"] = co2["model_n"].apply(get_model_base)

# Merge: keep all used car listings, attach CO2/specs where match found
merged2 = used.merge(
    co2[["brand_n", "model_base", "year", "co2_g_km", "engine_size_l", "motor_kw", "fuel_consumption_l_100km"]],
    on=["brand_n", "model_base", "year"],
    how="left"
)

# Match rate check
match_count = merged2["co2_g_km"].notna().sum()
total = len(merged2)
match_rate = (match_count / total) * 100 if total else 0

print("Merged rows:", total)
print("CO2 matched rows:", match_count)
print("CO2 match rate (%):", round(match_rate, 2))

# ✅ IMPORTANT: overwrite the original file that Power BI uses
merged2.to_csv("Datasets/merged_powerbi_ready.csv", index=False)
print("\n✅ Overwritten: Datasets/merged_powerbi_ready.csv")
