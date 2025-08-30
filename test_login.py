#!/usr/bin/env python3
"""
Test script to debug the login process specifically
"""

import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Load environment variables
load_dotenv()

BETTER_EMAIL = os.getenv("BETTER_EMAIL")
BETTER_PASSWORD = os.getenv("BETTER_PASSWORD")

def test_login_detailed():
    """Test the login process with detailed debugging."""
    print(f"🔐 Testing Better login process")
    print(f"Email: {BETTER_EMAIL}")
    print(f"Password: {'*' * len(BETTER_PASSWORD) if BETTER_PASSWORD else 'NOT SET'}")
    print("="*80)
    
    if not BETTER_EMAIL or not BETTER_PASSWORD:
        print("❌ ERROR: Email or password not set in .env file!")
        return
    
    with sync_playwright() as playwright:
        # Launch browser in visible mode
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = context.new_page()
        
        try:
            print("🌐 Step 1: Navigate to Better homepage...")
            page.goto("https://bookings.better.org.uk/", wait_until="domcontentloaded")
            
            # Take screenshot of homepage immediately
            page.screenshot(path="login_test_1_homepage.png")
            print("📸 Screenshot: login_test_1_homepage.png")
            
            print("⏳ Step 2: Wait for page to fully load...")
            page.wait_for_timeout(5000)  # Wait 5 seconds for cookie popup
            
            print("🍪 Step 3: Check for cookie popup...")
            cookie_handled = False
            
            # Look for cookie consent buttons
            cookie_selectors = [
                'text="Accept All Cookies"',
                'button:has-text("Accept All Cookies")',
                'text="Accept all cookies"',
                'button:has-text("Accept all cookies")',
                '[data-testid="accept-all-cookies"]',
                '.cookie-accept-all',
                'button:has-text("Accept")'
            ]
            
            for selector in cookie_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=3000):
                        print(f"✅ Found cookie button: {selector}")
                        element.click()
                        cookie_handled = True
                        print("🍪 Accepted cookies")
                        page.wait_for_timeout(2000)  # Wait for popup to disappear
                        break
                except Exception as e:
                    print(f"❌ Cookie selector {selector} failed: {e}")
            
            if not cookie_handled:
                print("ℹ️ No cookie popup found")
            
            # Take screenshot after cookie handling
            page.screenshot(path="login_test_2_after_cookies.png")
            print("📸 Screenshot: login_test_2_after_cookies.png")
            
            print("🔍 Step 4: Look for login elements...")
            
            # Check if already logged in
            try:
                logout_element = page.locator('text="Log out"').first
                if logout_element.is_visible(timeout=2000):
                    print("✅ Already logged in!")
                    return
            except:
                pass
            
            # Look for login button/link
            login_selectors = [
                'button:has-text("Log in")',
                'a:has-text("Log in")', 
                'button:has-text("Sign in")',
                'a:has-text("Sign in")',
                '[data-testid="login"]',
                '.login-button',
                'text="Log in"'
            ]
            
            login_clicked = False
            for selector in login_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        print(f"✅ Found login element: {selector}")
                        element.click()
                        login_clicked = True
                        print("🖱️ Clicked login button")
                        break
                except Exception as e:
                    print(f"❌ Selector {selector} failed: {e}")
            
            if not login_clicked:
                print("❌ Could not find login button!")
                page.screenshot(path="login_test_3_no_login_button.png")
                return
            
            # Wait for login page/modal to load
            print("⏳ Step 5: Waiting for login page to load...")
            page.wait_for_timeout(3000)
            
            # Debug: Check if URL changed (navigation occurred)
            new_url = page.url
            if new_url != "https://bookings.better.org.uk/":
                print(f"✅ Navigation occurred to: {new_url}")
            else:
                print("ℹ️ Still on homepage - checking for modal/popup...")
                
                # Look for modal containers
                modal_selectors = [
                    '[role="dialog"]',
                    '.modal',
                    '.popup',
                    '.login-modal',
                    '.auth-modal',
                    '[data-testid*="modal"]',
                    '[class*="Modal"]'
                ]
                
                modal_found = False
                for selector in modal_selectors:
                    try:
                        modal = page.locator(selector).first
                        if modal.is_visible(timeout=1000):
                            print(f"✅ Found modal: {selector}")
                            modal_found = True
                            break
                    except:
                        continue
                
                if not modal_found:
                    print("❌ No modal found - login button may not have worked")
            
            page.screenshot(path="login_test_4_after_login_click.png")
            print("📸 Screenshot: login_test_4_after_login_click.png")
            
            print("🔍 Step 6: Look for email field...")
            
            # Debug: Print current URL and page title
            current_url = page.url
            page_title = page.title()
            print(f"🔍 Current URL: {current_url}")
            print(f"🔍 Page title: {page_title}")
            
            # Look for input fields WITHIN the modal
            modal_selector = '[class*="Modal"]'
            modal_inputs = page.locator(f'{modal_selector} input').all()
            print(f"🔍 Found {len(modal_inputs)} input fields in modal")
            for i, input_field in enumerate(modal_inputs):
                try:
                    input_type = input_field.get_attribute('type') or 'text'
                    input_name = input_field.get_attribute('name') or 'no-name'
                    input_id = input_field.get_attribute('id') or 'no-id'
                    input_placeholder = input_field.get_attribute('placeholder') or 'no-placeholder'
                    print(f"  Modal Input {i+1}: type='{input_type}', name='{input_name}', id='{input_id}', placeholder='{input_placeholder}'")
                except:
                    print(f"  Modal Input {i+1}: Could not get attributes")
            
            # Try to find email/username field WITHIN the modal
            email_selectors = [
                f'{modal_selector} input[name="username"]',  # This is what we found!
                f'{modal_selector} input[id="username"]',    # This too!
                f'{modal_selector} input[type="email"]',
                f'{modal_selector} input[name="email"]',
                f'{modal_selector} input[name="Email"]',
                f'{modal_selector} input[id*="email"]',
                f'{modal_selector} input[id*="Email"]',
                f'{modal_selector} input[placeholder*="email"]',
                f'{modal_selector} input[placeholder*="Email"]',
                f'{modal_selector} input[placeholder*="E-mail"]',
                f'{modal_selector} input[placeholder*="username"]',
                f'{modal_selector} input[placeholder*="Username"]',
                f'{modal_selector} input[data-testid*="email"]',
                f'{modal_selector} input[class*="email"]',
                # Also try without modal scope as fallback
                'input[type="email"]',
                'input[name="email"]',
                'input[name="username"]',
                'input[placeholder*="email"]'
            ]
            
            email_filled = False
            for selector in email_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=3000):
                        print(f"✅ Found email field: {selector}")
                        element.fill(BETTER_EMAIL)
                        email_filled = True
                        print(f"✏️ Filled email: {BETTER_EMAIL}")
                        break
                except Exception as e:
                    print(f"❌ Email selector {selector} failed: {e}")
            
            if not email_filled:
                print("❌ Could not find email field!")
                page.screenshot(path="login_test_5_no_email_field.png")
                return
            
            print("🔍 Step 7: Look for password field...")
            
            # Try to find password field WITHIN the modal
            password_selectors = [
                f'{modal_selector} input[type="password"]',
                f'{modal_selector} input[name="password"]',
                f'{modal_selector} input[id*="password"]',
                # Also try without modal scope as fallback
                'input[type="password"]',
                'input[name="password"]',
                'input[id*="password"]'
            ]
            
            password_filled = False
            for selector in password_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=3000):
                        print(f"✅ Found password field: {selector}")
                        element.fill(BETTER_PASSWORD)
                        password_filled = True
                        print("✏️ Filled password: ********")
                        break
                except Exception as e:
                    print(f"❌ Password selector {selector} failed: {e}")
            
            if not password_filled:
                print("❌ Could not find password field!")
                page.screenshot(path="login_test_6_no_password_field.png")
                return
            
            page.screenshot(path="login_test_7_form_filled.png")
            print("📸 Screenshot: login_test_7_form_filled.png")
            
            print("🔍 Step 8: Submit form...")
            
            # Try to submit WITHIN the modal
            submit_selectors = [
                f'{modal_selector} button[type="submit"]',
                f'{modal_selector} input[type="submit"]',
                f'{modal_selector} button:has-text("Log in")',
                f'{modal_selector} button:has-text("Sign in")',
                f'{modal_selector} button:has-text("Continue")',
                # Also try without modal scope as fallback
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Log in")',
                'button:has-text("Sign in")',
                'button:has-text("Continue")'
            ]
            
            submitted = False
            for selector in submit_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        print(f"✅ Found submit button: {selector}")
                        element.click()
                        submitted = True
                        print("🖱️ Clicked submit button")
                        break
                except Exception as e:
                    print(f"❌ Submit selector {selector} failed: {e}")
            
            if not submitted:
                print("❌ Could not find submit button!")
                page.screenshot(path="login_test_8_no_submit.png")
                return
            
            # Wait for login to complete
            print("⏳ Waiting for login to complete...")
            page.wait_for_timeout(5000)
            
            page.screenshot(path="login_test_9_after_submit.png")
            print("📸 Screenshot: login_test_9_after_submit.png")
            
            # Check if login was successful
            try:
                logout_element = page.locator('text="Log out"').first
                if logout_element.is_visible(timeout=3000):
                    print("🎉 LOGIN SUCCESSFUL!")
                else:
                    print("❌ Login may have failed - no logout button found")
            except:
                print("❌ Login verification failed")
            
            # Keep browser open for inspection
            print("👀 Browser staying open for 30 seconds for inspection...")
            page.wait_for_timeout(30000)
            
        except Exception as e:
            print(f"❌ Error during login test: {str(e)}")
            page.screenshot(path="login_test_error.png")
            
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    test_login_detailed()