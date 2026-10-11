"""
run_sql_analysis.py
--------------------
Executes all SQL analysis scripts against data/clinic_operations.db.
Uses sqlite3.complete_statement() to parse statements safely without naive ';' splitting.
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

def parse_sql_statements(sql_content: str) -> list[tuple[str, str]]:
    """
    Safely parses a multi-statement SQL file into (header_title, sql_statement) tuples
    using sqlite3.complete_statement() rather than naive string splitting.
    """
    statements = []
    buffer_lines = []
    current_header = None

    for line in sql_content.splitlines():
        stripped = line.strip()
        if stripped.startswith("-- Query"):
            current_header = stripped
        if not stripped or stripped.startswith("--"):
            continue

        buffer_lines.append(line)
        candidate = "\n".join(buffer_lines)
        if sqlite3.complete_statement(candidate):
            stmt = candidate.strip()
            if stmt:
                title = current_header or f"Query {len(statements) + 1}"
                statements.append((title, stmt))
            buffer_lines = []
            current_header = None

    return statements

def run_all_queries() -> int:
    print(f"Connecting to {DB_PATH} to execute SQL analysis suite...\n")
    conn = sqlite3.connect(DB_PATH)
    total_executed = 0

    for sql_file in SQL_FILES:
        file_path = os.path.join(SQL_DIR, sql_file)
        print("=" * 80)
        print(f"EXECUTING: {sql_file}")
        print("=" * 80)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        parsed_queries = parse_sql_statements(content)
        for title, q in parsed_queries:
            print(f"\n>>> {title}")
            df_res = pd.read_sql_query(q, conn)
            print(df_res.to_string(index=False))
            total_executed += 1
        print("\n")

    conn.close()
    print(f"All {total_executed} SQL analysis queries executed successfully!")
    return total_executed

if __name__ == "__main__":
    run_all_queries()
