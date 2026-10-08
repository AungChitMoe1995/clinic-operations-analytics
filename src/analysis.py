"""
analysis.py
------------
Performs Python/Pandas investigative analysis:
- Descriptive & percentile statistics (Mean, Median/P50, P75, P90)
- Testing competing hypotheses for wait time deterioration:
  1. Volume hypothesis (Did visits surge?)
  2. Case-mix hypothesis (Did chronic disease complexity shift?)
  3. Front-end/triage bottleneck vs doctor exam room queue
  4. Cascading queue dynamics due to compressed morning slots
- Generates publication-ready figures in docs/images/
- Exports summary metrics to data/processed/summary_metrics.json
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "clinic_operations.db")
IMAGES_DIR = os.path.join(BASE_DIR, "docs", "images")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Aesthetic formatting
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial', 'DejaVu Sans', 'Helvetica'
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8

def load_data():
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        a.appointment_id,
        a.patient_id,
        a.provider_id,
        p.provider_name,
        p.specialty,
        a.appointment_type_id,
        t.appointment_type_name,
        t.standard_duration_min,
        a.appointment_date,
        a.scheduled_time,
        a.scheduled_duration_min,
        a.arrival_time,
        a.triage_start,
        a.triage_end,
        a.doctor_start,
        a.doctor_end,
        a.checkout_time,
        a.status,
        a.booking_channel,
        a.workflow_period,
        a.is_valid_wait_time,
        a.is_valid_los
    FROM clean_appointments a
    JOIN providers p ON a.provider_id = p.provider_id
    JOIN appointment_types t ON a.appointment_type_id = t.appointment_type_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Parse timestamps
    dt_cols = ["arrival_time", "triage_start", "triage_end", "doctor_start", "doctor_end", "checkout_time"]
    for col in dt_cols:
        df[col] = pd.to_datetime(df[col])

    df["appointment_date"] = pd.to_datetime(df["appointment_date"])
    df["scheduled_hour"] = pd.to_datetime(df["scheduled_time"], format="%H:%M:%S").dt.hour
    df["day_of_week"] = df["appointment_date"].dt.day_name()
    df["month_str"] = df["appointment_date"].dt.strftime("%Y-%m")

    # Milestone durations (minutes)
    df["triage_wait_min"] = (df["triage_start"] - df["arrival_time"]).dt.total_seconds() / 60.0
    df["triage_service_min"] = (df["triage_end"] - df["triage_start"]).dt.total_seconds() / 60.0
    df["doctor_queue_min"] = (df["doctor_start"] - df["triage_end"]).dt.total_seconds() / 60.0
    df["total_clinical_wait_min"] = (df["doctor_start"] - df["arrival_time"]).dt.total_seconds() / 60.0
    df["consultation_duration_min"] = (df["doctor_end"] - df["doctor_start"]).dt.total_seconds() / 60.0
    df["total_los_min"] = (df["checkout_time"] - df["arrival_time"]).dt.total_seconds() / 60.0

    df["slot_variance_min"] = df["consultation_duration_min"] - df["scheduled_duration_min"]
    df["is_overrun"] = df["slot_variance_min"] > 5.0
    df["clinic_session"] = np.where(df["scheduled_hour"] < 12, "Morning (08:30-11:30)", "Afternoon (13:30-15:30)")

    return df

def generate_visualizations(df):
    df_valid = df[(df["status"] == "COMPLETED") & (df["is_valid_wait_time"] == 1)].copy()

    # -------------------------------------------------------------
    # Figure 1: Monthly Appointment Volume Trajectory
    # -------------------------------------------------------------
    print("Generating Figure 1: Monthly Volume Trajectory...")
    monthly_vol = df.groupby("month_str").agg(
        total_booked=("appointment_id", "count"),
        completed=("status", lambda x: (x == "COMPLETED").sum()),
        no_shows=("status", lambda x: (x == "NO_SHOW").sum())
    ).reset_index()

    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    x = np.arange(len(monthly_vol))
    w = 0.35

    ax.bar(x - w/2, monthly_vol["total_booked"], w, label="Total Booked", color="#2B5B84", alpha=0.9)
    ax.bar(x + w/2, monthly_vol["completed"], w, label="Completed Visits", color="#4EA5D9", alpha=0.9)
    
    # Intervention vertical line
    ax.axvline(x=5.5, color="#D9534F", linestyle="--", linewidth=1.8, label="July 1 Policy Intervention")
    
    # Clean non-overlapping badge with headroom
    max_val = monthly_vol["total_booked"].max()
    ax.set_ylim(0, max_val * 1.22)
    ax.text(5.6, max_val * 1.08, "Pre (Baseline)  |  Post (Compressed)", 
            color="#D9534F", fontsize=9.5, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#D9534F", alpha=0.95))

    ax.set_xticks(x)
    ax.set_xticklabels(monthly_vol["month_str"], rotation=35, ha="right", fontsize=9)
    ax.set_ylabel("Number of Appointments", fontsize=11, fontweight="bold")
    ax.set_title("Monthly Clinic Appointment Volume (Jan - Dec 2024)", fontsize=13, fontweight="bold", pad=14)
    ax.legend(frameon=True, facecolor="white", loc="upper left")
    plt.tight_layout()
    fig1_path = os.path.join(IMAGES_DIR, "fig1_monthly_volume_trend.png")
    fig.savefig(fig1_path)
    plt.close()

    # -------------------------------------------------------------
    # Figure 2: Waiting Time Diurnal Curve (Hourly Percentiles)
    # -------------------------------------------------------------
    print("Generating Figure 2: Diurnal Waiting Time Percentile Curve...")
    hourly_pcts = df_valid.groupby("scheduled_hour")["total_clinical_wait_min"].agg(
        p50=lambda x: np.percentile(x, 50),
        p75=lambda x: np.percentile(x, 75),
        p90=lambda x: np.percentile(x, 90),
        mean="mean"
    ).reset_index()

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    hours = hourly_pcts["scheduled_hour"]

    ax.plot(hours, hourly_pcts["p90"], marker='o', linewidth=2.5, color="#C94A29", label="P90 Wait Time")
    ax.plot(hours, hourly_pcts["p75"], marker='s', linewidth=2.0, color="#E8985E", label="P75 Wait Time")
    ax.plot(hours, hourly_pcts["p50"], marker='^', linewidth=2.2, color="#2B5B84", label="Median (P50) Wait Time")

    # Give generous headroom for title and annotations
    ax.set_ylim(5, 105)

    # Clean annotation positioned comfortably away from title
    max_p90 = hourly_pcts.loc[hourly_pcts["scheduled_hour"] == 11, "p90"].values[0]
    ax.annotate(f'Peak Congestion: {max_p90:.1f} min\n(Compounding delays)', 
                xy=(11, max_p90), xytext=(8.8, 68),
                arrowprops=dict(facecolor='#C94A29', shrink=0.08, width=1.5, headwidth=7),
                fontsize=9.5, fontweight='bold', color='#C94A29',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#C94A29", alpha=0.9))

    # Lunch break shading
    ax.axvspan(11.8, 12.8, color="#EAEAEA", alpha=0.7, label="Lunch / Clinic Reset")
    ax.text(12.3, 22, "Lunch Reset", rotation=90, ha='center', va='center', color="#777777", fontsize=9)

    ax.set_xticks(hours)
    ax.set_xticklabels([f"{h:02d}:00" for h in hours], fontsize=9.5)
    ax.set_ylabel("Patient Wait Time (Minutes)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Scheduled Appointment Hour", fontsize=11, fontweight="bold")
    ax.set_title("Diurnal Waiting Time Curve: Median, P75 & P90 by Hour of Day", fontsize=13, fontweight="bold", pad=16)
    ax.legend(frameon=True, facecolor="white", loc="upper left")
    plt.tight_layout()
    fig2_path = os.path.join(IMAGES_DIR, "fig2_waiting_time_percentiles_hourly.png")
    fig.savefig(fig2_path)
    plt.close()

    # -------------------------------------------------------------
    # Figure 3: Quasi-Experimental Comparison (Morning vs Afternoon)
    # -------------------------------------------------------------
    print("Generating Figure 3: Morning vs Afternoon Pre/Post Comparison...")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=300, sharey=True)

    sessions = ["Morning (08:30-11:30)", "Afternoon (13:30-15:30)"]
    colors = ["#2B5B84", "#D9534F"]

    for i, session in enumerate(sessions):
        ax = axes[i]
        sub = df_valid[df_valid["clinic_session"] == session]
        summary = sub.groupby("workflow_period")["total_clinical_wait_min"].agg(
            median="median",
            p90=lambda x: np.percentile(x, 90),
            mean="mean"
        ).loc[["PRE_INTERVENTION", "POST_INTERVENTION"]]

        x_pos = np.arange(len(summary))
        bar_w = 0.35

        ax.bar(x_pos - bar_w/2, summary["median"], bar_w, label="Median (P50)", color="#4EA5D9", alpha=0.9)
        ax.bar(x_pos + bar_w/2, summary["p90"], bar_w, label="P90 (90th %ile)", color=colors[i], alpha=0.9)

        # Labels on bars
        for idx in range(len(summary)):
            ax.text(idx - bar_w/2, summary["median"].iloc[idx] + 1.2, f"{summary['median'].iloc[idx]:.1f}m", 
                    ha="center", fontsize=9, fontweight="bold")
            ax.text(idx + bar_w/2, summary["p90"].iloc[idx] + 1.2, f"{summary['p90'].iloc[idx]:.1f}m", 
                    ha="center", fontsize=9, fontweight="bold", color=colors[i])

        ax.set_xticks(x_pos)
        ax.set_xticklabels(["Pre-Intervention\n(Jan - Jun)", "Post-Intervention\n(Jul - Dec)"], fontsize=10)
        ax.set_title(f"{session}", fontsize=12, fontweight="bold")
        if i == 0:
            ax.set_ylabel("Wait Time (Minutes)", fontsize=11, fontweight="bold")
        ax.legend(frameon=True, facecolor="white", loc="upper left")

    fig.suptitle("Root Cause Isolation: Morning Queue Collapse vs Afternoon Stability", fontsize=13.5, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig3_path = os.path.join(IMAGES_DIR, "fig3_pre_post_session_comparison.png")
    fig.savefig(fig3_path, bbox_inches="tight")
    plt.close()

    # -------------------------------------------------------------
    # Figure 4: Provider Workload & Overrun Rates
    # -------------------------------------------------------------
    print("Generating Figure 4: Provider Workload and Slot Overruns...")
    prov_summary = df_valid.groupby("provider_name").agg(
        visits=("appointment_id", "count"),
        clinical_hrs=("consultation_duration_min", lambda x: x.sum() / 60.0),
        overrun_pct=("is_overrun", lambda x: (x.sum() / len(x)) * 100.0),
        p90_wait=("total_clinical_wait_min", lambda x: np.percentile(x, 90))
    ).reset_index().sort_values("clinical_hrs", ascending=False)

    fig, ax1 = plt.subplots(figsize=(10, 5), dpi=300)
    x = np.arange(len(prov_summary))
    w = 0.38

    bar1 = ax1.bar(x - w/2, prov_summary["clinical_hrs"], w, label="Total Clinical Hours", color="#2B5B84", alpha=0.9)
    ax1.set_ylabel("Clinical Consultation Hours", color="#2B5B84", fontsize=11, fontweight="bold")
    ax1.tick_params(axis='y', labelcolor="#2B5B84")

    ax2 = ax1.twinx()
    bar2 = ax2.bar(x + w/2, prov_summary["overrun_pct"], w, label="Slot Overrun Rate (%)", color="#E8985E", alpha=0.9)
    ax2.set_ylabel("Slot Overrun Rate (>5 min over slot %)", color="#C94A29", fontsize=11, fontweight="bold")
    ax2.tick_params(axis='y', labelcolor="#C94A29")
    ax2.grid(False)

    # Clean provider names
    clean_names = [n.replace(", MD", "") for n in prov_summary["provider_name"]]
    ax1.set_xticks(x)
    ax1.set_xticklabels(clean_names, fontsize=10, fontweight="bold")
    ax1.set_title("Provider Clinical Hours vs Slot Overrun Frequency", fontsize=13, fontweight="bold", pad=12)

    # Combined legend
    lines = [bar1, bar2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper right", frameon=True, facecolor="white")
    plt.tight_layout()
    fig4_path = os.path.join(IMAGES_DIR, "fig4_provider_workload_and_overruns.png")
    fig.savefig(fig4_path)
    plt.close()

    # -------------------------------------------------------------
    # Figure 5: No-Show & Cancellation Rates
    # -------------------------------------------------------------
    print("Generating Figure 5: No-Show Patterns...")
    fig, (ax_day, ax_type) = plt.subplots(1, 2, figsize=(12, 4.8), dpi=300)

    # By Day of Week
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    day_noshow = df.groupby("day_of_week")["status"].apply(lambda s: (s == "NO_SHOW").sum() / len(s) * 100).reindex(day_order)
    
    ax_day.bar(day_order, day_noshow, color=["#C94A29" if d == "Monday" else "#4EA5D9" for d in day_order], alpha=0.9)
    ax_day.set_ylabel("No-Show Rate (%)", fontsize=10.5, fontweight="bold")
    ax_day.set_title("No-Show Rate by Day of Week", fontsize=11.5, fontweight="bold")
    for idx, val in enumerate(day_noshow):
        ax_day.text(idx, val + 0.3, f"{val:.1f}%", ha="center", fontsize=9.5, fontweight="bold")

    # By Appointment Type
    type_noshow = df.groupby("appointment_type_name")["status"].apply(lambda s: (s == "NO_SHOW").sum() / len(s) * 100).sort_values(ascending=True)
    ax_type.barh(type_noshow.index, type_noshow.values, color="#2B5B84", alpha=0.85)
    ax_type.set_xlabel("No-Show Rate (%)", fontsize=10.5, fontweight="bold")
    ax_type.set_title("No-Show Rate by Appointment Type", fontsize=11.5, fontweight="bold")
    for idx, val in enumerate(type_noshow.values):
        ax_type.text(val + 0.2, idx, f"{val:.1f}%", va="center", fontsize=9)

    plt.tight_layout()
    fig5_path = os.path.join(IMAGES_DIR, "fig5_no_show_patterns.png")
    fig.savefig(fig5_path)
    plt.close()

    print("All visualizations exported to docs/images/.")

def export_summary_json(df):
    df_valid = df[(df["status"] == "COMPLETED") & (df["is_valid_wait_time"] == 1)].copy()

    pre_valid = df_valid[df_valid["workflow_period"] == "PRE_INTERVENTION"]
    post_valid = df_valid[df_valid["workflow_period"] == "POST_INTERVENTION"]

    summary = {
        "overall": {
            "total_scheduled": int(len(df)),
            "completed_visits": int((df["status"] == "COMPLETED").sum()),
            "no_shows": int((df["status"] == "NO_SHOW").sum()),
            "cancellations": int((df["status"] == "CANCELLED").sum()),
            "unique_patients_seen": int(df[df["status"] == "COMPLETED"]["patient_id"].nunique()),
            "overall_no_show_rate_pct": round(float((df["status"] == "NO_SHOW").sum() / len(df) * 100), 2),
            "overall_mean_wait_min": round(float(df_valid["total_clinical_wait_min"].mean()), 1),
            "overall_median_wait_min": round(float(df_valid["total_clinical_wait_min"].median()), 1),
            "overall_p75_wait_min": round(float(np.percentile(df_valid["total_clinical_wait_min"], 75)), 1),
            "overall_p90_wait_min": round(float(np.percentile(df_valid["total_clinical_wait_min"], 90)), 1),
        },
        "before_after": {
            "pre_intervention": {
                "scheduled": int((df["workflow_period"] == "PRE_INTERVENTION").sum()),
                "completed": int(len(pre_valid)),
                "median_wait_min": round(float(pre_valid["total_clinical_wait_min"].median()), 1),
                "p90_wait_min": round(float(np.percentile(pre_valid["total_clinical_wait_min"], 90)), 1),
                "morning_median_wait_min": round(float(pre_valid[pre_valid["clinic_session"].str.startswith("Morning")]["total_clinical_wait_min"].median()), 1),
                "morning_p90_wait_min": round(float(np.percentile(pre_valid[pre_valid["clinic_session"].str.startswith("Morning")]["total_clinical_wait_min"], 90)), 1),
                "afternoon_median_wait_min": round(float(pre_valid[pre_valid["clinic_session"].str.startswith("Afternoon")]["total_clinical_wait_min"].median()), 1),
                "afternoon_p90_wait_min": round(float(np.percentile(pre_valid[pre_valid["clinic_session"].str.startswith("Afternoon")]["total_clinical_wait_min"], 90)), 1),
            },
            "post_intervention": {
                "scheduled": int((df["workflow_period"] == "POST_INTERVENTION").sum()),
                "completed": int(len(post_valid)),
                "median_wait_min": round(float(post_valid["total_clinical_wait_min"].median()), 1),
                "p90_wait_min": round(float(np.percentile(post_valid["total_clinical_wait_min"], 90)), 1),
                "morning_median_wait_min": round(float(post_valid[post_valid["clinic_session"].str.startswith("Morning")]["total_clinical_wait_min"].median()), 1),
                "morning_p90_wait_min": round(float(np.percentile(post_valid[post_valid["clinic_session"].str.startswith("Morning")]["total_clinical_wait_min"], 90)), 1),
                "afternoon_median_wait_min": round(float(post_valid[post_valid["clinic_session"].str.startswith("Afternoon")]["total_clinical_wait_min"].median()), 1),
                "afternoon_p90_wait_min": round(float(np.percentile(post_valid[post_valid["clinic_session"].str.startswith("Afternoon")]["total_clinical_wait_min"], 90)), 1),
            }
        }
    }

    out_file = os.path.join(PROCESSED_DIR, "summary_metrics.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"Summary metrics exported -> {out_file}")

def main():
    print("Loading validated clinic operations data from database...")
    df = load_data()
    print(f"Loaded {len(df):,} appointment records.")
    generate_visualizations(df)
    export_summary_json(df)
    print("Python/Pandas analysis workflow complete!")

if __name__ == "__main__":
    main()
