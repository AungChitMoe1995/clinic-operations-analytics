"""
streamlit_app.py
----------------
Clinic Operations Analytics: Investigating Patient Flow, Waiting Time and Provider Workload
Metro North Family Health Centre — Operational Decision Support & Queuing Intelligence

Deployable to Streamlit Community Cloud (https://share.streamlit.io/).
"""

import os
import json
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & METADATA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Clinic Operations Analytics | Decision Support",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. PATHS & CACHED DATA LOADERS
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "dashboard", "dashboard_data.json")
CSV_PATH = os.path.join(BASE_DIR, "data", "processed", "clean_appointments.csv")
PPTX_PATH = os.path.join(BASE_DIR, "docs", "presentation", "clinic_operations_executive_briefing.pptx")
ER_IMG_PATH = os.path.join(BASE_DIR, "docs", "images", "data_model.png")
SLIDES_DIR = os.path.join(BASE_DIR, "docs", "presentation", "slides_preview")

@st.cache_data
def load_dashboard_json():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@st.cache_data
def load_raw_data():
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df["appointment_date"] = pd.to_datetime(df["appointment_date"])
        return df
    return pd.DataFrame()

slices_data = load_dashboard_json()
raw_df = load_raw_data()

# -----------------------------------------------------------------------------
# 3. EXECUTIVE COLOR PALETTE
# -----------------------------------------------------------------------------
NAVY_PRIMARY = "#1E3A8A"
NAVY_DARK = "#0F172A"
BLUE_ACCENT = "#2563EB"
CRIMSON_ALERT = "#E11D48"
EMERALD_GREEN = "#059669"
AMBER_WARN = "#D97706"
SLATE_MUTED = "#64748B"
LIGHT_BG = "#F8FAFC"
BORDER_COLOR = "#E2E8F0"

