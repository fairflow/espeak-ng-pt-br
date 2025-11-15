#!/usr/bin/env python3
"""
Fill [ipa] placeholder tags in language materials with actual IPA from eSpeak NG.

This script:
1. Scans all .txt files in language_materials/
2. Finds lines with format: phrase | translation | [ipa]
3. Calls espeak-ng to generate IPA for the phrase
4. Replaces [ipa] with the actual IPA transcription
5. Backs up original files before modifying
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Language code mapping for eSpeak NG
ESPEAK_LANG_MAP = {
    'pt': 'pt-br',  # Portuguese (Brazilian)
    'fr': 'fr-fr',  # French
    'nl': 'nl',     # Dutch
}

def get_ipa_from_espeak(text: str, lang_code: str, espeak_cmd: str = 'espeak-ng') -> str:
    """
    Get IPA transcription from eSpeak NG.
    
    Args:
        text: The text to transcribe
        lang_code: Language code (pt, fr, nl)
        espeak_cmd: Path to espeak-ng executable
    
    Returns:
        IPA transcription string, or [error] if failed
    """
    espeak_lang = ESPEAK_LANG_MAP.get(lang_code, lang_code)
    
    try:
        # Run espeak-ng with IPA output
        result = subprocess.run(
            [espeak_cmd, '-v', espeak_lang, '-q', '--ipa', text],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            ipa = result.stdout.strip()
            # Remove any whitespace and newlines
            ipa = ' '.join(ipa.split())
            return ipa if ipa else '[empty]'
        else:
            print(f"  ⚠️  eSpeak error for '{text}': {result.stderr}", file=sys.stderr)
            return '[error]'
            
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  Timeout for '{text}'", file=sys.stderr)
        return '[timeout]'
    except FileNotFoundError:
        print("  ❌ espeak-ng not found! Please install eSpeak NG.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"  ⚠️  Error processing '{text}': {e}", file=sys.stderr)
        return '[error]'

def process_file(file_path: Path, lang_code: str, dry_run: bool = False, espeak_cmd: str = 'espeak-ng') -> tuple[int, int]:
    """
    Process a single file, filling [ipa] tags.
    
    Args:
        file_path: Path to the file
        lang_code: Language code (pt, fr, nl)
        dry_run: If True, don't actually modify files
        espeak_cmd: Path to espeak-ng executable
    
    Returns:
        Tuple of (lines_processed, lines_updated)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"  ❌ Error reading {file_path}: {e}", file=sys.stderr)
        return (0, 0)
    
    updated_lines = []
    lines_processed = 0
    lines_updated = 0
    
    # Pattern: phrase | translation | [ipa]
    pattern = re.compile(r'^([^|#]+)\s*\|\s*([^|]+)\s*\|\s*\[ipa\]\s*$')
    
    for line in lines:
        match = pattern.match(line)
        
        if match:
            phrase = match.group(1).strip()
            translation = match.group(2).strip()
            lines_processed += 1
            
            # Get IPA from eSpeak
            ipa = get_ipa_from_espeak(phrase, lang_code, espeak_cmd)
            
            # Replace [ipa] with actual IPA
            new_line = f"{phrase} | {translation} | {ipa}\n"
            updated_lines.append(new_line)
            lines_updated += 1
            
            print(f"  ✓ {phrase[:40]:<40} → {ipa}")
        else:
            # Keep line as-is
            updated_lines.append(line)
    
    # Write updated content (if not dry run and changes were made)
    if not dry_run and lines_updated > 0:
        # Create backup
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        except Exception as e:
            print(f"  ⚠️  Warning: Could not create backup: {e}", file=sys.stderr)
        
        # Write updated file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)
        except Exception as e:
            print(f"  ❌ Error writing {file_path}: {e}", file=sys.stderr)
            return (lines_processed, 0)
    
    return (lines_processed, lines_updated)

def main():
    """Main function to process all language materials."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Fill [ipa] tags in language materials with eSpeak NG IPA transcriptions'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '--lang',
        choices=['pt', 'fr', 'nl', 'all'],
        default='all',
        help='Process only specific language (default: all)'
    )
    
    args = parser.parse_args()
    
    # Find language_materials directory
    script_dir = Path(__file__).parent
    materials_dir = script_dir / 'language_materials'
    
    if not materials_dir.exists():
        print(f"❌ Language materials directory not found: {materials_dir}")
        sys.exit(1)
    
    # Find espeak-ng executable (try local build first)
    espeak_cmd = 'espeak-ng'
    local_espeak = script_dir / 'src' / 'espeak-ng'
    if local_espeak.exists():
        espeak_cmd = str(local_espeak)
        print(f"🔧 Using local eSpeak NG: {local_espeak}")
    else:
        print(f"🔧 Using system eSpeak NG")
    
    print("🔍 Scanning language materials for [ipa] tags...")
    print(f"📂 Directory: {materials_dir}")
    if args.dry_run:
        print("🔬 DRY RUN MODE - No files will be modified")
    print()
    
    # Get language directories to process
    if args.lang == 'all':
        lang_dirs = [d for d in materials_dir.iterdir() if d.is_dir() and d.name in ESPEAK_LANG_MAP]
    else:
        lang_dirs = [materials_dir / args.lang]
    
    total_files = 0
    total_processed = 0
    total_updated = 0
    
    # Process each language
    for lang_dir in sorted(lang_dirs):
        if not lang_dir.exists():
            continue
            
        lang_code = lang_dir.name
        print(f"📚 Processing {lang_code.upper()} materials...")
        
        # Find all .txt files
        txt_files = list(lang_dir.rglob('*.txt'))
        
        if not txt_files:
            print(f"  No .txt files found in {lang_dir}")
            continue
        
        for txt_file in sorted(txt_files):
            # Skip backup files
            if txt_file.suffix == '.bak':
                continue
            
            print(f"\n  📄 {txt_file.relative_to(materials_dir)}")
            
            processed, updated = process_file(txt_file, lang_code, args.dry_run, espeak_cmd)
            
            if processed == 0:
                print(f"     No [ipa] tags found")
            else:
                print(f"     {updated}/{processed} lines updated")
            
            total_files += 1
            total_processed += processed
            total_updated += updated
        
        print()
    
    # Summary
    print("=" * 70)
    print(f"✅ Summary:")
    print(f"   Files processed: {total_files}")
    print(f"   Lines with [ipa]: {total_processed}")
    print(f"   Lines updated: {total_updated}")
    
    if args.dry_run:
        print()
        print("   ℹ️  This was a dry run. Run without --dry-run to apply changes.")
    else:
        print()
        print("   💾 Original files backed up with .bak extension")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
