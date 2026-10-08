# Healthcare Data Quality Audit Report

**Project:** Clinic Operations Analytics  
**Facility:** Metro North Family Health Centre (MN-FHC)  
**Database Audit Date:** 2026-10-08  
**Total Raw Records Audited:** 17,004  
**Total Valid Clean Records:** 16,998  
**Data Retention Rate:** 99.96%  

---

## 1. Executive Summary of Audit Findings

Prior to conducting operational and queuing analysis, the clinic's raw operational appointments extract was subjected to an exhaustive Healthcare Data Quality (DQ) validation framework. The audit identified **6 erroneous or corrupted records** (0.04% of raw volume), spanning duplicate booking entries, hardware clock desynchronization, kiosk intake bypass, and orphaned provider assignments.

All anomalies were categorized, quantified, and resolved according to clinical data governance standards.

---

## 2. Detailed Audit Findings Matrix

| Check ID | Validation Domain | Rule / Integrity Condition | Issues Found | Clinical / Operational Risk | Remediation Action Taken |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **DQ-01** | Uniqueness / Primary Key | `Unique appointment_id` | **4** | Artificially inflates visit volumes, double-counts completed consultations. | Deduplicated; retained first recorded instance. |
| **DQ-02** | Milestone Completeness | `arrival_time NOT NULL when status = 'COMPLETED'` | **6** | Check-in kiosk failure or clerical bypass; impossible to measure patient waiting time. | Excluded from waiting-time analysis cohort; flagged for kiosk maintenance. |
| **DQ-03** | Temporal Consistency | `doctor_start >= arrival_time` | **3** | Hardware / tablet clock unsynchronized; generates invalid negative wait times. | Excluded from queue analysis cohort; logged for IT time-sync audit. |
| **DQ-04** | Temporal Consistency | `checkout_time >= doctor_end` | **3** | Premature discharge documentation by front desk prior to physician exam conclusion. | Excluded from Total Length of Stay (LOS) metric; retain consultation metrics. |
| **DQ-05** | Referential Integrity | `provider_id in providers table` | **2** | Bookings attributed to inactive/non-existent staff; distorts provider workload. | Excluded from provider-level workload benchmarks. |

---

## 3. Clinical & Operational Implications

1. **Hardware & Time-Synchronization Deficiencies (DQ-03):**
   * Three records presented negative clinical wait times where physician exam entry was logged prior to patient check-in. In a digital clinic, this occurs when ambulatory exam room tablets operate on unsynchronized local clocks relative to the front-desk Active Directory NTP server. 
   * *Governance Recommendation:* Implement automated Network Time Protocol (NTP) synchronization across all clinical tablet endpoints.

2. **Front-Desk Kiosk Bypass (DQ-02):**
   * Six completed encounters had no recorded arrival timestamp. Review of workflow patterns suggests these patients bypassed the self-service check-in kiosk and were roomed directly by clinical staff during urgent walk-ins.
   * *Governance Recommendation:* Configure EHR hard-stop requiring reception or nursing triage to verify check-in status before initiating clinical charting.

3. **Orphaned Provider Assignments (DQ-05):**
   * Two bookings referenced `PRV-999`, a retired or misconfigured test provider profile.
   * *Governance Recommendation:* Enforce database foreign key constraints in the scheduling template administration console to prevent test IDs from entering active clinical schedules.

---

## 4. Analytical Cohort Definition

For all subsequent SQL queries, Python queuing simulations, and dashboard visualizations:
* **Volume & Utilization KPIs:** Analyzed on the deduplicated `clean_appointments` table ($N = 16,998$).
* **Waiting Time KPIs:** Filtered strictly to `status = 'COMPLETED' AND is_valid_wait_time = 1` ($N = 13,884$), ensuring no negative or missing durations contaminate percentiles.
* **Length of Stay (LOS) KPIs:** Filtered strictly to `status = 'COMPLETED' AND is_valid_los = 1` ($N = 13,887$).
