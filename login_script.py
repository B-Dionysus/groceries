import os
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth


MARIANOS_EMAIL = os.getenv("MARIANOS_EMAIL", "your-email@example.com")
MARIANOS_PASSWORD = os.getenv("MARIANOS_PASSWORD", "your-password-here")
SESSION_FILE = "marianos_session.json"


def login():
    # Stealth v2 wraps sync_playwright directly
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

        try:
            # 1. Email input (avoiding the honeypot)
            print("Locating visible email input...")
            email_selector = 'input#signInName, input[type="text"]:visible, input[type="email"]:not([aria-hidden="true"])'
            email_input = page.locator(email_selector).first
            email_input.wait_for(state="visible", timeout=25000)
            
            email_input.click()
            time.sleep(0.5)
            page.keyboard.type(MARIANOS_EMAIL, delay=85)
            time.sleep(0.8)

            # 2. Password input
            print("Locating visible password input...")
            password_selector = 'input#password, input[type="password"]:not([aria-hidden="true"])'
            password_input = page.locator(password_selector).first
            password_input.wait_for(state="visible", timeout=10000)
            
            password_input.click()
            time.sleep(0.5)
            page.keyboard.type(MARIANOS_PASSWORD, delay=90)
            time.sleep(1.0)

            # 3. Submit
            print("Submitting login form...")
            submit_btn = page.locator('button#next, button[type="submit"]:visible').first
            submit_btn.click()

            print("\nWaiting for redirect back to Mariano's...")
            print("(If 2FA / SMS verification is requested, complete it in the browser.)")

            # 4. Wait for redirect
            page.wait_for_url(lambda url: "login.kroger.com" not in url, timeout=60000)
            page.wait_for_load_state("networkidle", timeout=10000)

            # 5. Save session state
            context.storage_state(path=SESSION_FILE)
            print(f"\n🎉 SUCCESS! Session saved to {SESSION_FILE}")

        except Exception as e:
            print(f"\nEncountered an issue: {e}")
            print("Keeping browser open for 15 seconds to inspect...")
            time.sleep(15)
        finally:
            browser.close()


if __name__ == "__main__":
    login()
