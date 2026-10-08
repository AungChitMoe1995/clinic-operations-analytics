-- =====================================================================
-- 04. PATIENT WAITING TIME & QUEUING DYNAMICS ANALYSIS
-- File: sql/04_waiting_time_analysis.sql
-- Description: Analyzes patient waiting times across milestone stages,
--              calculates Mean, Median (P50), P75, and P90 percentiles
--              using SQL CTEs and Window Functions, and profiles bottlenecks.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Query 4.1: Overall Waiting Time Milestones (Mean & Standard Deviation)
-- Business Question: What is the average duration of each patient journey stage?
-- ---------------------------------------------------------------------
SELECT 
    COUNT(*) AS completed_encounters_analyzed,
    ROUND(AVG((julianday(triage_start) - julianday(arrival_time)) * 1440), 1) AS avg_triage_wait_min,
    ROUND(AVG((julianday(triage_end) - julianday(triage_start)) * 1440), 1) AS avg_triage_service_min,
    ROUND(AVG((julianday(doctor_start) - julianday(triage_end)) * 1440), 1) AS avg_doctor_queue_min,
    ROUND(AVG((julianday(doctor_start) - julianday(arrival_time)) * 1440), 1) AS avg_total_clinical_wait_min,
    ROUND(AVG((julianday(doctor_end) - julianday(doctor_start)) * 1440), 1) AS avg_consultation_duration_min,
    ROUND(AVG((julianday(checkout_time) - julianday(arrival_time)) * 1440), 1) AS avg_total_clinic_los_min
FROM clean_appointments
WHERE is_valid_wait_time = 1;

-- ---------------------------------------------------------------------
-- Query 4.2: Percentile Distribution of Total Clinical Wait (Arrival -> Doctor Start)
-- Business Question: What are the Median (P50), P75, and P90 wait times?
-- Demonstrates: Advanced SQL Window Functions & Percentile Approximation
-- ---------------------------------------------------------------------
WITH wait_calculations AS (
    SELECT 
        appointment_id,
        ROUND((julianday(doctor_start) - julianday(arrival_time)) * 1440, 2) AS wait_min,
        NTILE(100) OVER (ORDER BY (julianday(doctor_start) - julianday(arrival_time)) * 1440) AS percentile_bucket
    FROM clean_appointments
    WHERE is_valid_wait_time = 1
)
SELECT 
    ROUND(AVG(wait_min), 1) AS mean_wait_min,
    ROUND(MAX(CASE WHEN percentile_bucket = 50 THEN wait_min END), 1) AS median_p50_wait_min,
    ROUND(MAX(CASE WHEN percentile_bucket = 75 THEN wait_min END), 1) AS p75_wait_min,
    ROUND(MAX(CASE WHEN percentile_bucket = 90 THEN wait_min END), 1) AS p90_wait_min,
    ROUND(MAX(CASE WHEN percentile_bucket = 95 THEN wait_min END), 1) AS p95_wait_min
FROM wait_calculations;

-- ---------------------------------------------------------------------
-- Query 4.3: Waiting Time by Appointment Hour of the Day (Diurnal Queue Curve)
-- Business Question: At what hour of the operating day is congestion greatest?
-- ---------------------------------------------------------------------
WITH hourly_waits AS (
    SELECT 
        strftime('%H', scheduled_time) || ':00' AS scheduled_hour,
        (julianday(doctor_start) - julianday(arrival_time)) * 1440 AS wait_min,
        NTILE(100) OVER (
            PARTITION BY strftime('%H', scheduled_time)
            ORDER BY (julianday(doctor_start) - julianday(arrival_time)) * 1440
        ) AS pct_tile
    FROM clean_appointments
    WHERE is_valid_wait_time = 1
)
SELECT 
    scheduled_hour,
    COUNT(*) AS visits_seen,
    ROUND(AVG(wait_min), 1) AS mean_wait_min,
    ROUND(MAX(CASE WHEN pct_tile = 50 THEN wait_min END), 1) AS median_wait_min,
    ROUND(MAX(CASE WHEN pct_tile = 90 THEN wait_min END), 1) AS p90_wait_min
FROM hourly_waits
GROUP BY scheduled_hour
ORDER BY scheduled_hour;

-- ---------------------------------------------------------------------
-- Query 4.4: Waiting Time by Clinical Appointment Type
-- Business Question: Which visit categories experience the longest patient delays?
-- ---------------------------------------------------------------------
WITH type_waits AS (
    SELECT 
        t.appointment_type_name,
        (julianday(a.doctor_start) - julianday(a.arrival_time)) * 1440 AS wait_min,
        NTILE(100) OVER (
            PARTITION BY t.appointment_type_name
            ORDER BY (julianday(a.doctor_start) - julianday(a.arrival_time)) * 1440
        ) AS pct_tile
    FROM clean_appointments a
    JOIN appointment_types t ON a.appointment_type_id = t.appointment_type_id
    WHERE a.is_valid_wait_time = 1
)
SELECT 
    appointment_type_name,
    COUNT(*) AS completed_visits,
    ROUND(AVG(wait_min), 1) AS mean_wait_min,
    ROUND(MAX(CASE WHEN pct_tile = 50 THEN wait_min END), 1) AS median_wait_min,
    ROUND(MAX(CASE WHEN pct_tile = 90 THEN wait_min END), 1) AS p90_wait_min
FROM type_waits
GROUP BY appointment_type_name
ORDER BY p90_wait_min DESC;
