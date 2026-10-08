"""
generate_presentation.py
-------------------------
Generates an executive-ready, highly polished, stylish PowerPoint (.pptx)
briefing deck for the Clinic Operations Analytics case study.

Redesigned with:
- 16:9 widescreen layout (13.333" x 7.5")
- Slide 3: Full dedicated, uncluttered slide for the Relational ER Diagram (data_model.png)
- Slide 4: Full dedicated slide for Healthcare Data Quality (DQ) Audit & Governance
- Total 11 slides with generous whitespace, large scannable typography (12-28pt),
  and McKinsey/BCG healthcare consulting style.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "docs", "presentation")
OUTPUT_PPTX = os.path.join(OUTPUT_DIR, "clinic_operations_executive_briefing.pptx")
IMG_DIR = os.path.join(BASE_DIR, "docs", "images")

# Refined Executive Color Palette
C_NAVY_DARK = RGBColor(15, 23, 42)      # #0F172A - Deep Slate Navy
C_PRIMARY = RGBColor(30, 58, 138)        # #1E3A8A - Header Primary Navy
C_BLUE = RGBColor(37, 99, 235)          # #2563EB - Royal Accent Blue
C_CRIMSON = RGBColor(225, 29, 72)       # #E11D48 - Alert / P90 Tail
C_EMERALD = RGBColor(5, 150, 105)       # #059669 - Positive / Control / Governance
C_DARK = RGBColor(30, 41, 59)           # #1E293B - Body text
C_SLATE = RGBColor(71, 85, 105)         # #475569 - Secondary text
C_MUTED = RGBColor(100, 116, 139)       # #64748B - Muted labels
C_CARD_BG = RGBColor(248, 250, 252)     # #F8FAFC - Soft gray card fill
C_CARD_BORDER = RGBColor(226, 232, 240) # #E2E8F0 - Clean border
C_WHITE = RGBColor(255, 255, 255)       # Pure White

def build_presentation():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_slide_header(slide, title, subtitle, category="HEALTHCARE CLINICAL OPERATIONS ANALYTICS"):
        # Category Tag
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.733), Inches(0.28))
        tf_c = cat_box.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = 0
        p_c = tf_c.paragraphs[0]
        p_c.text = category.upper()
        p_c.font.size = Pt(10.5)
        p_c.font.bold = True
        p_c.font.color.rgb = C_BLUE

        # Slide Main Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.62), Inches(11.733), Inches(0.5))
        tf_t = t_box.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
        p_t = tf_t.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = C_PRIMARY

        # Subtitle / Executive One-Liner Takeaway
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.15), Inches(11.733), Inches(0.35))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle
        p_sub.font.size = Pt(13)
        p_sub.font.color.rgb = C_SLATE

        # Subtle elegant divider line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.52), Inches(11.733), Inches(0.015))
        line.fill.solid()
        line.fill.fore_color.rgb = C_CARD_BORDER
        line.line.color.rgb = C_CARD_BORDER

    def add_card(slide, left, top, width, height, fill_color=C_CARD_BG, border_color=C_CARD_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.2)
        return shape

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (PREMIUM EXECUTIVE NAVY DESIGN)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_NAVY_DARK
    bg1.line.color.rgb = C_NAVY_DARK

    card1 = add_card(s1, Inches(0.9), Inches(0.85), Inches(11.533), Inches(5.8), C_WHITE, C_WHITE)

    t1_box = s1.shapes.add_textbox(Inches(1.5), Inches(1.3), Inches(10.333), Inches(3.2))
    tf1 = t1_box.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "🏥 CLINICAL GOVERNANCE & HEALTHCARE OPERATIONS BRIEFING"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = C_BLUE
    p.space_after = Pt(14)

    p2 = tf1.add_paragraph()
    p2.text = "Clinic Operations Analytics:\nInvestigating Patient Flow, Waiting Times & Provider Workload"
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = C_PRIMARY
    p2.space_after = Pt(14)

    p3 = tf1.add_paragraph()
    p3.text = "An Empirical EHR Audit of 16,998 Outpatient Encounters at Metro North Family Health Centre"
    p3.font.size = Pt(14.5)
    p3.font.color.rgb = C_SLATE

    # Key stats pill row
    stat_box = s1.shapes.add_textbox(Inches(1.5), Inches(4.3), Inches(10.333), Inches(0.8))
    tf_stat = stat_box.text_frame
    tf_stat.word_wrap = True
    p_s = tf_stat.paragraphs[0]
    p_s.text = "📊 16,998 Scheduled Encounters   |   👥 2,775 Active Patients   |   🩺 4 Attending Physicians   |   📅 250 Operating Days (2024)"
    p_s.font.size = Pt(13)
    p_s.font.bold = True
    p_s.font.color.rgb = C_PRIMARY

    # Author metadata
    auth_box = s1.shapes.add_textbox(Inches(1.5), Inches(5.1), Inches(10.333), Inches(1.1))
    tf_auth = auth_box.text_frame
    tf_auth.word_wrap = True
    
    p_a1 = tf_auth.paragraphs[0]
    p_a1.text = "Prepared by: Clinical Data Analyst & Health Informatics Specialist (MBBS)"
    p_a1.font.size = Pt(13)
    p_a1.font.bold = True
    p_a1.font.color.rgb = C_DARK

    p_a2 = tf_auth.add_paragraph()
    p_a2.text = "Presented to: Chief Medical Officers, Clinical Governance Committees & Health Service Executives"
    p_a2.font.size = Pt(11.5)
    p_a2.font.color.rgb = C_MUTED

    p_a3 = tf_auth.add_paragraph()
    p_a3.text = "Analytical Stack: Relational SQLite | SQL CTEs & Window Functions | Python (Pandas/Seaborn) | Interactive Chart.js"
    p_a3.font.size = Pt(11)
    p_a3.font.color.rgb = C_BLUE

    # =========================================================================
    # SLIDE 2: EXECUTIVE SUMMARY (SBAR FRAMEWORK - CLEAR 2-COLUMN BALANCED LAYOUT)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_slide_header(
        s2,
        "Executive Briefing: SBAR Clinical Operations Framework",
        "Structured clinical governance summary identifying root cause and cost-neutral corrective actions"
    )

    left_x = Inches(0.8)
    col_w = Inches(5.6)

    # 1. Situation Card
    add_card(s2, left_x, Inches(1.75), col_w, Inches(1.55))
    s_box = s2.shapes.add_textbox(left_x + Inches(0.2), Inches(1.85), col_w - Inches(0.4), Inches(1.35))
    tf_s = s_box.text_frame
    tf_s.word_wrap = True
    p = tf_s.paragraphs[0]
    p.text = "SITUATION (The Operational Challenge)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p.space_after = Pt(4)
    p2 = tf_s.add_paragraph()
    p2.text = "Following the July 1 launch of a Chronic Disease Campaign, lobby waiting times and patient dissatisfaction escalated rapidly, with severe mid-morning congestion and provider fatigue."
    p2.font.size = Pt(12)
    p2.font.color.rgb = C_DARK
    p2.line_spacing = 1.25

    # 2. Background Card
    add_card(s2, left_x, Inches(3.45), col_w, Inches(1.55))
    b_box = s2.shapes.add_textbox(left_x + Inches(0.2), Inches(3.55), col_w - Inches(0.4), Inches(1.35))
    tf_b = b_box.text_frame
    tf_b.word_wrap = True
    p = tf_b.paragraphs[0]
    p.text = "BACKGROUND (Initial Executive Hypothesis)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_BLUE
    p.space_after = Pt(4)
    p2 = tf_b.add_paragraph()
    p2.text = "Leadership attributed delays to uncontrollable demand surge and physician pacing, considering expensive interventions: extending operating hours or hiring additional locum clinicians."
    p2.font.size = Pt(12)
    p2.font.color.rgb = C_DARK
    p2.line_spacing = 1.25

    # 3. Assessment Card
    add_card(s2, left_x, Inches(5.15), col_w, Inches(1.85), C_WHITE, C_CRIMSON)
    a_box = s2.shapes.add_textbox(left_x + Inches(0.2), Inches(5.25), col_w - Inches(0.4), Inches(1.65))
    tf_a = a_box.text_frame
    tf_a.word_wrap = True
    p = tf_a.paragraphs[0]
    p.text = "ASSESSMENT (The Empirical Data Evidence)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_CRIMSON
    p.space_after = Pt(4)
    p2 = tf_a.add_paragraph()
    p2.text = "• Booked volume grew only +12.5% (+2 patients/doctor/day).\n• Afternoon clinics stayed flat (P90 wait was 35.2m Pre vs 35.8m Post).\n• Morning P90 wait surged +82% (41.9m to 76.3m) due to unbuffered 15-min slots colliding with complex 24.5-min chronic reviews."
    p2.font.size = Pt(12)
    p2.font.color.rgb = C_DARK
    p2.line_spacing = 1.25

    # RIGHT COLUMN: RECOMMENDATION
    right_x = Inches(6.7)
    rec_w = Inches(5.833)
    add_card(s2, right_x, Inches(1.75), rec_w, Inches(5.25), C_WHITE, C_PRIMARY)

    r_box = s2.shapes.add_textbox(right_x + Inches(0.3), Inches(1.95), rec_w - Inches(0.6), Inches(4.85))
    tf_r = r_box.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "RECOMMENDATION: Cost-Neutral 4-Point Action Plan"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_PRIMARY
    p.space_after = Pt(14)

    recs_bullets = [
        ("🔹 Protected 30-Min Chronic Care Templates:", 
         "Mandate 30-minute booking templates for multi-morbid care plans. Resolves the severe template mismatch with actual 24.5-minute consult times."),
        ("🔹 10:30 AM Mid-Morning Catch-Up Buffer:", 
         "Insert a single unbooked 15-minute administrative slot to act as a queuing circuit breaker, absorbing stochastic morning overruns before the 11:00 AM wave."),
        ("🔹 Dynamic Front-End Nursing Intake:", 
         "Reallocate existing nursing roster to staff a 3rd triage vital-signs intake station during peak arrival congestion (08:30–10:15 AM)."),
        ("🔹 Automated Sunday 16:00 SMS Reminders:", 
         "Target the elevated 12.88% Monday no-show rate with proactive automated confirmations to smooth weekly clinic utilization.")
    ]

    for title_r, desc_r in recs_bullets:
        pr_t = tf_r.add_paragraph()
        pr_t.text = title_r
        pr_t.font.size = Pt(13)
        pr_t.font.bold = True
        pr_t.font.color.rgb = C_DARK

        pr_d = tf_r.add_paragraph()
        pr_d.text = desc_r
        pr_d.font.size = Pt(12)
        pr_d.font.color.rgb = C_SLATE
        pr_d.space_after = Pt(10)
        pr_d.line_spacing = 1.2

    pr_imp = tf_r.add_paragraph()
    pr_imp.text = "🎯 Target Outcome: Reduces morning P90 wait to <35m with ZERO clinician recruitment cost."
    pr_imp.font.size = Pt(12)
    pr_imp.font.bold = True
    pr_imp.font.color.rgb = C_EMERALD

    # =========================================================================
    # SLIDE 3: RELATIONAL DATA ARCHITECTURE (FULL DEDICATED SLIDE FOR ER DIAGRAM)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_slide_header(
        s3,
        "Relational Data Architecture: Outpatient EHR & Operational Scheduling Model",
        "Multi-table schema linking Synthea EHR patient master index to operational milestone timestamps",
        category="CLINICAL DATA MODEL & ARCHITECTURE"
    )

    # Full widescreen card for the ER diagram
    er_card_w = Inches(11.733)
    er_card_h = Inches(5.4)
    add_card(s3, Inches(0.8), Inches(1.7), er_card_w, er_card_h, C_WHITE, C_CARD_BORDER)

    er_img_path = os.path.join(IMG_DIR, "data_model.png")
    if os.path.exists(er_img_path):
        # Image aspect ratio is ~1.55. At 8.0" width -> ~5.15" height, perfectly centered in 11.7" x 5.4"
        img_w = Inches(8.0)
        img_left = Inches(0.8) + (er_card_w - img_w) / 2
        s3.shapes.add_picture(er_img_path, img_left, Inches(1.8), width=img_w)

    # =========================================================================
    # SLIDE 4: HEALTHCARE DATA QUALITY (DQ) AUDIT & GOVERNANCE (DEDICATED SLIDE)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_slide_header(
        s4,
        "Healthcare Data Quality (DQ) Audit & Governance Framework",
        "Algorithmic data cleaning pipeline resolving 6 real-world EHR anomalies to ensure cohort integrity",
        category="CLINICAL DATA GOVERNANCE & VALIDATION"
    )

    # Top Row: 3 Architecture / Volume Stat Pillars (Height 0.95")
    top_y = Inches(1.58)
    pillar_w = Inches(3.68)
    pillar_gap = Inches(0.34)
    pillar_h = Inches(0.95)

    pillars = [
        ("AUDITED ENCOUNTER COHORT", "16,998 Visits Audited", "2,775 Synthea active patients | 4 clinicians | 250 operating days"),
        ("MILESTONE TIMESTAMP GATES", "5 Sequential Milestones", "Arrival Kiosk -> Triage -> Doctor Start -> Doctor End -> Checkout"),
        ("HEALTHCARE DQ COMPLIANCE", "100% Validated Clean", "Algorithmic audit quarantined edge cases prior to statistical modeling")
    ]

    for i, (cat_p, main_p, sub_p) in enumerate(pillars):
        px = Inches(0.8) + i * (pillar_w + pillar_gap)
        add_card(s4, px, top_y, pillar_w, pillar_h, C_CARD_BG, C_CARD_BORDER)
        p_box = s4.shapes.add_textbox(px + Inches(0.18), top_y + Inches(0.10), pillar_w - Inches(0.36), pillar_h - Inches(0.20))
        tf_p = p_box.text_frame
        tf_p.word_wrap = True
        
        p = tf_p.paragraphs[0]
        p.text = cat_p
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = C_BLUE

        p2 = tf_p.add_paragraph()
        p2.text = main_p
        p2.font.size = Pt(15)
        p2.font.bold = True
        p2.font.color.rgb = C_PRIMARY

        p3 = tf_p.add_paragraph()
        p3.text = sub_p
        p3.font.size = Pt(10.5)
        p3.font.color.rgb = C_SLATE

    # Middle / Bottom: 4 Structured Governance Cards in a 2x2 Grid
    g_start_y = Inches(2.72)
    g_card_w = Inches(5.68)
    g_card_h = Inches(1.55)
    g_gap_x = Inches(0.373)
    g_gap_y = Inches(0.18)

    dq_cards = [
        ("1. Milestone Completeness (Kiosk Bypasses)", C_PRIMARY,
         "• Identified 6 acute walk-in encounters lacking kiosk arrival timestamps.\n• Clinical Mechanism: Emergent triage bypass before administrative registration.\n• Resolution: Quarantined from waiting time models to prevent artificial zero-wait bias."),
        
        ("2. Temporal Order & Tablet Clock Drift", C_BLUE,
         "• Detected 3 encounters where triage start preceded arrival timestamp.\n• Clinical Mechanism: Front-desk tablet hardware clock desynchronization.\n• Resolution: Quarantined time-sync faults to guarantee valid logical timestamps."),
        
        ("3. Session Discharge Integrity", C_EMERALD,
         "• Audited 3 encounters missing final checkout timestamps at clinic close.\n• Clinical Mechanism: Unclosed EHR sessions when patients left without front-desk stop.\n• Resolution: Quarantined from Total Clinic Length of Stay (LOS) calculations."),
        
        ("4. Referential Key & Test Entity Cleansing", C_CRIMSON,
         "• Resolved 4 duplicate booking keys via primary key deduplication (earliest retained).\n• Quarantined 2 test provider records (PRV-999) from physician workload benchmarks.\n• Final Clean Mart: 16,998 certified rows with 100% relational integrity.")
    ]

    for idx, (dq_title, dq_color, dq_body) in enumerate(dq_cards):
        r = idx // 2
        c = idx % 2
        gx = Inches(0.8) + c * (g_card_w + g_gap_x)
        gy = g_start_y + r * (g_card_h + g_gap_y)

        add_card(s4, gx, gy, g_card_w, g_card_h, C_WHITE, dq_color)
        c_box = s4.shapes.add_textbox(gx + Inches(0.18), gy + Inches(0.10), g_card_w - Inches(0.36), g_card_h - Inches(0.20))
        tf_c = c_box.text_frame
        tf_c.word_wrap = True

        p_t = tf_c.paragraphs[0]
        p_t.text = dq_title
        p_t.font.size = Pt(12.5)
        p_t.font.bold = True
        p_t.font.color.rgb = dq_color
        p_t.space_after = Pt(2)

        p_b = tf_c.add_paragraph()
        p_b.text = dq_body
        p_b.font.size = Pt(10.5)
        p_b.font.color.rgb = C_DARK
        p_b.line_spacing = 1.2

    # Bottom Governance Callout Banner
    gov_y = Inches(6.15)
    gov_h = Inches(0.92)
    add_card(s4, Inches(0.8), gov_y, Inches(11.733), gov_h, C_NAVY_DARK, C_NAVY_DARK)

    gov_box = s4.shapes.add_textbox(Inches(1.0), gov_y + Inches(0.08), Inches(11.333), Inches(0.76))
    tf_gov = gov_box.text_frame
    tf_gov.word_wrap = True

    p_g1 = tf_gov.paragraphs[0]
    p_g1.text = "🛡️ CLINICAL DATA GOVERNANCE VERIFICATION"
    p_g1.font.size = Pt(11)
    p_g1.font.bold = True
    p_g1.font.color.rgb = RGBColor(56, 189, 248) # Sky blue
    p_g1.space_after = Pt(2)

    p_g2 = tf_gov.add_paragraph()
    p_g2.text = "All 16,998 analyzed encounters were algorithmically audited across 5 relational constraints, ensuring 100% compliance before statistical modeling."
    p_g2.font.size = Pt(11)
    p_g2.font.color.rgb = C_WHITE

    # =========================================================================
    # HELPER FUNCTION FOR CHARTS SLIDES (SLIDES 5 TO 9)
    # =========================================================================
    def build_chart_slide(slide, title, subtitle, img_filename, metric_title, metric_val, metric_sub, bullets):
        add_slide_header(slide, title, subtitle)

        chart_w = Inches(7.4)
        chart_h = Inches(5.3)
        add_card(slide, Inches(0.8), Inches(1.7), chart_w, chart_h, C_WHITE, C_CARD_BORDER)

        img_path = os.path.join(IMG_DIR, img_filename)
        if os.path.exists(img_path):
            slide.shapes.add_picture(img_path, Inches(0.9), Inches(1.85), width=Inches(7.2))

        panel_x = Inches(8.5)
        panel_w = Inches(4.033)
        add_card(slide, panel_x, Inches(1.7), panel_w, chart_h, C_CARD_BG, C_CARD_BORDER)

        p_box = slide.shapes.add_textbox(panel_x + Inches(0.25), Inches(1.9), panel_w - Inches(0.5), chart_h - Inches(0.4))
        tf_p = p_box.text_frame
        tf_p.word_wrap = True

        p_stat_cat = tf_p.paragraphs[0]
        p_stat_cat.text = metric_title.upper()
        p_stat_cat.font.size = Pt(11)
        p_stat_cat.font.bold = True
        p_stat_cat.font.color.rgb = C_BLUE

        p_stat_val = tf_p.add_paragraph()
        p_stat_val.text = metric_val
        p_stat_val.font.size = Pt(28)
        p_stat_val.font.bold = True
        p_stat_val.font.color.rgb = C_PRIMARY
        p_stat_val.space_after = Pt(2)

        p_stat_sub = tf_p.add_paragraph()
        p_stat_sub.text = metric_sub
        p_stat_sub.font.size = Pt(12)
        p_stat_sub.font.color.rgb = C_SLATE
        p_stat_sub.space_after = Pt(16)

        for b_title, b_desc in bullets:
            pb_t = tf_p.add_paragraph()
            pb_t.text = f"• {b_title}"
            pb_t.font.size = Pt(13)
            pb_t.font.bold = True
            pb_t.font.color.rgb = C_DARK

            pb_d = tf_p.add_paragraph()
            pb_d.text = b_desc
            pb_d.font.size = Pt(12)
            pb_d.font.color.rgb = C_SLATE
            pb_d.space_after = Pt(10)
            pb_d.line_spacing = 1.25

    # =========================================================================
    # SLIDE 5: VOLUME ANALYSIS (VISUAL 1)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    build_chart_slide(
        s5,
        "Testing the Demand Hypothesis: Monthly Operational Volume",
        "Empirical volume tracking disproves the assumption of uncontrollable patient overload",
        "fig1_monthly_volume_trend.png",
        "Volume Growth Impact",
        "+12.5%",
        "From ~64 to ~72 visits / day clinic-wide",
        [
            ("Orderly Demand Increase:", 
             "Total bookings increased from 7,998 visits (Pre) to 9,000 visits (Post). This represents ~2 additional patients per clinician per day."),
            ("Stable Completion Rates (81.7%):", 
             "Consultation completion rates held steady across all 12 months (81.6% Pre vs 81.8% Post), ruling out patient abandonment."),
            ("Executive Takeaway:", 
             "An orderly 12.5% increase across a 4-physician clinic does not trigger queuing failure. The root problem lies in schedule structure.")
        ]
    )

    # =========================================================================
    # SLIDE 6: DIURNAL WAITING TIME CURVE (VISUAL 2)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    build_chart_slide(
        s6,
        "Diurnal Dynamics: Identifying the Mid-Morning Backlog Wave",
        "Hourly P50 vs P90 waiting time tracking reveals unbuffered queuing cascades",
        "fig2_waiting_time_percentiles_hourly.png",
        "Peak Morning Tail Wait",
        "86.8 min",
        "P90 Wait Time at 10:00 – 11:00 AM",
        [
            ("Why P90 Matters (Worst 10% Delays):", 
             "While median wait is 21.1m, P90 reveals severe backlog outliers. International benchmarks (NHS, Australia, Singapore) mandate percentiles because averages conceal patient distress."),
            ("Compounding Queuing Cascade:", 
             "Clinic opens smoothly at 08:00 AM (24m P90). By 10:30 AM, stochastic consult delays compound exponentially into an 86.8m backlog."),
            ("Midday Reset Effect:", 
             "Between 12:00 and 13:00, doctors clear charts. Wait times drop back to 21–23m at 13:00, proving the collapse is isolated to morning scheduling.")
        ]
    )

    # =========================================================================
    # SLIDE 7: ROOT CAUSE ISOLATION (VISUAL 3)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    build_chart_slide(
        s7,
        "Root Cause Isolation: Morning Session Collapse vs Afternoon Control",
        "Quasi-experimental evaluation establishes causal link to 15-minute slot compression",
        "fig3_pre_post_session_comparison.png",
        "Morning Wait Time Surge",
        "+82.1%",
        "Pre: 41.9m ➔ Post: 76.3m (Afternoon flat at 35.8m)",
        [
            ("Natural Clinical Experiment:", 
             "On July 1, management compressed morning slots from 20m to 15m, while leaving afternoon slots unchanged at 20m (serving as a natural control group)."),
            ("Afternoon Control Group (Stable):", 
             "Afternoon P90 wait times remained completely flat (35.2m Pre vs 35.8m Post) across the exact same providers and examination rooms."),
            ("Causal Conclusion:", 
             "If disease seasonality or raw volume drove delays, afternoon clinics would have collapsed too. Eliminating the 5-minute morning buffer caused the crisis.")
        ]
    )

    # =========================================================================
    # SLIDE 8: CLINICAL COMPLEXITY & PROVIDER BURDEN (VISUALS 4 & 5)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    build_chart_slide(
        s8,
        "Clinical Complexity Mismatch & Clinician Workload Profile",
        "Dr. Vance carried complex chronic disease reviews incompatible with 15-minute slots",
        "fig4_provider_workload_and_overruns.png",
        "Clinician Overrun Peak",
        "48.3%",
        "Dr. Arthur Vance (Internal Medicine) Overruns",
        [
            ("Chronic Care Case-Mix Strain:", 
             "Chronic disease reviews average 24.5 minutes due to multi-morbidity medication reconciliation—fundamentally incompatible with 15-minute booking templates."),
            ("Dr. Arthur Vance, MD:", 
             "Carried the largest chronic disease panel, delivering 1,307 clinical hours with a 48.3% slot overrun rate (vs ~29–32% for generalist colleagues)."),
            ("Clinical Realism:", 
             "Dr. Vance is not inefficient. Squeezing complex multi-morbid patients into shortened morning slots forced predictable schedule slippage.")
        ]
    )

    # =========================================================================
    # SLIDE 9: MISSED APPOINTMENTS BY DAY (VISUAL 6)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    build_chart_slide(
        s9,
        "Patient Adherence: Analyzing No-Show Patterns by Weekday",
        "Monday morning no-show spike creates operational friction and unutilized capacity",
        "fig5_no_show_patterns.png",
        "Monday No-Show Spike",
        "12.88%",
        "vs 10.48% Midweek Baseline (~23% higher)",
        [
            ("The Weekend Decay Effect:", 
             "Missed appointments peak sharply on Mondays due to weekend lead-time forgetfulness and emerging start-of-week work schedule conflicts."),
            ("Access vs Overbooking Friction:", 
             "Shortening slots to 'hedge' against no-shows backfired: on high-attendance days, clinics experienced catastrophic lobby gridlock."),
            ("Targeted Operational Solution:", 
             "Deploy automated 2-way SMS confirmation prompts on Sunday at 16:00, paired with a modest 5–8% Monday morning overbooking buffer.")
        ]
    )

    # =========================================================================
    # SLIDE 10: INTERACTIVE EXECUTIVE DASHBOARD (HIGH-IMPACT VISUAL)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_slide_header(
        s10,
        "Interactive Decision Support Tool: Executive Operations Dashboard",
        "A standalone web application providing multi-dimensional operational intelligence"
    )

    hero_img_path = os.path.join(IMG_DIR, "dashboard_preview_hero.png")
    if not os.path.exists(hero_img_path):
        prev_img_path = os.path.join(IMG_DIR, "dashboard_preview.png")
        if os.path.exists(prev_img_path):
            from PIL import Image
            img_raw = Image.open(prev_img_path)
            hero_crop = img_raw.crop((0, 0, img_raw.width, min(1555, img_raw.height)))
            hero_crop.save(hero_img_path)

    dash_w = Inches(7.4)
    dash_h = Inches(5.3)
    add_card(s10, Inches(0.8), Inches(1.7), dash_w, dash_h, C_WHITE, C_CARD_BORDER)

    if os.path.exists(hero_img_path):
        # Perfectly centered hero dashboard preview (Header, filters, HR guide, KPIs, and Visuals 1 & 2)
        # 7.15" width x 4.83" height centered in 7.4" x 5.3" card (0.125" x-padding, 0.235" y-padding)
        s10.shapes.add_picture(hero_img_path, Inches(0.925), Inches(1.935), width=Inches(7.15))

    d_panel_x = Inches(8.5)
    d_panel_w = Inches(4.033)
    add_card(s10, d_panel_x, Inches(1.7), d_panel_w, dash_h, C_CARD_BG, C_CARD_BORDER)

    d_box = s10.shapes.add_textbox(d_panel_x + Inches(0.25), Inches(1.85), d_panel_w - Inches(0.5), dash_h - Inches(0.3))
    tf_d = d_box.text_frame
    tf_d.word_wrap = True

    p_tag = tf_d.paragraphs[0]
    p_tag.text = "OPERATIONAL DECISION SUPPORT"
    p_tag.font.size = Pt(11)
    p_tag.font.bold = True
    p_tag.font.color.rgb = C_BLUE

    p_title = tf_d.add_paragraph()
    p_title.text = "Interactive Features"
    p_title.font.size = Pt(20)
    p_title.font.bold = True
    p_title.font.color.rgb = C_PRIMARY
    p_title.space_after = Pt(10)

    features = [
        ("Multi-Dimensional Filtering", 
         "Instant cohort drill-down across 3 operational periods (Full Year, Pre, Post) and individual clinicians."),
        ("Built-in Evaluator & HR Guide", 
         "On-screen plain English definitions of Median (P50), P90 tail risk, and Slot Overrun rates for hospital boards."),
        ("Zero-Lag Architecture", 
         "15 pre-computed JSON slices guarantee instantaneous Chart.js updates without server roundtrips."),
        ("Accessible Deployment", 
         "Runs directly in standard web browsers with zero installation requirements or external dependencies.")
    ]

    for f_title, f_desc in features:
        pf_t = tf_d.add_paragraph()
        pf_t.text = f"• {f_title}:"
        pf_t.font.size = Pt(12)
        pf_t.font.bold = True
        pf_t.font.color.rgb = C_DARK

        pf_d = tf_d.add_paragraph()
        pf_d.text = f_desc
        pf_d.font.size = Pt(11)
        pf_d.font.color.rgb = C_SLATE
        pf_d.space_after = Pt(8)
        pf_d.line_spacing = 1.2

    pf_badge = tf_d.add_paragraph()
    pf_badge.text = "🎯 Live Tool: Open dashboard/index.html in any browser"
    pf_badge.font.size = Pt(10.5)
    pf_badge.font.bold = True
    pf_badge.font.color.rgb = C_EMERALD

    # =========================================================================
    # SLIDE 11: STRATEGIC ROADMAP & PROJECTED OUTCOMES (CLEAR 2x2 + BANNER)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_slide_header(
        s11,
        "Strategic Recommendations & Implementation Roadmap",
        "A cost-neutral operational restructuring plan restoring clinic waiting times to <35 minutes"
    )

    grid_w = Inches(5.6)
    grid_h = Inches(1.95)
    gap_x = Inches(0.533)
    gap_y = Inches(0.25)
    start_x = Inches(0.8)
    start_y = Inches(1.72)

    card_data = [
        ("1. Protected Chronic Care Templates", C_PRIMARY,
         "• Mandate 30-minute booking templates for multi-morbid Care Plans.\n• Hard-stop EHR templates to prevent complex cases booking into 15m slots.\n• Eliminates structural schedule overrun at the source."),
        ("2. Mid-Morning 10:30 AM Catch-Up Buffer", C_BLUE,
         "• Insert a single 15-minute unbooked administrative slot across morning clinics.\n• Functions as a mathematical queuing circuit breaker.\n• Absorbs upstream overruns and resets lobby waiting before 11:00 AM."),
        ("3. Dynamic Front-End Nursing Intake", C_EMERALD,
         "• Reallocate nursing shift rosters to staff a 3rd triage vital-signs station.\n• Focus intake coverage on peak morning arrivals (08:30–10:15 AM).\n• Eliminates the 18-minute front-desk triage lobby choke point."),
        ("4. Automated Sunday 16:00 SMS Reminders", C_CRIMSON,
         "• Deploy automated 2-way SMS confirmation prompts on Sunday afternoon.\n• Targets the 12.88% Monday no-show surge caused by weekend lag.\n• Pairs with a modest 5–8% Monday overbooking buffer to stabilize volume.")
    ]

    for idx, (c_title, c_color, c_bullets) in enumerate(card_data):
        row = idx // 2
        col = idx % 2
        cx = start_x + col * (grid_w + gap_x)
        cy = start_y + row * (grid_h + gap_y)

        add_card(s11, cx, cy, grid_w, grid_h, C_WHITE, c_color)

        c_box = s11.shapes.add_textbox(cx + Inches(0.2), cy + Inches(0.12), grid_w - Inches(0.4), grid_h - Inches(0.24))
        tf_c = c_box.text_frame
        tf_c.word_wrap = True

        p_t = tf_c.paragraphs[0]
        p_t.text = c_title
        p_t.font.size = Pt(13.5)
        p_t.font.bold = True
        p_t.font.color.rgb = c_color
        p_t.space_after = Pt(4)

        p_b = tf_c.add_paragraph()
        p_b.text = c_bullets
        p_b.font.size = Pt(11.5)
        p_b.font.color.rgb = C_DARK
        p_b.line_spacing = 1.25

    # Bottom Target Outcomes Card
    bot_y = Inches(6.05)
    bot_h = Inches(1.05)
    add_card(s11, Inches(0.8), bot_y, Inches(11.733), bot_h, C_NAVY_DARK, C_NAVY_DARK)

    bot_box = s11.shapes.add_textbox(Inches(1.0), bot_y + Inches(0.12), Inches(11.333), Inches(0.8))
    tf_bot = bot_box.text_frame
    tf_bot.word_wrap = True

    p_b1 = tf_bot.paragraphs[0]
    p_b1.text = "🎯 PROJECTED OPERATIONAL IMPACT (COST-NEUTRAL INTERVENTIONS)"
    p_b1.font.size = Pt(12)
    p_b1.font.bold = True
    p_b1.font.color.rgb = RGBColor(56, 189, 248)
    p_b1.space_after = Pt(2)

    p_b2 = tf_bot.add_paragraph()
    p_b2.text = "✔ Morning P90 wait times reduced from 76.3m to <35.0m    |    ✔ Provider slot overruns reduced from 48.3% to <20.0%    |    ✔ Zero clinician hiring budget required"
    p_b2.font.size = Pt(12)
    p_b2.font.bold = True
    p_b2.font.color.rgb = C_WHITE

    prs.save(OUTPUT_PPTX)
    print(f"Executive Presentation rebuilt successfully with 11 slides -> {OUTPUT_PPTX}")

if __name__ == "__main__":
    build_presentation()
