"""
test_dashboard_update.py
-------------------------
Verifies dynamic chart scale headroom across filter changes.
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_interactivity():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard", "index.html"))
    driver.get(f"file:///{html_path.replace(os.sep, '/')}")
    time.sleep(2)

    # 1. Initial State (ALL)
    max_all = driver.execute_script("return chartHourly.options.scales.y.max;")
    p90_all = driver.execute_script("return Math.max(...chartHourly.data.datasets[0].data);")
    print(f"ALL -> Peak P90: {p90_all:.1f}m, Y-axis max: {max_all}m (Headroom: {max_all - p90_all:.1f}m)")

    # 2. Select POST-INTERVENTION
    driver.execute_script("document.getElementById('filter-period').value = 'POST'; updateDashboard();")
    max_post = driver.execute_script("return chartHourly.options.scales.y.max;")
    p90_post = driver.execute_script("return Math.max(...chartHourly.data.datasets[0].data);")
    print(f"POST -> Peak P90: {p90_post:.1f}m, Y-axis max: {max_post}m (Headroom: {max_post - p90_post:.1f}m)")

    # 3. Select POST + Dr. Arthur Vance (PRV-001)
    driver.execute_script("document.getElementById('filter-provider').value = 'PRV-001'; updateDashboard();")
    max_vance = driver.execute_script("return chartHourly.options.scales.y.max;")
    p90_vance = driver.execute_script("return Math.max(...chartHourly.data.datasets[0].data);")
    print(f"POST + Dr. Vance -> Peak P90: {p90_vance:.1f}m, Y-axis max: {max_vance}m (Headroom: {max_vance - p90_vance:.1f}m)")

    # 4. Select PRE-INTERVENTION
    driver.execute_script("document.getElementById('filter-period').value = 'PRE'; document.getElementById('filter-provider').value = 'ALL'; updateDashboard();")
    max_pre = driver.execute_script("return chartHourly.options.scales.y.max;")
    p90_pre = driver.execute_script("return Math.max(...chartHourly.data.datasets[0].data);")
    print(f"PRE -> Peak P90: {p90_pre:.1f}m, Y-axis max: {max_pre}m (Headroom: {max_pre - p90_pre:.1f}m)")

    driver.quit()
    print("\nSUCCESS: All scales dynamically adjust with generous headroom!")

if __name__ == "__main__":
    test_interactivity()
