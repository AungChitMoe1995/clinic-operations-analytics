-- =====================================================================
-- CLINIC OPERATIONS ANALYTICS — RELATIONAL DATABASE SCHEMA
-- Database Engine: SQLite 3
-- Target File: data/clinic_operations.db
-- =====================================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- 1. Master Patient Index (Synthea EHR Layer)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS patients;
CREATE TABLE patients (
    patient_id      TEXT PRIMARY KEY,
    birth_date      DATE NOT NULL,
    gender          TEXT NOT NULL CHECK (gender IN ('M', 'F')),
    race            TEXT,
    ethnicity       TEXT,
    city            TEXT,
    state           TEXT,
    zip_code        TEXT
);

-- ---------------------------------------------------------------------
-- 2. Providers (Operational Layer)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS providers;
CREATE TABLE providers (
    provider_id             TEXT PRIMARY KEY,
    provider_name           TEXT NOT NULL,
    specialty               TEXT NOT NULL,
    target_daily_capacity   INTEGER NOT NULL CHECK (target_daily_capacity > 0)
);

-- ---------------------------------------------------------------------
-- 3. Appointment Service Catalog (Operational Layer)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS appointment_types;
CREATE TABLE appointment_types (
    appointment_type_id     TEXT PRIMARY KEY,
    appointment_type_name   TEXT NOT NULL UNIQUE,
    standard_duration_min   INTEGER NOT NULL CHECK (standard_duration_min > 0),
    description             TEXT
);

-- ---------------------------------------------------------------------
-- 4. Problem List / Chronic Conditions (Synthea EHR Layer)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS conditions;
CREATE TABLE conditions (
    condition_id    TEXT PRIMARY KEY,
    patient_id      TEXT NOT NULL,
    snomed_code     TEXT NOT NULL,
    description     TEXT NOT NULL,
    onset_date      DATE NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

-- ---------------------------------------------------------------------
-- 5. Documented Clinical Encounters (Synthea EHR Layer)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS encounters;
CREATE TABLE encounters (
    encounter_id        TEXT PRIMARY KEY,
    patient_id          TEXT NOT NULL,
    encounter_class     TEXT NOT NULL,
    reason_code         TEXT,
    reason_description  TEXT,
    clinical_start      TEXT NOT NULL,
    clinical_stop       TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

-- ---------------------------------------------------------------------
-- 6. Operational Appointments (Patient Flow Fact Table)
-- Note: Raw staging allows audit of duplicates/anomalies prior to clean table creation.
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS appointments;
CREATE TABLE appointments (
    appointment_id          TEXT,
    patient_id              TEXT NOT NULL,
    encounter_id            TEXT,
    provider_id             TEXT NOT NULL,
    appointment_type_id     TEXT NOT NULL,
    appointment_date        DATE NOT NULL,
    scheduled_time          TEXT NOT NULL,
    scheduled_duration_min  INTEGER NOT NULL,
    arrival_time            TEXT,
    triage_start            TEXT,
    triage_end              TEXT,
    doctor_start            TEXT,
    doctor_end              TEXT,
    checkout_time           TEXT,
    status                  TEXT NOT NULL CHECK (status IN ('COMPLETED', 'NO_SHOW', 'CANCELLED')),
    booking_channel         TEXT NOT NULL CHECK (booking_channel IN ('PATIENT_PORTAL', 'PHONE', 'IN_PERSON')),
    workflow_period         TEXT NOT NULL CHECK (workflow_period IN ('PRE_INTERVENTION', 'POST_INTERVENTION'))
);

-- ---------------------------------------------------------------------
-- Analytical Performance Indexes
-- ---------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_provider ON appointments(provider_id);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
CREATE INDEX IF NOT EXISTS idx_appointments_workflow ON appointments(workflow_period);
CREATE INDEX IF NOT EXISTS idx_appointments_type ON appointments(appointment_type_id);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_conditions_patient ON conditions(patient_id);
CREATE INDEX IF NOT EXISTS idx_encounters_patient ON encounters(patient_id);
