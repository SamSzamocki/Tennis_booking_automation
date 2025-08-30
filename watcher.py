 #!/usr/bin/env python3
"""
Better/GLL Tennis Court Availability Monitor
Checks for available tennis court slots and sends notifications when found.
"""

import os
import re
import sys
import time
import smtplib
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Load environment variables (override any existing ones)
load_dotenv(override=True)

# Required configuration
BETTER_EMAIL = os.getenv("BETTER_EMAIL")
BETTER_PASSWORD = os.getenv("BETTER_PASSWORD")

# Tennis court locations to monitor
TENNIS_LOCATIONS = [
    {
        "name": "Highbury Tennis",
        "base_url": "https://bookings.better.org.uk/location/islington-tennis-centre/highbury-tennis"
    },
    {
        "name": "Rosemary Gardens Tennis", 
        "base_url": "https://bookings.better.org.uk/location/islington-tennis-centre/rosemary-gardens-tennis"
    }
]

# Optional email notifications
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

# Optional Pushover notifications
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")

# Telegram notification settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8218022688:AAEeVfxC_TKJaMIQW2D9IeN9Vf0LYOe1Sgk")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Validate required environment variables
if not (BETTER_EMAIL and BETTER_PASSWORD):
    print("ERROR: Missing required environment variables:", file=sys.stderr)
    print("Required: BETTER_EMAIL, BETTER_PASSWORD", file=sys.stderr)
    sys.exit(2)


def send_email(subject: str, body: str):
    """Send email notification if SMTP is configured."""
    if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_TO]):
        print("Email notification skipped - SMTP not fully configured")
        return
    
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = EMAIL_TO
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [EMAIL_TO], msg.as_string())
        print("Email notification sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")


def send_telegram(message: str):
    """Send Telegram notification if configured."""
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        print("Telegram notification skipped - TELEGRAM_CHAT_ID not configured")
        print("To get your chat ID, message your bot and visit:")
        print(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates")
        return
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        response = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        })
        if response.status_code == 200:
            print("Telegram notification sent successfully")
        else:
            print(f"Telegram notification failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Failed to send Telegram notification: {e}")


def send_pushover(title: str, message: str):
    """Send Pushover push notification if configured."""
    if not (PUSHOVER_USER_KEY and PUSHOVER_API_TOKEN):
        print("Pushover notification skipped - not configured")
        return
    
    try:
        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": PUSHOVER_API_TOKEN,
                "user": PUSHOVER_USER_KEY,
                "title": title,
                "message": message,
            },
            timeout=10,
        )
        if response.status_code == 200:
            print("Pushover notification sent successfully")
        else:
            print(f"Pushover notification failed: {response.status_code}")
    except Exception as e:
        print(f"Failed to send Pushover notification: {e}")


def get_weekend_dates():
    """Get the dates for this weekend (Friday, Saturday, Sunday)."""
    today = datetime.now()
    
    # Find the Friday of this week (weekday 4)
    days_since_friday = (today.weekday() - 4) % 7
    friday = today - timedelta(days=days_since_friday)
    
    # If it's before Friday, get this week's weekend
    # If it's Friday or later, get this week's weekend
    weekend_dates = []
    for i in range(3):  # Friday (0), Saturday (1), Sunday (2)
        date = friday + timedelta(days=i)
        weekend_dates.append(date.strftime("%Y-%m-%d"))
    
    return weekend_dates

def generate_weekend_urls(base_url):
    """Generate booking URLs for all weekend dates."""
    weekend_dates = get_weekend_dates()
    return [f"{base_url}/{date}/by-time" for date in weekend_dates]

def is_weekend():
    """Check if today is Friday, Saturday, or Sunday."""
    today = datetime.now().weekday()
    return today in [4, 5, 6]  # Friday=4, Saturday=5, Sunday=6


def handle_cookie_popup(page):
    """Handle cookie consent popup if it appears."""
    try:
        # Wait a moment for popup to appear
        page.wait_for_timeout(2000)
        
        # Look for cookie consent buttons
        cookie_selectors = [
            'text="Accept All Cookies"',
            'button:has-text("Accept All Cookies")',
            'text="Accept all cookies"',
            'button:has-text("Accept all cookies")',
            '[data-testid="accept-all-cookies"]',
            '.cookie-accept-all'
        ]
        
        for selector in cookie_selectors:
            try:
                if page.locator(selector).is_visible(timeout=2000):
                    page.click(selector, timeout=3000)
                    print("Accepted cookie consent")
                    page.wait_for_timeout(1000)  # Wait for popup to disappear
                    return True
            except PlaywrightTimeout:
                continue
        
        print("No cookie popup found or already handled")
        return False
        
    except Exception as e:
        print(f"Cookie handling encountered an issue: {e}")
        return False


