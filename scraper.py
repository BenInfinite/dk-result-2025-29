import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from io import BytesIO
from PIL import Image
import subprocess

# ----------------------------
# CONFIG
# ----------------------------
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)  # Only one folder for all images

URL = "https://dhankesari.org/"

MAX_IMAGE_DOWNLOADS = 3
MAX_RETRIES = 3

# ----------------------------
# Fetch webpage and images
# ----------------------------
response = requests.get(URL, timeout=10)
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

    if img_url.startswith("//"):
        img_url = "https:" + img_url
    elif img_url.startswith("/"):
        img_url = URL.rstrip("/") + img_url

    filename = f"img{downloaded+1}.jpg"
    filepath = os.path.join(IMAGE_DIR, filename)  # save directly in images/

    attempt = 1
    while attempt <= MAX_RETRIES:
        try:
            # Download
            img_data = requests.get(img_url, timeout=10)
            img_data.raise_for_status()

            # Validate image
            img_file = BytesIO(img_data.content)
            img = Image.open(img_file)
            img.verify()

            # Save locally
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
# Commit & push images to repo
# ----------------------------
if downloaded > 0:
    try:
        subprocess.run(["git", "add", IMAGE_DIR], check=True)
        commit_msg = f"Add {downloaded} images"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"⬆️ {downloaded} images committed and pushed to repo")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git push failed: {e}")

# ----------------------------
# Summary
# ----------------------------
print(f"\n🎉 Summary: {downloaded} images saved locally and pushed to the repo in folder {IMAGE_DIR}")