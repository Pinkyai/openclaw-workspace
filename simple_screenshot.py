#!/usr/bin/env python3
"""
Simple Website Screenshot Tool
Uses html2image to capture the website
"""

from html2image import Html2Image
import os

def take_simple_screenshot():
    """Take a screenshot using html2image"""
    
    try:
        print("📸 Initializing screenshot tool...")
        hti = Html2Image()
        
        print("🌐 Capturing website...")
        # Take screenshot of the local website
        screenshot = hti.screenshot(
            url='http://localhost:8080',
            save_as='website_screenshot.png',
            size=(1920, 1080)
        )
        
        if screenshot and os.path.exists('website_screenshot.png'):
            print("✅ Screenshot saved: website_screenshot.png")
            
            # Also create a Telegram-optimized version
            from PIL import Image
            with Image.open('website_screenshot.png') as img:
                # Resize for Telegram (max dimensions while maintaining aspect ratio)
                img.thumbnail((1200, 800), Image.Resampling.LANCZOS)
                img.save('/home/pinky/.openclaw/workspace/dark-website-project/telegram_screenshot.png', 'PNG', quality=95)
                print("✅ Telegram-optimized screenshot saved!")
            
            return True
        else:
            print("❌ Screenshot capture failed")
            return False
            
    except Exception as e:
        print(f"❌ Screenshot error: {e}")
        return False

if __name__ == "__main__":
    success = take_simple_screenshot()
    if success:
        print("🎉 Screenshot completed successfully!")
        print("📍 Screenshot location: /home/pinky/.openclaw/workspace/dark-website-project/telegram_screenshot.png")
    else:
        print("💥 Screenshot failed - website might still be loading or server issue")
        exit(1)