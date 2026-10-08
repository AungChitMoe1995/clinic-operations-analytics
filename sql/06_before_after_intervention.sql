-- =====================================================================
-- 06. BEFORE VS AFTER WORKFLOW INTERVENTION INVESTIGATION
-- File: sql/06_before_after_intervention.sql
-- Description: Quasi-experimental comparative analysis evaluating clinic
--              KPIs before (Jan-Jun) vs after (Jul-Dec) the July 1
--              Morning Slot Compression & Chronic Care Campaign.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Query 6.1: High-Level Operational KPI Comparison (Pre vs Post)
-- Business Question: What high-level clinic metrics changed after July 1?
-- ---------------------------------------------------------------------
WITH pre_post_metrics AS (
    SELECT 
        workflow_period,
        COUNT(*) AS total_scheduled,
        COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) AS completed_visits,
        ROUND(COUNT(CASE WHEN status = 'NO_SHOW' THEN 1 END) * 100.0 / COUNT(*), 2) AS no_show_rate_pct,
        ROUND(COUNT(CASE WHEN status = 'CANCELLED' THEN 1 END) * 100.0 / COUNT(*), 2) AS cancellation_rate_pct
    FROM clean_appointments
    GROUP BY workflow_period
),
wait_metrics AS (
    SELECT 
        workflow_period,
        ROUND(AVG((julianday(doctor_start) - julianday(arrival_time)) * 1440), 1) AS mean_wait_min,
        ROUND(AVG((julianday(triage_start) - julianday(arrival_time)) * 1440), 1) AS mean_triage_wait_min,
        ROUND(AVG((julianday(doctor_start) - julianday(triage_end)) * 1440), 1) AS mean_doc_queue_min,
        ROUND(AVG((julianday(doctor_end) - julianday(doctor_start)) * 1440), 1) AS mean_consult_min
    FROM clean_appointments
    WHERE is_valid_wait_time = 1
    GROUP BY workflow_period
)
SELECT 
    p.workflow_period,
    p.total_scheduled,
    p.completed_visits,
    p.no_show_rate_pct,
    p.cancellation_rate_pct,
    w.mean_triage_wait_min,
    w.mean_doc_queue_min,
    w.mean_wait_min,
    w.mean_consult_min
FROM pre_post_metrics p
JOIN wait_metrics w ON p.workflow_period = w.workflow_period;

-- ---------------------------------------------------------------------
-- Query 6.2: Percentile Wait Breakdown: Morning vs Afternoon Session (Root Cause Isolation)
-- Business Question: Did waiting time explode uniformly or exclusively during morning clinics?
-- ---------------------------------------------------------------------
WITH session_waits AS (
    SELECT 
        workflow_period,
        CASE 
            WHEN CAST(strftime('%H', scheduled_time) AS INTEGER) < 12 THEN 'Morning Clinic (08:30-11:30)'
            ELSE 'Afternoon Clinic (13:30-15:30)'
        END AS clinic_session,
        (julianday(doctor_start) - julianday(arrival_time)) * 1440 AS wait_min,
        NTILE(100) OVER (
            PARTITION BY workflow_period, 
                         CASE WHEN CAST(strftime('%H', scheduled_time) AS INTEGER) < 12 THEN 'Morning' ELSE 'Afternoon' END
            ORDER BY (julianday(doctor_start) - julianday(arrival_time)) * 1440
        ) AS pct_tile
    FROM clean_appointments
    WHERE is_valid_wait_time = 1
)
SELECT 
    workflow_period,
    clinic_session,
    COUNT(*) AS completed_visits,
    ROUND(AVG(wait_min), 1) AS mean_wait_min,
    ROUND(MAX(CASE WHEN pct_tile = 50 THEN wait_min END), 1) AS median_wait_min,
    ROUND(MAX(CASE WHEN pct_tile = 75 THEN wait_min END), 1) AS p75_wait_min,
    ROUND(MAX(CASE WHEN pct_tile = 90 THEN wait_min END), 1) AS p90_wait_min
FROM session_waits
GROUP BY workflow_period, clinic_session
ORDER BY clinic_session, workflow_period;

-- ---------------------------------------------------------------------
-- Query 6.3: Appointment Mix Shift Pre vs Post Intervention
-- Business Question: Did the proportion of complex chronic visits in morning slots increase?
-- ---------------------------------------------------------------------
SELECT 
    workflow_period,
    COUNT(*) AS total_morning_scheduled,
    ROUND(COUNT(CASE WHEN appointment_type_id = 'APT-CHRON' THEN 1 END) * 100.0 / COUNT(*), 1) AS chronic_care_pct,
    ROUND(COUNT(CASE WHEN appointment_type_id = 'APT-ROUT' THEN 1 END) * 100.0 / COUNT(*), 1) AS routine_pct,
    ROUND(COUNT(CASE WHEN appointment_type_id = 'APT-ACUT' THEN 1 END) * 100.0 / COUNT(*), 1) AS acute_pct,
    ROUND(COUNT(CASE WHEN scheduled_duration_min = 15 THEN 1 END) * 100.0 / COUNT(*), 1) AS pct_15min_compressed_slots
FROM clean_appointments
WHERE CAST(strftime('%H', scheduled_time) AS INTEGER) < 12
GROUP BY workflow_period;
