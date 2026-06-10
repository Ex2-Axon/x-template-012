"""fix_env.py

This script updates the GITHUB_REPO variable in the project's .env file.
It uses the name of the current repository folder (the parent folder of this script)
as the new value for GITHUB_REPO.

Example usage:
    python fix_env.py

This is useful when the local folder name should match the GitHub repository name
stored in the environment configuration.
"""

from __future__ import annotations

import re
from pathlib import Path


def update_github_repo(env_path: Path) -> None:
    """Update the GITHUB_REPO value in the specified .env file.

    Args:
        env_path: Path to the .env file to update.

    Behavior:
        - If the .env file contains a GITHUB_REPO line, update its value.
        - If the line does not exist, append it to the end of the file.
        - Preserve existing content and line endings as much as possible.
    """
    if not env_path.exists():
        raise FileNotFoundError(f"Env file not found: {env_path}")

    # Use the folder name containing this script as the new repository name.
    current_repo = env_path.parent.name

    # Read the existing .env content so we can update or append the value.
    content = env_path.read_text(encoding="utf-8")

    # Match a line beginning with GITHUB_REPO=, allowing optional spaces around '='.
    pattern = re.compile(r"^(GITHUB_REPO\s*=\s*).*$", re.MULTILINE)

    if pattern.search(content):
        # Replace existing GITHUB_REPO value with the current folder name.
        content = pattern.sub(rf"\1{current_repo}", content)
    else:
        # Append the GITHUB_REPO setting if it does not already exist.
        if not content.endswith("\n"):
            content += "\n"
        content += f"GITHUB_REPO={current_repo}\n"

    # Write the updated content back to the .env file.
    env_path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    # Locate the .env file in the same folder as this script.
    env_file = Path(__file__).resolve().parent / ".env"

    update_github_repo(env_file)

    # Output a confirmation message including the new repo value.
    print(f"Updated {env_file} -> GITHUB_REPO={env_file.parent.name}")
