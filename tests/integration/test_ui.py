import subprocess
import sys
import time


def test_streamlit_ui_starts():
    """Smoke test: ensure Streamlit app runs without crashing immediately."""
    # Start streamlit in a subprocess
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "apps/web/Home.py", "--server.headless=true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        # Give it a few seconds to boot
        time.sleep(5)

        # Check if process is still alive (didn’t crash)
        assert proc.poll() is None, "Streamlit crashed on startup"
    finally:
        proc.terminate()
        proc.wait()