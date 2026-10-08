# Methodology: Outpatient Clinic Operations Analytics

**Facility:** Metro North Family Health Centre (MN-FHC)  
**Study Period:** January 1, 2024 – December 31, 2024 (250 Operating Weekdays)  
**Analytical Architecture:** Integrated Outpatient EHR & Operational Patient-Flow Data Mart  
**Role:** Medical Software Coordinator & Clinical Informatics Analyst  

---

## 1. Clinical Context & Analytical Purpose

Community outpatient clinics represent stochastic queuing systems characterized by variable patient arrival times, heterogeneous clinical consultation durations, and rigid administrative schedule templates. 

In Q3 2024, Metro North Family Health Centre experienced a severe deterioration in operational flow:
* Patient complaints regarding waiting lobby delays doubled.
* Severe waiting room crowding emerged between 10:00 and 11:30 AM.
* Attending physicians routinely ran 30 to 45 minutes behind schedule by midday.

Management initially hypothesized that total patient volume had outgrown clinic physical capacity following a mid-year operational intervention. This study was commissioned to investigate:
> **What caused operational bottlenecks in the clinic, at which milestone stages did they occur, and what practical changes can restore clinic flow without sacrificing clinical quality?**

---

## 2. Quasi-Experimental Study Design

To evaluate the operational bottleneck with scientific rigor and avoid naive correlation-causation fallacies, the 12-month observation period was evaluated as a natural quasi-experiment:

```text
┌───────────────────────────────────────────────┬───────────────────────────────────────────────┐
│ BASELINE PERIOD (PRE-INTERVENTION)            │ POST-INTERVENTION PERIOD                      │
│ January 1, 2024 – June 30, 2024 (Months 1–6) │ July 1, 2024 – December 31, 2024 (Months 7–12)│
├───────────────────────────────────────────────┼───────────────────────────────────────────────┤
│ • Morning Schedule: 20-min staggered slots    │ • Morning Schedule: 15-min compressed slots   │
│ • Stable queuing and buffer times             │ • "Chronic Care Quality Campaign" launched    │
│ • Baseline P90 Wait: 39.2 minutes             │ • Morning P90 Wait: Exploded to 76.3 minutes  │
│ • Afternoon Schedule: Standard 20-min slots   │ • Afternoon Schedule: UNCHANGED (20-min slots)│
└───────────────────────────────────────────────┴───────────────────────────────────────────────┘
```

### The Analytical Advantage of Session Segmentation:
By comparing the **Morning Session** (experimental group: slots compressed to 15 min) against the **Afternoon Session** (internal control group: slots maintained at standard 20 min) within the exact same clinic, providers, and physical rooms, we isolated whether deterioration was driven by general clinic-wide demand or specific scheduling template compression.

---

## 3. Data Architecture & Lineage

The data pipeline integrates clinical EHR data with operational scheduling timestamps:

1. **Synthea EHR Layer (`patients`, `conditions`, `encounters`):**
   * Modeled using official MITRE Synthea™ outpatient population generators.
   * Provides authentic demographic distributions (age cohorts, gender, race, postal codes) and active clinical problem lists (SNOMED-CT codes for Essential Hypertension `59621000`, Type 2 Diabetes `44054006`, Asthma `195967001`, CKD `709044004`, COPD `13645005`).
   * Reflects enterprise EHR architecture: an `encounter_id` is created and charted **only** when a visit is completed.

2. **Synthetic Clinic Operational Layer (`appointments`, `providers`, `appointment_types`):**
   * Modeled using discrete-event outpatient queuing physics.
   * Tracks discrete milestone timestamps along the entire care journey:
     $$\text{Arrival Time} \longrightarrow \text{Triage Start} \longrightarrow \text{Triage End} \longrightarrow \text{Doctor Start} \longrightarrow \text{Doctor End} \longrightarrow \text{Checkout}$$

---

## 4. Operational Metric Formulations

All operational intervals are derived continuously from milestone timestamps:

