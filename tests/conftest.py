"""
Shared fixtures for Playwright end-to-end tests.

Starts a local Shiny app server once per test session so all Playwright tests
can connect to the same running instance.
"""

import subprocess
import time
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PORT = 8765
APP_URL = f"http://127.0.0.1:{APP_PORT}"


@pytest.fixture(scope="session")
def app_server():
    """Launch the Shiny app on a fixed port and shut it down after the session."""
    proc = subprocess.Popen(
        ["python", "-m", "shiny", "run", "--port", str(APP_PORT), "src/app.py"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Allow enough time for the app to load data and bind the port
    time.sleep(30)
    yield APP_URL
    proc.terminate()
    proc.wait(timeout=10)
