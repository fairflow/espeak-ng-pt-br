#!/usr/bin/env python3
"""
Automatically add translations and IPA to French word files.

Uses:
- Google Translate API (via deep-translator) for translations
- eSpeak NG for IPA pronunciation

Processes word files and updates [translation needed] and [ipa] placeholders.
"""

import subprocess
import re
from pathlib import Path
from deep_translator import GoogleTranslator

def get_espeak_ipa(word, lang='fr-fr'):
    """Get IPA pronunciation from eSpeak NG."""
    try:
        # Use local build with local data directory
        import os
        env = os.environ.copy()
        env['ESPEAK_DATA_PATH'] = './espeak-ng-data'
        
        result = subprocess.run(
            ['./src/espeak-ng', '-q', '-v', lang, '--ipa', word],
            capture_output=True,
            text=True,
            timeout=5,
            env=env
        )
        if result.returncode == 0:
            ipa = result.stdout.strip()
            # Remove leading/trailing whitespace and newlines
            ipa = ' '.join(ipa.split())
            return f"[{ipa}]" if ipa else "[ipa]"
        return "[ipa]"
    except Exception as e:
        print(f"  ⚠ eSpeak error for '{word}': {e}")
        return "[ipa]"

def get_translation(word, source='fr', target='en'):
    """Get translation using Google Translate."""
    try:
        translator = GoogleTranslator(source=source, target=target)
        translation = translator.translate(word)
        return translation if translation else "[translation needed]"
    except Exception as e:
        print(f"  ⚠ Translation error for '{word}': {e}")
        return "[translation needed]"

def process_word_file(file_path, dry_run=False):
    """Process a word file and add translations and IPA."""
    lines = []
    updates_count = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_stripped = line.strip()
            
            # Keep comments and empty lines as-is
            if not line_stripped or line_stripped.startswith('#'):
                lines.append(line)
                continue
            
            # Parse word line: word | translation | [ipa]
            if '|' in line_stripped:
                parts = [p.strip() for p in line_stripped.split('|')]
                if len(parts) >= 3:
                    word = parts[0]
                    translation = parts[1]
                    ipa = parts[2]
                    
                    updated = False
                    
                    # Update translation if needed
                    if translation == "[translation needed]":
                        new_translation = get_translation(word)
                        translation = new_translation
                        updated = True
                    
                    # Update IPA if needed
                    if ipa == "[ipa]":
                        new_ipa = get_espeak_ipa(word)
                        ipa = new_ipa
                        updated = True
                    
                    if updated:
                        updates_count += 1
                        if not dry_run:
                            print(f"    ✓ {word}: {translation} | {ipa}")
                    
                    lines.append(f"{word} | {translation} | {ipa}\n")
                else:
                    lines.append(line)
            else:
                lines.append(line)
    
    if not dry_run and updates_count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    
    return updates_count

def main():
    base_dir = Path(__file__).parent / "language_materials" / "fr"
    
    if not base_dir.exists():
        print(f"Error: {base_dir} not found")
        return
    
    print("Processing French word files...")
    print("=" * 50)
    
    # Find all word files
    word_files = sorted(base_dir.glob("words-*/words-*.txt"))
    
    if not word_files:
        print("No word files found!")
        return
    
    total_updates = 0
    
    for word_file in word_files:
        print(f"\n{word_file.parent.name}/{word_file.name}:")
        updates = process_word_file(word_file)
        total_updates += updates
        
        if updates == 0:
            print("  ℹ No updates needed (all translations and IPA present)")
    
    print("\n" + "=" * 50)
    print(f"✓ Complete! Updated {total_updates} entries across {len(word_files)} files")

if __name__ == "__main__":
    main()