def login_to_better(page):
    """
    Log into Better/GLL booking system.
    Handles the authentication flow on bookings.better.org.uk
    """
    print("Navigating to Better booking system...")
    page.goto("https://bookings.better.org.uk/", wait_until="domcontentloaded")
    
    # Wait for page to fully load, then handle cookie popup
    print("Waiting for page to load...")
    page.wait_for_timeout(5000)  # Wait 5 seconds for cookie popup to appear
    
    print("Handling cookie popup...")
    handle_cookie_popup(page)
    
    # Look for sign-in link or button
    try:
        # Check if already logged in
        try:
            logout_element = page.locator('text="Log out"').first
            if logout_element.is_visible(timeout=2000):
                print("Already logged in")
                return
        except:
            pass
        
        # Look for login button
        login_selectors = [
            'button:has-text("Log in")',
            'a:has-text("Log in")', 
            'button:has-text("Sign in")',
            'a:has-text("Sign in")',
            '[data-testid="login"]',
            'text="Log in"'
        ]
        
        login_clicked = False
        for selector in login_selectors:
            try:
                element = page.locator(selector).first
                if element.is_visible(timeout=2000):
                    element.click()
                    login_clicked = True
                    print("Clicked login button")
                    break
            except PlaywrightTimeout:
                continue
        
        if not login_clicked:
            raise Exception("Could not find login button")
        
        # Wait for login modal to appear
        page.wait_for_timeout(3000)
        
        # Look for the modal
        modal_selector = '[class*="Modal"]'
        try:
            modal = page.locator(modal_selector).first
            if not modal.is_visible(timeout=3000):
                raise Exception("Login modal did not appear")
            print("Login modal detected")
        except:
            raise Exception("Could not find login modal")
        
        # Fill in username (email) field within modal
        username_selectors = [
            f'{modal_selector} input[name="username"]',
            f'{modal_selector} input[id="username"]',
            f'{modal_selector} input[type="email"]',
            f'{modal_selector} input[name="email"]'
        ]
        
        username_filled = False
        for selector in username_selectors:
            try:
                element = page.locator(selector).first
                if element.is_visible(timeout=3000):
                    element.fill(BETTER_EMAIL)
                    username_filled = True
                    print("Filled username field")
                    break
            except PlaywrightTimeout:
                continue
        
        if not username_filled:
            raise Exception("Could not find username input field in modal")
        
        # Fill in password field within modal
        password_selectors = [
            f'{modal_selector} input[type="password"]',
            f'{modal_selector} input[name="password"]',
            f'{modal_selector} input[id="password"]'
        ]
        
        password_filled = False
        for selector in password_selectors:
            try:
                element = page.locator(selector).first
                if element.is_visible(timeout=3000):
                    element.fill(BETTER_PASSWORD)
                    password_filled = True
                    print("Filled password field")
                    break
            except PlaywrightTimeout:
                continue
        
        if not password_filled:
            raise Exception("Could not find password input field in modal")
        
        # Submit the form within modal
        submit_selectors = [
            f'{modal_selector} button[type="submit"]',
            f'{modal_selector} input[type="submit"]',
            f'{modal_selector} button:has-text("Log in")',
            f'{modal_selector} button:has-text("Sign in")',
            f'{modal_selector} button:has-text("Continue")'
        ]
        
        submitted = False
        for selector in submit_selectors:
            try:
                element = page.locator(selector).first
                if element.is_visible(timeout=2000):
                    element.click()
                    submitted = True
                    print("Clicked submit button")
                    break
            except PlaywrightTimeout:
                continue
        
        if not submitted:
            raise Exception("Could not find submit button in modal")
        
        # Wait for login to complete
        page.wait_for_timeout(5000)
        print("Login completed")
    
    except Exception as e:
        print(f"Login process encountered an issue: {e}")
        print("Continuing anyway - may already be logged in")


