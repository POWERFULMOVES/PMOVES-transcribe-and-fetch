import asyncio
import sys
from playwright.async_api import async_playwright

async def main():
    print(f"Running with policy: {asyncio.get_event_loop_policy().__class__.__name__}")
    async with async_playwright() as p:
        browser = None
        try:
            print("Attempting to launch Chromium...")
            browser = await p.chromium.launch()
            print("Chromium launched successfully.")
            await browser.close()
            print("Chromium closed.")
        except Exception as e:
            print(f"Error launching/closing browser: {e}")
            if "Missing browsers" in str(e):
                print("Playwright error suggests browsers might not be installed correctly for this environment.")
                print("Try running: .venv\\Scripts\\activate && python -m playwright install --with-deps")
        finally:
            if browser: # Check if browser object exists
                try:
                    # Check if connected before trying to close, to avoid errors if already closed or failed to connect
                    if browser.is_connected(): # is_connected() is a more reliable check
                        await browser.close()
                        print("Browser closed in finally block.")
                except Exception as close_err:
                    print(f"Error closing browser in finally block: {close_err}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())