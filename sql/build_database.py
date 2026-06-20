"""
build_database.py
------------------
Loads the four source CSVs, creates the SQLite database using
schema.sql, and bulk-inserts the data. Run this once before
using the SQL queries or launching the Streamlit app.

Usage:
    python build_database.py
"""

import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "food_wastage.db"
DATA_DIR = BASE_DIR / "database"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def load_csvs():
    providers = pd.read_csv(DATA_DIR / "providers_data.csv")
    receivers = pd.read_csv(DATA_DIR / "receivers_data.csv")
    food = pd.read_csv(DATA_DIR / "food_listings_data.csv")
    claims = pd.read_csv(DATA_DIR / "claims_data.csv")

    # Normalize date columns to ISO format for reliable SQL date functions
    food["Expiry_Date"] = pd.to_datetime(food["Expiry_Date"]).dt.strftime("%Y-%m-%d")
    claims["Timestamp"] = pd.to_datetime(claims["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")

    return providers, receivers, food, claims


def build_database():
    providers, receivers, food, claims = load_csvs()

    # Fresh DB every run so the script is idempotent
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    with open(SCHEMA_PATH, "r") as f:
        cur.executescript(f.read())

    providers.to_sql("Providers", conn, if_exists="append", index=False)
    receivers.to_sql("Receivers", conn, if_exists="append", index=False)
    food.to_sql("Food_Listings", conn, if_exists="append", index=False)
    claims.to_sql("Claims", conn, if_exists="append", index=False)

    conn.commit()

    # Sanity checks
    counts = {}
    for table in ["Providers", "Receivers", "Food_Listings", "Claims"]:
        counts[table] = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    orphan_food = cur.execute("""
        SELECT COUNT(*) FROM Food_Listings f
        LEFT JOIN Providers p ON f.Provider_ID = p.Provider_ID
        WHERE p.Provider_ID IS NULL
    """).fetchone()[0]

    orphan_claims = cur.execute("""
        SELECT COUNT(*) FROM Claims c
        LEFT JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        LEFT JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
        WHERE f.Food_ID IS NULL OR r.Receiver_ID IS NULL
    """).fetchone()[0]

    conn.close()

    print("Database built at:", DB_PATH)
    print("Row counts:", counts)
    print("Orphaned food rows (bad Provider_ID):", orphan_food)
    print("Orphaned claim rows (bad Food_ID/Receiver_ID):", orphan_claims)


if __name__ == "__main__":
    build_database()