def parse_court_availability(html: str):
    """
    Parse the Better booking page HTML to find available tennis court slots.
    Returns list of available slots with their details.
    """
    soup = BeautifulSoup(html, "html.parser")
    available_slots = []
    seen_times = set()  # Track time slots to prevent duplicates
    
    # Method 1: Look for "Book" buttons (most reliable indicator)
    book_buttons = soup.find_all(['button', 'a'], string=re.compile(r'Book', re.IGNORECASE))
    for button in book_buttons:
        # Find the container that holds this booking slot
        container = button.parent
        for _ in range(8):  # Walk up the DOM tree
            if container and container.name:
                container_text = container.get_text()
                
                # Look for time pattern (HH:MM - HH:MM)
                time_match = re.search(r'(\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2})', container_text)
                # Look for price pattern (£X.XX)
                price_match = re.search(r'£\s*(\d+\.?\d*)', container_text)
                # Look for spaces available
                spaces_match = re.search(r'(\d+)\s+spaces?\s+available', container_text, re.IGNORECASE)
                
                if time_match and spaces_match:
                    spaces = int(spaces_match.group(1))
                    if spaces > 0:
                        # Get booking URL
                        book_url = ""
                        if button.name == 'a' and button.get('href'):
                            href = button['href']
                            book_url = href if href.startswith('http') else f"https://bookings.better.org.uk{href}"
                        
                        slot_info = {
                            'time': time_match.group(1),
                            'price': f"£{price_match.group(1)}" if price_match else "",
                            'spaces': spaces,
                            'book_url': book_url,
                            'raw_text': container_text.strip()
                        }
                        
                        # Avoid duplicates using set for efficiency
                        if time_match.group(1) not in seen_times:
                            seen_times.add(time_match.group(1))
                            available_slots.append(slot_info)
                        break
            container = container.parent if container else None
    
    # Method 2: Fallback - Look for text patterns (original method)
    if not available_slots:
        availability_patterns = [
            r"(\d+)\s+spaces?\s+available",  # "1 space available", "3 spaces available"
            r"(\d+)\s+courts?\s+available",  # "1 court available", "2 courts available"
            r"available\s*:\s*(\d+)",        # "available: 2"
            r"(\d+)\s+remaining",            # "2 remaining"
            r"(\d+)\s+spaces?\s+left",       # "1 space left"
            r"Book\s*.*?(\d+)\s+spaces?",    # Near "Book" button with spaces
        ]
    
        # Find all text nodes that might contain availability information
        for text_node in soup.find_all(string=True):
            text = text_node.strip()
            if not text:
                continue
                
            for pattern in availability_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    spaces = int(match.group(1))
                    if spaces > 0:
                        # Find the parent container to extract more details
                        container = text_node.parent
                        
                        # Walk up the DOM to find a larger container with time/price info
                        for _ in range(5):
                            if container and container.name:
                                # Look for time information in this container
                                time_text = ""
                                price_text = ""
                                book_url = ""
                                
                                # Extract time (HH:MM - HH:MM format)
                                time_match = re.search(r'\b(\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2})\b', 
                                                     container.get_text())
                                if time_match:
                                    time_text = time_match.group(1)
                                
                                # Extract price (£X.XX format)
                                price_match = re.search(r'£\s*(\d+\.?\d*)', container.get_text())
                                if price_match:
                                    price_text = f"£{price_match.group(1)}"
                                
                                # Look for booking links
                                for link in container.find_all('a', href=True):
                                    href = link['href']
                                    if '/slot/' in href or 'book' in link.get_text().lower():
                                        if href.startswith('http'):
                                            book_url = href
                                        else:
                                            book_url = f"https://bookings.better.org.uk{href}"
                                        break
                                
                                if time_text:  # Only add if we found time information
                                    slot_info = {
                                        'time': time_text,
                                        'price': price_text,
                                        'spaces': spaces,
                                        'book_url': book_url,
                                        'raw_text': text
                                    }
                                    
                                    # Avoid duplicates using set for efficiency
                                    if time_text not in seen_times:
                                        seen_times.add(time_text)
                                        available_slots.append(slot_info)
                                    break
                            
                            container = container.parent if container else None
    
    return available_slots


