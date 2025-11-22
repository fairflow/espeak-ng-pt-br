#!/usr/bin/env python3
"""
Add IPA transcriptions to scene JSON files using espeak-ng.
Processes files one at a time.
"""

import os
import json
import subprocess
import sys

def get_ipa(text):
    """Get IPA transcription using local espeak-ng build."""
    try:
        result = subprocess.run(
            ['./src/.libs/espeak-ng', '-v', 'fr-fr', '-q', '--ipa', text],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=2
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception as e:
        print(f"  Error: {e}")
    return ""

def process_json_file(filepath):
    """Add IPA to a JSON file."""
    print(f"\nProcessing: {os.path.basename(filepath)}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated = 0
    for idx, entry in enumerate(data, 1):
        # Process if IPA is missing or empty
        if not entry.get('ipa') or entry.get('ipa') == "":
            french = entry['french']
            ipa = get_ipa(french)
            if ipa:
                entry['ipa'] = ipa
                updated += 1
            if idx % 10 == 0:
                print(f"  {idx}/{len(data)} processed...")
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Updated {updated} IPA entries")
    return updated

def main():
    json_dir = 'language_materials/fr/story-scenes-json'
    
    if not os.path.exists(json_dir):
        print(f"Error: {json_dir} not found")
        return
    
    json_files = sorted([f for f in os.listdir(json_dir) if f.endswith('.json')])
    
    print(f"Found {len(json_files)} JSON files")
    total_updated = 0
    
    for json_file in json_files:
        filepath = os.path.join(json_dir, json_file)
        updated = process_json_file(filepath)
        total_updated += updated
    
    print(f"\n{'='*60}")
    print(f"✓ Complete! Updated {total_updated} IPA entries across {len(json_files)} files")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
