-- =====================================================================
-- 05. PROVIDER WORKLOAD, CONSULTATION DURATION & OVERRUN ANALYSIS
-- File: sql/05_provider_workload.sql
-- Description: Analyzes clinician clinical volume, face-to-face consultation
--              duration against scheduled template slots, slot overrun frequency,
--              and downstream patient waiting times by provider.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Query 5.1: Provider Clinical Volume & Face-to-Face Consultation Hours
-- Business Question: How much total clinical time does each clinician deliver?
-- ---------------------------------------------------------------------
SELECT 
    p.provider_name,
    p.specialty,
    COUNT(a.appointment_id) AS completed_consultations,
    ROUND(SUM((julianday(a.doctor_end) - julianday(a.doctor_start)) * 1440) / 60.0, 1) AS total_clinical_hours,
    ROUND(AVG((julianday(a.doctor_end) - julianday(a.doctor_start)) * 1440), 1) AS avg_actual_consult_min,
    ROUND(AVG(a.scheduled_duration_min), 1) AS avg_scheduled_slot_min,
    ROUND(AVG((julianday(a.doctor_end) - julianday(a.doctor_start)) * 1440) - AVG(a.scheduled_duration_min), 1) AS avg_slot_variance_min
FROM providers p
JOIN clean_appointments a ON p.provider_id = a.provider_id
WHERE a.is_valid_wait_time = 1
GROUP BY p.provider_id, p.provider_name, p.specialty
ORDER BY total_clinical_hours DESC;

-- ---------------------------------------------------------------------
-- Query 5.2: Slot Overrun Frequency by Provider
-- Business Question: Which doctors frequently exceed their scheduled slot duration?
-- (Clinical definition: actual consultation exceeding scheduled slot by > 5 min)
-- ---------------------------------------------------------------------
SELECT 
    p.provider_name,
    p.specialty,
    COUNT(a.appointment_id) AS total_completed,
    COUNT(CASE 
        WHEN ((julianday(a.doctor_end) - julianday(a.doctor_start)) * 1440) > (a.scheduled_duration_min + 5) 
        THEN 1 
    END) AS overrunning_consultations,
    ROUND(COUNT(CASE 
        WHEN ((julianday(a.doctor_end) - julianday(a.doctor_start)) * 1440) > (a.scheduled_duration_min + 5) 
        THEN 1 
    END) * 100.0 / COUNT(a.appointment_id), 2) AS slot_overrun_rate_pct
FROM providers p
JOIN clean_appointments a ON p.provider_id = a.provider_id
WHERE a.is_valid_wait_time = 1
GROUP BY p.provider_id, p.provider_name, p.specialty
ORDER BY slot_overrun_rate_pct DESC;

-- ---------------------------------------------------------------------
-- Query 5.3: Patient Waiting Time Experienced by Provider Panel
-- Business Question: Do patients waiting for specific providers experience longer delays?
-- ---------------------------------------------------------------------
WITH provider_waits AS (
    SELECT 
        p.provider_name,
        (julianday(a.doctor_start) - julianday(a.arrival_time)) * 1440 AS wait_min,
        NTILE(100) OVER (
            PARTITION BY p.provider_name 
            ORDER BY (julianday(a.doctor_start) - julianday(a.arrival_time)) * 1440
        ) AS pct_tile
    FROM clean_appointments a
    JOIN providers p ON a.provider_id = p.provider_id
    WHERE a.is_valid_wait_time = 1
)
SELECT 
    provider_name,
    COUNT(*) AS completed_visits,
    ROUND(AVG(wait_min), 1) AS mean_wait_min,
    ROUND(MAX(CASE WHEN pct_tile = 50 THEN wait_min END), 1) AS median_wait_min,
    ROUND(MAX(CASE WHEN pct_tile = 90 THEN wait_min END), 1) AS p90_wait_min
FROM provider_waits
GROUP BY provider_name
ORDER BY p90_wait_min DESC;
