import os
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from io import BytesIO
from PIL import Image

# ----------------------------
# CONFIG
# ----------------------------
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)  # Only one folder for all images

URL = "https://dhankesari.org/"
MAX_IMAGE_DOWNLOADS = 3
MAX_RETRIES = 3

# Get today's date for filenames
today_str = datetime.now().strftime("%Y%m%d")

# ----------------------------
# Remove old images for today (overwrite mode)
# ----------------------------
overwrite_mode = False
for file in os.listdir(IMAGE_DIR):
    if file.startswith(today_str) and file.endswith(".jpg"):
        os.remove(os.path.join(IMAGE_DIR, file))
        overwrite_mode = True
        print(f"🗑️ Removed old file: {file}")

# ----------------------------
# Fetch webpage and images
# ----------------------------
try:
    response = requests.get(URL, timeout=10)
    response.raise_for_status()
except Exception as e:
    print(f"❌ Failed to fetch webpage: {e}")
    sys.exit(0)  # exit gracefully

soup = BeautifulSoup(response.text, "lxml")
img_tags = soup.find_all("img")

# ----------------------------
# Download images
# ----------------------------
downloaded = 0

for img_tag in img_tags:
    if downloaded >= MAX_IMAGE_DOWNLOADS:
        break

    img_url = img_tag.get("src")
    if not img_url or not img_url.lower().endswith(".jpg"):
        continue

    # Normalize image URL
    if img_url.startswith("//"):
        img_url = "https:" + img_url
    elif img_url.startswith("/"):
        img_url = URL.rstrip("/") + img_url

    filename = f"{today_str}_img{downloaded+1}.jpg"
    filepath = os.path.join(IMAGE_DIR, filename)

    attempt = 1
    while attempt <= MAX_RETRIES:
        try:
            img_data = requests.get(img_url, timeout=10)
            img_data.raise_for_status()

            # Validate image
            img_file = BytesIO(img_data.content)
            img = Image.open(img_file)
            img.verify()

            # Save image
            with open(filepath, "wb") as f:
                f.write(img_data.content)

            print(f"✅ Image {downloaded+1} saved as {filename} (attempt {attempt})")
            downloaded += 1
            break

        except Exception as e:
            print(f"❌ Failed on attempt {attempt} for Image {downloaded+1}: {e}")
            attempt += 1
            time.sleep(2)

# ----------------------------
# Summary
# ----------------------------
if downloaded > 0:
    if overwrite_mode:
        print(f"📂 Updated {downloaded} images for {today_str}")
    else:
        print(f"📂 Added {downloaded} images for {today_str}")
else:
    print("⚠️ No images downloaded today.")

sys.exit(0)  # Always success