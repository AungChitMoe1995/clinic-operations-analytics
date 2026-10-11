"""
test_pipeline_integrity.py
--------------------------
Automated pytest suite verifying data lineage, healthcare DQ anomaly counts,
operational queuing metrics, relational integrity, and dashboard slice structures.
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "clinic_operations.db")
RAW_APT_CSV = os.path.join(BASE_DIR, "data", "raw", "operational", "appointments.csv")
CLEAN_APT_CSV = os.path.join(BASE_DIR, "data", "processed", "clean_appointments.csv")
DASH_JSON = os.path.join(BASE_DIR, "dashboard", "dashboard_data.json")


def test_raw_vs_clean_record_counts():
    """Verify 17,004 raw appointments audit down to exactly 16,998 clean records."""
    df_raw = pd.read_csv(RAW_APT_CSV)
    df_clean = pd.read_csv(CLEAN_APT_CSV)
    assert len(df_raw) == 17004, f"Expected 17,004 raw records, got {len(df_raw)}"
    assert len(df_clean) == 16998, f"Expected 16,998 clean records, got {len(df_clean)}"


def test_dq_anomaly_counts():
    """Verify exact healthcare Data Quality (DQ) anomaly counts (4/6/3/3/2) in raw dataset."""
    df_raw = pd.read_csv(RAW_APT_CSV)

    # 1. Duplicate primary keys (4 duplicates)
    dup_count = df_raw.duplicated(subset=["appointment_id"], keep="first").sum()
    assert dup_count == 4

    df_dedup = df_raw.drop_duplicates(subset=["appointment_id"], keep="first").copy()

    # 2. Invalid test provider PRV-999 (2 records)
    invalid_prov = (df_dedup["provider_id"] == "PRV-999").sum()
    assert invalid_prov == 2

    completed = df_dedup[df_dedup["status"] == "COMPLETED"].copy()

    # 3. Missing arrival timestamp on completed visits (6 records)
    missing_arrival = completed["arrival_time"].isna().sum()
    assert missing_arrival == 6

    # 4. Negative clinical wait time: doctor_start < arrival_time (3 records)
    valid_arr_doc = completed[completed["arrival_time"].notna() & completed["doctor_start"].notna()]
    neg_wait = (valid_arr_doc["doctor_start"] < valid_arr_doc["arrival_time"]).sum()
    assert neg_wait == 3

    # 5. Premature checkout timestamp: checkout_time < doctor_end (3 records)
    valid_chk_doc = completed[completed["checkout_time"].notna() & completed["doctor_end"].notna()]
    bad_checkout = (valid_chk_doc["checkout_time"] < valid_chk_doc["doctor_end"]).sum()
    assert bad_checkout == 3


def test_cohort_volume_and_attendance_breakdown():
    """Verify completed, no-show, cancelled counts, active patients seen, and operating days."""
    df_clean = pd.read_csv(CLEAN_APT_CSV)
    status_counts = df_clean["status"].value_counts().to_dict()

    assert status_counts.get("COMPLETED") == 13891
    assert status_counts.get("NO_SHOW") == 1898
    assert status_counts.get("CANCELLED") == 1209

    # Active patients seen in completed consultations = 2,775
    completed_patients = df_clean[df_clean["status"] == "COMPLETED"]["patient_id"].nunique()
    assert completed_patients == 2775
    assert df_clean["appointment_date"].nunique() == 250


def test_session_wait_time_percentiles():
    """Verify morning queue collapse (41.9m -> 76.3m P90) vs afternoon stability (35.2m vs 35.8m)."""
    df = pd.read_csv(CLEAN_APT_CSV)
    valid = df[(df["status"] == "COMPLETED") & (df["is_valid_wait_time"] == 1)].copy()

    arr = pd.to_datetime(valid["arrival_time"])
    doc = pd.to_datetime(valid["doctor_start"])
    valid["total_wait"] = (doc - arr).dt.total_seconds() / 60.0
    valid["hour"] = pd.to_datetime(valid["scheduled_time"], format="%H:%M:%S").dt.hour
    valid["session"] = np.where(valid["hour"] < 12, "MORNING", "AFTERNOON")

    morn_pre = valid[(valid["workflow_period"] == "PRE_INTERVENTION") & (valid["session"] == "MORNING")]["total_wait"]
    morn_post = valid[(valid["workflow_period"] == "POST_INTERVENTION") & (valid["session"] == "MORNING")]["total_wait"]
    aft_pre = valid[(valid["workflow_period"] == "PRE_INTERVENTION") & (valid["session"] == "AFTERNOON")]["total_wait"]
    aft_post = valid[(valid["workflow_period"] == "POST_INTERVENTION") & (valid["session"] == "AFTERNOON")]["total_wait"]

    assert round(np.percentile(morn_pre, 90), 1) == 41.9
    assert round(np.percentile(morn_post, 90), 1) == 76.3
    assert round(np.percentile(aft_pre, 90), 1) == 35.2
    assert round(np.percentile(aft_post, 90), 1) == 35.8


def test_dashboard_json_slices():
    """Verify all 15 pre-aggregated slices exist in dashboard_data.json with complete keys."""
    assert os.path.exists(DASH_JSON)
    with open(DASH_JSON, "r", encoding="utf-8") as f:
        slices = json.load(f)

    expected_periods = ["ALL", "PRE", "POST"]
    expected_provs = ["ALL", "PRV-001", "PRV-002", "PRV-003", "PRV-004"]
    required_sections = {"kpis", "monthly", "hourly", "session", "apt_type", "providers", "noshow"}

    assert len(slices) == 15
    for p in expected_periods:
        for prv in expected_provs:
            key = f"{p}_{prv}"
            assert key in slices, f"Missing slice {key}"
            assert required_sections.issubset(slices[key].keys())


def test_sqlite_database_tables():
    """Verify SQLite database contains all core tables with expected row counts."""
    assert os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    expected_counts = {
        "patients": 2800,
        "providers": 4,
        "appointment_types": 5,
        "appointments": 17004,
        "clean_appointments": 16998
    }
    for table, exp_cnt in expected_counts.items():
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        actual = cur.fetchone()[0]
        assert actual == exp_cnt, f"Table {table}: expected {exp_cnt}, got {actual}"

    conn.close()
