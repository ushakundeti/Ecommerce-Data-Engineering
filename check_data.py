import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "ecommerce.csv"

df = pd.read_csv(DATA_FILE)

print("Dataset loaded successfully!")
print("Number of records:", len(df))
print("\\nFirst 5 records:")
print(df.head())
print("\\nColumn names:")
print(df.columns.tolist())