# -----------------------------------------------------------------------------
# 4. CUSTOM CSS STYLING
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Global Container */
    .main {
        background-color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Header Branding */
    .clinic-header-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .clinic-title {
        color: #0f172a;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .clinic-subtitle {
        color: #64748b;
        font-size: 13.5px;
        margin-bottom: 0px;
    }
    .badge-lead {
        display: inline-block;
        background: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        border-radius: 9999px;
        padding: 3px 12px;
        font-size: 12px;
        font-weight: 600;
    }

    /* Metric Cards */
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        border-left: 4px solid #2563eb;
    }
    .metric-card-danger {
        border-left-color: #e11d48;
    }
    .metric-card-success {
        border-left-color: #059669;
    }
    .metric-card-warning {
        border-left-color: #d97706;
    }
    .metric-title {
        color: #64748b;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .metric-value {
        color: #0f172a;
        font-size: 26px;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 4px;
    }
    .metric-sub {
        color: #64748b;
        font-size: 11.5px;
    }

    /* Guide Box */
    .guide-box {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }
    .guide-title {
        color: #1e3a8a;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .guide-desc {
        color: #334155;
        font-size: 12.5px;
        line-height: 1.5;
    }

    /* Chart Containers */
    .chart-container-title {
        color: #0f172a;
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 2px;
    }
    .chart-container-subtitle {
        color: #64748b;
        font-size: 12px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. SIDEBAR CONTROLS & NAVIGATION
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/hospital-3.png", width=64)
    st.title("Clinic Operations")
    st.caption("Metro North Family Health Centre\nEHR Queuing & Capacity Mart")
    st.markdown("---")

    # Main Navigation
    st.subheader("🧭 Navigation")
    nav_mode = st.radio(
        "Select Perspective:",
        [
            "📊 Executive Dashboard",
            "📋 SBAR Clinical Governance",
            "🔍 Encounter Data Explorer",
            "🏛️ Relational Data Model",
            "📑 Slide Deck & Reports"
        ],
        index=0
    )

    st.markdown("---")
    st.subheader("🎯 Operational Cohort Filters")

    period_options = {
        "Full Year 2024 (Baseline & Post)": "all",
        "Pre-Intervention (Jan - Jun)": "pre",
        "Post-Intervention (Jul - Dec)": "post"
    }
    selected_period_label = st.selectbox(
        "Operational Period:",
        list(period_options.keys()),
        index=0
    )
    period_key = period_options[selected_period_label]

    provider_options = {
        "All Attending Clinicians (4 Providers)": "all",
        "Dr. Arthur Vance, MD (Internal Medicine)": "PRV-001",
        "Dr. Elena Rostova, MD (Family Medicine)": "PRV-002",
        "Dr. Marcus Brody, MD (Family Medicine)": "PRV-003",
        "Dr. Sarah Jenkins, MD (Preventive Care)": "PRV-004"
    }
    selected_provider_label = st.selectbox(
        "Attending Clinician:",
        list(provider_options.keys()),
        index=0
    )
    provider_key = provider_options[selected_provider_label]

    slice_id = f"{period_key}_{provider_key}"
    curr_slice = slices_data.get(slice_id, slices_data.get("all_all", {}))

    st.markdown("---")
    st.caption("⚡ **Fast Slicing Engine**: 15 pre-computed relational mart aggregations for zero-lag UI response.")
    st.markdown("""
    <div style="font-size:11px; color:#64748b; line-height:1.4;">
        <strong>Clinical Persona:</strong> MBBS Doctor & EHR Software Coordinator<br>
        <strong>Focus:</strong> Outpatient Wait-Times, Stochastic Overruns & Resource Allocation
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 6. HEADER BANNER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="clinic-header-card">
    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;">
        <div>
            <div class="clinic-title">
                🏥 Clinic Operations Analytics: Patient Flow & Waiting Time
            </div>
            <div class="clinic-subtitle">
                <strong>Facility:</strong> Metro North Family Health Centre &nbsp;|&nbsp; 
                <strong>Observation Window:</strong> Jan 1, 2024 – Dec 31, 2024 (250 Operating Days) &nbsp;|&nbsp;
                <strong>Population:</strong> 2,775 Active Synthea EHR Cohort (16,998 Audited Encounters)
            </div>
        </div>
        <div style="text-align:right;">
            <span class="badge-lead">Clinical & Informatics Portfolio Project</span>
            <div style="font-size:11px; color:#64748b; margin-top:4px;">Lead MBBS Doctor & Clinical Data Analyst</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# VIEW 1: EXECUTIVE DASHBOARD
# =============================================================================
if nav_mode == "📊 Executive Dashboard":

    # --- HR & Evaluator Guide Accordion ---
    with st.expander("💡 How to Read Operational Metrics (Clinical Evaluator & HR Recruiter Guide)", expanded=True):
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            st.markdown("""
            **Median Wait (P50)**  
            *Typical Patient Experience:* Exactly 50% of patients waited less than this, and 50% waited longer. Unlike mathematical averages, the median is not distorted by rare extreme outliers.
            """)
        with col_g2:
            st.markdown("""
            **P90 Wait Time (90th Percentile)**  
            *Worst 10% Queuing Delays:* The cutoff separating the fastest 90% from the slowest 10%. In NHS, Australia, and Singapore MOH healthcare standards, P90 identifies severe clinic logjams triggering patient walkouts.
            """)
        with col_g3:
            st.markdown("""
            **Slot Overrun Rate (%)**  
            *Consultation Mismatch:* Percentage of clinical consults running >5 minutes past scheduled slot duration. Isolates doctor workload strain and template mismatch.
            """)

    # --- KPI Scorecards ---
    kpis = curr_slice.get("kpis", {})
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Booked Visits</div>
            <div class="metric-value">{kpis.get('total_booked', 0):,}</div>
            <div class="metric-sub">{kpis.get('avg_daily_booked', 0)} visits / day</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card metric-card-success">
            <div class="metric-title">Completed Consults</div>
            <div class="metric-value">{kpis.get('completed', 0):,}</div>
            <div class="metric-sub">{kpis.get('completion_rate', 0)}% completion rate</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Unique Patients</div>
            <div class="metric-value">{kpis.get('unique_patients', 0):,}</div>
            <div class="metric-sub">Synthea active panel</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Median Wait (P50)</div>
            <div class="metric-value">{kpis.get('p50_wait', 0)} <span style="font-size:16px; font-weight:500;">min</span></div>
            <div class="metric-sub">Typical experience</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
        <div class="metric-card metric-card-danger">
            <div class="metric-title">P90 Wait Time</div>
            <div class="metric-value">{kpis.get('p90_wait', 0)} <span style="font-size:16px; font-weight:500;">min</span></div>
            <div class="metric-sub">Worst 10% tail delay</div>
        </div>
        """, unsafe_allow_html=True)

    with c6:
        st.markdown(f"""
        <div class="metric-card metric-card-warning">
            <div class="metric-title">No-Show Rate</div>
            <div class="metric-value">{kpis.get('noshow_rate', 0)}%</div>
            <div class="metric-sub">{kpis.get('noshow_count', 0):,} missed visits</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # --- ROW 1: Visual 1 & Visual 2 ---
    col_v1, col_v2 = st.columns(2)

    with col_v1:
        st.markdown('<div class="chart-container-title">Visual 1: Monthly Appointment Volume Trajectory</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-container-subtitle">Tracking clinic demand before and after the July 1 operational intervention</div>', unsafe_allow_html=True)
        
        m_data = curr_slice.get("monthly", {})
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=m_data.get("labels", []),
            y=m_data.get("booked", []),
            name="Total Booked",
            marker_color="#1E3A8A"
        ))
        fig1.add_trace(go.Bar(
            x=m_data.get("labels", []),
            y=m_data.get("completed", []),
            name="Completed Visits",
            marker_color="#3B82F6"
        ))
        fig1.update_layout(
            barmode="group",
            height=340,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="Visits")
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_v2:
        st.markdown('<div class="chart-container-title">Visual 2: Diurnal Waiting Time Curve (Hourly Percentiles)</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-container-subtitle">Median (Typical) vs P90 (Worst 10% Delays) across operating day (08:00 – 16:00)</div>', unsafe_allow_html=True)
        
        d_data = curr_slice.get("diurnal", {})
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=d_data.get("labels", []),
            y=d_data.get("p90", []),
            name="P90 Wait (Worst 10% Delays)",
            mode="lines+markers",
            line=dict(color="#E11D48", width=3),
            marker=dict(size=7, color="#E11D48")
        ))
        fig2.add_trace(go.Scatter(
            x=d_data.get("labels", []),
            y=d_data.get("median", []),
            name="Median Wait (Typical Patient)",
            mode="lines+markers",
            line=dict(color="#1E3A8A", width=3),
            marker=dict(size=7, color="#1E3A8A")
        ))
        fig2.update_layout(
            height=340,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="Scheduled Appointment Hour"),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="Wait Time (Minutes)")
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # --- ROW 2: Visual 3 & Visual 4 ---
    col_v3, col_v4 = st.columns(2)

    with col_v3:
        st.markdown('<div class="chart-container-title">Visual 3: Root Cause Isolation: Morning vs Afternoon Stability</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-container-subtitle">Contrasting compressed morning slots against stable afternoon sessions (Pre vs Post)</div>', unsafe_allow_html=True)
        
        s_data = curr_slice.get("session_comparison", {})
        morn = s_data.get("morning", {})
        aft = s_data.get("afternoon", {})

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            name="Median (P50)",
            x=["Morning (Pre)", "Morning (Post)", "Afternoon (Pre)", "Afternoon (Post)"],
            y=[morn.get("median_pre", 0), morn.get("median_post", 0), aft.get("median_pre", 0), aft.get("median_post", 0)],
            marker_color=["#38BDF8", "#38BDF8", "#38BDF8", "#38BDF8"]
        ))
        fig3.add_trace(go.Bar(
            name="P90 Wait (Worst 10%)",
            x=["Morning (Pre)", "Morning (Post)", "Afternoon (Pre)", "Afternoon (Post)"],
            y=[morn.get("p90_pre", 0), morn.get("p90_post", 0), aft.get("p90_pre", 0), aft.get("p90_post", 0)],
            marker_color=["#1E3A8A", "#E11D48", "#1E3A8A", "#059669"]
        ))
        fig3.update_layout(
            barmode="group",
            height=340,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="Wait Time (Minutes)")
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_v4:
        st.markdown('<div class="chart-container-title">Visual 4: Patient Waiting Time by Appointment Type</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-container-subtitle">Evaluating clinical complexity: Typical Wait (Median) vs Worst 10% Tail (P90)</div>', unsafe_allow_html=True)
        
        apt_data = curr_slice.get("apt_type", {})
        labels = apt_data.get("labels", [])
        med_vals = apt_data.get("median", [])
        p90_vals = apt_data.get("p90", [])

        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            y=labels,
            x=med_vals,
            name="Median Wait (Typical)",
            orientation="h",
            marker_color="#0D9488"
        ))
        fig4.add_trace(go.Bar(
            y=labels,
            x=p90_vals,
            name="P90 Wait (Worst 10% Delays)",
            orientation="h",
            marker_color="#F59E0B"
        ))
        fig4.update_layout(
            barmode="group",
            height=340,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="Wait Time (Minutes)"),
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # --- ROW 3: Visual 5 & Visual 6 ---
    col_v5, col_v6 = st.columns(2)

    with col_v5:
        st.markdown('<div class="chart-container-title">Visual 5: Clinician Workload & Slot Overrun Profile</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-container-subtitle">Annual Clinical Hours vs Slot Overrun Rate (% exceeding scheduled booking)</div>', unsafe_allow_html=True)
        
        prv_data = curr_slice.get("providers", {})
        p_labels = prv_data.get("labels", [])
        p_hours = prv_data.get("hours", [])
        p_overrun = prv_data.get("overrun", [])

        fig5 = go.Figure()
        fig5.add_trace(go.Bar(
            x=p_labels,
            y=p_hours,
            name="Clinical Hours Delivered",
            marker_color="#2563EB",
            yaxis="y"
        ))
        fig5.add_trace(go.Bar(
            x=p_labels,
            y=p_overrun,
            name="Slot Overrun Rate (%)",
            marker_color="#E11D48",
            yaxis="y2"
        ))
        fig5.update_layout(
            barmode="group",
            height=340,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
            yaxis=dict(title="Clinical Hours", showgrid=True, gridcolor="#f1f5f9"),
            yaxis2=dict(title="Overrun Rate (%)", overlaying="y", side="right", showgrid=False, range=[0, 60])
        )
        st.plotly_chart(fig5, use_container_width=True)

    with col_v6:
        st.markdown('<div class="chart-container-title">Visual 6: Patient Missed Appointments by Day of Week</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-container-subtitle">Identifying weekday attendance friction to inform operational booking buffers</div>', unsafe_allow_html=True)
        
        ns_data = curr_slice.get("noshow", {})
        days = ns_data.get("labels", [])
        rates = ns_data.get("data", [])
        colors = ["#E11D48" if "Mon" in d else "#3B82F6" for d in days]

        fig6 = go.Figure()
        fig6.add_trace(go.Bar(
            x=days,
            y=rates,
            name="No-Show Rate (%)",
            marker_color=colors,
            text=[f"{r:.1f}%" for r in rates],
            textposition="auto"
        ))
        fig6.update_layout(
            height=340,
            margin=dict(l=20, r=20, t=30, b=20),
            plot_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="Weekday"),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="No-Show Rate (%)", range=[0, 16])
        )
        st.plotly_chart(fig6, use_container_width=True)


# =============================================================================
# VIEW 2: SBAR CLINICAL GOVERNANCE
# =============================================================================
elif nav_mode == "📋 SBAR Clinical Governance":
    st.subheader("📋 Clinical Governance Briefing: SBAR Framework")
    st.markdown("Structured clinical and operational analysis for Health Service Executives and Chief Medical Officers.")

    col_sbar1, col_sbar2 = st.columns([1, 1])

    with col_sbar1:
        with st.container():
            st.markdown("""
            ### 1. SITUATION
            **The Operational Challenge**  
            Following the July 1 launch of an ambitious Chronic Disease Management campaign, patient complaints regarding lobby waiting times escalated dramatically. Clinic operations experienced acute mid-morning lobby congestion and clinician fatigue.
            """)
            st.divider()

        with st.container():
            st.markdown("""
            ### 2. BACKGROUND
            **Initial Executive Hypothesis**  
            Clinic executive leadership initially attributed delays to uncontrollable demand surge and physician pacing, considering expensive interventions: extending clinic operating hours or recruiting additional locum medical officers.
            """)
            st.divider()

        with st.container():
            st.markdown("""
            ### 3. ASSESSMENT
            **The Empirical Data Evidence**  
            - **Volume Impact:** Booked patient volume grew by only **+12.5%** (~2 additional patients per doctor per day).
            - **Control Stability:** Afternoon clinics remained remarkably stable (**35.2m Pre vs 35.8m Post**), disproving clinical pace or disease seasonality hypotheses.
            - **Queue Collapse:** Morning P90 wait times surged by **+82.1% (41.9m to 76.3m)** due to shortening morning slots from 20 to 15 minutes, which mathematically collided with complex 24.5-minute chronic disease consults.
            """)

    with col_sbar2:
        st.markdown("""
        ### 4. RECOMMENDATION
        #### Cost-Neutral 4-Point Restructuring Plan
        
        1. **🔹 Protected 30-Min Chronic Care Templates**  
           *Action:* Mandate dedicated 30-minute EHR templates for multi-morbid care plans.  
           *Impact:* Eliminates the structural 9.5-minute overrun per chronic encounter at the source.
        
        2. **🔹 10:30 AM Mid-Morning Catch-Up Buffer**  
           *Action:* Insert a single unbooked 15-minute administrative slot into morning sessions.  
           *Impact:* Functions as a queuing circuit breaker, absorbing stochastic morning slippage before the 11:00 AM wave.
        
        3. **🔹 Dynamic Front-End Nursing Intake**  
           *Action:* Reallocate nursing rosters to activate a 3rd vital-signs triage desk during peak arrival hours (08:30–10:15 AM).  
           *Impact:* Eliminates the 18-minute front-desk triage lobby choke point.
        
        4. **🔹 Automated Sunday 16:00 SMS Reminders**  
           *Action:* Deploy automated 2-way SMS confirmation prompts on Sunday afternoons.  
           *Impact:* Targets the elevated 12.88% Monday no-show rate caused by weekend scheduling forgetfulness, paired with a modest 5–8% Monday overbooking buffer.
        
        ---
        
        #### 🎯 Projected Operational Impact
        - **Morning P90 Wait Time:** Reduced from **76.3m to <35.0m**
        - **Provider Slot Overruns:** Reduced from **48.3% to <20.0%**
        - **Recruitment Budget Required:** **$0 (100% Cost-Neutral)**
        """)


# =============================================================================
# VIEW 3: ENCOUNTER DATA EXPLORER
# =============================================================================
elif nav_mode == "🔍 Encounter Data Explorer":
    st.subheader("🔍 Encounter Data Explorer")
    st.markdown("Filter, audit, and inspect the underlying 16,998 outpatient encounters directly.")

    if not raw_df.empty:
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            all_types = ["All Types"] + sorted(raw_df["appointment_type_name"].dropna().unique().tolist())
            selected_type = st.selectbox("Filter Appointment Type:", all_types)
        with col_f2:
            all_statuses = ["All Statuses"] + sorted(raw_df["status"].dropna().unique().tolist())
            selected_status = st.selectbox("Filter Encounter Status:", all_statuses)
        with col_f3:
            all_periods = ["All Periods"] + sorted(raw_df["workflow_period"].dropna().unique().tolist())
            selected_period = st.selectbox("Filter Workflow Period:", all_periods)

        filtered_df = raw_df.copy()
        if selected_type != "All Types":
            filtered_df = filtered_df[filtered_df["appointment_type_name"] == selected_type]
        if selected_status != "All Statuses":
            filtered_df = filtered_df[filtered_df["status"] == selected_status]
        if selected_period != "All Periods":
            filtered_df = filtered_df[filtered_df["workflow_period"] == selected_period]

        st.caption(f"Showing **{len(filtered_df):,}** of **{len(raw_df):,}** encounters.")

        # Data preview
        display_cols = [
            "appointment_id", "patient_id", "provider_name", "appointment_type_name",
            "appointment_date", "scheduled_time", "status", "workflow_period"
        ]
        available_cols = [c for c in display_cols if c in filtered_df.columns]
        st.dataframe(filtered_df[available_cols].head(500), use_container_width=True)

        # Download CSV
        csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Filtered Cohort (.CSV)",
            data=csv_bytes,
            file_name="clinic_encounters_filtered.csv",
            mime="text/csv"
        )
    else:
        st.warning("Clean appointments CSV dataset not found in data/processed/clean_appointments.csv.")


# =============================================================================
# VIEW 4: RELATIONAL DATA MODEL
# =============================================================================
elif nav_mode == "🏛️ Relational Data Model":
    st.subheader("🏛️ Relational Data Architecture & Quality Governance")
    st.markdown("Multi-table schema linking Synthea EHR patient master index to operational milestone timestamps.")

    if os.path.exists(ER_IMG_PATH):
        st.image(ER_IMG_PATH, use_container_width=True, caption="Figure: High-Resolution Outpatient Relational Data Model (SQLite Data Mart)")
    else:
        st.info("ER diagram image located at docs/images/data_model.png")

    st.markdown("---")
    st.subheader("🛡️ Healthcare Data Quality (DQ) Audit Summary")
    
    dq_col1, dq_col2 = st.columns(2)
    with dq_col1:
        st.markdown("""
        **1. Milestone Completeness (Kiosk Bypasses)**  
        - *Detected:* 6 acute walk-in encounters lacking kiosk arrival timestamps.  
        - *Clinical Root Cause:* Emergent triage bypass before administrative registration.  
        - *Resolution:* Quarantined from wait-time models to prevent artificial zero-wait bias.

        **2. Temporal Chronology & Hardware Drift**  
        - *Detected:* 3 encounters where triage start preceded arrival timestamp.  
        - *Clinical Root Cause:* Front-desk tablet clock desynchronization.  
        - *Resolution:* Quarantined time-sync faults to guarantee valid logical timestamps.
        """)
    with dq_col2:
        st.markdown("""
        **3. Session Discharge Integrity**  
        - *Detected:* 3 encounters missing final checkout timestamps at clinic close.  
        - *Clinical Root Cause:* Unclosed EHR sessions when patients exited without front-desk stop.  
        - *Resolution:* Quarantined from Total Clinic Length of Stay (LOS) calculations.

        **4. Referential Key & Test Entity Deduplication**  
        - *Detected:* 4 duplicate booking keys and 2 test provider records (`PRV-999`).  
        - *Resolution:* Earliest booking retained, test provider quarantined. Final mart certified 16,998 rows with 100% relational integrity.
        """)


# =============================================================================
# VIEW 5: SLIDE DECK & REPORTS
# =============================================================================
elif nav_mode == "📑 Slide Deck & Reports":
    st.subheader("📑 Executive PowerPoint Briefing Deck")
    st.markdown("Download and inspect the 11-slide widescreen executive briefing deck created for healthcare leadership.")

    if os.path.exists(PPTX_PATH):
        with open(PPTX_PATH, "rb") as f:
            pptx_bytes = f.read()
        st.download_button(
            label="📥 Download Executive Presentation (.PPTX)",
            data=pptx_bytes,
            file_name="clinic_operations_executive_briefing.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
    
    st.markdown("---")
    st.subheader("🖼️ Slide Previews (11 Widescreen Slides)")

    if os.path.exists(SLIDES_DIR):
        slide_files = sorted([f for f in os.listdir(SLIDES_DIR) if f.lower().endswith((".png", ".jpg"))], key=lambda x: int(''.join(filter(str.isdigit, x)) or 0))
        for s_file in slide_files:
            s_path = os.path.join(SLIDES_DIR, s_file)
            st.image(s_path, caption=s_file.replace(".PNG", "").replace(".JPG", ""), use_container_width=True)
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
