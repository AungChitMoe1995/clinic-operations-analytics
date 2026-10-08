# Streamlit Community Cloud Deployment Guide

**Application:** Clinic Operations Analytics: Outpatient Patient Flow & Provider Workload  
**Target Platform:** [Streamlit Community Cloud](https://share.streamlit.io/)  
**Primary Entry Point:** `streamlit_app.py` *(or `app.py`)*  

---

## 1. Overview

The Clinic Operations Analytics application is engineered for zero-configuration, instant deployment on **Streamlit Community Cloud**. It provides healthcare executives, clinical leaders, and health service managers with an interactive decision-support interface featuring:

- **Multi-Dimensional Cohort Drill-Down:** 15 pre-computed relational slices across 3 operational periods and 4 attending physicians.
- **Interactive Plotly Visualizations:** 6 core queuing figures with interactive tooltips, custom hover states, and clear clinical thresholds.
- **SBAR Clinical Governance Framework:** Direct translation of analytical evidence into a cost-neutral 4-point operational action plan.
- **Encounter Data Explorer:** Searchable encounter table with multi-column filtering and filtered CSV dataset export.
- **Artifact Downloads:** Built-in download buttons for the raw dataset, high-res ER diagram, and executive PowerPoint presentation (`.pptx`).

---

## 2. Step-by-Step Deployment Instructions

### Step 1: Push Repository to GitHub
Ensure all repository files are committed and pushed to your remote GitHub repository:
```bash
git add .
git commit -m "feat: configure clinic operations app for Streamlit Community Cloud"
git push origin main
```

### Step 2: Connect to Streamlit Community Cloud
1. Navigate to **[https://share.streamlit.io/](https://share.streamlit.io/)**.
2. Sign in with your **GitHub account**.

### Step 3: Configure New App
Click the **"New app"** button and enter the following settings:
- **Repository:** `AungChitMoe1995/clinic-operations-analytics`
- **Branch:** `main`
- **Main file path:** `streamlit_app.py` *(or `app.py`)*
- **App URL (optional):** Customize your subdomain (e.g., `clinic-operations-analytics.streamlit.app`)

### Step 4: Click "Deploy!"
Streamlit Cloud will automatically:
1. Detect `requirements.txt` and install `streamlit`, `plotly`, `pandas`, `numpy`, and `pillow`.
2. Load UI configuration from `.streamlit/config.toml` (clinical executive theme: `#2563EB` primary, `#F8FAFC` background).
3. Execute `streamlit_app.py`, accessing `dashboard/dashboard_data.json` and `data/processed/clean_appointments.csv`.
4. Render the live application with sub-second response times.

---

## 3. Key Deployment Configuration Files

| File | Purpose |
| :--- | :--- |
| [`streamlit_app.py`](../streamlit_app.py) | Main interactive multi-page Streamlit application. |
| [`app.py`](../app.py) | Entry point alias automatically redirecting to `streamlit_app.py`. |
| [`.streamlit/config.toml`](../.streamlit/config.toml) | Theme customization, server settings, and telemetry deactivation. |
| [`requirements.txt`](../requirements.txt) | Python dependencies required for Cloud deployment. |
| [`dashboard/dashboard_data.json`](../dashboard/dashboard_data.json) | 15 pre-aggregated data slices ensuring sub-second cold start on the Cloud free tier. |
| [`data/processed/clean_appointments.csv`](../data/processed/clean_appointments.csv) | 16,998 certified rows for the Encounter Data Explorer. |

---

## 4. Local Testing Before Deployment
To test the exact cloud environment locally:
```bash
streamlit run streamlit_app.py
```
Open `http://localhost:8501` to verify all views, filter dropdowns, and download buttons.
