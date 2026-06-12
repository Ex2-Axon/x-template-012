#!/usr/bin/env python3
"""
Run the exact automation steps for the current x-template repo.

This script executes the following sequence of actions:
1. Install Node dependencies with pnpm using the local package.json and pnpm-lock.yaml
2. Run github_push.py to commit and push the changes to GitHub
3. Wait 1 minute to allow GitHub Pages to rebuild
4. Run screenshot_template.py to generate a screenshot of the updated page
5. Delete the generated node_modules directory to clean up local dependencies
6. Run copy_image_to_gallery.py to rename and copy the screenshot into gallery/public

File details:
- screenshot_template.py: builds and executes a temporary Playwright script to capture a screenshot of the GitHub Pages URL from .env.
- github_push.py: stages working tree changes, creates a commit, and pushes to the configured GitHub repository using credentials from .env.
- .env: expected to contain GITHUB_OWNER, GITHUB_REPO, and GITHUB_TOKEN for the push step. Optional settings include GITHUB_BRANCH and screenshot options.
- package.json / pnpm-lock.yaml: dependency manifests used by pnpm install.
- node_modules: local dependency folder created by pnpm and removed after screenshot generation.
"""

import shutil
import subprocess
import sys
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
SCREENSHOT_SCRIPT = PROJECT_DIR / "screenshot_template.py"
GITHUB_PUSH_SCRIPT = PROJECT_DIR / "github_push.py"
COPY_IMAGE_SCRIPT = PROJECT_DIR / "copy_image_to_gallery.py"
NODE_MODULES_DIR = PROJECT_DIR / "node_modules"


def resolve_executable(name):
    """Resolve a command from PATH, including Windows .cmd/.exe variants."""
    path = shutil.which(name)
    if path:
        return path
    if sys.platform == "win32":
        for suffix in [".cmd", ".exe", ".ps1"]:
            path = shutil.which(name + suffix)
            if path:
                return path
    raise FileNotFoundError(f"Command not found: {name}")


def load_env(env_path=".env"):
    """Load environment variables from the repo-local .env file."""
    env = {}
    path = PROJECT_DIR / env_path
    if not path.exists():
        return env
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def get_repo_name():
    """Determine the repo name from .env or fallback to the directory name."""
    env = load_env()
    return env.get("GITHUB_REPO", PROJECT_DIR.name)


def run_command(command, cwd=None):
    """Run a command and print stdout/stderr in real time."""
    print(f"\n> Running: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd or PROJECT_DIR)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {result.returncode}: {' '.join(command)}")


def install_dependencies():
    """Step 1: Install Node.js dependencies for the current repo using pnpm."""
    print("Step 1/6: Installing dependencies with pnpm...")
    pnpm_cmd = resolve_executable("pnpm")
    run_command([pnpm_cmd, "install"], cwd=PROJECT_DIR)
    print("✅ Installed dependencies from package.json and pnpm-lock.yaml.")


def push_changes():
    """Step 2: Run github_push.py to commit and push the repo changes."""
    print("\nStep 2/6: Running github_push.py...")
    run_command([sys.executable, str(GITHUB_PUSH_SCRIPT)], cwd=PROJECT_DIR)
    print("✅ GitHub push step completed.")


def take_screenshot():
    """Step 4: Run screenshot_template.py to capture the app screenshot."""
    print("Step 4/6: Running screenshot_template.py...")
    run_command([sys.executable, str(SCREENSHOT_SCRIPT)], cwd=PROJECT_DIR)
    print("Screenshot step completed and screenshot file generated.")


def delay_one_minute():
    """Step 3: Wait 1 minute to allow GitHub Pages to rebuild."""
    print("\nStep 3/6: Waiting 1 minute for GitHub Pages to rebuild...")
    for remaining in range(60, 0, -1):
        print(f"  ⏳ Waiting... {remaining} seconds remaining", end="\r")
        time.sleep(1)
    print("✅ 1 minute delay completed.                             \n")


def remove_node_modules():
    """Step 5: Delete the local node_modules folder to clean up after installation."""
    print("Step 5/6: Removing node_modules...")
    if NODE_MODULES_DIR.exists():
        shutil.rmtree(NODE_MODULES_DIR)
        print("✅ Removed node_modules folder.")
    else:
        print("ℹ️ node_modules folder does not exist; skipping removal.")


def copy_image_to_gallery():
    """Step 6: Run copy_image_to_gallery.py to move screenshot to gallery/public."""
    print("\nStep 6/6: Running copy_image_to_gallery.py...")
    run_command([sys.executable, str(COPY_IMAGE_SCRIPT)], cwd=PROJECT_DIR)
    print("✅ copy_image_to_gallery.py completed.")


def main():
    repo_name = get_repo_name()
    print(f"Starting {repo_name} automated step runner...\n")
    try:
        install_dependencies()        # Step 1: Install with pnpm
        push_changes()                # Step 2: Push to GitHub
        delay_one_minute()            # Step 3: Wait for GitHub Pages rebuild
        take_screenshot()             # Step 4: Take screenshot
        remove_node_modules()         # Step 5: Clean up node_modules
        copy_image_to_gallery()       # Step 6: Copy screenshot to gallery/public
        print("\n✅ All steps completed successfully.")
    except Exception as exc:
        print(f"\n❌ Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