def check_location_for_date(page, location, date_str, debug_mode):
    """Check a specific tennis location for availability on a specific date."""
    location_name = location["name"]
    watch_url = f"{location['base_url']}/{date_str}/by-time"
    
    print(f"\n🎾 Checking {location_name} for {date_str}...")
    print(f"URL: {watch_url}")
    
    try:
        # Navigate to the specific court booking page
        page.goto(watch_url, wait_until="domcontentloaded", timeout=30000)
        
        # Handle cookie popup on the booking page if it appears
        handle_cookie_popup(page)
        
        # Wait for booking widget to fully load - use adaptive approach
        print("⏳ Waiting for booking widget to load...")
        
        # Wait a bit for initial content
        page.wait_for_timeout(5000)
        
        # Try to wait for any booking-related elements
        try:
            page.wait_for_selector('button, a', timeout=10000)  # Wait for any buttons/links
            print("✅ Found interactive elements")
        except:
            print("⚠️ No interactive elements found")
        
        # Additional wait for dynamic content
        page.wait_for_timeout(10000)
        
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
        
        # Verification: Check if we're on the right page
        page_title = page.title()
        current_url = page.url
        print(f"Page title: {page_title}")
        print(f"Current URL: {current_url}")
        
        # Take screenshot if in debug mode
        if debug_mode:
            screenshot_path = f"debug_screenshot_{location_name.replace(' ', '_')}_{time.strftime('%Y%m%d_%H%M%S')}.png"
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved: {screenshot_path}")
        
        # Parse the page for available slots
        html_content = page.content()
        
        # Save HTML content if in debug mode
        if debug_mode:
            html_path = f"debug_page_{location_name.replace(' ', '_')}_{time.strftime('%Y%m%d_%H%M%S')}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"Page HTML saved: {html_path}")
        
        available_slots = parse_court_availability(html_content)
        
        return {
            "location": location_name,
            "url": watch_url,
            "slots": available_slots
        }
        
    except Exception as e:
        print(f"Error checking {location_name}: {str(e)}")
        return {
            "location": location_name,
            "url": watch_url,
            "slots": [],
            "error": str(e)
        }


def check_location_all_weekend_dates(page, location, debug_mode):
    """Check a location for all weekend dates and return combined results."""
    weekend_dates = get_weekend_dates()
    all_slots = []
    location_name = location["name"]
    
    for date_str in weekend_dates:
        try:
            result = check_location_for_date(page, location, date_str, debug_mode)
            if result["slots"]:
                # Add date info to each slot
                for slot in result["slots"]:
                    slot["date"] = date_str
                all_slots.extend(result["slots"])
        except Exception as e:
            print(f"Error checking {location_name} for {date_str}: {e}")
    
    return {
        "location": location_name,
        "slots": all_slots,
        "error": None if all_slots else "No slots found for any weekend date"
    }


