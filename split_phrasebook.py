#!/usr/bin/env python3
"""
Split phrasebook_complete.json into topic-based text files for any language.

Usage:
    python3 split_phrasebook.py [language_code]
    
Examples:
    python3 split_phrasebook.py fr
    python3 split_phrasebook.py pt
    python3 split_phrasebook.py es

Supported languages: fr (French), pt (Portuguese), es (Spanish), it (Italian), de (German)
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

# Language configuration
LANGUAGES = {
    'fr': {'name': 'French', 'key': 'french'},
    'pt': {'name': 'Portuguese', 'key': 'portuguese'},
    'es': {'name': 'Spanish', 'key': 'spanish'},
    'it': {'name': 'Italian', 'key': 'italian'},
    'de': {'name': 'German', 'key': 'german'},
}

# Topic file mapping (consistent across all languages)
TOPIC_FILES = {
    "greetings": "01-greetings.txt",
    "farewells": "02-farewells.txt",
    "courtesy": "03-courtesy-basics.txt",
    "introductions": "04-introductions.txt",
    "asking_for_help": "05-asking-for-help.txt",
    "directions": "06-directions.txt",
    "shopping": "07-shopping.txt",
    "restaurant": "08-restaurant.txt",
    "conversation": "09-conversation.txt",
    "feelings": "10-feelings-emotions.txt",
    "exclamations": "11-exclamations.txt",
    "basics": "basics.txt",
}


def split_phrasebook(lang_code):
    """Split phrasebook for a given language."""
    
    # Validate language
    if lang_code not in LANGUAGES:
        print(f"❌ Unknown language code: {lang_code}")
        print(f"   Supported: {', '.join(LANGUAGES.keys())}")
        return False
    
    lang_config = LANGUAGES[lang_code]
    lang_key = lang_config['key']
    lang_name = lang_config['name']
    
    # Check input file exists
    input_file = Path(f'language_materials/{lang_code}/phrasebook_complete.json')
    if not input_file.exists():
        print(f"❌ File not found: {input_file}")
        print(f"   Please create phrasebook_complete.json for {lang_name} first.")
        return False
    
    print(f"📖 Processing {lang_name} phrasebook...")
    print(f"   Source: {input_file}")
    
    # Load phrasebook
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            phrasebook = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {input_file}: {e}")
        return False
    
    if "phrases" not in phrasebook:
        print(f"❌ No 'phrases' key found in {input_file}")
        return False
    
    # Group phrases by situation
    by_situation = defaultdict(list)
    for phrase in phrasebook["phrases"]:
        situation = phrase.get("situation")
        if not situation:
            print(f"   ⚠️  Phrase missing 'situation': {phrase}")
            continue
        
        # Extract fields
        text = phrase.get(lang_key, phrase.get("text", ""))
        english = phrase.get("english", "")
        ipa = phrase.get("ipa", "")
        level = phrase.get("level", "A")
        
        if not text:
            print(f"   ⚠️  Phrase missing '{lang_key}' field: {phrase}")
            continue
        
        by_situation[situation].append({
            "text": text,
            "english": english,
            "ipa": ipa,
            "level": level
        })
    
    # Create output directory
    output_dir = Path(f'language_materials/{lang_code}/phrasebook-topics')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write each topic file
    print(f"\n📝 Creating topic files in {output_dir}/")
    total_phrases = 0
    
    for situation, filename in TOPIC_FILES.items():
        if situation not in by_situation:
            print(f"   ⚠️  No phrases for situation: {situation}")
            continue
        
        phrases = by_situation[situation]
        output_file = output_dir / filename
        
        # Sort by level (A, B, C, D), then by text
        phrases.sort(key=lambda p: (p['level'], p['text']))
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# {lang_name} Phrasebook - {situation.replace('_', ' ').title()}\n")
            f.write(f"# Level distribution: {', '.join(sorted(set(p['level'] for p in phrases)))}\n")
            f.write(f"# Format: {lang_key} | english | [ipa]\n\n")
            
            # Phrases
            for phrase in phrases:
                ipa_str = f"[{phrase['ipa']}]" if phrase['ipa'] else "[ipa]"
                line = f"{phrase['text']} | {phrase['english']} | {ipa_str}\n"
                f.write(line)
        
        total_phrases += len(phrases)
        print(f"   ✓ {filename}: {len(phrases)} phrases")
    
    print(f"\n✅ Complete! {len([s for s in TOPIC_FILES if s in by_situation])} topic files created")
    print(f"📊 Total phrases: {total_phrases}")
    print(f"📍 Location: {output_dir}")
    
    return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 split_phrasebook.py <language_code>")
        print(f"\nSupported languages:")
        for code, config in LANGUAGES.items():
            print(f"  {code} - {config['name']}")
        sys.exit(1)
    
    lang_code = sys.argv[1].lower()
    success = split_phrasebook(lang_code)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
