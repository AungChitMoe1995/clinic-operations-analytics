# Data Dictionary: Clinic Operations Analytics

**Project:** Clinic Operations Analytics: Investigating Patient Flow, Waiting Time and Provider Workload  
**Facility:** Metro North Family Health Centre (MN-FHC)  
**Observation Window:** January 1, 2024 – December 31, 2024  
**Data Architecture:** Relational Outpatient Model (Synthea EHR Layer + Synthetic Clinic Operational Layer)  

---

## 1. Overview of Data Tables

The database consists of 6 relational tables representing the intersection of an Electronic Health Record (EHR) and an Outpatient Practice Management / Scheduling System (e.g., Epic Cadence / Cerner Scheduling):

| Table Name | Layer | Purpose | Primary Key | Foreign Keys |
| :--- | :--- | :--- | :--- | :--- |
| **`patients`** | Synthea EHR | Master Patient Index & demographic baseline | `patient_id` | None |
| **`conditions`** | Synthea EHR | Diagnosed chronic conditions & clinical problem list | `condition_id` | `patient_id` |
| **`encounters`** | Synthea EHR | Charted and billed clinical encounters | `encounter_id` | `patient_id` |
| **`providers`** | Operational | Attending clinical staff and specialties | `provider_id` | None |
| **`appointment_types`** | Operational | Clinical service catalog & planned durations | `appointment_type_id` | None |
| **`appointments`** | Operational Fact | Operational patient flow and milestone timestamps | `appointment_id` | `patient_id`, `provider_id`, `appointment_type_id`, `encounter_id` |

---

## 2. Table Specifications

### 2.1 `patients` (Master Patient Index — Synthea Layer)
Contains baseline demographic records for the clinic's active patient panel. Derived using MITRE Synthea population models.

| Field Name | Type | Nullable | Key / Constraint | Description & Clinical Context | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `patient_id` | TEXT | NO | PK | Universally unique patient identifier (UUID). | `'b3c8f12a-45e1-482a-921f-8273619a0011'` |
| `birth_date` | DATE | NO | `YYYY-MM-DD` | Date of birth. Used to derive patient age cohorts (`<18`, `18–39`, `40–64`, `65+`). | `'1974-06-21'` |
| `gender` | TEXT | NO | `M`, `F` | Administrative gender recorded in EHR. | `'F'` |
| `race` | TEXT | YES | - | Self-reported racial demographic. | `'white'`, `'asian'`, `'black'` |
| `ethnicity` | TEXT | YES | - | Ethnicity classification. | `'nonhispanic'`, `'hispanic'` |
| `city` | TEXT | YES | - | Municipality of primary residence. | `'Boston'` |
| `state` | TEXT | YES | - | State of residence. | `'MA'` |
| `zip_code` | TEXT | YES | - | Postal zip code. | `'02115'` |

---

### 2.2 `conditions` (Active Problem List — Synthea Layer)
Contains chronic clinical comorbidities documented in the patient's EHR chart. Used to analyze the relationship between clinical disease burden and appointment scheduling patterns.

| Field Name | Type | Nullable | Key / Constraint | Description & Clinical Context | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `condition_id` | TEXT | NO | PK | Unique condition record identifier. | `'CND-001048'` |
| `patient_id` | TEXT | NO | FK $\rightarrow$ `patients.patient_id` | Patient associated with diagnosis. | `'b3c8f12a-...'` |
| `snomed_code` | TEXT | NO | Standard Code | SNOMED-CT clinical concept code. | `'59621000'` (Hypertension), `'44054006'` (Type 2 Diabetes) |
| `description` | TEXT | NO | - | Clinical diagnosis description. | `'Essential hypertension'` |
| `onset_date` | DATE | NO | `YYYY-MM-DD` | Date condition was first charted. | `'2018-09-12'` |

---

### 2.3 `encounters` (Billed EHR Encounters — Synthea Layer)
Represents documented, completed clinical visits in the EHR. In hospital revenue cycles and clinical documentation, a record exists here **only** when a patient was seen by a clinician.

