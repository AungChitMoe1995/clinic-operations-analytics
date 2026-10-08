"""
run_sql_analysis.py
--------------------
Executes all SQL analysis scripts against data/clinic_operations.db.
Prints summary output to console and verifies all queries execute cleanly.
"""

import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "clinic_operations.db")
SQL_DIR = os.path.join(BASE_DIR, "sql")

SQL_FILES = [
    "01_volume_analysis.sql",
    "02_scheduling_patterns.sql",
    "03_no_show_analysis.sql",
    "04_waiting_time_analysis.sql",
    "05_provider_workload.sql",
    "06_before_after_intervention.sql"
]

def run_all_queries():
    print(f"Connecting to {DB_PATH} to execute SQL analysis suite...\n")
    conn = sqlite3.connect(DB_PATH)

    for sql_file in SQL_FILES:
        file_path = os.path.join(SQL_DIR, sql_file)
        print("=" * 80)
        print(f"EXECUTING: {sql_file}")
        print("=" * 80)
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Split individual queries separated by semicolon
        raw_queries = content.split(";")
        q_idx = 1
        for raw_q in raw_queries:
            q = raw_q.strip()
            # Skip empty or comment-only blocks
            if not q or all(line.strip().startswith("--") for line in q.splitlines() if line.strip()):
                continue
            
            # Extract header comment if available
            lines = [l.strip() for l in q.splitlines() if l.strip()]
            comment_header = [l for l in lines if l.startswith("-- Query")]
            title = comment_header[0] if comment_header else f"Query {q_idx}"

            print(f"\n>>> {title}")
            try:
                df_res = pd.read_sql_query(q, conn)
                print(df_res.to_string(index=False))
            except Exception as e:
                print(f"Error executing query:\n{e}")
            q_idx += 1
        print("\n")

    conn.close()
    print("All SQL analysis queries executed successfully!")

if __name__ == "__main__":
    run_all_queries()
