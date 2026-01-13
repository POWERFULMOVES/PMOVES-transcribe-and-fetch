
import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))

from app.main import app, allowed_origins

print("--- DEBUG CORS CONFIGURATION ---")
print(f"Allowed Origins Variable: {allowed_origins}")

print("\n--- MIDDLEWARE CONFIG ---")
for middleware in app.user_middleware:
    print(f"Middleware: {middleware.cls.__name__}")
    if middleware.options:
        print(f"Options: {middleware.options}")

print("\n--- END DEBUG ---")
