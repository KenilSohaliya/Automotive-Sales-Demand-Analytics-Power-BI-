import pandas as pd

used_cars_path = "Datasets/used_cars_germany_2023.csv"
co2_path = "Datasets/co2_emission_train.csv"

used_cars_df = pd.read_csv(used_cars_path)
co2_df = pd.read_csv(co2_path)

print("Used Cars Dataset:")
print(used_cars_df.head())
print(used_cars_df.info())
print(used_cars_df.isnull().sum())

print("\n" + "-" * 50 + "\n")

print("CO2 Emission Dataset:")
print(co2_df.head())
print(co2_df.info())
print(co2_df.isnull().sum())
