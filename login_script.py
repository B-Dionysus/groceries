import os
import time
from playwright.sync_api import sync_playwright

MARIANOS_EMAIL = os.getenv("MARIANOS_EMAIL", "marianos@sixbynine.com")
MARIANOS_PASSWORD = os.getenv("MARIANOS_PASSWORD", "Unpadded~Dedicator~Debrief2")
SESSION_FILE = "marianos_session.json"


def dismiss_popups(page):
    """
    Looks for common dismiss/close buttons with a short timeout.
    If none are found, it silently passes.
    """
    possible_close_buttons = [
        'button[aria-label="Close"]',
        'button[aria-label="Close dialog"]',
        'button.kds-Modal-closeButton',
        'button:has-text("Maybe Later")',
        'button:has-text("Accept All Cookies")',
        'button#onetrust-accept-btn-handler',
    ]

    for selector in possible_close_buttons:
        try:
            # We give each selector just 1.5 seconds so we don't stall execution
            btn = page.locator(selector).first
            if btn.is_visible(timeout=1500):
                print(f"Dismissing popup via: {selector}")
                btn.click()
                page.wait_for_timeout(500)  # Brief pause for the modal animation
        except Exception:
            pass


def login():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-http2"]
        )
        
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = context.new_page()

        print("Navigating to Mariano's sign-in page...")
        page.goto("https://www.marianos.com/signin", wait_until="domcontentloaded")

        # 1. Check and dismiss any initial popup if present
        dismiss_popups(page)

        try:
          try:
            # 1. Wait for the real visible email field (avoiding the honeypot)
            print("Entering email...")
            # We look for #signInName first (standard Azure B2C), or any VISIBLE text/email input
            email_selector = 'input#signInName, input[type="text"]:visible, input[type="email"]:not([aria-hidden="true"])'
            
            email_input = page.locator(email_selector).first
            email_input.wait_for(state="visible", timeout=20000)
            
            email_input.click()
            page.keyboard.type(MARIANOS_EMAIL, delay=60)

            # 2. Wait for the real password field
            print("Entering password...")
            password_selector = 'input#password, input[type="password"]:not([aria-hidden="true"])'
            
            password_input = page.locator(password_selector).first
            password_input.wait_for(state="visible", timeout=10000)
            
            password_input.click()
            page.keyboard.type(MARIANOS_PASSWORD, delay=60)

            # 3. Click the Submit button
            # Azure B2C submit buttons are usually id="next" or type="submit"
            print("Submitting login form...")
            submit_btn = page.locator('button#next, button[type="submit"]:visible').first
            submit_btn.click()

            # 4. Wait for redirection away from the Azure B2C login domain
            print("\nSubmitted! Waiting for redirect back to Mariano's...")
            print("(If a CAPTCHA or 2FA code is requested, complete it in the browser window.)")

            page.wait_for_url(lambda url: "login.kroger.com" not in url, timeout=60000)
            page.wait_for_load_state("networkidle", timeout=10000)

            # 5. Save the session
            context.storage_state(path=SESSION_FILE)
            print(f"\n🎉 SUCCESS! Session saved to {SESSION_FILE}")

          except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(10)

        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(5)
        finally:
            browser.close()


if __name__ == "__main__":
    login()
