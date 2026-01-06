import subprocess
import sys
import webbrowser
import time
import os
import tempfile

LOCK_FILE = os.path.join(tempfile.gettempdir(), "learning_app_browser.lock")


def main():
    # Get directory where the EXE lives
    exe_dir = os.path.dirname(sys.executable)

    # app.py is ONE LEVEL UP from dist/
    app_path = os.path.abspath(os.path.join(exe_dir, "..", "app.py"))

    if not os.path.exists(app_path):
        return  # Fail silently (avoids infinite loops)

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            app_path,
            "--server.port=8501",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=os.path.dirname(app_path),  # IMPORTANT
    )

    time.sleep(4)

    if not os.path.exists(LOCK_FILE):
        webbrowser.open("http://localhost:8501")
        with open(LOCK_FILE, "w"):
            pass

    process.wait()


if __name__ == "__main__":
    main()