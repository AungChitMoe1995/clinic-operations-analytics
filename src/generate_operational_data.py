"""
generate_operational_data.py
-----------------------------
Generates synthetic clinic operational layer:
- providers.csv
- appointment_types.csv
- appointments.csv (Operational fact table with milestone timestamps)
- encounters.csv (Synthea-aligned clinical encounters for completed visits)

Simulates realistic outpatient queuing physics:
- Pre-intervention (Jan-Jun): Baseline 20-min morning slots, stable queuing.
- Post-intervention (Jul-Dec): 15-min compressed morning slots + Chronic Care initiative,
  triggering queue cascades (P90 wait times jumping from ~26m to ~54m) while afternoon
  clinics remain stable.
- Injects realistic healthcare data quality anomalies (~0.2% edge cases) for Phase 7 audit.
"""

import os
import uuid
import random
from datetime import datetime, date, timedelta, time
import pandas as pd
import numpy as np

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

SYNTHEA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "synthea")
OPERATIONAL_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "operational")
os.makedirs(OPERATIONAL_DIR, exist_ok=True)

# 1. Define Providers
PROVIDERS = [
    {
        "provider_id": "PRV-001",
        "provider_name": "Dr. Arthur Vance, MD",
        "specialty": "Internal Medicine",
        "target_daily_capacity": 11
    },
    {
        "provider_id": "PRV-002",
        "provider_name": "Dr. Brenda Chen, MD",
        "specialty": "Family Medicine",
        "target_daily_capacity": 13
    },
    {
        "provider_id": "PRV-003",
        "provider_name": "Dr. Tariq Al-Mansoor, MD",
        "specialty": "Family Medicine",
        "target_daily_capacity": 11
    },
    {
        "provider_id": "PRV-004",
        "provider_name": "Dr. Sarah Jenkins, MD",
        "specialty": "Pediatrics & Family Medicine",
        "target_daily_capacity": 11
    }
]

# 2. Define Appointment Types
APPOINTMENT_TYPES = [
    {
        "appointment_type_id": "APT-ROUT",
        "appointment_type_name": "Routine Follow-Up",
        "standard_duration_min": 15,
        "description": "Stable chronic follow-up, lab review, repeat prescription"
    },
    {
        "appointment_type_id": "APT-ACUT",
        "appointment_type_name": "Acute / Same-Day Illness",
        "standard_duration_min": 15,
        "description": "URTI, acute infection, minor musculoskeletal injury"
    },
    {
        "appointment_type_id": "APT-NEWP",
        "appointment_type_name": "Comprehensive New Patient",
        "standard_duration_min": 30,
        "description": "Initial intake, comprehensive history and physical"
    },
    {
        "appointment_type_id": "APT-CHRON",
        "appointment_type_name": "Chronic Disease Care Plan Review",
        "standard_duration_min": 30,
        "description": "Multi-morbidity diabetic/hypertensive review and care plan"
    },
    {
        "appointment_type_id": "APT-PREV",
        "appointment_type_name": "Preventive Wellness / Health Check",
        "standard_duration_min": 30,
        "description": "Annual adult wellness, pediatric developmental screening"
    }
]

# Operating calendar: Weekdays in 2024 excluding major US holidays
HOLIDAYS_2024 = {
    date(2024, 1, 1),   # New Year
    date(2024, 1, 15),  # MLK Day
    date(2024, 2, 19),  # Presidents Day
    date(2024, 5, 27),  # Memorial Day
    date(2024, 6, 19),  # Juneteenth
    date(2024, 7, 4),   # Independence Day
    date(2024, 9, 2),   # Labor Day
    date(2024, 10, 14), # Indigenous Peoples Day
    date(2024, 11, 11), # Veterans Day
    date(2024, 11, 28), # Thanksgiving
    date(2024, 11, 29), # Day after Thanksgiving
    date(2024, 12, 25), # Christmas
}

def get_clinic_dates():
    start = date(2024, 1, 1)
    end = date(2024, 12, 31)
    curr = start
    dates = []
    while curr <= end:
        if curr.weekday() < 5 and curr not in HOLIDAYS_2024:
            dates.append(curr)
        curr += timedelta(days=1)
    return dates

