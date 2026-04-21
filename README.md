# 📸 Instagram Account Scraper
A research-grade Instagram scraper that extracts all posts from a target account — metadata, captions, likes, dates — and downloads every media file. Built for the **PDID (Profile-based Disinformation Detection)** research pipeline.
---
## ✦ Features
- 🔍 Scrapes **all posts and reels** from any public Instagram account
- 📥 Downloads media (video + audio merged to `.mp4`, images as `.jpg`) via **yt-dlp**
- 📊 Outputs a styled **Excel file per account** with clickable media hyperlinks
- 🔁 Supports **multiple accounts** in a single session
- 💾 Saves everything **locally** next to the script — no hardcoded paths
- 🍪 Reads cookies directly from your Chrome profile — no manual export
---
## 📁 Output Structure
```
Final-Git/
├── Main.py
├── Setup.py
├── requirements.txt
├── .gitignore
├── accounts/
│   ├── username.xlsx          ← scraped metadata + hyperlinks
│   └── username-media/        ← downloaded videos and images
│       ├── ABC123.mp4
│       └── XYZabc.jpg
└── chrome_profile/            ← saved Chrome session (auto-generated)
```
---
## ⚙️ Setup
**1. Clone the repo**
```bash
git clone https://github.com/rayedrah/Insta-nt.git
cd Insta-nt
```
**2. Install dependencies**
```bash
pip install -r requirements.txt --break-system-packages
```
*(Remove `--break-system-packages` if not on Arch Linux)*

**OR use a virtual environment (recommended):**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Run the setup script**
```bash
python Setup.py
```
This will:
- Install all dependencies (`yt-dlp`, `undetected-chromedriver`, `openpyxl`, `requests`)
- Open a Chrome window pointed at Instagram login
- Save your session to `chrome_profile/` for future runs
**4. Log in to Instagram** in the browser window that opens, then press **Enter** in the terminal.
---
## 🚀 Usage
```bash
python Main.py
```
```
Enter Instagram username (or 'exit'): nasa
[*] Collecting post URLs for @nasa ...
[*] Found 248 unique post URLs.
[*] Created accounts/nasa.xlsx
  [1/248] https://www.instagram.com/nasa/reel/ABC123/
  [+] Downloaded: ABC123.mp4
  [2/248] ...
```
You can scrape multiple accounts back to back — just enter the next username when prompted. Type `exit` to quit.
---
## 📦 Dependencies
| Package | Purpose |
|---|---|
| `yt-dlp` | Media download (video + audio) |
| `undetected-chromedriver` | Selenium with bot-detection bypass |
| `openpyxl` | Excel file generation |
| `requests` | HTTP requests |
> All installed automatically by `Setup.py` or via `pip install -r requirements.txt`.
---
## 📋 Excel Output
Each account gets its own `.xlsx` file with the following columns:
| Column | Description |
|---|---|
| URL | Direct link to the post |
| Username | Account handle |
| Caption | Full post caption |
| Likes | Like count |
| Comments | Comment count |
| Date | Post timestamp |
| Media File | Hyperlink to downloaded file |
| Media Type | `video` or `image` |
| Scraped At | Timestamp of scrape |
---
## ⚠️ Notes
- **Chrome must be version 146** — update `version_main=146` in both scripts if your Chrome version differs
- The `chrome_profile/` and `accounts/` folders are excluded from version control via `.gitignore`
- This tool is intended for **academic and research use only**
---
## 🔬 Part of the PDID Pipeline
This scraper is part of the **Profile-based Disinformation Detection (PDID)** project at Purdue University's GRAIL Lab, focused on collecting and analyzing social media content for deepfake and disinformation research.
---
<p align="center">
  Stay Curious ✦ Stay Encrypted
</p>
