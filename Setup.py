import subprocess
import sys
import time
import os
import platform

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROFILE_DIR = os.path.join(BASE_DIR, "chrome_profile")

# ── install system dependencies ──────────────────────────────────────────────

print("[*] Checking for ffmpeg...")
try:
    subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print("[+] ffmpeg is already installed.\n")
except (subprocess.CalledProcessError, FileNotFoundError):
    print("[!] ffmpeg not found. Installing...")
    system = platform.system()
    
    if system == "Darwin":  # macOS
        print("[*] Detected macOS. Installing via Homebrew...")
        subprocess.check_call(["brew", "install", "ffmpeg"])
    elif system == "Linux":
        print("[*] Detected Linux. Installing via package manager...")
        # Try to detect package manager
        if os.path.exists("/usr/bin/pacman"):  # Arch
            subprocess.check_call(["sudo", "pacman", "-S", "--noconfirm", "ffmpeg"])
        elif os.path.exists("/usr/bin/apt"):  # Debian/Ubuntu
            subprocess.check_call(["sudo", "apt", "install", "-y", "ffmpeg"])
        elif os.path.exists("/usr/bin/dnf"):  # Fedora
            subprocess.check_call(["sudo", "dnf", "install", "-y", "ffmpeg"])
        else:
            print("[!] Could not detect package manager. Please install ffmpeg manually.")
            sys.exit(1)
    else:
        print("[!] Unsupported OS. Please install ffmpeg manually.")
        sys.exit(1)
    
    print("[+] ffmpeg installed.\n")

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

# ── import after installation ─────────────────────────────────────────────────
import undetected_chromedriver as uc

# ── login ─────────────────────────────────────────────────────────────────────

options = uc.ChromeOptions()
options.add_argument(f"--user-data-dir={PROFILE_DIR}")

driver = uc.Chrome(version_main=146, options=options)
driver.get("https://www.instagram.com/accounts/login/")

print("[*] Browser is open, log in manually.")
print("[*] After logging in press Enter in this terminal...")
input()

driver.quit()
print("[*] Session saved. Run Main.py now.")
