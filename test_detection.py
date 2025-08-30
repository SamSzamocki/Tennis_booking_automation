#!/usr/bin/env python3
"""
Temporary test script to check detection logic on a specific URL with known available slots
"""

import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from watcher import parse_court_availability, handle_cookie_popup, login_to_better

# Load environment variables
load_dotenv()

# Test URL with known available slots (September 5th)
TEST_URL = "https://bookings.better.org.uk/location/islington-tennis-centre/highbury-tennis/2025-09-05/by-time"

def test_detection():
    """Test the detection logic on a specific URL with available slots."""
    print(f"🧪 Testing detection logic on URL with known available slots")
    print(f"URL: {TEST_URL}")
    print(f"Date: September 5th, 2025 (Known available slots)")
    print("="*80)
    
    with sync_playwright() as playwright:
        # Launch browser in visible mode for testing
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = context.new_page()
        
        try:
            # Step 1: Login to Better
            print("🔐 Logging in to Better...")
            login_to_better(page)
            
            # Step 2: Navigate to test URL
            print(f"🌐 Navigating to test URL...")
            page.goto(TEST_URL, wait_until="domcontentloaded", timeout=30000)
            
            # Handle cookie popup
            handle_cookie_popup(page)
            
            # Wait for booking widget to fully load - use simpler approach
            print("⏳ Waiting for booking widget to load...")
            print("🔍 Checking for page content...")
            
            # Wait a bit for initial content
            page.wait_for_timeout(5000)
            
            # Try to wait for any booking-related elements
            try:
                print("🔍 Looking for booking elements...")
                page.wait_for_selector('button, a', timeout=10000)  # Wait for any buttons/links
                print("✅ Found interactive elements")
            except:
                print("⚠️ No interactive elements found")
            
            # Additional wait for dynamic content
            print("⏳ Waiting additional 10 seconds for dynamic content...")
            page.wait_for_timeout(10000)
            
            # Save HTML BEFORE scrolling
            html_before = page.content()
            html_before_path = f"test_detection_BEFORE_scroll_{time.strftime('%Y%m%d_%H%M%S')}.html"
            with open(html_before_path, 'w', encoding='utf-8') as f:
                f.write(html_before)
            print(f"💾 HTML before scroll saved: {html_before_path}")
            
            # Scroll gradually to ensure all slots are loaded (lazy loading)
            print("📜 Scrolling gradually to load all slots...")
            page.evaluate("""
                // Scroll gradually to trigger all lazy loading
                let scrollHeight = document.body.scrollHeight;
                let currentScroll = 0;
                let scrollStep = 500; // Scroll 500px at a time
                
                function gradualScroll() {
                    window.scrollTo(0, currentScroll);
                    currentScroll += scrollStep;
                    if (currentScroll < scrollHeight) {
                        setTimeout(gradualScroll, 200); // Wait 200ms between scrolls
                    }
                }
                gradualScroll();
            """)
            page.wait_for_timeout(5000)  # Wait for all scrolling and loading to complete
            
            # Step 3: Take screenshot for reference
            screenshot_path = f"test_detection_screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"
            page.screenshot(path=screenshot_path)
            print(f"📸 Screenshot saved: {screenshot_path}")
            
            # Step 4: Save HTML AFTER scrolling for analysis
            html_content = page.content()
            html_path = f"test_detection_AFTER_scroll_{time.strftime('%Y%m%d_%H%M%S')}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"💾 HTML after scroll saved: {html_path}")
            
            # Compare HTML sizes
            print(f"📊 HTML before scroll: {len(html_before)} characters")
            print(f"📊 HTML after scroll: {len(html_content)} characters")
            if len(html_content) > len(html_before):
                print("✅ More content loaded after scrolling!")
            
            # Step 5: Test our detection logic
            print("\n🔍 Testing detection logic...")
            available_slots = parse_court_availability(html_content)
            
            # Step 6: Display results
            print("\n" + "="*60)
            print("🎾 DETECTION RESULTS")
            print("="*60)
            
            if available_slots:
                print(f"✅ SUCCESS! Found {len(available_slots)} available slot(s):")
                print()
                
                for i, slot in enumerate(available_slots, 1):
                    print(f"Slot {i}:")
                    print(f"  ⏰ Time: {slot['time']}")
                    print(f"  💰 Price: {slot['price']}")
                    print(f"  🏟️ Spaces: {slot['spaces']}")
                    print(f"  🔗 Book URL: {slot['book_url']}")
                    print(f"  📝 Raw text: {slot['raw_text'][:100]}...")
                    print()
                
                print("🎉 Detection logic is working correctly!")
                
            else:
                print("❌ No slots detected - this suggests our detection logic needs improvement")
                print("Let's analyze the HTML to see what patterns we're missing...")
                
                # Look for any text containing "available" or "Book"
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content, "html.parser")
                
                print("\n🔍 Searching for 'available' text in HTML:")
                available_texts = soup.find_all(string=lambda text: text and 'available' in text.lower())
                for text in available_texts[:10]:  # Show first 10 matches
                    print(f"  - {text.strip()}")
                
                print("\n🔍 Searching for 'Book' buttons:")
                book_elements = soup.find_all(['button', 'a'], string=lambda text: text and 'book' in text.lower())
                for element in book_elements[:5]:  # Show first 5 matches
                    print(f"  - {element.name}: {element.get_text().strip()}")
            
            print("="*60)
            
            # Keep browser open for manual inspection
            print("\n👀 Browser will stay open for 30 seconds for manual inspection...")
            page.wait_for_timeout(30000)
            
        except Exception as e:
            print(f"❌ Error during test: {str(e)}")
            
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    test_detection()
