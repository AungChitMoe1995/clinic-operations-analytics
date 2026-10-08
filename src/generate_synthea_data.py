"""
generate_synthea_data.py
-------------------------
Generates the Synthea-compliant EHR baseline data:
- patients.csv (Demographic Master Patient Index)
- conditions.csv (Chronic Disease Problem List with SNOMED-CT codes)

Reproducible synthetic cohort modeled after MITRE Synthea specifications.
"""

import os
import uuid
import random
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np

# Set fixed seed for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "synthea")
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_PATIENTS = 2800

# Common Massachusetts towns in Synthea
CITIES_ZIPS = [
    ("Boston", "02115"),
    ("Boston", "02118"),
    ("Cambridge", "02138"),
    ("Somerville", "02143"),
    ("Quincy", "02169"),
    ("Brookline", "02445"),
    ("Newton", "02458"),
    ("Medford", "02155"),
    ("Malden", "02148"),
    ("Waltham", "02451")
]

RACES = ["white", "black", "asian", "other"]
RACE_WEIGHTS = [0.55, 0.22, 0.16, 0.07]

ETHNICITIES = ["nonhispanic", "hispanic"]
ETHNICITY_WEIGHTS = [0.82, 0.18]

# SNOMED Chronic conditions mapping
CHRONIC_CONDITIONS = [
    ("59621000", "Essential hypertension", 0.32),
    ("44054006", "Type 2 diabetes mellitus", 0.18),
    ("195967001", "Asthma", 0.14),
    ("709044004", "Chronic kidney disease stage 2/3", 0.08),
    ("13645005", "Chronic obstructive pulmonary disease", 0.06),
    ("238131007", "Overweight", 0.25),
    ("15777000", "Prediabetes", 0.12),
]

def generate_patients(n):
    patients = []
    today = date(2024, 1, 1)

    for _ in range(n):
        patient_id = str(uuid.uuid4())
        gender = np.random.choice(["M", "F"], p=[0.48, 0.52])
        
        # Age distribution: 12% <18, 33% 18-39, 35% 40-64, 20% 65+
        age_group = np.random.choice(["pediatric", "young_adult", "middle_age", "senior"], p=[0.12, 0.33, 0.35, 0.20])
        if age_group == "pediatric":
            age_years = np.random.randint(1, 18)
        elif age_group == "young_adult":
            age_years = np.random.randint(18, 40)
        elif age_group == "middle_age":
            age_years = np.random.randint(40, 65)
        else:
            age_years = np.random.randint(65, 88)
        
        birth_date = today - timedelta(days=int(age_years * 365.25 + np.random.randint(0, 365)))
        race = np.random.choice(RACES, p=RACE_WEIGHTS)
        ethnicity = np.random.choice(ETHNICITIES, p=ETHNICITY_WEIGHTS)
        city, zip_code = CITIES_ZIPS[np.random.choice(len(CITIES_ZIPS))]

        patients.append({
            "patient_id": patient_id,
            "birth_date": birth_date.strftime("%Y-%m-%d"),
            "gender": gender,
            "race": race,
            "ethnicity": ethnicity,
            "city": city,
            "state": "MA",
            "zip_code": zip_code,
            "_age": age_years
        })

    return pd.DataFrame(patients)

def generate_conditions(df_patients):
    conditions = []
    cond_counter = 1000

    for _, row in df_patients.iterrows():
        p_id = row["patient_id"]
        age = row["_age"]

        # Probability of chronic condition increases with age
        for snomed, desc, base_prob in CHRONIC_CONDITIONS:
            # Age modulation
            prob = base_prob
            if age < 18:
                if snomed == "195967001": # Asthma
                    prob = 0.20
                else:
                    prob = 0.01
            elif age >= 65:
                prob = min(0.75, base_prob * 2.2)
            elif age >= 40:
                prob = min(0.60, base_prob * 1.5)
            
            if np.random.rand() < prob:
                onset_years_ago = np.random.randint(1, min(15, max(2, age - 10 if age > 10 else 2)))
                onset_date = date(2024, 1, 1) - timedelta(days=onset_years_ago * 365 + np.random.randint(0, 300))
                cond_counter += 1
                conditions.append({
                    "condition_id": f"CND-{cond_counter}",
                    "patient_id": p_id,
                    "snomed_code": snomed,
                    "description": desc,
                    "onset_date": onset_date.strftime("%Y-%m-%d")
                })

    return pd.DataFrame(conditions)

def main():
    print("Generating Synthea EHR baseline data...")
    df_patients = generate_patients(NUM_PATIENTS)
    df_conditions = generate_conditions(df_patients)

    # Remove helper column before export
    df_patients_export = df_patients.drop(columns=["_age"])

    patients_path = os.path.join(OUTPUT_DIR, "patients.csv")
    conditions_path = os.path.join(OUTPUT_DIR, "conditions.csv")

    df_patients_export.to_csv(patients_path, index=False)
    df_conditions.to_csv(conditions_path, index=False)

    print(f"Generated {len(df_patients_export)} patients -> {patients_path}")
    print(f"Generated {len(df_conditions)} chronic condition entries -> {conditions_path}")

if __name__ == "__main__":
    main()
