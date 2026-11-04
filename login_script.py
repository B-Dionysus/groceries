        # await page.fill("input[type='email']", "marianos@sixbynine.com")
        # await page.fill("input[type='password']", "ADIDIEx2m")
import asyncio
from playwright.async_api import async_playwright

async def download_marianos_receipt():
    async with async_playwright() as p:
        print("Launching visible browser with persistent context...")
        
        # 1. Use launch_persistent_context to store cookies and profile data locally
        # 2. Set headless=False so it renders naturally like a standard browser
        context = await p.chromium.launch_persistent_context(
            user_data_dir="./marianos_profile",
            headless=False, 
            viewport={'width': 1280, 'height': 800},
            args=["--disable-http2"] # Keeps connections on reliable HTTP/1.1
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        # Increase connection timeout limits to handle script initialization overhead
        page.set_default_navigation_timeout(60000)
        
        try:
            print("Navigating to Mariano's portal...")
            # Navigate explicitly to the base secure URL string
            await page.goto("https://marianos.com", wait_until="commit")
            
            # Pause to see if it renders or triggers a login check
            await asyncio.sleep(5)
            
            print("Entering credentials...")        
            await page.fill("input[type='email']", "marianos@sixbynine.com")
            await page.fill("input[type='password']", "ADIDIEx2m")
            await page.click("button[type='submit']")
            await page.wait_for_load_state("networkidle")
            
            print("Fetching recent purchases...")
            await page.goto("https://marianos.com", wait_until="networkidle")
            
            # Print snapshot
            await page.pdf(path="marianos_receipt.pdf", format="A4")
            print("Success! Saved to marianos_receipt.pdf")
            
        except Exception as e:
            print(f"An unexpected error occurred during execution: {e}")
            # Take a screenshot to see exactly where it got stuck or what it loaded
            await page.screenshot(path="timeout_diagnostic.png")
            print("Diagnostic screenshot saved to timeout_diagnostic.png")
            
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(download_marianos_receipt())
