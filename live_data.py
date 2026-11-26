
import sqlite3
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "ecommerce.csv"
DB_FILE = BASE_DIR / "ecommerce.db"

API_URL = "https://dummyjson.com/carts?limit=30"
PRODUCT_URL = "https://dummyjson.com/products?limit=0"

COLUMNS = [
    "order_id", "order_date", "customer", "product",
    "category", "quantity", "price", "city"
]


# 1. Create database
def create_database():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ecommerce_orders (
                order_id TEXT PRIMARY KEY,
                order_date TEXT,
                customer TEXT,
                product TEXT,
                category TEXT,
                quantity INTEGER,
                price REAL,
                city TEXT
            )
        """)


# 2. Load original dataset
def load_existing_dataset():
    if not DATA_FILE.exists():
        print("Dataset not found:", DATA_FILE)
        return

    with sqlite3.connect(DB_FILE) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM ecommerce_orders"
        ).fetchone()[0]

        if count == 0:
            df = pd.read_csv(DATA_FILE)

            missing = set(COLUMNS) - set(df.columns)
            if missing:
                raise ValueError(f"Missing CSV columns: {missing}")

            df = df[COLUMNS]
            df.to_sql(
                "ecommerce_orders",
                conn,
                if_exists="append",
                index=False
            )
            print("Original records loaded:", len(df))


# 3. Fetch product categories
def fetch_categories():
    response = requests.get(PRODUCT_URL, timeout=30)
    response.raise_for_status()

    products = response.json().get("products", [])

    return {
        str(p["id"]): p.get("category", "Uncategorized")
        for p in products
    }


# 4. Fetch sample shopping cart records
def fetch_live_data():
    categories = fetch_categories()

    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    carts = response.json().get("carts", [])
    records = []

    for cart in carts:
        for product in cart.get("products", []):
            product_id = str(product["id"])

            records.append({
                "order_id": f"API-{cart['id']}-{product_id}",
                "order_date": datetime.now().strftime("%Y-%m-%d"),
                "customer": f"Customer {cart['userId']}",
                "product": product.get("title", "Unknown"),
                "category": categories.get(
                    product_id, "Uncategorized"
                ),
                "quantity": product.get("quantity", 0),
                "price": product.get("price", 0),
                "city": "API Sample Data"
            })

    return pd.DataFrame(records, columns=COLUMNS)


# 5. Save new records and correct old API categories
def save_new_records(df):
    inserted = 0

    with sqlite3.connect(DB_FILE) as conn:
        for _, row in df.iterrows():
            values = tuple(row[column] for column in COLUMNS)

            cursor = conn.execute("""
                INSERT OR IGNORE INTO ecommerce_orders
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, values)

            inserted += cursor.rowcount

            # Correct category even when the order already exists
            conn.execute("""
                UPDATE ecommerce_orders
                SET category = ?
                WHERE order_id = ?
            """, (row["category"], row["order_id"]))

    return inserted


# 6. Read all database records
def get_all_records():
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql_query(
            "SELECT * FROM ecommerce_orders",
            conn
        )


# 7. Main collection function
def collect_live_data():
    create_database()
    load_existing_dataset()

    print("Fetching sample data from public API...")

    live_df = fetch_live_data()

    print("API records received:", len(live_df))

    new_count = save_new_records(live_df)

    all_records = get_all_records()

    print("New records inserted:", new_count)
    print("Total database records:", len(all_records))

    return new_count, all_records


if __name__ == "__main__":
    collect_live_data()
