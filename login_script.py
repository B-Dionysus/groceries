import os
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

MARIANOS_EMAIL = os.getenv("MARIANOS_EMAIL", "marianos@sixbynine.com")
MARIANOS_PASSWORD = os.getenv("MARIANOS_PASSWORD", "Unpadded~Dedicator~Debrief2")
SESSION_FILE = "marianos_session.json"


def login():
    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-http2",
            ]
        )
        
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = context.new_page()

        print("Navigating to Mariano's...")
        page.goto("https://www.marianos.com/signin", wait_until="domcontentloaded")

        # Let the page settle and see if a popup appears
        time.sleep(3)

        # Quick attempt to auto-dismiss common popups
        for selector in [
            'button[aria-label="Close"]',
            'button[aria-label="Close dialog"]',
            'button.kds-Modal-closeButton',
            'button:has-text("Maybe Later")',
            'button#onetrust-accept-btn-handler',
        ]:
            try:
                el = page.locator(selector).first
                if el.is_visible():
                    print(f"Auto-dismissing popup: {selector}")
                    el.click()
                    time.sleep(1)
                    break
            except Exception:
                pass

        try:
            # 1. Email input
            print("Looking for email input...")
            email_selector = 'input#signInName, input[type="text"]:visible, input[type="email"]:not([aria-hidden="true"])'
            email_input = page.locator(email_selector).first
            
            # 20 second timeout: plenty of time to click any popup manually if it's in the way!
            email_input.wait_for(state="visible", timeout=20000)
            
            email_input.click()
            time.sleep(0.3)
            page.keyboard.type(MARIANOS_EMAIL, delay=70)
            time.sleep(0.5)

            # 2. Password input
            print("Looking for password input...")
            password_selector = 'input#password, input[type="password"]:not([aria-hidden="true"])'
            password_input = page.locator(password_selector).first
            password_input.wait_for(state="visible", timeout=10000)
            
            password_input.click()
            time.sleep(0.3)
            page.keyboard.type(MARIANOS_PASSWORD, delay=70)
            time.sleep(0.8)

            # 3. Submit
            print("Submitting login form...")
            submit_btn = page.locator('button#next, button[type="submit"]:visible').first
            submit_btn.click()

            print("\nWaiting for redirect back to Mariano's...")
            page.wait_for_url(lambda url: "login.kroger.com" not in url, timeout=60000)
            page.wait_for_load_state("networkidle", timeout=10000)

            # 4. Save session state
            context.storage_state(path=SESSION_FILE)
            print(f"\n🎉 SUCCESS! Session saved to {SESSION_FILE}")

        except Exception as e:
            print(f"\nStopped: {e}")
            print("Leaving browser open for 20 seconds...")
            time.sleep(20)
        finally:
            browser.close()


if __name__ == "__main__":
    login()
