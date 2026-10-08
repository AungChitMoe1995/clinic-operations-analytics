"""
generate_dashboard_preview.py
------------------------------
Generates a high-resolution composite dashboard preview image:
- dashboard/dashboard_preview.png
- docs/images/dashboard_preview.png

Renders KPI cards, title banner, and stitches key analytical charts
into a polished executive overview for the portfolio README.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, "docs", "images")
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")

def create_preview():
    fig = plt.figure(figsize=(16, 12), dpi=200, facecolor="#F8FAFC")
    
    # Outer layout: Header banner + KPI cards + 4 chart panels
    gs = gridspec.GridSpec(3, 2, height_ratios=[0.8, 2.5, 2.5], hspace=0.28, wspace=0.18, 
                           left=0.04, right=0.96, top=0.94, bottom=0.04)

    # 1. Header Banner & KPI Cards
    ax_header = fig.add_subplot(gs[0, :])
    ax_header.set_facecolor("#FFFFFF")
    for spine in ax_header.spines.values():
        spine.set_color("#E2E8F0")
        spine.set_linewidth(1.2)
    ax_header.set_xticks([])
    ax_header.set_yticks([])

    # Header text
    ax_header.text(0.02, 0.72, "Metro North Family Health Centre — Clinic Operations Dashboard", 
                   fontsize=16, fontweight="bold", color="#1E3A8A", va="center")
    ax_header.text(0.02, 0.40, "Investigating Patient Flow, Waiting Times & Provider Workload | 12-Month Outpatient Study (N = 16,998 visits)", 
                   fontsize=10.5, color="#64748B", va="center")

    # Draw 5 KPI Boxes inside header
    kpis = [
        ("TOTAL VISITS", "16,998", "68.0 visits/day", "#1E3A8A"),
        ("COMPLETED", "13,891", "81.7% show rate", "#0D9488"),
        ("MEDIAN WAIT", "21.1 m", "Arrival → Doctor", "#1E3A8A"),
        ("P90 WAIT TIME", "55.9 m", "Peak: 76.3m (Morning)", "#E11D48"),
        ("NO-SHOW RATE", "11.2%", "1,898 missed visits", "#F59E0B")
    ]
    
    box_w = 0.165
    start_x = 0.02
    box_y = 0.08
    box_h = 0.24

    for i, (label, val, sub, color) in enumerate(kpis):
        bx = start_x + i * 0.198
        rect = plt.Rectangle((bx, box_y), box_w, box_h, facecolor="#F1F5F9", 
                             edgecolor="#CBD5E1", linewidth=0.8, transform=ax_header.transAxes, clip_on=False)
        ax_header.add_patch(rect)
        ax_header.text(bx + 0.01, box_y + 0.17, label, fontsize=7.5, fontweight="bold", color="#64748B", transform=ax_header.transAxes)
        ax_header.text(bx + 0.01, box_y + 0.07, val, fontsize=12.5, fontweight="bold", color=color, transform=ax_header.transAxes)
        ax_header.text(bx + 0.01, box_y - 0.01, sub, fontsize=6.8, color="#64748B", transform=ax_header.transAxes)

    # 2. Insert Chart Images
    chart_configs = [
        (gs[1, 0], "fig1_monthly_volume_trend.png"),
        (gs[1, 1], "fig2_waiting_time_percentiles_hourly.png"),
        (gs[2, 0], "fig3_pre_post_session_comparison.png"),
        (gs[2, 1], "fig4_provider_workload_and_overruns.png"),
    ]

    for grid_pos, img_name in chart_configs:
        ax = fig.add_subplot(grid_pos)
        ax.axis("off")
        img_path = os.path.join(IMAGES_DIR, img_name)
        if os.path.exists(img_path):
            img = Image.open(img_path)
            ax.imshow(img)
            ax.set_aspect("auto")

    preview_path1 = os.path.join(DASHBOARD_DIR, "dashboard_preview.png")
    preview_path2 = os.path.join(IMAGES_DIR, "dashboard_preview.png")
    
    fig.savefig(preview_path1, dpi=200, bbox_inches="tight")
    fig.savefig(preview_path2, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"Generated dashboard preview -> {preview_path1}")
    print(f"Generated dashboard preview -> {preview_path2}")

if __name__ == "__main__":
    create_preview()
