import os
import requests
from dotenv import load_dotenv

# 1. โหลดค่าคอนฟิกจากไฟล์ .env
load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("GITHUB_OWNER")
REPO = os.getenv("GITHUB_REPO")

# 2. ตั้งค่า Endpoint และ Headers สำหรับ GitHub API
url = f"https://api.github.com/repos/{OWNER}/{REPO}/pages"

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28"
}

# 3. กำหนดข้อมูลที่ต้องการส่ง (เลือก build_type เป็น workflow)
data = {
    "source": {
        "branch": "main",
        "path": "/"
    },
    "build_type": "workflow"
}

# 4. ส่งคำสั่ง PUT Request ไปยัง GitHub
if not TOKEN or not OWNER or not REPO:
    print("ERROR: Missing GITHUB_TOKEN, GITHUB_OWNER, or GITHUB_REPO in .env")
    raise SystemExit(1)

try:
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code in (200, 201, 204):
        print("Success: GitHub Pages site configured.")
        if response.text:
            print(response.text)
    elif response.status_code == 409 and 'already enabled' in response.text.lower():
        print("Success: GitHub Pages is already enabled.")
    else:
        print(f"Error: status code {response.status_code}")
        print(response.text)
        raise SystemExit(1)

except Exception as e:
    print(f"Connection error: {e}")
    raise SystemExit(1)
