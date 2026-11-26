
import pandas as pd
from pathlib import Path

# 1. Set project paths
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "ecommerce.csv"
OUTPUT_DIR = BASE_DIR / "output"

# Create output folder
OUTPUT_DIR.mkdir(exist_ok=True)

# 2. Read CSV dataset
print("Reading E-commerce dataset...")

df = pd.read_csv(DATA_FILE)

print("Original number of records:", len(df))

# 3. Check missing values
print("\nMissing values:")
print(df.isnull().sum())

# 4. Remove duplicate orders
df = df.drop_duplicates(subset="order_id")

# 5. Convert columns into correct data types
df["order_date"] = pd.to_datetime(
    df["order_date"], errors="coerce"
)

df["quantity"] = pd.to_numeric(
    df["quantity"], errors="coerce"
)

df["price"] = pd.to_numeric(
    df["price"], errors="coerce"
)

# 6. Remove invalid records
df = df.dropna(
    subset=[
        "order_id",
        "order_date",
        "customer",
        "product",
        "category",
        "quantity",
        "price",
        "city"
    ]
)

df = df[
    (df["quantity"] > 0) &
    (df["price"] >= 0)
]

# 7. Calculate total sales
df["total_sales"] = df["quantity"] * df["price"]

# 8. Calculate sales summary
total_orders = len(df)
total_revenue = df["total_sales"].sum()
total_quantity = df["quantity"].sum()
average_order_value = (
    total_revenue / total_orders if total_orders else 0
)

print("\n========== SALES SUMMARY ==========")
print("Total Orders:", total_orders)
print("Total Revenue: Rs.", total_revenue)
print("Total Quantity:", total_quantity)
print("Average Order Value: Rs.", average_order_value)

# 9. Product-wise sales
product_sales = df.groupby(
    "product"
)["total_sales"].sum().reset_index()

# 10. Category-wise sales
category_sales = df.groupby(
    "category"
)["total_sales"].sum().reset_index()

# 11. City-wise sales
city_sales = df.groupby(
    "city"
)["total_sales"].sum().reset_index()

# 12. Monthly sales
df["month"] = df["order_date"].dt.to_period("M").astype(str)

monthly_sales = df.groupby(
    "month"
)["total_sales"].sum().reset_index()

# 13. Save cleaned data and reports
df.to_csv(OUTPUT_DIR / "cleaned_ecommerce.csv", index=False)

product_sales.to_csv(
    OUTPUT_DIR / "product_sales.csv", index=False
)

category_sales.to_csv(
    OUTPUT_DIR / "category_sales.csv", index=False
)

city_sales.to_csv(
    OUTPUT_DIR / "city_sales.csv", index=False
)

monthly_sales.to_csv(
    OUTPUT_DIR / "monthly_sales.csv", index=False
)

print("\nAll reports saved successfully!")
print("Data Engineering Pipeline completed!")