| Operational Metric | Formula | Clinical & Operational Definition |
| :--- | :--- | :--- |
| **`triage_wait_min`** | `(triage_start - arrival_time) * 1440` | Lobby waiting time prior to nursing intake. |
| **`triage_service_min`** | `(triage_end - triage_start) * 1440` | Nursing vitals collection and EHR chief complaint charting. |
| **`doctor_queue_min`** | `(doctor_start - triage_end) * 1440` | Sub-waiting queue between vitals completion and exam room entry. |
| **`total_clinical_wait_min`** | `(doctor_start - arrival_time) * 1440` | **Primary Wait KPI:** Total patient wait from check-in to physician consultation. |
| **`consultation_duration_min`**| `(doctor_end - doctor_start) * 1440` | Physician face-to-face consultation and exam time. |
| **`slot_variance_min`** | `consult_dur - scheduled_duration` | Discrepancy between actual clinical time and planned administrative slot. |
| **`total_los_min`** | `(checkout_time - arrival_time) * 1440` | Total patient length of stay inside the ambulatory facility. |

### Why Upper Percentiles Matter (P50 vs P90)
In healthcare analytics, waiting time distributions are heavily right-skewed. Arithmetic averages conceal severe tail delays. A clinic with a mean wait of 28 minutes may have a 90th percentile (P90) of 76 minutes, meaning 1 in 10 patients suffers intolerable delays.

---

## 5. Healthcare Data Quality Audit Protocol

Prior to ingestion into the analytical warehouse, all raw operational records were evaluated against a 6-point clinical data governance framework (`sql/data_quality.sql` & `src/data_quality.py`):
1. **Uniqueness:** Deduplicated 4 duplicate booking records.
2. **Temporal Validity:** Excluded 3 records exhibiting negative wait times (`doctor_start < arrival_time`) caused by ambulatory tablet clock desynchronization.
3. **Milestone Completeness:** Flagged 6 completed encounters missing check-in timestamps due to kiosk bypass.
4. **Referential Integrity:** Reassigned/flagged 2 records linked to non-existent test provider `PRV-999`.
5. **Chart Linkage:** Audited revenue cycle consistency between scheduling status and clinical encounters.

---

## 6. Root-Cause Decomposition & Queuing Dynamics

The analysis tested 4 competing hypotheses for the wait time surge:

```text
HYPOTHESIS 1: "Total clinic patient volume increased beyond facility capacity."
  ↳ TEST: Monthly volume rose only 12.5% (from 1,333 to 1,500 booked/month).
  ↳ RESULT: REJECTED. A 12.5% volume increase cannot mathematically account for an 82% surge in P90 wait.

HYPOTHESIS 2: "Afternoon clinic flow deteriorated at the same rate as mornings."
  ↳ TEST: Segmented waiting times by operating session across both halves of the year.
  ↳ RESULT: REJECTED. Afternoon P90 wait was 35.2m (Pre) vs 35.8m (Post) — statistically unchanged.
           Morning P90 wait surged from 41.9m (Pre) to 76.3m (Post).
           The problem was 100% confined to morning sessions.

HYPOTHESIS 3: "Front-end nursing intake acted as a secondary bottleneck."
  ↳ TEST: Measured arrival-to-triage interval.
  ↳ RESULT: CONFIRMED. Triage wait increased from 4.5m to 8.6m during morning check-in spikes.

HYPOTHESIS 4: "Compressing morning slots eliminated schedule buffers, triggering cascading queue failure."
  ↳ TEST: Evaluated consultation duration vs slot length (Dr. Arthur Vance averaged 22.4 min consults; 
           48.3% slot overrun rate).
  ↳ RESULT: CONFIRMED. By Little's Law, when server utilization approaches 100% with zero buffer,
           stochastic overruns compound exponentially across consecutive appointments.
```

---

## 7. Translation to Actionable Clinical Operations

Analytical findings directly inform 4 realistic operational interventions:
1. **Dynamic Complexity Scheduling:** Restrict 15-minute slots to `Routine Follow-Ups` and `Acute Same-Day Visits`; mandate protected 30-minute bookings for `Chronic Disease Care Plan Reviews`.
2. **Mid-Morning Catch-Up Buffers:** Reserve an unbooked 15-minute administrative slot at 10:30 AM on all clinician templates to absorb upstream overruns and reset the schedule.
3. **Peak Triage Staffing:** Stagger nursing schedules to operate a 3rd triage intake station between 08:30 and 10:15 AM.
4. **Risk-Stratified No-Show Management:** Shift away from compressed overbooking to 48-hour automated SMS confirmations targeted at Monday mornings and young adult cohorts.
