-- =====================================================================
-- 02. SCHEDULING PATTERNS & APPOINTMENT MIX ANALYSIS
-- File: sql/02_scheduling_patterns.sql
-- Description: Examines appointment type mix, booking channel utilization,
--              provider appointment distribution, and hourly slot density.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Query 2.1: Appointment Type Distribution & Planned Resource Allocation
-- Business Question: What clinical appointment types dominate the schedule?
-- ---------------------------------------------------------------------
SELECT 
    t.appointment_type_id,
    t.appointment_type_name,
    t.standard_duration_min,
    COUNT(a.appointment_id) AS total_scheduled,
    ROUND(COUNT(a.appointment_id) * 100.0 / (SELECT COUNT(*) FROM clean_appointments), 2) AS pct_of_total_schedule,
    COUNT(CASE WHEN a.status = 'COMPLETED' THEN 1 END) AS completed_visits,
    ROUND(COUNT(CASE WHEN a.status = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(a.appointment_id), 2) AS completion_rate_pct
FROM appointment_types t
JOIN clean_appointments a ON t.appointment_type_id = a.appointment_type_id
GROUP BY t.appointment_type_id, t.appointment_type_name, t.standard_duration_min
ORDER BY total_scheduled DESC;

-- ---------------------------------------------------------------------
-- Query 2.2: Provider Caseload Distribution by Appointment Type
-- Business Question: How do appointment types distribute across individual clinicians?
-- ---------------------------------------------------------------------
SELECT 
    p.provider_name,
    p.specialty,
    COUNT(a.appointment_id) AS total_scheduled,
    ROUND(COUNT(CASE WHEN a.appointment_type_id = 'APT-CHRON' THEN 1 END) * 100.0 / COUNT(a.appointment_id), 1) AS chronic_care_pct,
    ROUND(COUNT(CASE WHEN a.appointment_type_id = 'APT-ROUT' THEN 1 END) * 100.0 / COUNT(a.appointment_id), 1) AS routine_pct,
    ROUND(COUNT(CASE WHEN a.appointment_type_id = 'APT-ACUT' THEN 1 END) * 100.0 / COUNT(a.appointment_id), 1) AS acute_pct,
    ROUND(COUNT(CASE WHEN a.appointment_type_id = 'APT-NEWP' THEN 1 END) * 100.0 / COUNT(a.appointment_id), 1) AS new_patient_pct
FROM providers p
JOIN clean_appointments a ON p.provider_id = a.provider_id
GROUP BY p.provider_id, p.provider_name, p.specialty
ORDER BY total_scheduled DESC;

-- ---------------------------------------------------------------------
-- Query 2.3: Hourly Appointment Density & Peak Scheduling Windows
-- Business Question: When are patient appointments most heavily concentrated?
-- ---------------------------------------------------------------------
SELECT 
    strftime('%H', scheduled_time) || ':00' AS hour_of_day,
    CASE 
        WHEN CAST(strftime('%H', scheduled_time) AS INTEGER) < 12 THEN 'Morning Session'
        ELSE 'Afternoon Session'
    END AS session_name,
    COUNT(*) AS total_appointments_booked,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM clean_appointments), 2) AS pct_of_daily_bookings
FROM clean_appointments
GROUP BY strftime('%H', scheduled_time)
ORDER BY strftime('%H', scheduled_time);
