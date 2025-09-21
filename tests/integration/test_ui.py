"""
test_ui.py

Purpose:
--------
Smoke test to ensure the Streamlit app starts without crashing.
This does not validate UI functionality, only that the app 
boots successfully for each supported domain.
"""

import subprocess
import sys
import time
import pytest


@pytest.mark.parametrize("domain", ["supermarket", "pharmacy"])
def test_streamlit_ui_starts(domain):
    """Ensure Streamlit app runs without crashing immediately."""
    # Start streamlit in a subprocess with DOMAIN env var
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m", "streamlit", "run", "app/streamlit_app.py",
            "--server.headless=true",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**dict(**{**{}}, DOMAIN=domain), **dict()},  # minimal env, inject DOMAIN
    )

    try:
        # Give it a few seconds to boot
        time.sleep(3)

        # Check if process is still alive (didn’t crash)
        assert proc.poll() is None, f"Streamlit crashed on startup for domain={domain}"
    finally:
        proc.terminate()
        proc.wait(timeout=5)