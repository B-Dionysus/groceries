        # await page.fill("input[type='email']", "marianos@sixbynine.com")
        # await page.fill("input[type='password']", "ADIDIEx2m")
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def download_marianos_receipt():
    # 1. Initialize the stealth engine wrapper
    async with Stealth().use_async(async_playwright()) as p:
        print("Launching stealth browser context...")
        browser = await p.chromium.launch(
           headless=True,
           args=["--disable-http2"]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # 2. Go to the sign-in page
        print("Navigating to Mariano's sign-in page...")
        await page.goto("https://marianos.com")
        
        # NOTE: Supply your real username and password credentials here
        print("Entering credentials...")        
        await page.fill("input[type='email']", "marianos@sixbynine.com")
        await page.fill("input[type='password']", "ADIDIEx2m")
        await page.click("button[type='submit']")
        await page.wait_for_load_state("networkidle")
        
        # 3. Pull transaction history page
        print("Fetching purchase history dashboard...")
        await page.goto("https://marianos.com")
        await page.wait_for_load_state("networkidle")
        
        # 4. Generate the statement capture
        await page.pdf(path="marianos_receipt.pdf", format="A4")
        print("Success! Captured and saved to marianos_receipt.pdf")
        
        await browser.close()

# Kick off the async loop
if __name__ == "__main__":
    asyncio.run(download_marianos_receipt())
