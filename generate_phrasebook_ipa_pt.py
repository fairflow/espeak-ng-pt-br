#!/usr/bin/env python3
"""
Generate IPA transcriptions for Portuguese phrasebook using eSpeak.
"""
import json
import subprocess
import os
from pathlib import Path

# Set eSpeak NG data path
os.environ['ESPEAK_DATA_PATH'] = '/Users/matthew/Software/working/adaptive-text/espeak-ng/espeak-ng-data'

def get_ipa(text, voice='pt-br'):
    """Get IPA transcription from eSpeak."""
    try:
        result = subprocess.run(
            ['espeak', '-v', voice, '-q', '--ipa', text],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip().replace('_', '').replace('\n', ' ')
        return ""
    except Exception as e:
        print(f"Error getting IPA for '{text}': {e}")
        return ""

def main():
    # Load Portuguese phrasebook
    input_file = Path('language_materials/pt/phrasebook_complete.json')
    print(f"Loading {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        phrasebook = json.load(f)
    
    # Generate IPA for all phrases
    print("Generating IPA transcriptions using eSpeak pt-br...")
    total = len(phrasebook["phrases"])
    
    for i, phrase in enumerate(phrasebook["phrases"], 1):
        portuguese = phrase["portuguese"]
        phrase["ipa"] = get_ipa(portuguese, voice='pt-br')
        
        if i % 10 == 0:
            print(f"  {i}/{total} processed")
        if i % 25 == 0:
            print(f"    Sample: '{portuguese}' → [{phrase['ipa']}]")
    
    # Save
    output_file = Path('language_materials/pt/phrasebook_complete.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(phrasebook, f, ensure_ascii=False, indent=2)
    
    # Stats
    has_ipa = sum(1 for p in phrasebook["phrases"] if p["ipa"])
    print(f"\n✅ Complete! {total} phrases processed")
    print(f"📍 Location: {output_file}")
    print(f"📊 IPA generated: {has_ipa}/{total}")
    
    if has_ipa < total:
        print(f"⚠️  {total - has_ipa} phrases missing IPA")

if __name__ == '__main__':
    main()
