-- =====================================================================
-- CLINIC OPERATIONS ANALYTICS — DATA QUALITY VALIDATION SUITE
-- File: sql/data_quality.sql
-- Description: Audits raw appointments table for integrity anomalies,
--              temporal violations, missing clinical milestones, and
--              referential inconsistencies.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Check for Duplicate Appointment Identifiers (PK Integrity)
-- Risk: Inflates appointment volume and distorts clinical KPIs.
-- ---------------------------------------------------------------------
SELECT 
    appointment_id,
    COUNT(*) AS occurrence_count
FROM appointments
GROUP BY appointment_id
HAVING COUNT(*) > 1;

-- ---------------------------------------------------------------------
-- 2. Completed Encounters with Missing Arrival Timestamp
-- Risk: Check-in kiosk offline or clerical bypass; invalidates wait time math.
-- ---------------------------------------------------------------------
SELECT 
    appointment_id,
    patient_id,
    provider_id,
    appointment_date,
    scheduled_time,
    status
FROM appointments
WHERE status = 'COMPLETED'
  AND arrival_time IS NULL;

-- ---------------------------------------------------------------------
-- 3. Temporal Impossibility: Doctor Start Occurring Before Arrival
-- Risk: Tablet/kiosk clock desync; generates negative clinical waiting times.
-- ---------------------------------------------------------------------
SELECT 
    appointment_id,
    arrival_time,
    doctor_start,
    ROUND((julianday(doctor_start) - julianday(arrival_time)) * 1440, 2) AS wait_time_minutes
FROM appointments
WHERE status = 'COMPLETED'
  AND doctor_start IS NOT NULL
  AND arrival_time IS NOT NULL
  AND doctor_start < arrival_time;

-- ---------------------------------------------------------------------
-- 4. Temporal Impossibility: Checkout Occurring Before Doctor Completion
-- Risk: Patient marked discharged before face-to-face exam finished.
-- ---------------------------------------------------------------------
SELECT 
    appointment_id,
    doctor_start,
    doctor_end,
    checkout_time,
    ROUND((julianday(checkout_time) - julianday(doctor_end)) * 1440, 2) AS checkout_variance_min
FROM appointments
WHERE status = 'COMPLETED'
  AND doctor_end IS NOT NULL
  AND checkout_time IS NOT NULL
  AND checkout_time < doctor_end;

-- ---------------------------------------------------------------------
-- 5. Referential Integrity: Orphaned Providers
-- Risk: Bookings assigned to non-existent or inactive staff.
-- ---------------------------------------------------------------------
SELECT 
    a.appointment_id,
    a.provider_id,
    a.appointment_date
FROM appointments a
LEFT JOIN providers p ON a.provider_id = p.provider_id
WHERE p.provider_id IS NULL;

-- ---------------------------------------------------------------------
-- 6. Clinical EHR Linkage Consistency
-- Risk: Completed visits missing encounter IDs (unbilled) or cancelled visits with linked encounter.
-- ---------------------------------------------------------------------
SELECT 
    appointment_id,
    status,
    encounter_id,
    'COMPLETED but missing encounter_id' AS issue_description
FROM appointments
WHERE status = 'COMPLETED' AND encounter_id IS NULL

UNION ALL

SELECT 
    appointment_id,
    status,
    encounter_id,
    'NON-COMPLETED but has encounter_id' AS issue_description
FROM appointments
WHERE status != 'COMPLETED' AND encounter_id IS NOT NULL;
