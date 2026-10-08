"""
generate_er_diagram.py
-----------------------
Renders a clean, high-resolution Entity-Relationship (ER) diagram
for the outpatient clinic data model with ample card heights, generous padding,
and zero text overflow:
- docs/images/data_model.png
- docs/data_model.png
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
IMAGES_DIR = os.path.join(DOCS_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

def render_er_diagram():
    fig, ax = plt.subplots(figsize=(16, 10.5), dpi=300)
    ax.set_facecolor("#F8FAFC")
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10.5)
    ax.axis("off")

    # Title & Subtitle
    ax.text(8.0, 9.9, "Relational Data Architecture: Outpatient EHR & Operational Scheduling Model", 
            ha="center", fontsize=16, fontweight="bold", color="#1E3A8A")
    ax.text(8.0, 9.5, "Metro North Family Health Centre — Operational Data Mart (SQLite Data Lineage)", 
            ha="center", fontsize=11.5, color="#64748B")

    # Helper function to draw an entity table with automated height protection
    def draw_entity(x, y, w, h, title, layer_tag, fields, header_color="#1E3A8A"):
        header_h = 0.65
        body_h = h - header_h

        # Header rect
        rect_header = patches.FancyBboxPatch(
            (x, y + body_h), w, header_h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor=header_color, edgecolor="#94A3B8", linewidth=1.2
        )
        ax.add_patch(rect_header)
        ax.text(x + 0.22, y + body_h + 0.32, title, fontsize=10.5, fontweight="bold", color="#FFFFFF", va="center")
        ax.text(x + w - 0.22, y + body_h + 0.32, layer_tag, fontsize=8.0, fontweight="bold", color="#E2E8F0", va="center", ha="right")

        # Body rect
        rect_body = patches.FancyBboxPatch(
            (x, y), w, body_h,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            facecolor="#FFFFFF", edgecolor="#CBD5E1", linewidth=1.2
        )
        ax.add_patch(rect_body)

        # Fields with comfortable vertical spacing
        num_fields = len(fields)
        line_spacing = min(0.33, (body_h - 0.3) / max(num_fields, 1))

        for idx, (f_name, f_type, is_key) in enumerate(fields):
            line_y = y + body_h - 0.28 - (idx * line_spacing)
            
            # Key indicator
            if is_key == "PK":
                key_str = "[PK]"
                key_color = "#E11D48"
            elif is_key == "FK":
                key_str = "[FK]"
                key_color = "#0D9488"
            else:
                key_str = ""
                key_color = "#94A3B8"

            if key_str:
                ax.text(x + 0.22, line_y, key_str, fontsize=8.5, fontweight="bold", color=key_color, va="center")
            
            # Field name
            ax.text(x + 0.82, line_y, f_name, fontsize=8.8, color="#1E293B", va="center")
            
            # Field data type
            ax.text(x + w - 0.25, line_y, f_type, fontsize=8.2, color="#64748B", va="center", ha="right")

    # 1. patients (Synthea) - 8 fields -> needs h >= 3.8
    draw_entity(0.8, 5.0, 4.0, 4.0, "patients", "Synthea EHR", [
        ("patient_id", "TEXT", "PK"),
        ("birth_date", "DATE", ""),
        ("gender", "TEXT", ""),
        ("race", "TEXT", ""),
        ("ethnicity", "TEXT", ""),
        ("city", "TEXT", ""),
        ("state", "TEXT", ""),
        ("zip_code", "TEXT", "")
    ], header_color="#2B5B84")

    # 2. conditions (Synthea) - 5 fields -> needs h >= 2.8
    draw_entity(0.8, 1.4, 4.0, 3.0, "conditions", "Synthea EHR", [
        ("condition_id", "TEXT", "PK"),
        ("patient_id", "TEXT", "FK"),
        ("snomed_code", "TEXT", ""),
        ("description", "TEXT", ""),
        ("onset_date", "DATE", "")
    ], header_color="#2B5B84")

    # 3. clean_appointments (Fact table) - 17 fields -> needs h >= 7.2
    draw_entity(5.6, 1.4, 4.8, 7.6, "clean_appointments", "Operational Fact Mart", [
        ("appointment_id", "TEXT", "PK"),
        ("patient_id", "TEXT", "FK"),
        ("encounter_id", "TEXT", "FK"),
        ("provider_id", "TEXT", "FK"),
        ("appointment_type_id", "TEXT", "FK"),
        ("appointment_date", "DATE", ""),
        ("scheduled_time", "TEXT", ""),
        ("scheduled_duration_min", "INT", ""),
        ("arrival_time", "DATETIME", ""),
        ("triage_start", "DATETIME", ""),
        ("triage_end", "DATETIME", ""),
        ("doctor_start", "DATETIME", ""),
        ("doctor_end", "DATETIME", ""),
        ("checkout_time", "DATETIME", ""),
        ("status", "TEXT", ""),
        ("booking_channel", "TEXT", ""),
        ("workflow_period", "TEXT", "")
    ], header_color="#1E3A8A")

    # 4. providers (Operational) - 4 fields -> needs h >= 2.4
    draw_entity(11.2, 6.4, 4.0, 2.6, "providers", "Operational Dim", [
        ("provider_id", "TEXT", "PK"),
        ("provider_name", "TEXT", ""),
        ("specialty", "TEXT", ""),
        ("target_daily_capacity", "INT", "")
    ], header_color="#0D9488")

    # 5. appointment_types (Operational) - 4 fields -> needs h >= 2.4
    draw_entity(11.2, 3.8, 4.0, 2.4, "appointment_types", "Operational Dim", [
        ("appointment_type_id", "TEXT", "PK"),
        ("appointment_type_name", "TEXT", ""),
        ("standard_duration_min", "INT", ""),
        ("description", "TEXT", "")
    ], header_color="#0D9488")

    # 6. encounters (Synthea) - 3 fields -> needs h >= 2.1
    draw_entity(11.2, 1.4, 4.0, 2.2, "encounters", "Synthea EHR", [
        ("encounter_id", "TEXT", "PK"),
        ("patient_id", "TEXT", "FK"),
        ("encounter_class", "TEXT", "")
    ], header_color="#2B5B84")

    # Relational Connectors
    # patients -> clean_appointments
    ax.annotate("", xy=(5.6, 7.2), xytext=(4.8, 7.2),
                arrowprops=dict(arrowstyle="->", color="#2B5B84", lw=1.8))
    ax.text(5.2, 7.35, "1 : M", fontsize=9, fontweight="bold", color="#2B5B84", ha="center")

    # patients -> conditions
    ax.annotate("", xy=(2.8, 4.4), xytext=(2.8, 5.0),
                arrowprops=dict(arrowstyle="->", color="#2B5B84", lw=1.8))
    ax.text(3.1, 4.65, "1 : M", fontsize=9, fontweight="bold", color="#2B5B84")

    # providers -> clean_appointments
    ax.annotate("", xy=(10.4, 7.2), xytext=(11.2, 7.2),
                arrowprops=dict(arrowstyle="->", color="#0D9488", lw=1.8))
    ax.text(10.8, 7.35, "1 : M", fontsize=9, fontweight="bold", color="#0D9488", ha="center")

    # appointment_types -> clean_appointments
    ax.annotate("", xy=(10.4, 4.8), xytext=(11.2, 4.8),
                arrowprops=dict(arrowstyle="->", color="#0D9488", lw=1.8))
    ax.text(10.8, 4.95, "1 : M", fontsize=9, fontweight="bold", color="#0D9488", ha="center")

    # encounters -> clean_appointments
    ax.annotate("", xy=(10.4, 2.4), xytext=(11.2, 2.4),
                arrowprops=dict(arrowstyle="->", color="#2B5B84", lw=1.8))
    ax.text(10.8, 2.55, "1 : M", fontsize=9, fontweight="bold", color="#2B5B84", ha="center")

    # Legend / Key
    ax.text(0.8, 0.7, "Layer Legend:   ■ Synthea EHR (Demographics & Chronic Conditions)   ■ Operational Fact Mart (Milestone Timestamps)   ■ Master Clinical Reference & Catalogs", 
            fontsize=9.5, color="#475569", fontweight="bold")

    out_path1 = os.path.join(IMAGES_DIR, "data_model.png")
    out_path2 = os.path.join(DOCS_DIR, "data_model.png")
    fig.savefig(out_path1, bbox_inches="tight", facecolor=fig.get_facecolor(), edgecolor="none")
    fig.savefig(out_path2, bbox_inches="tight", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print("ER Diagram regenerated successfully with ample padding and zero text overflow!")

if __name__ == "__main__":
    render_er_diagram()
