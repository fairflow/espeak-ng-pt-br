#!/usr/bin/env python3
"""
Convert French story scenes from Format 1 to Format 2.

Format 1 (old): [{"french": "...", "english": "...", "ipa": "..."}, ...]
Format 2 (new): {"fr": [...], "scene_number": 1, "scene_title": "..."}

This standardizes all story scenes to use the same structured format.
"""

import json
from pathlib import Path
import re


def extract_scene_info(filename):
    """
    Extract scene number and title from filename.
    Example: "scene-01-le-café-du-matin.json" -> (1, "Le Café du Matin")
    """
    stem = Path(filename).stem
    
    # Match pattern: scene-XX-title
    match = re.match(r'scene-(\d+)-(.*)', stem)
    if match:
        scene_num = int(match.group(1))
        # Convert hyphenated title to proper title case
        title = match.group(2).replace('-', ' ').title()
        return scene_num, title
    
    return None, stem


def convert_scene_file(input_path, output_path):
    """Convert a single scene file from Format 1 to Format 2."""
    
    # Read old format
    with open(input_path, 'r', encoding='utf-8') as f:
        old_data = json.load(f)
    
    # Validate it's Format 1 (a list)
    if not isinstance(old_data, list):
        print(f"⚠️  Skipping {input_path.name} - already in Format 2")
        return False
    
    # Extract scene info from filename
    scene_num, scene_title = extract_scene_info(input_path.name)
    
    # Convert to Format 2
    new_data = {
        "fr": [
            {
                "fr": phrase.get("french", ""),
                "english": phrase.get("english", ""),
                "ipa": phrase.get("ipa", "")
            }
            for phrase in old_data
        ],
        "scene_number": scene_num if scene_num else 0,
        "scene_title": scene_title
    }
    
    # Write new format
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    
    phrase_count = len(old_data)
    print(f"✅ Converted {input_path.name}: {phrase_count} phrases")
    return True


def main():
    """Convert all French scene files."""
    
    # Paths
    scenes_dir = Path(__file__).parent.parent / "language_materials" / "fr" / "story-scenes-json"
    
    if not scenes_dir.exists():
        print(f"❌ Error: {scenes_dir} not found")
        return
    
    # Find all scene files
    scene_files = sorted(scenes_dir.glob("scene-*.json"))
    
    if not scene_files:
        print(f"❌ No scene files found in {scenes_dir}")
        return
    
    print(f"📂 Found {len(scene_files)} scene files in {scenes_dir}")
    print(f"🔄 Converting to Format 2...\n")
    
    converted_count = 0
    skipped_count = 0
    
    for scene_file in scene_files:
        if convert_scene_file(scene_file, scene_file):
            converted_count += 1
        else:
            skipped_count += 1
    
    print(f"\n✨ Conversion complete!")
    print(f"   Converted: {converted_count} files")
    if skipped_count > 0:
        print(f"   Skipped: {skipped_count} files (already in Format 2)")
    print(f"\n💡 Next steps:")
    print(f"   1. Test Scene by Scene mode with French")
    print(f"   2. Test Practice Mode with French")
    print(f"   3. Simplify code to remove dual-format handling")
    print(f"   4. Commit changes")


if __name__ == "__main__":
    main()
