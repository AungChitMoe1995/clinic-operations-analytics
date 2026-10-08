-- =====================================================================
-- 01. VISIT VOLUME & UTILIZATION ANALYSIS
-- File: sql/01_volume_analysis.sql
-- Description: Analyzes clinic appointment volume, completed visits,
--              unique patient reach, and monthly trend trajectory.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Query 1.1: Overall Clinic Volume Summary
-- Business Question: What is the clinic's total booked vs completed volume?
-- ---------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_scheduled_appointments,
    COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) AS total_completed_visits,
    COUNT(CASE WHEN status = 'NO_SHOW' THEN 1 END) AS total_no_shows,
    COUNT(CASE WHEN status = 'CANCELLED' THEN 1 END) AS total_cancellations,
    COUNT(DISTINCT patient_id) AS total_unique_patients_booked,
    COUNT(DISTINCT CASE WHEN status = 'COMPLETED' THEN patient_id END) AS total_unique_patients_seen,
    ROUND(COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(*), 2) AS completion_rate_pct,
    ROUND(COUNT(CASE WHEN status = 'NO_SHOW' THEN 1 END) * 100.0 / COUNT(*), 2) AS no_show_rate_pct,
    ROUND(COUNT(CASE WHEN status = 'CANCELLED' THEN 1 END) * 100.0 / COUNT(*), 2) AS cancellation_rate_pct
FROM clean_appointments;

-- ---------------------------------------------------------------------
-- Query 1.2: Monthly Visit Volume & Active Patient Trajectory
-- Business Question: How did monthly appointment activity fluctuate in 2024?
-- ---------------------------------------------------------------------
SELECT 
    strftime('%Y-%m', appointment_date) AS year_month,
    workflow_period,
    COUNT(*) AS total_booked,
    COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) AS completed_visits,
    COUNT(DISTINCT patient_id) AS unique_patients,
    ROUND(COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) * 1.0 / COUNT(DISTINCT appointment_date), 1) AS avg_completed_per_day
FROM clean_appointments
GROUP BY strftime('%Y-%m', appointment_date), workflow_period
ORDER BY year_month;

-- ---------------------------------------------------------------------
-- Query 1.3: Day of Week Operational Load
-- Business Question: Which weekdays experience the heaviest patient demand?
-- ---------------------------------------------------------------------
SELECT 
    CASE CAST(strftime('%w', appointment_date) AS INTEGER)
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
    END AS day_of_week,
    COUNT(*) AS total_scheduled,
    COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) AS completed_visits,
    ROUND(COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) * 1.0 / COUNT(DISTINCT appointment_date), 1) AS avg_visits_per_operating_day
FROM clean_appointments
GROUP BY strftime('%w', appointment_date)
ORDER BY CAST(strftime('%w', appointment_date) AS INTEGER);
