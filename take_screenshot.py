#!/usr/bin/env python3
"""
Website Screenshot Tool for Telegram
Takes a screenshot of the dark website and saves it
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import os

def take_website_screenshot():
    """Take a screenshot of the dark website"""
    
    # Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    
    try:
        print("🚀 Starting Chrome driver...")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        print("📸 Navigating to website...")
        driver.get("http://localhost:8080")
        
        # Wait for page to load and animations to complete
        time.sleep(3)
        
        print("📷 Taking screenshot...")
        screenshot_path = "/home/pinky/.openclaw/workspace/dark-website-project/screenshot.png"
        driver.save_screenshot(screenshot_path)
        
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        # Also create a smaller version for Telegram
        with Image.open(screenshot_path) as img:
            # Resize for better Telegram viewing
            img.thumbnail((1200, 800), Image.Resampling.LANCZOS)
            telegram_path = "/home/pinky/.openclaw/workspace/dark-website-project/telegram_screenshot.png"
            img.save(telegram_path)
            print(f"✅ Telegram-optimized screenshot saved: {telegram_path}")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ Screenshot failed: {e}")
        return False

if __name__ == "__main__":
    success = take_website_screenshot()
    if success:
        print("🎉 Screenshot completed successfully!")
    else:
        print("💥 Screenshot failed!")
        exit(1)