-- =====================================================================
-- 03. MISSED APPOINTMENT DYNAMICS (NO-SHOWS & CANCELLATIONS)
-- File: sql/03_no_show_analysis.sql
-- Description: Investigates clinic missed appointments across appointment
--              types, days of the week, booking channels, and patient age demographics.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Query 3.1: Missed Appointments by Clinical Appointment Type
-- Business Question: Which clinical appointment types suffer the highest no-show rates?
-- ---------------------------------------------------------------------
SELECT 
    t.appointment_type_name,
    COUNT(a.appointment_id) AS total_scheduled,
    COUNT(CASE WHEN a.status = 'NO_SHOW' THEN 1 END) AS no_shows,
    COUNT(CASE WHEN a.status = 'CANCELLED' THEN 1 END) AS cancellations,
    ROUND(COUNT(CASE WHEN a.status = 'NO_SHOW' THEN 1 END) * 100.0 / COUNT(a.appointment_id), 2) AS no_show_rate_pct,
    ROUND(COUNT(CASE WHEN a.status = 'CANCELLED' THEN 1 END) * 100.0 / COUNT(a.appointment_id), 2) AS cancellation_rate_pct,
    ROUND((COUNT(CASE WHEN a.status = 'NO_SHOW' THEN 1 END) + COUNT(CASE WHEN a.status = 'CANCELLED' THEN 1 END)) * 100.0 / COUNT(a.appointment_id), 2) AS total_lost_capacity_pct
FROM clean_appointments a
JOIN appointment_types t ON a.appointment_type_id = t.appointment_type_id
GROUP BY t.appointment_type_name
ORDER BY no_show_rate_pct DESC;

-- ---------------------------------------------------------------------
-- Query 3.2: Missed Appointments by Day of Week
-- Business Question: Are no-shows significantly higher on specific weekdays (e.g. Mondays)?
-- ---------------------------------------------------------------------
SELECT 
    CASE CAST(strftime('%w', a.appointment_date) AS INTEGER)
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
    END AS day_of_week,
    COUNT(*) AS total_scheduled,
    COUNT(CASE WHEN a.status = 'NO_SHOW' THEN 1 END) AS no_shows,
    ROUND(COUNT(CASE WHEN a.status = 'NO_SHOW' THEN 1 END) * 100.0 / COUNT(*), 2) AS no_show_rate_pct,
    ROUND(COUNT(CASE WHEN a.status = 'CANCELLED' THEN 1 END) * 100.0 / COUNT(*), 2) AS cancellation_rate_pct
FROM clean_appointments a
GROUP BY strftime('%w', a.appointment_date)
ORDER BY CAST(strftime('%w', a.appointment_date) AS INTEGER);

-- ---------------------------------------------------------------------
-- Query 3.3: No-Show Rate by Patient Age Cohort (Synthea Demographics Cross-Tab)
-- Business Question: Does patient age cohort correlate with missed appointment rates?
-- ---------------------------------------------------------------------
WITH patient_age_groups AS (
    SELECT 
        a.appointment_id,
        a.status,
        (strftime('%Y', a.appointment_date) - strftime('%Y', p.birth_date)) AS patient_age,
        CASE 
            WHEN (strftime('%Y', a.appointment_date) - strftime('%Y', p.birth_date)) < 18 THEN 'Pediatric (<18)'
            WHEN (strftime('%Y', a.appointment_date) - strftime('%Y', p.birth_date)) BETWEEN 18 AND 39 THEN 'Young Adult (18-39)'
            WHEN (strftime('%Y', a.appointment_date) - strftime('%Y', p.birth_date)) BETWEEN 40 AND 64 THEN 'Middle Age (40-64)'
            ELSE 'Senior (65+)'
        END AS age_cohort
    FROM clean_appointments a
    JOIN patients p ON a.patient_id = p.patient_id
)
SELECT 
    age_cohort,
    COUNT(*) AS total_appointments,
    COUNT(CASE WHEN status = 'NO_SHOW' THEN 1 END) AS no_shows,
    ROUND(COUNT(CASE WHEN status = 'NO_SHOW' THEN 1 END) * 100.0 / COUNT(*), 2) AS no_show_rate_pct,
    ROUND(COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(*), 2) AS completion_rate_pct
FROM patient_age_groups
GROUP BY age_cohort
ORDER BY no_show_rate_pct DESC;