def main():
    """Main function to check for available tennis courts."""
    # Check if it's weekend (Friday, Saturday, Sunday)
    if not is_weekend():
        print(f"Today is not a weekend day. Exiting.")
        print("This script only runs on Friday, Saturday, and Sunday.")
        return
    
    # Check for debug mode
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    weekend_dates = get_weekend_dates()
    print(f"Starting Better tennis court monitor at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Monitoring {len(TENNIS_LOCATIONS)} locations for weekend dates:")
    print(f"Weekend dates: {', '.join(weekend_dates)}")
    for location in TENNIS_LOCATIONS:
        print(f"  - {location['name']}")
    print(f"Debug mode: {'ON' if debug_mode else 'OFF'}")
    
    with sync_playwright() as playwright:
        # Launch browser (headless for production, set to False for debugging)
        print("🔧 Launching browser...")
        browser = playwright.chromium.launch(headless=not debug_mode)
        print("✅ Browser launched successfully")
        print("🔧 Creating browser context...")
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        print("🔧 Creating new page...")
        page = context.new_page()
        print("✅ Browser setup complete")
        
        try:
            # Step 1: Login to Better
            login_to_better(page)
            
            # Step 2: Check all tennis locations
            all_results = []
            total_slots_found = 0
            
            for location in TENNIS_LOCATIONS:
                result = check_location_all_weekend_dates(page, location, debug_mode)
                all_results.append(result)
                if result["slots"]:
                    total_slots_found += len(result["slots"])
            
            # Step 3: Process results
            if total_slots_found > 0:
                print(f"\n🎾 FOUND {total_slots_found} AVAILABLE SLOT(S) ACROSS {len([r for r in all_results if r['slots']])} LOCATION(S)!")
                
                # Format notification message
                message_parts = ["🎾 Tennis Courts Available at Islington Tennis Centre!\n"]
                
                for result in all_results:
                    if result["slots"]:
                        message_parts.append(f"\n📍 {result['location']}:")
                        for slot in result["slots"]:
                            details = f"📅 {slot.get('date', 'Unknown date')} | ⏰ {slot['time']}"
                            if slot['price']:
                                details += f" | 💰 {slot['price']}"
                            details += f" | 🏟️ {slot['spaces']} spaces"
                            if slot['book_url']:
                                details += f" | 🔗 {slot['book_url']}"
                            message_parts.append(details)
                
                message_parts.append(f"\nChecked at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Add URLs for each location
                message_parts.append("\nBooking pages:")
                for result in all_results:
                    for location in TENNIS_LOCATIONS:
                        if location['name'] == result['location']:
                            weekend_dates = get_weekend_dates()
                            for date in weekend_dates:
                                url = f"{location['base_url']}/{date}/by-time"
                                message_parts.append(f"• {result['location']} ({date}): {url}")
                            break
                
                message = "\n".join(message_parts)
                
                print("\n" + "="*60)
                print(message)
                print("="*60)
                
                # Send notifications via Telegram (split if too long)
                telegram_message = f"🎾 <b>Tennis Courts Available!</b>\n\n{message}"
                
                # Telegram has a 4096 character limit, so split if needed
                if len(telegram_message) > 4000:
                    # Send summary first
                    summary = f"🎾 <b>Tennis Courts Available!</b>\n\n🎾 FOUND {total_slots_found} AVAILABLE SLOT(S) ACROSS {len([r for r in all_results if r['slots']])} LOCATION(S)!\n\nDetailed breakdown in next messages..."
                    send_telegram(summary)
                    
                    # Send each location separately
                    for result in all_results:
                        if result["slots"]:
                            location_message = f"📍 <b>{result['location']}</b>:\n\n"
                            for slot in result["slots"]:
                                details = f"📅 {slot.get('date', 'Unknown date')} | ⏰ {slot['time']}"
                                if slot['price']:
                                    details += f" | 💰 {slot['price']}"
                                details += f" | 🏟️ {slot['spaces']} spaces"
                                if slot['book_url']:
                                    details += f"\n🔗 {slot['book_url']}"
                                location_message += details + "\n\n"
                            
                            # Split location message if still too long
                            if len(location_message) > 4000:
                                # Send slots in batches
                                batch_message = f"📍 <b>{result['location']}</b>:\n\n"
                                for i, slot in enumerate(result["slots"]):
                                    slot_details = f"📅 {slot.get('date', 'Unknown date')} | ⏰ {slot['time']}"
                                    if slot['price']:
                                        slot_details += f" | 💰 {slot['price']}"
                                    slot_details += f" | 🏟️ {slot['spaces']} spaces"
                                    if slot['book_url']:
                                        slot_details += f"\n🔗 {slot['book_url']}"
                                    slot_details += "\n\n"
                                    
                                    if len(batch_message + slot_details) > 3800:
                                        send_telegram(batch_message)
                                        batch_message = f"📍 <b>{result['location']}</b> (continued):\n\n" + slot_details
                                    else:
                                        batch_message += slot_details
                                
                                if batch_message.strip():
                                    send_telegram(batch_message)
                            else:
                                send_telegram(location_message)
                else:
                    send_telegram(telegram_message)
                
                # send_email("🎾 Tennis Courts Available!", message)  # Disabled in favor of Telegram
                # send_pushover("Tennis Courts Available", message)  # Disabled in favor of Telegram
                
                # Exit with code 1 to indicate slots were found (useful for cron alerts)
                sys.exit(1)
            else:
                print(f"\nNo available slots found at any location")
                for result in all_results:
                    status = "✅ Checked" if "error" not in result else f"❌ Error: {result['error']}"
                    print(f"  - {result['location']}: {status}")
                print(f"Check completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                sys.exit(0)
                
        except Exception as e:
            error_msg = f"Error occurred: {str(e)}"
            print(error_msg, file=sys.stderr)
            
            # Optionally send error notifications
            if SMTP_USER and EMAIL_TO:
                send_email("Tennis Monitor Error", f"Error in tennis court monitor:\n\n{error_msg}")
            
            sys.exit(2)
        
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