| Field Name | Type | Nullable | Key / Constraint | Description & Clinical Context | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `encounter_id` | TEXT | NO | PK | Unique EHR clinical encounter UUID. | `'enc-8921a-...'` |
| `patient_id` | TEXT | NO | FK $\rightarrow$ `patients.patient_id` | Patient seen during the encounter. | `'b3c8f12a-...'` |
| `encounter_class` | TEXT | NO | - | EHR visit category (`ambulatory`, `wellness`). | `'ambulatory'` |
| `reason_code` | TEXT | YES | - | Primary SNOMED / ICD diagnosis reason code. | `'44054006'` |
| `reason_description` | TEXT | YES | - | Primary clinical reason for encounter. | `'Diabetes mellitus type 2 evaluation'` |
| `clinical_start` | DATETIME | NO | `YYYY-MM-DD HH:MM:SS` | Timestamp when physician opened and started charting. | `'2024-03-12 10:14:00'` |
| `clinical_stop` | DATETIME | NO | `YYYY-MM-DD HH:MM:SS` | Timestamp when physician signed and closed the chart. | `'2024-03-12 10:38:00'` |

---

### 2.4 `providers` (Attending Clinical Staff — Operational Layer)
Contains profile information for the clinic's core attending medical staff.

| Field Name | Type | Nullable | Key / Constraint | Description & Clinical Profile | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `provider_id` | TEXT | NO | PK | Unique provider identifier. | `'PRV-001'` |
| `provider_name` | TEXT | NO | - | Provider name and credentials. | `'Dr. Arthur Vance, MD'` |
| `specialty` | TEXT | NO | - | Primary clinical discipline. | `'Internal Medicine'` |
| `target_daily_capacity` | INTEGER | NO | `> 0` | Planned daily target visit capacity. | `12` |

---

### 2.5 `appointment_types` (Clinical Service Catalog — Operational Layer)
Reference table defining standard outpatient visit classifications and their scheduled baseline slot durations.

| Field Name | Type | Nullable | Key / Constraint | Description & Clinical Guidelines | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `appointment_type_id` | TEXT | NO | PK | Unique appointment type code. | `'APT-CHRON'` |
| `appointment_type_name` | TEXT | NO | UNIQUE | Clinical visit classification. | `'Chronic Disease Care Plan Review'` |
| `standard_duration_min` | INTEGER | NO | `15` or `30` | Standard scheduled slot allocation in minutes. | `30` |
| `description` | TEXT | YES | - | Booking instructions and clinical scope. | `'Multi-morbidity review, medication titration'` |

---

### 2.6 `appointments` (Operational Patient Flow Fact Table)
The core operational fact table tracking scheduling, patient arrivals, nursing intake, physician consultations, and checkout milestones.

| Field Name | Type | Nullable | Key / Constraint | Description & Clinical Operational Context | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `appointment_id` | TEXT | NO | PK | Unique appointment booking identifier. | `'APT-2024-00412'` |
| `patient_id` | TEXT | NO | FK $\rightarrow$ `patients` | Patient booked for appointment. | `'b3c8f12a-...'` |
| `encounter_id` | TEXT | YES | FK $\rightarrow$ `encounters` | Linked EHR clinical encounter. Populated **only** when `status = 'COMPLETED'`. `NULL` for No-Shows and Cancellations. | `'enc-8921a-...'` or `NULL` |
| `provider_id` | TEXT | NO | FK $\rightarrow$ `providers` | Scheduled attending physician. | `'PRV-001'` |
| `appointment_type_id` | TEXT | NO | FK $\rightarrow$ `appointment_types` | Booked visit category. | `'APT-ROUT'` |
| `appointment_date` | DATE | NO | `YYYY-MM-DD` | Date of scheduled appointment. | `'2024-08-14'` |
| `scheduled_time` | TEXT | NO | `HH:MM` | Scheduled appointment start time. | `'09:30'` |
| `scheduled_duration_min`| INTEGER | NO | `15`, `20`, `30` | Duration allocated on provider template. (15 min in morning post-intervention; 20/30 min otherwise). | `15` |
| `arrival_time` | DATETIME | YES | `YYYY-MM-DD HH:MM:SS` | Patient check-in timestamp at front desk. `NULL` for No-Shows/Cancellations. | `'2024-08-14 09:18:22'` |
| `triage_start` | DATETIME | YES | `YYYY-MM-DD HH:MM:SS` | Nurse calls patient into triage station. | `'2024-08-14 09:32:10'` |
| `triage_end` | DATETIME | YES | `YYYY-MM-DD HH:MM:SS` | Nurse finishes vitals and intake documentation. | `'2024-08-14 09:37:45'` |
| `doctor_start` | DATETIME | YES | `YYYY-MM-DD HH:MM:SS` | Doctor enters exam room and starts consultation. | `'2024-08-14 09:58:30'` |
| `doctor_end` | DATETIME | YES | `YYYY-MM-DD HH:MM:SS` | Doctor finishes consultation and exits exam room. | `'2024-08-14 10:24:15'` |
| `checkout_time` | DATETIME | YES | `YYYY-MM-DD HH:MM:SS` | Front desk checkout, payment, and follow-up booking. | `'2024-08-14 10:28:00'` |
| `status` | TEXT | NO | `COMPLETED`, `NO_SHOW`, `CANCELLED` | Final operational disposition. | `'COMPLETED'` |
| `booking_channel` | TEXT | NO | `PATIENT_PORTAL`, `PHONE`, `IN_PERSON` | Booking intake method. | `'PATIENT_PORTAL'` |
| `workflow_period` | TEXT | NO | `PRE_INTERVENTION`, `POST_INTERVENTION` | Operational era (`PRE`: Jan–Jun 2024; `POST`: Jul–Dec 2024). | `'POST_INTERVENTION'` |

