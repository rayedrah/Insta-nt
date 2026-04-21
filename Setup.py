import undetected_chromedriver as uc
import subprocess
import sys
import time
import os

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROFILE_DIR = os.path.join(BASE_DIR, "chrome_profile")

# ── install dependencies ──────────────────────────────────────────────────────

print("[*] Installing / updating dependencies...")

deps = [
    "yt-dlp",
    "undetected-chromedriver",
    "openpyxl",
    "requests",
]

for dep in deps:
    print(f"  installing {dep}...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--upgrade", dep, "--break-system-packages", "-q"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

print("[+] All dependencies installed.\n")

# ── login ─────────────────────────────────────────────────────────────────────

options = uc.ChromeOptions()
options.add_argument(f"--user-data-dir={PROFILE_DIR}")

driver = uc.Chrome(version_main=146, options=options)
driver.get("https://www.instagram.com/accounts/login/")

print("[*] Browser is open, log in manually.")
print("[*] After logging in press Enter in this terminal...")
input()

driver.quit()
print("[*] Session saved. Run main.py now.")