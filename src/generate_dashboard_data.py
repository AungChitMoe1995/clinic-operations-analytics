"""
generate_dashboard_data.py
---------------------------
Queries data/clinic_operations.db and builds the pre-aggregated
analytical datasets for all 15 combinations of:
- Operational Period (ALL, PRE, POST)
- Attending Clinician (ALL, PRV-001, PRV-002, PRV-003, PRV-004)

Injects this multi-dimensional data directly into dashboard/index.html
so that every chart and KPI card dynamically updates in real-time
when any filter dropdown is selected!
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "clinic_operations.db")
HTML_PATH = os.path.join(BASE_DIR, "dashboard", "index.html")

def build_dashboard_data():
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        a.appointment_id,
        a.patient_id,
        a.provider_id,
        p.provider_name,
        a.appointment_type_id,
        t.appointment_type_name,
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
        a.is_valid_wait_time
    FROM clean_appointments a
    JOIN providers p ON a.provider_id = p.provider_id
    JOIN appointment_types t ON a.appointment_type_id = t.appointment_type_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Preprocess
    df["arrival_time"] = pd.to_datetime(df["arrival_time"])
    df["doctor_start"] = pd.to_datetime(df["doctor_start"])
    df["doctor_end"] = pd.to_datetime(df["doctor_end"])
    df["appointment_date"] = pd.to_datetime(df["appointment_date"])
    df["scheduled_hour"] = pd.to_datetime(df["scheduled_time"], format="%H:%M:%S").dt.hour
    df["day_of_week"] = df["appointment_date"].dt.day_name()
    df["month_idx"] = df["appointment_date"].dt.month

    # Milestone metrics
    df["wait_min"] = (df["doctor_start"] - df["arrival_time"]).dt.total_seconds() / 60.0
    df["consult_min"] = (df["doctor_end"] - df["doctor_start"]).dt.total_seconds() / 60.0
    df["is_overrun"] = (df["consult_min"] - df["scheduled_duration_min"]) > 5.0
    df["clinic_session"] = np.where(df["scheduled_hour"] < 12, "Morning", "Afternoon")

    periods = {
        "ALL": df,
        "PRE": df[df["workflow_period"] == "PRE_INTERVENTION"],
        "POST": df[df["workflow_period"] == "POST_INTERVENTION"]
    }

    providers = {
        "ALL": None,
        "PRV-001": "PRV-001",
        "PRV-002": "PRV-002",
        "PRV-003": "PRV-003",
        "PRV-004": "PRV-004"
    }

    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    hours_list = [8, 9, 10, 11, 13, 14, 15]
    days_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    apt_type_order = [
        "Chronic Disease Care Plan Review",
        "Comprehensive New Patient",
        "Routine Follow-Up",
        "Acute / Same-Day Illness",
        "Preventive Wellness / Health Check"
    ]
    apt_short_names = [
        "Chronic Care Review",
        "Comprehensive New Patient",
        "Routine Follow-Up",
        "Acute Illness",
        "Preventive Health Check"
    ]
    prov_ids = ["PRV-001", "PRV-003", "PRV-002", "PRV-004"]
    prov_short_names = ["Dr. Arthur Vance", "Dr. Tariq Al-Mansoor", "Dr. Brenda Chen", "Dr. Sarah Jenkins"]

    dashboard_slices = {}

    for p_key, p_df in periods.items():
        for prov_key, prov_id in providers.items():
            slice_key = f"{p_key}_{prov_key}"
            
            # Apply provider filter if not ALL
            if prov_id is not None:
                sub_df = p_df[p_df["provider_id"] == prov_id]
            else:
                sub_df = p_df

            # Valid completed wait cohort
            sub_valid = sub_df[(sub_df["status"] == "COMPLETED") & (sub_df["is_valid_wait_time"] == 1)]

            # 1. KPIs
            n_booked = len(sub_df)
            n_completed = int((sub_df["status"] == "COMPLETED").sum())
            n_noshow = int((sub_df["status"] == "NO_SHOW").sum())
            n_patients = int(sub_df[sub_df["status"] == "COMPLETED"]["patient_id"].nunique())
            
            op_days = 250 if p_key == "ALL" else 125
            visits_per_day = round(n_booked / op_days, 1) if op_days > 0 else 0
            comp_rate = round(n_completed / n_booked * 100, 1) if n_booked > 0 else 0
            noshow_rate = round(n_noshow / n_booked * 100, 1) if n_booked > 0 else 0
            
            med_wait = round(float(sub_valid["wait_min"].median()), 1) if len(sub_valid) > 0 else 0
            p90_wait = round(float(np.percentile(sub_valid["wait_min"], 90)), 1) if len(sub_valid) > 0 else 0

            p90_subtext = f"Worst 10% waited ≥ {p90_wait:.1f}m"
            if p_key == "POST":
                p90_subtext = f"Worst 10% waited ≥ {p90_wait:.1f}m (Peak: 76.3m)"
            elif p_key == "PRE":
                p90_subtext = f"Worst 10% waited ≥ {p90_wait:.1f}m (Baseline)"

            kpis = {
                "booked": f"{n_booked:,}",
                "booked_sub": f"~{visits_per_day} appointments / day",
                "completed": f"{n_completed:,}",
                "completed_sub": f"{comp_rate}% Completion Rate",
                "patients": f"{n_patients:,}",
                "median": f"{med_wait:.1f} m",
                "p90": f"{p90_wait:.1f} m",
                "p90_sub": p90_subtext,
                "noshow": f"{noshow_rate:.1f}%",
                "noshow_sub": f"{n_noshow:,} Missed Appointments"
            }

            # 2. Monthly Volume
            if p_key == "ALL":
                m_labels = month_names
                m_booked = [int((sub_df["month_idx"] == m).sum()) for m in range(1, 13)]
                m_comp = [int(((sub_df["month_idx"] == m) & (sub_df["status"] == "COMPLETED")).sum()) for m in range(1, 13)]
            elif p_key == "PRE":
                m_labels = month_names[:6]
                m_booked = [int((sub_df["month_idx"] == m).sum()) for m in range(1, 7)]
                m_comp = [int(((sub_df["month_idx"] == m) & (sub_df["status"] == "COMPLETED")).sum()) for m in range(1, 7)]
            else: # POST
                m_labels = month_names[6:]
                m_booked = [int((sub_df["month_idx"] == m).sum()) for m in range(7, 13)]
                m_comp = [int(((sub_df["month_idx"] == m) & (sub_df["status"] == "COMPLETED")).sum()) for m in range(7, 13)]

            # 3. Hourly Curve
            h_labels = [f"{h:02d}:00" for h in hours_list]
            h_p90 = []
            h_med = []
            for h in hours_list:
                h_vals = sub_valid[sub_valid["scheduled_hour"] == h]["wait_min"]
                if len(h_vals) > 0:
                    h_p90.append(round(float(np.percentile(h_vals, 90)), 1))
                    h_med.append(round(float(h_vals.median()), 1))
                else:
                    h_p90.append(0)
                    h_med.append(0)

            # 4. Session Comparison (Morning vs Afternoon Pre vs Post)
            # If sub_df is specific to provider, compute session breakdown for that provider
            p_sub = df if prov_id is None else df[df["provider_id"] == prov_id]
            p_sub_valid = p_sub[(p_sub["status"] == "COMPLETED") & (p_sub["is_valid_wait_time"] == 1)]
            
            m_pre = p_sub_valid[(p_sub_valid["workflow_period"] == "PRE_INTERVENTION") & (p_sub_valid["clinic_session"] == "Morning")]["wait_min"]
            m_post = p_sub_valid[(p_sub_valid["workflow_period"] == "POST_INTERVENTION") & (p_sub_valid["clinic_session"] == "Morning")]["wait_min"]
            a_pre = p_sub_valid[(p_sub_valid["workflow_period"] == "PRE_INTERVENTION") & (p_sub_valid["clinic_session"] == "Afternoon")]["wait_min"]
            a_post = p_sub_valid[(p_sub_valid["workflow_period"] == "POST_INTERVENTION") & (p_sub_valid["clinic_session"] == "Afternoon")]["wait_min"]

            sess_labels = ['Morning Clinic (Pre)', 'Morning Clinic (Post)', 'Afternoon Clinic (Pre)', 'Afternoon Clinic (Post)']
            sess_med = [
                round(float(m_pre.median()), 1) if len(m_pre) > 0 else 0,
                round(float(m_post.median()), 1) if len(m_post) > 0 else 0,
                round(float(a_pre.median()), 1) if len(a_pre) > 0 else 0,
                round(float(a_post.median()), 1) if len(a_post) > 0 else 0
            ]
            sess_p90 = [
                round(float(np.percentile(m_pre, 90)), 1) if len(m_pre) > 0 else 0,
                round(float(np.percentile(m_post, 90)), 1) if len(m_post) > 0 else 0,
                round(float(np.percentile(a_pre, 90)), 1) if len(a_pre) > 0 else 0,
                round(float(np.percentile(a_post, 90)), 1) if len(a_post) > 0 else 0
            ]

            # 5. Appointment Type
            apt_med = []
            apt_p90 = []
            for apt_t in apt_type_order:
                apt_vals = sub_valid[sub_valid["appointment_type_name"] == apt_t]["wait_min"]
                if len(apt_vals) > 0:
                    apt_med.append(round(float(apt_vals.median()), 1))
                    apt_p90.append(round(float(np.percentile(apt_vals, 90)), 1))
                else:
                    apt_med.append(0)
                    apt_p90.append(0)

            # 6. Provider Workload (hours & overruns)
            # If provider filter is active, highlight or focus on that provider
            prov_hours = []
            prov_overruns = []
            for pid in prov_ids:
                prv_vals = sub_df[sub_df["provider_id"] == pid]
                prv_valid = prv_vals[(prv_vals["status"] == "COMPLETED") & (prv_vals["is_valid_wait_time"] == 1)]
                total_hrs = round(float(prv_valid["consult_min"].sum() / 60.0), 1) if len(prv_valid) > 0 else 0
                overrun_rate = round(float(prv_valid["is_overrun"].sum() / len(prv_valid) * 100), 1) if len(prv_valid) > 0 else 0
                prov_hours.append(total_hrs)
                prov_overruns.append(overrun_rate)

            # 7. No-Show by Day
            ns_days = []
            for day in days_list:
                day_rows = sub_df[sub_df["day_of_week"] == day]
                if len(day_rows) > 0:
                    ns_rate = round(float((day_rows["status"] == "NO_SHOW").sum() / len(day_rows) * 100), 2)
                    ns_days.append(ns_rate)
                else:
                    ns_days.append(0)

            dashboard_slices[slice_key] = {
                "kpis": kpis,
                "monthly": {"labels": m_labels, "booked": m_booked, "completed": m_comp},
                "hourly": {"labels": h_labels, "p90": h_p90, "median": h_med},
                "session": {"labels": sess_labels, "median": sess_med, "p90": sess_p90},
                "apt_type": {"labels": apt_short_names, "median": apt_med, "p90": apt_p90},
                "providers": {"labels": prov_short_names, "hours": prov_hours, "overrun": prov_overruns},
                "noshow": {"labels": days_list, "data": ns_days}
            }

    print(f"Generated {len(dashboard_slices)} interactive data slices.")
    return dashboard_slices

def inject_into_html(slices):
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # Convert slices to JSON string
    json_str = json.dumps(slices, indent=2)

    # Replace DASHBOARD_DATA in HTML
    start_tag = "// Embedded analytical metrics"
    end_tag = "let chartMonthly, chartHourly, chartPrePost, chartAptType, chartProvider, chartNoShow;"

    replacement = f"""// Embedded analytical metrics
    const DASHBOARD_DATA = {json_str};

    {end_tag}"""

    # Find and replace the block
    if start_tag in html and end_tag in html:
        part1 = html[:html.find(start_tag)]
        part2 = html[html.find(end_tag) + len(end_tag):]
        new_script = f"""{part1}// Embedded analytical metrics
    const DASHBOARD_DATA = {json_str};

    let chartMonthly, chartHourly, chartPrePost, chartAptType, chartProvider, chartNoShow;

    function initCharts() {{
        const initial = DASHBOARD_DATA['ALL_ALL'];

        // Chart 1: Monthly Volume
        const ctxMonthly = document.getElementById('chartMonthlyVol').getContext('2d');
        chartMonthly = new Chart(ctxMonthly, {{
            type: 'bar',
            data: {{
                labels: initial.monthly.labels,
                datasets: [
                    {{
                        label: 'Total Booked',
                        data: initial.monthly.booked,
                        backgroundColor: '#1E3A8A'
                    }},
                    {{
                        label: 'Completed Visits',
                        data: initial.monthly.completed,
                        backgroundColor: '#3B82F6'
                    }}
                ]
            }},
            options: {{
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ position: 'top' }} }},
                scales: {{ y: {{ beginAtZero: true }} }}
            }}
        }});

        // Chart 2: Hourly Diurnal Curve
        const ctxHourly = document.getElementById('chartHourlyCurve').getContext('2d');
        chartHourly = new Chart(ctxHourly, {{
            type: 'line',
            data: {{
                labels: initial.hourly.labels,
                datasets: [
                    {{
                        label: 'P90 Wait (Worst 10% Delays)',
                        data: initial.hourly.p90,
                        borderColor: '#E11D48',
                        backgroundColor: 'rgba(225, 29, 72, 0.1)',
                        fill: true,
                        tension: 0.3,
                        pointRadius: 5
                    }},
                    {{
                        label: 'Median Wait (Typical Patient)',
                        data: initial.hourly.median,
                        borderColor: '#1E3A8A',
                        backgroundColor: 'transparent',
                        tension: 0.3,
                        pointRadius: 5
                    }}
                ]
            }},
            options: {{
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ 
                    legend: {{ position: 'top' }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                if (context.datasetIndex === 0) {{
                                    return 'P90 Wait: ' + context.parsed.y + ' min (Worst 10% Cutoff)';
                                }} else {{
                                    return 'Median Wait: ' + context.parsed.y + ' min (Typical Patient)';
                                }}
                            }}
                        }}
                    }}
                }},
                scales: {{ 
                    y: {{ 
                        beginAtZero: true, 
                        title: {{ display: true, text: 'Wait Time (Minutes)' }} 
                    }} 
                }}
            }}
        }});

        // Chart 3: Pre vs Post Session Comparison
        const ctxPrePost = document.getElementById('chartPrePost').getContext('2d');
        chartPrePost = new Chart(ctxPrePost, {{
            type: 'bar',
            data: {{
                labels: initial.session.labels,
                datasets: [
                    {{
                        label: 'Median Wait (Typical)',
                        data: initial.session.median,
                        backgroundColor: '#3B82F6'
                    }},
                    {{
                        label: 'P90 Wait (Worst 10% Delays)',
                        data: initial.session.p90,
                        backgroundColor: '#E11D48'
                    }}
                ]
            }},
            options: {{
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ 
                    legend: {{ position: 'top' }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                if (context.datasetIndex === 0) {{
                                    return 'Median Wait: ' + context.parsed.y + ' min (Typical Patient)';
                                }} else {{
                                    return 'P90 Wait: ' + context.parsed.y + ' min (Worst 10% Threshold)';
                                }}
                            }}
                        }}
                    }}
                }},
                scales: {{ 
                    y: {{ 
                        beginAtZero: true, 
                        title: {{ display: true, text: 'Wait Time (Minutes)' }}
                    }} 
                }}
            }}
        }});

        // Chart 4: Waiting Time by Appointment Type
        const ctxAptType = document.getElementById('chartAptType').getContext('2d');
        chartAptType = new Chart(ctxAptType, {{
            type: 'bar',
            data: {{
                labels: initial.apt_type.labels,
                datasets: [
                    {{
                        label: 'Median Wait (Typical)',
                        data: initial.apt_type.median,
                        backgroundColor: '#0D9488'
                    }},
                    {{
                        label: 'P90 Wait (Worst 10% Delays)',
                        data: initial.apt_type.p90,
                        backgroundColor: '#F59E0B'
                    }}
                ]
            }},
            options: {{
                indexAxis: 'y',
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ 
                    legend: {{ position: 'top' }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                if (context.datasetIndex === 0) {{
                                    return 'Median Wait: ' + context.parsed.x + ' min (Typical)';
                                }} else {{
                                    return 'P90 Wait: ' + context.parsed.x + ' min (Worst 10% Delay)';
                                }}
                            }}
                        }}
                    }}
                }},
                scales: {{ 
                    x: {{ 
                        beginAtZero: true, 
                        title: {{ display: true, text: 'Wait Time (Minutes)' }} 
                    }} 
                }}
            }}
        }});

        // Chart 5: Provider Workload (Side-by-Side Dual Grouped Bars)
        const ctxProvider = document.getElementById('chartProvider').getContext('2d');
        chartProvider = new Chart(ctxProvider, {{
            type: 'bar',
            data: {{
                labels: initial.providers.labels,
                datasets: [
                    {{
                        label: 'Clinical Hours (Left Axis)',
                        data: initial.providers.hours,
                        backgroundColor: '#1E3A8A',
                        borderRadius: 4,
                        yAxisID: 'y'
                    }},
                    {{
                        label: 'Slot Overrun Rate % (Right Axis)',
                        data: initial.providers.overrun,
                        backgroundColor: '#E11D48',
                        borderRadius: 4,
                        yAxisID: 'y1'
                    }}
                ]
            }},
            options: {{
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'top' }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                if (context.datasetIndex === 0) {{
                                    return 'Clinical Hours: ' + context.parsed.y + ' hrs';
                                }} else {{
                                    return 'Slot Overrun Rate: ' + context.parsed.y + '%';
                                }}
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{ 
                        type: 'linear', 
                        position: 'left', 
                        beginAtZero: true, 
                        title: {{ display: true, text: 'Clinical Hours (hrs)' }} 
                    }},
                    y1: {{ 
                        type: 'linear', 
                        position: 'right', 
                        beginAtZero: true, 
                        max: 60, 
                        grid: {{ drawOnChartArea: false }}, 
                        title: {{ display: true, text: 'Slot Overrun Rate (%)' }} 
                    }}
                }}
            }}
        }});

        // Chart 6: No-Show by Day
        const ctxNoShow = document.getElementById('chartNoShow').getContext('2d');
        chartNoShow = new Chart(ctxNoShow, {{
            type: 'bar',
            data: {{
                labels: initial.noshow.labels,
                datasets: [
                    {{
                        label: 'No-Show Rate (%)',
                        data: initial.noshow.data,
                        backgroundColor: ['#E11D48', '#3B82F6', '#3B82F6', '#3B82F6', '#3B82F6']
                    }}
                ]
            }},
            options: {{
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: 'No-Show %' }} }} }}
            }}
        }});

        // Trigger dynamic scale initialization
        updateDashboard();
    }}

    function updateDashboard() {{
        const period = document.getElementById('filter-period').value;
        const provider = document.getElementById('filter-provider').value;
        const key = `${{period}}_${{provider}}`;
        const slice = DASHBOARD_DATA[key] || DASHBOARD_DATA['ALL_ALL'];

        // 1. Update KPI Cards
        document.getElementById('kpi-booked').textContent = slice.kpis.booked;
        document.getElementById('kpi-booked-sub').textContent = slice.kpis.booked_sub;
        document.getElementById('kpi-completed').textContent = slice.kpis.completed;
        document.getElementById('kpi-patients').textContent = slice.kpis.patients;
        document.getElementById('kpi-median').textContent = slice.kpis.median;
        document.getElementById('kpi-p90').textContent = slice.kpis.p90;
        document.getElementById('kpi-p90-sub').textContent = slice.kpis.p90_sub;
        document.getElementById('kpi-noshow').textContent = slice.kpis.noshow;

        // 2. Update Visual 1: Monthly Volume
        chartMonthly.data.labels = slice.monthly.labels;
        chartMonthly.data.datasets[0].data = slice.monthly.booked;
        chartMonthly.data.datasets[1].data = slice.monthly.completed;
        const maxM = Math.max(...slice.monthly.booked, ...slice.monthly.completed, 10);
        chartMonthly.options.scales.y.max = Math.ceil((maxM * 1.18) / 100) * 100;
        chartMonthly.update();

        // 3. Update Visual 2: Hourly Diurnal Curve (DYNAMIC HEADROOM PREVENTS CLIPPING)
        chartHourly.data.labels = slice.hourly.labels;
        chartHourly.data.datasets[0].data = slice.hourly.p90;
        chartHourly.data.datasets[1].data = slice.hourly.median;
        const maxH = Math.max(...slice.hourly.p90, ...slice.hourly.median, 10);
        chartHourly.options.scales.y.max = Math.ceil((maxH * 1.25) / 10) * 10;
        chartHourly.update();

        // 4. Update Visual 3: Session Pre vs Post
        chartPrePost.data.datasets[0].data = slice.session.median;
        chartPrePost.data.datasets[1].data = slice.session.p90;
        const maxS = Math.max(...slice.session.median, ...slice.session.p90, 10);
        chartPrePost.options.scales.y.max = Math.ceil((maxS * 1.20) / 10) * 10;
        chartPrePost.update();

        // 5. Update Visual 4: Wait Time by Appointment Type
        chartAptType.data.labels = slice.apt_type.labels;
        chartAptType.data.datasets[0].data = slice.apt_type.median;
        chartAptType.data.datasets[1].data = slice.apt_type.p90;
        const maxA = Math.max(...slice.apt_type.median, ...slice.apt_type.p90, 10);
        chartAptType.options.scales.x.max = Math.ceil((maxA * 1.20) / 10) * 10;
        chartAptType.update();

        // 6. Update Visual 5: Provider Workload
        chartProvider.data.datasets[0].data = slice.providers.hours;
        chartProvider.data.datasets[1].data = slice.providers.overrun;
        const maxHrs = Math.max(...slice.providers.hours, 10);
        chartProvider.options.scales.y.max = Math.ceil((maxHrs * 1.15) / 100) * 100;
        const maxOv = Math.max(...slice.providers.overrun, 10);
        chartProvider.options.scales.y1.max = Math.ceil((maxOv * 1.25) / 10) * 10;
        chartProvider.update();

        // 7. Update Visual 6: No-Show by Day
        chartNoShow.data.datasets[0].data = slice.noshow.data;
        const maxNS = Math.max(...slice.noshow.data, 5);
        chartNoShow.options.scales.y.max = Math.ceil((maxNS * 1.30) / 5) * 5;
        chartNoShow.update();
    }}

    window.onload = initCharts;
</script>

</body>
</html>"""
        with open(HTML_PATH, "w", encoding="utf-8") as f:
            f.write(new_script)
        print(f"Successfully injected dynamic filtering datasets into {HTML_PATH}!")
    else:
        print("Warning: Could not find script anchor tags in HTML.")

def main():
    slices = build_dashboard_data()
    inject_into_html(slices)
    json_path = os.path.join(BASE_DIR, "dashboard", "dashboard_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(slices, f, indent=2)
    print(f"Successfully saved {json_path}!")

if __name__ == "__main__":
    main()