---

## 3. Operational Duration Formulas & Derived Metrics

All operational durations in SQL and Python are derived directly from the milestone timestamps (measured in continuous fractional minutes):

1. **Triage Waiting Time (`triage_wait_min`):**
   $$\text{triage\_wait\_min} = \frac{\text{julianday}(triage\_start) - \text{julianday}(arrival\_time)}{1 / 1440} = \frac{\text{seconds}}{60}$$
   *Clinical meaning:* Time spent in waiting room lobby before nurse vitals assessment.

2. **Triage Intake Duration (`triage_duration_min`):**
   $$\text{triage\_duration\_min} = \frac{\text{julianday}(triage\_end) - \text{julianday}(triage\_start)}{1 / 1440}$$
   *Clinical meaning:* Nursing vitals collection, allergy review, and chief complaint entry in EHR.

3. **Physician Sub-Wait Queue (`doctor_queue_min`):**
   $$\text{doctor\_queue\_min} = \frac{\text{julianday}(doctor\_start) - \text{julianday}(triage\_end)}{1 / 1440}$$
   *Clinical meaning:* Sub-wait queue between triage vitals completion and physician exam room entry.

4. **Primary Patient Waiting Time (`total_clinical_wait_min`):**
   $$\text{total\_clinical\_wait\_min} = \frac{\text{julianday}(doctor\_start) - \text{julianday}(arrival\_time)}{1 / 1440}$$
   *Clinical meaning:* Total patient-facing wait from front desk check-in until physician face-to-face consultation begins. **This is our primary operational KPI.**

5. **Physician Consultation Duration (`consultation_duration_min`):**
   $$\text{consultation\_duration\_min} = \frac{\text{julianday}(doctor\_end) - \text{julianday}(doctor\_start)}{1 / 1440}$$
   *Clinical meaning:* Physician face-to-face consultation, physical exam, and clinical decision-making.

6. **Slot Variance (`slot_variance_min`):**
   $$\text{slot\_variance\_min} = \text{consultation\_duration\_min} - \text{scheduled\_duration\_min}$$
   *Clinical meaning:* Discrepancy between actual physician face-to-face time and the administrative template slot. Positive values indicate a consultation overrun.

7. **Total Clinic Length of Stay (`total_los_min`):**
   $$\text{total\_los\_min} = \frac{\text{julianday}(checkout\_time) - \text{julianday}(arrival\_time)}{1 / 1440}$$
   *Clinical meaning:* Total time a patient spends inside the clinic facility from arrival to discharge.

---

## 4. Synthetic Data Disclaimer

> **Data Attribution Notice:** Clinical and demographic variables in this dataset were generated following the open-source MITRE Synthea™ patient simulation framework. Clinic operational scheduling, milestone timestamps, provider templates, and queuing dynamics were independently synthesized for this healthcare operations portfolio project. No real patient data, protected health information (PHI), or actual clinical records were utilized.
