"""
load_to_sqlite.py
------------------
Executes sql/schema.sql and ingests raw CSV data into SQLite database:
data/clinic_operations.db

Validates record counts and schema structure.
"""

import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "clinic_operations.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "sql", "schema.sql")

RAW_SYNTHEA = os.path.join(BASE_DIR, "data", "raw", "synthea")
RAW_OPERATIONAL = os.path.join(BASE_DIR, "data", "raw", "operational")

TABLE_FILES = [
    ("patients", os.path.join(RAW_SYNTHEA, "patients.csv")),
    ("providers", os.path.join(RAW_OPERATIONAL, "providers.csv")),
    ("appointment_types", os.path.join(RAW_OPERATIONAL, "appointment_types.csv")),
    ("conditions", os.path.join(RAW_SYNTHEA, "conditions.csv")),
    ("encounters", os.path.join(RAW_SYNTHEA, "encounters.csv")),
    ("appointments", os.path.join(RAW_OPERATIONAL, "appointments.csv")),
]

def load_database():
    print(f"Connecting to SQLite database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Apply DDL Schema
    print(f"Applying schema from: {SCHEMA_PATH}")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()
    print("Schema applied successfully.")

    # 2. Ingest CSV Data
    for table_name, csv_path in TABLE_FILES:
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Missing required CSV file: {csv_path}")
        
        print(f"Loading {csv_path} -> table '{table_name}'...")
        df = pd.read_csv(csv_path)
        # Ingest into SQLite table
        df.to_sql(table_name, conn, if_exists="append", index=False)
        
        # Verify row count
        count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"  -> Successfully loaded {count:,} rows into '{table_name}'.")

    conn.commit()
    conn.close()
    print("\nDatabase build complete: data/clinic_operations.db is ready for analysis!")

if __name__ == "__main__":
    load_database()