def get_consult_duration(apt_type, provider_id):
    """Calculates realistic doctor face-to-face consultation duration (minutes)"""
    if apt_type == "APT-ROUT":
        dur = np.random.normal(14.5, 2.5)
        return max(8.0, min(24.0, dur))
    elif apt_type == "APT-ACUT":
        dur = np.random.normal(15.0, 3.0)
        return max(8.0, min(26.0, dur))
    elif apt_type == "APT-PREV":
        dur = np.random.normal(27.0, 4.0)
        return max(18.0, min(42.0, dur))
    elif apt_type == "APT-NEWP":
        dur = np.random.normal(31.0, 5.0)
        return max(20.0, min(48.0, dur))
    elif apt_type == "APT-CHRON":
        # Dr. Arthur Vance (Internal Med) spends longer on complex chronic reviews
        mean_dur = 25.5 if provider_id == "PRV-001" else 23.5
        dur = np.random.normal(mean_dur, 4.0)
        return max(16.0, min(44.0, dur))
    return 15.0

def main():
    print("Loading Synthea patients & conditions...")
    df_patients = pd.read_csv(os.path.join(SYNTHEA_DIR, "patients.csv"))
    patient_ids = df_patients["patient_id"].tolist()

    df_conditions = pd.read_csv(os.path.join(SYNTHEA_DIR, "conditions.csv"))
    chronic_patients = set(df_conditions["patient_id"].unique())

    clinic_dates = get_clinic_dates()
    print(f"Total operating days in 2024: {len(clinic_dates)}")

    # Provider appointment weights
    provider_type_weights = {
        "PRV-001": {"APT-ROUT": 0.30, "APT-ACUT": 0.10, "APT-NEWP": 0.15, "APT-CHRON": 0.35, "APT-PREV": 0.10}, # Chronic heavy
        "PRV-002": {"APT-ROUT": 0.40, "APT-ACUT": 0.25, "APT-NEWP": 0.15, "APT-CHRON": 0.10, "APT-PREV": 0.10}, # Fast Family Med
        "PRV-003": {"APT-ROUT": 0.35, "APT-ACUT": 0.25, "APT-NEWP": 0.15, "APT-CHRON": 0.15, "APT-PREV": 0.10}, # Balanced
        "PRV-004": {"APT-ROUT": 0.25, "APT-ACUT": 0.40, "APT-NEWP": 0.15, "APT-CHRON": 0.05, "APT-PREV": 0.15}, # Pediatric/Acute
    }

    appointments = []
    encounters = []
    apt_counter = 10000

    for c_date in clinic_dates:
        is_post = c_date >= date(2024, 7, 1)
        workflow_period = "POST_INTERVENTION" if is_post else "PRE_INTERVENTION"

        # Daily scheduling for each provider
        for prov in PROVIDERS:
            p_id = prov["provider_id"]
            
            # Sessions: Morning (08:30 start) and Afternoon (13:30 start)
            # Slot structure:
            if not is_post:
                # Pre-intervention: 20-min slots morning (08:30 to 11:50 -> 10 slots), 
                # Afternoon 20-min slots (13:30 to 15:30 -> 6 slots)
                morning_slots = [
                    (time(8, 30), 20), (time(8, 50), 20), (time(9, 10), 20), (time(9, 30), 20),
                    (time(9, 50), 20), (time(10, 10), 20), (time(10, 30), 20), (time(10, 50), 20),
                    (time(11, 10), 20), (time(11, 30), 20)
                ]
            else:
                # Post-intervention: COMPRESSED 15-min slots morning (08:30 to 11:30 -> 12 slots)
                morning_slots = [
                    (time(8, 30), 15), (time(8, 45), 15), (time(9, 0), 15), (time(9, 15), 15),
                    (time(9, 30), 15), (time(9, 45), 15), (time(10, 0), 15), (time(10, 15), 15),
                    (time(10, 30), 15), (time(10, 45), 15), (time(11, 0), 15), (time(11, 15), 15)
                ]

            # Afternoon slots: constant across both periods (13:30 to 15:30)
            afternoon_slots = [
                (time(13, 30), 20), (time(13, 50), 20), (time(14, 10), 20),
                (time(14, 30), 20), (time(14, 50), 20), (time(15, 10), 20)
            ]

            all_day_slots = [(s[0], s[1], "MORNING") for s in morning_slots] + \
                            [(s[0], s[1], "AFTERNOON") for s in afternoon_slots]

            # Track provider state for queuing
            # Morning session doctor availability begins at 08:30
            doc_available_time_am = datetime.combine(c_date, time(8, 30))
            # Afternoon session doctor availability resets at 13:30 after lunch
            doc_available_time_pm = datetime.combine(c_date, time(13, 30))

            for slot_time, scheduled_dur, session in all_day_slots:
                apt_counter += 1
                apt_id = f"APT-2024-{apt_counter}"
                sched_dt = datetime.combine(c_date, slot_time)

                # Determine appointment type
                # In post-intervention morning, "Chronic Care Campaign" increases chronic visits
                weights_dict = provider_type_weights[p_id].copy()
                if is_post and session == "MORNING":
                    weights_dict["APT-CHRON"] = weights_dict.get("APT-CHRON", 0.1) * 1.6
                    # Renormalize
                    total_w = sum(weights_dict.values())
                    weights_dict = {k: v / total_w for k, v in weights_dict.items()}

                type_keys = list(weights_dict.keys())
                type_probs = [weights_dict[k] for k in type_keys]
                apt_type = np.random.choice(type_keys, p=type_probs)

                # Select patient: if chronic appointment, pick from chronic cohort with 80% prob
                if apt_type == "APT-CHRON" and len(chronic_patients) > 0 and np.random.rand() < 0.85:
                    patient_id = random.choice(list(chronic_patients))
                else:
                    patient_id = random.choice(patient_ids)

                # Booking channel
                booking_channel = np.random.choice(["PATIENT_PORTAL", "PHONE", "IN_PERSON"], p=[0.48, 0.38, 0.14])

                # Determine appointment status outcome
                # No-show probability: base 10.5%, higher on Monday (13%)
                no_show_prob = 0.13 if c_date.weekday() == 0 else 0.10
                if apt_type == "APT-ROUT":
                    no_show_prob += 0.02
                
                cancel_prob = 0.07

                rand_val = np.random.rand()
                if rand_val < no_show_prob:
                    status = "NO_SHOW"
                elif rand_val < no_show_prob + cancel_prob:
                    status = "CANCELLED"
                else:
                    status = "COMPLETED"

                # Milestone timestamps
                if status in ["NO_SHOW", "CANCELLED"]:
                    arrival_time = None
                    triage_start = None
                    triage_end = None
                    doctor_start = None
                    doctor_end = None
                    checkout_time = None
                    enc_id = None
                else:
                    # Completed visit flow
                    # 1. Arrival time: normal around scheduled time (-8 min early, std 7 min)
                    arrival_offset_min = np.random.normal(-8.0, 7.0)
                    arrival_dt = sched_dt + timedelta(minutes=arrival_offset_min)
                    # Cannot arrive before clinic open (08:00)
                    if arrival_dt.time() < time(8, 0):
                        arrival_dt = datetime.combine(c_date, time(8, 2, random.randint(0, 59)))

                    # 2. Triage wait:
                    # In post-intervention morning, nurse station has a queue due to compressed check-ins
                    if is_post and session == "MORNING" and sched_dt.time() >= time(9, 15):
                        triage_wait_min = np.random.uniform(7.0, 18.0)
                    else:
                        triage_wait_min = np.random.uniform(2.0, 7.0)
                    
                    triage_start_dt = max(arrival_dt + timedelta(minutes=triage_wait_min),
                                          datetime.combine(c_date, time(8, 15)))
                    
                    # 3. Triage duration (3.5 - 6.5 mins)
                    triage_dur_min = np.random.uniform(3.5, 6.5)
                    triage_end_dt = triage_start_dt + timedelta(minutes=triage_dur_min)

                    # 4. Doctor consultation start:
                    # Doctor cannot see patient before triage_end_dt AND cannot see before previous patient is finished!
                    doc_available = doc_available_time_am if session == "MORNING" else doc_available_time_pm
                    doc_start_dt = max(triage_end_dt + timedelta(minutes=np.random.uniform(1.0, 4.0)), doc_available)

                    # 5. Doctor consultation duration
                    actual_consult_min = get_consult_duration(apt_type, p_id)
                    doc_end_dt = doc_start_dt + timedelta(minutes=actual_consult_min)

                    # Update doctor availability for next patient in this session
                    if session == "MORNING":
                        doc_available_time_am = doc_end_dt + timedelta(minutes=np.random.uniform(0.5, 2.0)) # brief transition
                    else:
                        doc_available_time_pm = doc_end_dt + timedelta(minutes=np.random.uniform(0.5, 2.0))

                    # 6. Checkout: 2 to 6 mins after consult
                    checkout_dt = doc_end_dt + timedelta(minutes=np.random.uniform(2.0, 6.0))

                    # Formatting strings
                    arrival_time = arrival_dt.strftime("%Y-%m-%d %H:%M:%S")
                    triage_start = triage_start_dt.strftime("%Y-%m-%d %H:%M:%S")
                    triage_end = triage_end_dt.strftime("%Y-%m-%d %H:%M:%S")
                    doctor_start = doc_start_dt.strftime("%Y-%m-%d %H:%M:%S")
                    doctor_end = doc_end_dt.strftime("%Y-%m-%d %H:%M:%S")
                    checkout_time = checkout_dt.strftime("%Y-%m-%d %H:%M:%S")

                    # Generate linked EHR encounter
                    enc_id = str(uuid.uuid4())
                    enc_class = "wellness" if apt_type == "APT-PREV" else "ambulatory"
                    
                    enc_reason = {
                        "APT-ROUT": ("185349003", "Encounter for check up"),
                        "APT-ACUT": ("444814009", "Viral respiratory infection"),
                        "APT-NEWP": ("308335008", "Patient encounter procedure"),
                        "APT-CHRON": ("44054006", "Type 2 diabetes mellitus monitoring"),
                        "APT-PREV": ("410620009", "Well child/adult visit"),
                    }.get(apt_type, ("185349003", "Routine medical examination"))

                    encounters.append({
                        "encounter_id": enc_id,
                        "patient_id": patient_id,
                        "encounter_class": enc_class,
                        "reason_code": enc_reason[0],
                        "reason_description": enc_reason[1],
                        "clinical_start": doctor_start,
                        "clinical_stop": doctor_end
                    })

                appointments.append({
                    "appointment_id": apt_id,
                    "patient_id": patient_id,
                    "encounter_id": enc_id,
                    "provider_id": p_id,
                    "appointment_type_id": apt_type,
                    "appointment_date": c_date.strftime("%Y-%m-%d"),
                    "scheduled_time": slot_time.strftime("%H:%M:%S"),
                    "scheduled_duration_min": scheduled_dur,
                    "arrival_time": arrival_time,
                    "triage_start": triage_start,
                    "triage_end": triage_end,
                    "doctor_start": doctor_start,
                    "doctor_end": doctor_end,
                    "checkout_time": checkout_time,
                    "status": status,
                    "booking_channel": booking_channel,
                    "workflow_period": workflow_period
                })

    df_appointments = pd.DataFrame(appointments)
    df_encounters = pd.DataFrame(encounters)

    # -------------------------------------------------------------
    # Inject deliberate, realistic Data Quality anomalies (~0.2%)
    # for Phase 7 validation audit
    # -------------------------------------------------------------
    print("Injecting controlled data quality edge cases for DQ audit...")
    completed_indices = df_appointments[df_appointments["status"] == "COMPLETED"].index.tolist()

    # 1. Missing arrival time despite completed (kiosk offline / manual override) -> 6 records
    for idx in completed_indices[10:16]:
        df_appointments.loc[idx, "arrival_time"] = None

    # 2. Clock desync / negative wait time (doctor_start < arrival_time) -> 3 records
    for idx in completed_indices[30:33]:
        arr_val = datetime.strptime(df_appointments.loc[idx, "arrival_time"], "%Y-%m-%d %H:%M:%S")
        # Set doctor_start to 10 minutes BEFORE arrival
        bad_doc_start = arr_val - timedelta(minutes=10)
        df_appointments.loc[idx, "doctor_start"] = bad_doc_start.strftime("%Y-%m-%d %H:%M:%S")

    # 3. Checkout before doctor_end (clerical error) -> 3 records
    for idx in completed_indices[50:53]:
        doc_end_val = datetime.strptime(df_appointments.loc[idx, "doctor_end"], "%Y-%m-%d %H:%M:%S")
        bad_checkout = doc_end_val - timedelta(minutes=15)
        df_appointments.loc[idx, "checkout_time"] = bad_checkout.strftime("%Y-%m-%d %H:%M:%S")

    # 4. Duplicate appointment record -> 4 records duplicated
    dup_rows = df_appointments.loc[completed_indices[70:74]].copy()
    df_appointments = pd.concat([df_appointments, dup_rows], ignore_index=True)

    # 5. Invalid/orphaned provider ID -> 2 records
    df_appointments.loc[completed_indices[90:92], "provider_id"] = "PRV-999"

    # Export reference tables
    pd.DataFrame(PROVIDERS).to_csv(os.path.join(OPERATIONAL_DIR, "providers.csv"), index=False)
    pd.DataFrame(APPOINTMENT_TYPES).to_csv(os.path.join(OPERATIONAL_DIR, "appointment_types.csv"), index=False)
    
    # Export fact table & encounters
    df_appointments.to_csv(os.path.join(OPERATIONAL_DIR, "appointments.csv"), index=False)
    df_encounters.to_csv(os.path.join(SYNTHEA_DIR, "encounters.csv"), index=False)

    print(f"Generated {len(df_appointments)} appointments -> {OPERATIONAL_DIR}/appointments.csv")
    print(f"Generated {len(df_encounters)} linked EHR encounters -> {SYNTHEA_DIR}/encounters.csv")
    print("Generated providers.csv and appointment_types.csv successfully.")

if __name__ == "__main__":
    main()
