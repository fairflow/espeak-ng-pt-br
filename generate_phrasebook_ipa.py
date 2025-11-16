#!/usr/bin/env python3
"""
Generate IPA transcriptions for phrasebook using eSpeak.

Usage:
    python3 generate_phrasebook_ipa.py <language_code>
    
Examples:
    python3 generate_phrasebook_ipa.py fr
    python3 generate_phrasebook_ipa.py pt
    python3 generate_phrasebook_ipa.py es

Supported languages: fr (French), pt (Portuguese), es (Spanish), it (Italian), de (German), nl (Dutch)

Requirements:
    - espeak command (not espeak-ng)
    - Run in venv if needed: source venv/bin/activate
"""
import json
import sys
import subprocess
from pathlib import Path

# Language configuration
LANGUAGES = {
    'fr': {'name': 'French', 'key': 'french', 'voice': 'fr-fr'},
    'pt': {'name': 'Portuguese', 'key': 'portuguese', 'voice': 'pt-br'},
    'es': {'name': 'Spanish', 'key': 'spanish', 'voice': 'es'},
    'it': {'name': 'Italian', 'key': 'italian', 'voice': 'it'},
    'de': {'name': 'German', 'key': 'german', 'voice': 'de'},
    'nl': {'name': 'Dutch', 'key': 'dutch', 'voice': 'nl'},
}


def get_ipa(text, voice):
    """Get IPA transcription from eSpeak."""
    try:
        result = subprocess.run(
            ['espeak', '-q', '-v', voice, '--ipa', text],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            ipa = result.stdout.strip()
            # Clean up spacing
            ipa = ' '.join(ipa.split())
            return ipa
        return ""
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  Timeout for: {text}")
        return ""
    except FileNotFoundError:
        print(f"❌ espeak command not found. Please install espeak (not espeak-ng)")
        sys.exit(1)
    except Exception as e:
        print(f"  ⚠️  Error for '{text}': {e}")
        return ""


def generate_ipa(lang_code):
    """Generate IPA for all phrases in phrasebook."""
    
    # Validate language
    if lang_code not in LANGUAGES:
        print(f"❌ Unknown language code: {lang_code}")
        print(f"   Supported: {', '.join(LANGUAGES.keys())}")
        return False
    
    lang_config = LANGUAGES[lang_code]
    lang_key = lang_config['key']
    lang_name = lang_config['name']
    voice = lang_config['voice']
    
    # Check input file
    input_file = Path(f'language_materials/{lang_code}/phrasebook_complete.json')
    if not input_file.exists():
        print(f"❌ File not found: {input_file}")
        return False
    
    print(f"🔊 Generating IPA for {lang_name} phrasebook...")
    print(f"   Source: {input_file}")
    print(f"   Voice: {voice}")
    print()
    
    # Load phrasebook
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            phrasebook = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    
    if "phrases" not in phrasebook:
        print(f"❌ No 'phrases' key found")
        return False
    
    # Generate IPA for each phrase
    total = len(phrasebook["phrases"])
    success_count = 0
    
    for i, phrase in enumerate(phrasebook["phrases"], 1):
        text = phrase.get(lang_key, phrase.get("text", ""))
        
        if not text:
            print(f"  ⚠️  Phrase {i} missing '{lang_key}' field")
            continue
        
        # Generate IPA
        ipa = get_ipa(text, voice)
        
        if ipa:
            phrase["ipa"] = ipa
            success_count += 1
            
            # Show progress
            if i % 10 == 0:
                print(f"  Progress: {i}/{total} phrases processed")
            
            # Show samples
            if i % 25 == 0:
                print(f"    Sample: '{text}' → [{ipa}]")
        else:
            print(f"  ⚠️  Failed to generate IPA for: {text}")
            phrase["ipa"] = ""
    
    # Save updated phrasebook
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(phrasebook, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Complete! {success_count}/{total} phrases processed")
    print(f"📊 IPA generated: {success_count}/{total}")
    print(f"💾 Saved to: {input_file}")
    
    return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 generate_phrasebook_ipa.py <language_code>")
        print(f"\nSupported languages:")
        for code, config in LANGUAGES.items():
            print(f"  {code} - {config['name']} (voice: {config['voice']})")
        print("\nNote: Requires 'espeak' command (not espeak-ng)")
        print("      Run in venv if needed: source venv/bin/activate")
        sys.exit(1)
    
    lang_code = sys.argv[1].lower()
    success = generate_ipa(lang_code)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
