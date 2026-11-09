import os
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

MARIANOS_EMAIL = os.getenv("MARIANOS_EMAIL", "marianos@sixbynine.com")
MARIANOS_PASSWORD = os.getenv("MARIANOS_PASSWORD", "Unpadded~Dedicator~Debrief2")
SESSION_FILE = "marianos_session.json"

def dismiss_popups(page):
    """Checks for known Kroger/Mariano's modal close buttons and tries Escape."""
    # 1. Try pressing Escape first (closes most KDS modals instantly)
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)

    # 2. Look for explicit close buttons
    close_selectors = [
        'button[aria-label="Close"]',
        'button[aria-label="Close dialog"]',
        'button.kds-Modal-closeButton',
        'button:has-text("Maybe Later")',
        'button:has-text("Accept All Cookies")',
        'button#onetrust-accept-btn-handler',
        'button[data-testid="close-button"]',
    ]

    for sel in close_selectors:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=1000):
                print(f"Dismissed popup via: {sel}")
                btn.click()
                page.wait_for_timeout(500)
                break
        except Exception:
            pass


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

        # Modern Playwright handler: If ANY modal appears during an action, auto-close it
        modal_close = page.locator('button[aria-label="Close"], button.kds-Modal-closeButton').first
        page.add_locator_handler(modal_close, lambda: modal_close.click())

        print("Navigating to Mariano's...")
        page.goto("https://www.marianos.com/signin", wait_until="domcontentloaded")

        # Give any instant popups a moment to show and dismiss them
        page.wait_for_timeout(2000)
        dismiss_popups(page)

        try:
            # 1. Email input (ignoring hidden honeypot fields)
            print("Locating visible email input...")
            email_selector = 'input#signInName, input[type="text"]:visible, input[type="email"]:not([aria-hidden="true"])'
            email_input = page.locator(email_selector).first
            email_input.wait_for(state="visible", timeout=25000)
            
            # Dismiss again right before clicking in case a delayed popup appeared
            dismiss_popups(page)

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

            # 4. Wait for redirect away from Azure B2C login
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
