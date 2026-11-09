import os
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

MARIANOS_EMAIL = os.getenv("MARIANOS_EMAIL", "marianos@sixbynine.com")
MARIANOS_PASSWORD = os.getenv("MARIANOS_PASSWORD", "Unpadded~Dedicator~Debrief2")
SESSION_FILE = "marianos_session.json"


def login():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-http2",
            ]
        )
        
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/Chicago"
        )
        
        page = context.new_page()

        # Apply stealth patches to mask Playwright
        stealth_sync(page)

        print("Navigating to Mariano's...")
        page.goto("https://www.marianos.com/signin", wait_until="domcontentloaded")

        try:
            # 1. Email input
            print("Locating visible email input...")
            email_selector = 'input#signInName, input[type="text"]:visible, input[type="email"]:not([aria-hidden="true"])'
            email_input = page.locator(email_selector).first
            email_input.wait_for(state="visible", timeout=25000)
            
            # Click and pause briefly like a human
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
            time.sleep(1.0)  # Critical pause before clicking submit

            # 3. Submit
            print("Submitting login form...")
            submit_btn = page.locator('button#next, button[type="submit"]:visible').first
            submit_btn.click()

            print("\nWaiting for redirect back to Mariano's...")
            print("(If 2FA / SMS verification is requested, complete it in the browser.)")

            # Wait until we leave Kroger's login domain
            page.wait_for_url(lambda url: "login.kroger.com" not in url, timeout=60000)
            page.wait_for_load_state("networkidle", timeout=10000)

            # 4. Save session state
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
