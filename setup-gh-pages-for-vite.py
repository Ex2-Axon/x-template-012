import os
import re
import subprocess
import sys
from pathlib import Path


def get_repo_name():
    """Get repository name from current folder name."""
    current_dir = Path.cwd()
    return current_dir.name


def update_vite_config(repo_name):
    """Update vite.config.ts base path to match repo name."""
    vite_config_path = Path("vite.config.ts")
    if not vite_config_path.exists():
        print("⚠️ vite.config.ts not found")
        return False
    
    content = vite_config_path.read_text(encoding="utf-8")
    old_base_pattern = r"base:\s*['\"].*?['\"]"
    new_base = f'base: \'/{repo_name}/\''
    
    if re.search(old_base_pattern, content):
        content = re.sub(old_base_pattern, new_base, content)
        vite_config_path.write_text(content, encoding="utf-8")
        print(f"✅ Updated vite.config.ts base to: /{repo_name}/")
        return True
    else:
        # If base doesn't exist, add it
        plugins_line = "plugins:"
        if plugins_line in content:
            content = content.replace(plugins_line, f"{new_base},\n  plugins:")
            vite_config_path.write_text(content, encoding="utf-8")
            print(f"✅ Added vite.config.ts base: /{repo_name}/")
            return True
    return False


def update_workflow_files():
    """Update workflow files for Node.js 24 compatibility."""
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print("⚠️ Workflow directory not found")
        return False
    
    updated_count = 0
    for workflow_file in workflows_dir.glob("*.yml"):
        content = workflow_file.read_text(encoding="utf-8")
        original_content = content
        
        # Add FORCE_JAVASCRIPT_ACTIONS_TO_NODE24 env
        if "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24" not in content:
            on_section = "on:"
            if on_section in content:
                content = content.replace(
                    on_section,
                    "on:\n\nenv:\n  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: 'true'"
                )
        
        # Update actions from v4 to v5
        action_updates = [
            ("actions/checkout@v4", "actions/checkout@v5"),
            ("actions/setup-node@v4", "actions/setup-node@v5"),
            ("pnpm/action-setup@v4", "pnpm/action-setup@v5"),
            ("actions/upload-pages-artifact@v4", "actions/upload-pages-artifact@v5"),
            ("actions/deploy-pages@v4", "actions/deploy-pages@v5"),
            ("actions/upload-artifact@v4", "actions/upload-artifact@v5"),
        ]
        
        for old, new in action_updates:
            content = content.replace(old, new)
        
        if content != original_content:
            workflow_file.write_text(content, encoding="utf-8")
            print(f"✅ Updated workflow file: {workflow_file.name}")
            updated_count += 1
    
    return updated_count > 0


def get_command(cmd):
    """Get platform-appropriate command (add .cmd on Windows)."""
    if sys.platform == "win32" and not cmd.endswith(".cmd"):
        return f"{cmd}.cmd"
    return cmd


def setup_playwright():
    """Install Playwright and Chromium."""
    pnpm_cmd = get_command("pnpm")
    npx_cmd = get_command("npx")
    
    # Check if package.json exists
    if not Path("package.json").exists():
        print("⚠️ package.json not found, skipping Playwright setup")
        return False
    
    # Check if playwright is installed
    try:
        result = subprocess.run(
            [pnpm_cmd, "list", "playwright"],
            capture_output=True,
            text=True,
            check=False
        )
        if "playwright" in result.stdout:
            print("ℹ️ Playwright is already installed")
        else:
            print("📦 Installing Playwright...")
            subprocess.run([pnpm_cmd, "add", "-D", "playwright"], check=True)
    except Exception as e:
        print(f"⚠️ Error checking Playwright: {e}")
    
    # Install Chromium
    print("📦 Installing Playwright Chromium...")
    try:
        subprocess.run([npx_cmd, "playwright", "install", "chromium"], check=True)
        print("✅ Playwright setup complete")
        return True
    except Exception as e:
        print(f"⚠️ Error installing Chromium: {e}")
        return False


def main():
    print("🚀 Starting GitHub Pages setup script...")
    repo_name = get_repo_name()
    print(f"📂 Repository name detected: {repo_name}")
    
    print("\n--- Step 1: Update vite.config.ts ---")
    update_vite_config(repo_name)
    
    print("\n--- Step 2: Update workflow files ---")
    update_workflow_files()
    
    print("\n--- Step 3: Setup Playwright ---")
    setup_playwright()
    
    print("\n🎉 Setup complete!")


if __name__ == "__main__":
    main()

