#!/usr/bin/env python3
"""
Automatic screenshot taker for x-template projects.
Reads GITHUB_OWNER and GITHUB_REPO from .env,
sets SCREENSHOT_URL environment variable,
and runs an embedded Node/Playwright screenshot script.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent


def load_env_file(env_path=".env"):
    """Load environment variables from .env file."""
    env_vars = {}
    if Path(env_path).exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars


def get_screenshot_url(env_vars):
    """Generate screenshot URL from .env variables."""
    github_owner = env_vars.get("GITHUB_OWNER")
    github_repo = env_vars.get("GITHUB_REPO")
    
    if not github_owner or not github_repo:
        raise ValueError("Missing GITHUB_OWNER or GITHUB_REPO in .env file")
    
    return f"https://{github_owner}.github.io/{github_repo}/"


def get_screenshot_options(env_vars):
    output = env_vars.get("SCREENSHOT_OUTPUT", "screenshot.png")
    full_page = env_vars.get("SCREENSHOT_FULL_PAGE", "false").lower() != "false"
    delay_ms = int(env_vars.get("SCREENSHOT_DELAY_MS", "3000"))
    return output, full_page, delay_ms


def resolve_executable(name):
    """Find a command on PATH, including Windows variants."""
    path = shutil.which(name)
    if path:
        return path
    if sys.platform == "win32":
        for suffix in [".cmd", ".exe", ".ps1"]:
            path = shutil.which(name + suffix)
            if path:
                return path
    raise FileNotFoundError(f"Command not found: {name}")


def install_playwright_if_missing():
    """Install Playwright locally if it is not already installed."""
    node_modules = PROJECT_DIR / "node_modules"
    playwright_dir = node_modules / "playwright"
    if playwright_dir.exists():
        return

    print("⚠️ Playwright not found locally. Installing playwright...")
    pnpm = resolve_executable("pnpm")
    result = subprocess.run([pnpm, "install", "playwright"], cwd=PROJECT_DIR)
    if result.returncode != 0:
        raise RuntimeError("Failed to install playwright. Please run pnpm install manually.")


def build_screenshot_script(url, output, full_page, delay_ms):
    return f"""import {{ chromium }} from 'playwright';

const url = {json.dumps(url)};
const output = {json.dumps(output)};
const fullPage = {json.dumps(full_page)};
const delayMs = {delay_ms};

(async () => {{
  const browser = await chromium.launch();
  const page = await browser.newPage({{ viewport: {{ width: 1600, height: 900 }} }});
  console.log(`Navigating to ${{url}}`);
  await page.goto(url, {{ waitUntil: 'networkidle' }});
  if (delayMs > 0) {{
    console.log(`Waiting ${{delayMs}}ms for animations/load before screenshot`);
    await page.waitForTimeout(delayMs);
  }}
  await page.screenshot({{ path: output, fullPage }});
  await browser.close();
  console.log(`Screenshot saved to ${{output}}`);
}})().catch(error => {{
  console.error(error);
  process.exit(1);
}});
"""


def run_screenshot():
    env_vars = load_env_file()
    try:
        screenshot_url = get_screenshot_url(env_vars)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    output, full_page, delay_ms = get_screenshot_options(env_vars)
    repo_name = env_vars.get("GITHUB_REPO", "unknown")

    print(f"📸 Taking screenshot for: {repo_name}")
    print(f"🌐 URL: {screenshot_url}")

    install_playwright_if_missing()

    env = os.environ.copy()
    env.update(env_vars)
    env["SCREENSHOT_URL"] = screenshot_url

    script = build_screenshot_script(screenshot_url, output, full_page, delay_ms)

    temp_dir = Path.cwd()
    with tempfile.NamedTemporaryFile(
        "w",
        suffix=".mjs",
        delete=False,
        encoding="utf-8",
        dir=temp_dir,
        prefix="screenshot_temp_",
    ) as temp_file:
        temp_file.write(script)
        temp_path = Path(temp_file.name)

    try:
        result = subprocess.run(
            ["node", str(temp_path)],
            env=env,
            cwd=Path.cwd(),
        )
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("❌ Error: Node.js not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running screenshot: {e}")
        sys.exit(1)
    finally:
        try:
            Path(temp_path).unlink()
        except Exception:
            pass


if __name__ == "__main__":
    run_screenshot()
