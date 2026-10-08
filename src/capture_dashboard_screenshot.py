"""
capture_dashboard_screenshot.py
--------------------------------
Uses headless Chrome via Selenium to take a high-resolution,
pixel-perfect screenshot of the actual dashboard/index.html web application.

Saves directly to:
- dashboard/dashboard_preview.png
- docs/images/dashboard_preview.png
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = os.path.join(BASE_DIR, "dashboard", "index.html")
OUTPUT_PATH1 = os.path.join(BASE_DIR, "dashboard", "dashboard_preview.png")
OUTPUT_PATH2 = os.path.join(BASE_DIR, "docs", "images", "dashboard_preview.png")

def capture_screenshot():
    print(f"Loading web dashboard: file:///{HTML_PATH.replace(os.sep, '/')}")
    
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1550,1320')
    options.add_argument('--force-device-scale-factor=1.5') # High-DPI sharpness
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--hide-scrollbars')

    driver = webdriver.Chrome(options=options)
    
    file_url = f"file:///{os.path.abspath(HTML_PATH).replace(os.sep, '/')}"
    driver.get(file_url)
    
    # Wait 2.5 seconds to guarantee all fonts and Chart.js canvases are fully painted
    time.sleep(2.5)
    
    # Resize window to fit entire page height
    total_height = driver.execute_script("return document.body.scrollHeight")
    driver.set_window_size(1550, max(total_height + 40, 2200))
    time.sleep(0.5)
    
    driver.save_screenshot(OUTPUT_PATH1)
    # Also copy to docs/images/
    driver.save_screenshot(OUTPUT_PATH2)
    
    driver.quit()

    # Create hero crop (header + filters + HR guide + KPIs + Visuals 1 & 2)
    from PIL import Image
    img = Image.open(OUTPUT_PATH1)
    # Visual 1 & 2 bottom boundary is at y=1555 at scale factor 1.5
    hero_crop = img.crop((0, 0, img.width, min(1555, img.height)))
    hero_path = os.path.join(BASE_DIR, "docs", "images", "dashboard_preview_hero.png")
    hero_crop.save(hero_path)

    print(f"Successfully captured real browser screenshot -> {OUTPUT_PATH1}")
    print(f"Successfully captured real browser screenshot -> {OUTPUT_PATH2}")
    print(f"Successfully generated hero crop graphic -> {hero_path}")

if __name__ == "__main__":
    capture_screenshot()
