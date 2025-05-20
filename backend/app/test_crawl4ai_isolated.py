import asyncio
import sys
import json
import logging
import os

# Configure basic logging for the test script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add the project root to sys.path to allow imports like backend.app.crawl4ai_fetcher
# This assumes the script is in backend/app and the project root is two levels up.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from app.crawl4ai_fetcher import fetch_with_crawl4ai
except ImportError as e:
    logging.error(
        f"Failed to import fetch_with_crawl4ai: {e}. "
        f"Current sys.path: {sys.path}. "
        "Make sure you are running this script in an environment where 'backend.app.crawl4ai_fetcher' can be found. "
        "Typically, run from the project root directory (PMOVES-transcribe-and-fetch)."
    )
    sys.exit(1)

async def main_test_crawl4ai():
    test_url = "http://example.com"
    # Minimal parameters. fetch_with_crawl4ai uses .get() with defaults.
    params = {}
    logging.info(f"Attempting to fetch URL: {test_url} with crawl4ai (isolated test)...")
    logging.info(f"Current asyncio event loop policy before fetch: {asyncio.get_event_loop_policy().__class__.__name__}")

    try:
        # fetch_with_crawl4ai is an async generator
        async for event_str in fetch_with_crawl4ai(test_url, params):
            try:
                event = json.loads(event_str)
                logging.info(f"Received event: {event}")
                if event.get("type") == "error":
                    logging.error(f"Error from crawl4ai_fetcher: {event.get('message')}")
                    if event.get("details"):
                        logging.error(f"Details: {event.get('details')}")
                elif event.get("type") == "completed":
                    if event.get("data"):
                        logging.info(f"Fetch successful. Title: {event['data'].get('title')}")
                        # logging.info(f"Content (first 100 chars): {event['data'].get('content', '')[:100]}...")
                    else:
                        logging.warning("Fetch completed event received, but no data field found.")
            except json.JSONDecodeError:
                logging.warning(f"Received non-JSON event string: {event_str}")
            except Exception as e_event_proc:
                logging.error(f"Error processing event: {e_event_proc}", exc_info=True)
                logging.error(f"Problematic event string: {event_str}")

    except NotImplementedError as nie:
        logging.error(f"Caught NotImplementedError: {nie}", exc_info=True)
    except asyncio.CancelledError:
        logging.warning("The crawl4ai fetch operation was cancelled.")
    except Exception as e:
        logging.error(f"An unexpected error occurred during the test: {e}", exc_info=True)
    finally:
        logging.info("Isolated crawl4ai test finished.")

if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            current_policy = asyncio.get_event_loop_policy()
            # Only set the policy if it's not already a Proactor policy.
            if "WindowsProactorEventLoopPolicy" not in current_policy.__class__.__name__:
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                logging.info("Successfully set asyncio.WindowsProactorEventLoopPolicy.")
            else:
                logging.info("asyncio.WindowsProactorEventLoopPolicy or a compatible policy is already set.")
        except Exception as e_policy:
            # Catching RuntimeError if loop is already running, or other errors.
            logging.error(f"Could not set asyncio.WindowsProactorEventLoopPolicy: {e_policy}", exc_info=True)
            logging.info("Proceeding with current event loop policy.")
    
    logging.info(f"Running with Python version: {sys.version.replace(os.linesep, ' ')}")
    logging.info(f"Running on platform: {sys.platform}")
    logging.info(f"Current working directory: {os.getcwd()}")

    asyncio.run(main_test_crawl4ai())
