import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from datetime import datetime
import yt_dlp
import time
import os
import re

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROFILE_DIR = os.path.join(BASE_DIR, "chrome_profile")
OUTPUT_DIR  = os.path.join(BASE_DIR, "accounts")

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ── driver ────────────────────────────────────────────────────────────────────

def get_driver():
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    return uc.Chrome(version_main=146, options=options)


def is_logged_in(driver):
    driver.get("https://www.instagram.com/")
    time.sleep(3)
    return "Login" not in driver.title and "Log in" not in driver.page_source[:500]


# ── media download via yt-dlp ─────────────────────────────────────────────────

def download_media(post_url, media_dir, filename_base):
    """
    Downloads media using yt-dlp, reading cookies directly from the Chrome profile.
    Returns (local_path, media_type) or (None, None) on failure.
    """
    out_template = os.path.join(media_dir, f"{filename_base}.%(ext)s")

    ydl_opts = {
        "outtmpl": out_template,
        "quiet": True,
        "no_warnings": True,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        # reads cookies straight from the Chrome profile — no manual export needed
        "cookiesfrombrowser": ("chrome", PROFILE_DIR, None, None),
        "retries": 3,
        "fragment_retries": 3,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(post_url, download=True)

        ext = info.get("ext", "mp4")
        local_path = os.path.join(media_dir, f"{filename_base}.{ext}")

        if not os.path.exists(local_path):
            local_path = os.path.join(media_dir, f"{filename_base}.mp4")

        if not os.path.exists(local_path):
            for fname in os.listdir(media_dir):
                if fname.startswith(filename_base):
                    local_path = os.path.join(media_dir, fname)
                    ext = fname.rsplit(".", 1)[-1]
                    break

        if not os.path.exists(local_path):
            print(f"  [warn] yt-dlp finished but file not found for {post_url}")
            return None, None

        media_type = "video" if ext in ("mp4", "mkv", "webm", "mov") else "image"
        print(f"  [+] Downloaded: {os.path.basename(local_path)}")
        return local_path, media_type

    except yt_dlp.utils.DownloadError as e:
        print(f"  [error] yt-dlp: {e}")
        return None, None
    except Exception as e:
        print(f"  [error] yt-dlp unexpected: {e}")
        return None, None


# ── post URL collection ───────────────────────────────────────────────────────

def collect_post_urls(driver, username):
    driver.get(f"https://www.instagram.com/{username}/")
    time.sleep(5)

    if "Page Not Found" in driver.page_source or "Sorry, this page" in driver.page_source:
        print(f"[!] Profile '{username}' not found.")
        return []

    post_urls = set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    no_new_count = 0

    print(f"[*] Collecting post URLs for @{username} ...")

    while True:
        anchors = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/'], a[href*='/reel/']")
        for a in anchors:
            href = a.get_attribute("href")
            if href:
                href = re.sub(r"\?.*", "", href.rstrip("/")) + "/"
                post_urls.add(href)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            no_new_count += 1
            if no_new_count >= 3:
                break
        else:
            no_new_count = 0
        last_height = new_height

    print(f"[*] Found {len(post_urls)} unique post URLs.")
    return list(post_urls)


# ── single-post scraping ──────────────────────────────────────────────────────

def scrape_post(driver, url):
    driver.get(url)
    time.sleep(4)

    data = {
        "url": url,
        "username": None,
        "caption": None,
        "likes": None,
        "comments": None,
        "date": None,
        "media_type": None,
    }

    # username
    try:
        for a in driver.find_elements(By.CSS_SELECTOR, "a._a6hd, header a[role='link']"):
            t = a.text.strip()
            if t and "/" not in t:
                data["username"] = t
                break
    except Exception as e:
        print(f"  [warn] username: {e}")

    # caption
    for sel in ["span.x126k92a", "h1._ap3a", "div._a9zs span",
                "div[data-testid='post-comment-root'] span"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            text = el.text.strip()
            if text:
                data["caption"] = text
                break
        except Exception:
            pass

    # likes & comments
    try:
        page = driver.page_source
        m = re.search(r'([\d,]+)\s+like', page, re.IGNORECASE)
        if m:
            data["likes"] = m.group(1)
        m = re.search(r'([\d,]+)\s+comment', page, re.IGNORECASE)
        if m:
            data["comments"] = m.group(1)
    except Exception as e:
        print(f"  [warn] likes/comments: {e}")

    if data["likes"] is None:
        try:
            spans = driver.find_elements(By.CSS_SELECTOR, "span.x1ypdohk.x1s688f.x2fvf9.xe9ewy2")
            if spans:
                data["likes"] = spans[0].text
            if len(spans) >= 2:
                data["comments"] = spans[1].text
        except Exception:
            pass

    # date
    try:
        data["date"] = driver.find_element(
            By.CSS_SELECTOR, "time[datetime]"
        ).get_attribute("datetime")
    except Exception:
        pass

    # media type hint
    try:
        driver.find_element(By.CSS_SELECTOR, "video")
        data["media_type"] = "video"
    except Exception:
        data["media_type"] = "image"

    return data


# ── excel helpers ─────────────────────────────────────────────────────────────

HEADERS    = ["URL", "Username", "Caption", "Likes", "Comments",
              "Date", "Media File", "Media Type", "Scraped At"]
COL_WIDTHS = [50, 20, 60, 10, 12, 25, 45, 12, 22]

HEADER_FILL = PatternFill("solid", start_color="1F4E79", end_color="1F4E79")
HEADER_FONT = Font(bold=True, color="FFFFFF", name="Arial")
ROW_FONT    = Font(name="Arial", size=10)
LINK_FONT   = Font(name="Arial", size=10, color="0563C1", underline="single")
ALT_FILL    = PatternFill("solid", start_color="D6E4F0", end_color="D6E4F0")


def excel_path(username):
    return os.path.join(OUTPUT_DIR, f"{username}.xlsx")


def get_media_dir(username):
    path = os.path.join(OUTPUT_DIR, f"{username}-media")
    os.makedirs(path, exist_ok=True)
    return path


def setup_excel(username):
    path = excel_path(username)
    if not os.path.exists(path):
        wb = Workbook()
        ws = wb.active
        ws.title = username[:31]

        for col, (header, width) in enumerate(zip(HEADERS, COL_WIDTHS), 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = HEADER_FILL
            cell.font = HEADER_FONT
            cell.alignment = Alignment(horizontal="center", vertical="center")
            ws.column_dimensions[get_column_letter(col)].width = width

        ws.row_dimensions[1].height = 18
        ws.freeze_panes = "A2"
        wb.save(path)
        print(f"[*] Created {path}")
    else:
        print(f"[*] Appending to {path}")
    return path


def save_to_excel(path, data, local_media_path):
    wb = load_workbook(path)
    ws = wb.active

    row_idx = ws.max_row + 1
    fill = ALT_FILL if row_idx % 2 == 0 else None
    scraped_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row_values = [
        data["url"], data["username"], data["caption"],
        data["likes"], data["comments"], data["date"],
        None,
        data["media_type"], scraped_at,
    ]

    for col, val in enumerate(row_values, 1):
        cell = ws.cell(row=row_idx, column=col, value=val)
        cell.font = ROW_FONT
        cell.alignment = Alignment(vertical="top", wrap_text=(col == 3))
        if fill:
            cell.fill = fill

    media_cell = ws.cell(row=row_idx, column=7)
    if local_media_path:
        media_cell.value = os.path.basename(local_media_path)
        media_cell.hyperlink = local_media_path
        media_cell.font = LINK_FONT
    else:
        media_cell.value = "download failed"
        media_cell.font = ROW_FONT
    if fill:
        media_cell.fill = fill

    wb.save(path)


# ── main loop ─────────────────────────────────────────────────────────────────

driver = get_driver()

if not is_logged_in(driver):
    print("[!] Not logged in — run setup.py first.")
    driver.quit()
    exit()

print("[*] Logged in, using saved session.\n")

while True:
    username = input("Enter Instagram username (or 'exit'): ").strip().lstrip("@")

    if username.lower() == "exit":
        print("[*] Exiting.")
        break

    if not username:
        continue

    urls = collect_post_urls(driver, username)

    if not urls:
        print(f"[!] No posts found for @{username}, skipping.")
        continue

    xl_path = setup_excel(username)
    mdir    = get_media_dir(username)

    for i, url in enumerate(urls, 1):
        print(f"  [{i}/{len(urls)}] {url}")
        try:
            post_data = scrape_post(driver, url)

            shortcode = re.search(r'/(p|reel)/([^/]+)/', url)
            fname_base = shortcode.group(2) if shortcode else f"post_{i}"

            local_path, detected_type = download_media(url, mdir, fname_base)

            if detected_type:
                post_data["media_type"] = detected_type

            save_to_excel(xl_path, post_data, local_path)

        except Exception as e:
            print(f"  [error] {url}: {e}")

        time.sleep(2)

    print(f"[*] Done.")
    print(f"    Excel → {xl_path}")
    print(f"    Media → {mdir}\n")

driver.quit()