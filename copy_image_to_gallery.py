#!/usr/bin/env python3
"""
Copy screenshot.png from the current template folder to gallery/public
with the folder name as the new filename.

For example:
- x-template-013/screenshot.png → gallery/public/x-template-013.png
"""

import shutil
import sys
from pathlib import Path


def main():
    # Get the current directory (template folder)
    current_dir = Path(__file__).resolve().parent
    folder_name = current_dir.name
    
    # Source: screenshot.png in current directory
    source_file = current_dir / "screenshot.png"
    if not source_file.exists():
        print(f"❌ Error: {source_file} does not exist")
        sys.exit(1)
    
    # Destination: gallery/public/{folder_name}.png
    gallery_public_dir = current_dir.parent / "gallery" / "public"
    if not gallery_public_dir.exists():
        print(f"❌ Error: {gallery_public_dir} does not exist")
        sys.exit(1)
    
    # New filename based on folder name
    new_filename = f"{folder_name}.png"
    dest_file = gallery_public_dir / new_filename
    
    # Copy the file
    try:
        shutil.copy2(source_file, dest_file)
        print(f"✅ Successfully copied {source_file.name} → {dest_file}")
    except Exception as e:
        print(f"❌ Error copying file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
