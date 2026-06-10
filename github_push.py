import os
import subprocess
import sys
from pathlib import Path

# ป้องกันปัญหา UnicodeEncodeError ใน Windows CMD
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def load_env():
    """โหลดข้อมูลจาก .env (ค้นหาในโฟลเดอร์ปัจจุบันก่อน แล้วค่อยขยับไปโฟลเดอร์แม่)"""
    env = {}
    search_paths = [Path(__file__).parent / ".env", Path(__file__).parent.parent / ".env"]
    for p in search_paths:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        env[k.strip()] = v.strip().strip('"').strip("'")
            return env
    return None

def run_git_push():
    """ขั้นตอนการ Push งานขึ้น GitHub"""
    print("🚀 Starting GitHub Push Process...")
    env = load_env()
    if not env:
        print("❌ Error: .env file not found.")
        return

    token = env.get("GITHUB_TOKEN")
    owner = env.get("GITHUB_OWNER")
    repo = env.get("GITHUB_REPO")
    branch = env.get("GITHUB_BRANCH", "main")
    
    if not all([token, owner, repo]):
        print("❌ Error: Missing GITHUB_TOKEN, GITHUB_OWNER, or GITHUB_REPO in .env")
        return

    # สร้าง Remote URL ที่มี Token สำหรับ Auth อัตโนมัติ
    remote_url = f"https://{token}@github.com/{owner}/{repo}.git"
    
    # 1. Add
    print("📦 Adding changes...")
    subprocess.run("git add .", shell=True, cwd=str(Path(__file__).parent))
    
    # 2. Commit
    print("📝 Creating commit...")
    commit_msg = f"Automation Update: {subprocess.check_output('date /t', shell=True).decode().strip()} {subprocess.check_output('time /t', shell=True).decode().strip()}"
    subprocess.run(f'git commit -m "{commit_msg}"', shell=True, cwd=str(Path(__file__).parent))
    
    # 3. Push
    print(f"📤 Pushing to {branch}...")
    result = subprocess.run(f"git push {remote_url} {branch} --force", shell=True, cwd=str(Path(__file__).parent))
    
    if result.returncode == 0:
        print("✅ Push successful!")
    else:
        print("❌ Push failed.")

if __name__ == "__main__":
    run_git_push()
