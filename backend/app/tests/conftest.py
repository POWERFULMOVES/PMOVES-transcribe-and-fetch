import sys
import os
import tracemalloc

tracemalloc.start()

# Assuming conftest.py is in backend/app/tests/
# Navigate three levels up to reach the project root (c:/Users/russe/Documents/GitHub/PMOVES-transcribe-and-fetch)
# backend/app/tests/ -> backend/app/ -> backend/ -> project_root/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport # Import AsyncClient and ASGITransport for async tests
from fastapi import FastAPI # To type hint fastapi_app

# Assuming your FastAPI app instance is in backend.app.main
# Adjust the import path if your app instance is located elsewhere
from backend.app.main import app as main_fastapi_app # Renamed to avoid conflict with fixture name

@pytest.fixture(scope="session")
def fastapi_app() -> FastAPI:
    """Provides the FastAPI application instance."""
    return main_fastapi_app

@pytest.fixture(scope="session")
def event_loop():
    """
    Handles the event loop for pytest-asyncio.
    This fixture is often provided by pytest-asyncio itself,
    but defining it explicitly can sometimes help with complex setups.
    If pytest-asyncio is managing the loop correctly, this might not be strictly necessary
    but is kept for clarity and to ensure a session-scoped loop.
    """
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
def client():
    """
    Provides a TestClient instance for testing FastAPI endpoints.
    This client is configured to run against the main application.
    It's module-scoped to reuse the client across tests in a module,
    which can be more efficient than creating a new client for every test function.
    """
    # The client fixture implicitly uses the 'fastapi_app' fixture if it's available
    # and TestClient is initialized with it.
    # Let's ensure it explicitly uses the fastapi_app fixture for clarity.
    with TestClient(main_fastapi_app) as c: # Keep using main_fastapi_app directly here for TestClient
        yield c

# If you also need an asynchronous test client for direct async calls (not through TestClient)
# you might define an async fixture like this. However, for most FastAPI testing,
# the synchronous TestClient wrapper around an ASGI app is sufficient and simpler.
@pytest.fixture(scope="module")
async def async_client(fastapi_app: FastAPI): # fastapi_app fixture will be injected here
    """
    Provides an AsyncClient for making asynchronous HTTP requests directly
    to the FastAPI application using an ASGI transport.
    This is useful if you need to test async routes or WebSocket connections
    in a way that TestClient doesn't fully support, or if you prefer
    the httpx.AsyncClient interface.
    """
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        yield ac