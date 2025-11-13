#!/usr/bin/env python3
"""
Populate translations and IPA for all supported languages.

This script:
1. Processes phrase files to extract unique words
2. Adds translations using Google Translate
3. Adds IPA pronunciations using eSpeak NG

Supports multiple languages with language-specific configurations.
"""

import subprocess
import re
import os
from pathlib import Path
from deep_translator import GoogleTranslator

# Language configurations
LANGUAGES = {
    'fr': {
        'name': 'French',
        'espeak_voice': 'fr-fr',
        'translate_target': 'en',
        'common_words': {
            # Add common words with manual translations for better quality
            'allons': "let's go / we go",
            'bon': 'good',
            'merci': 'thank you',
            # ... etc
        }
    },
    'pt': {
        'name': 'Portuguese',
        'espeak_voice': 'pt-br',
        'translate_target': 'en',
        'common_words': {
            'obrigado': 'thank you (m)',
            'obrigada': 'thank you (f)',
            'bom': 'good',
            'sim': 'yes',
            'não': 'no',
            # ... etc
        }
    },
    'nl': {
        'name': 'Dutch',
        'espeak_voice': 'nl',
        'translate_target': 'en',
        'common_words': {}
    }
}


def get_espeak_ipa(word, lang_config):
    """Get IPA pronunciation from eSpeak NG."""
    try:
        env = os.environ.copy()
        env['ESPEAK_DATA_PATH'] = '../espeak-ng-data'
        
        result = subprocess.run(
            ['../src/espeak-ng', '-q', '-v', lang_config['espeak_voice'], '--ipa', word],
            capture_output=True,
            text=True,
            timeout=5,
            env=env
        )
        if result.returncode == 0:
            ipa = result.stdout.strip()
            ipa = ' '.join(ipa.split())
            return f"[{ipa}]" if ipa else "[ipa]"
        return "[ipa]"
    except Exception as e:
        print(f"  ⚠ eSpeak error for '{word}': {e}")
        return "[ipa]"


def get_translation(word, lang_code, lang_config):
    """Get translation using Google Translate."""
    # Check if word has manual translation
    if word in lang_config.get('common_words', {}):
        return lang_config['common_words'][word]
    
    try:
        translator = GoogleTranslator(
            source=lang_code,
            target=lang_config['translate_target']
        )
        translation = translator.translate(word)
        return translation if translation else "[translation needed]"
    except Exception as e:
        print(f"  ⚠ Translation error for '{word}': {e}")
        return "[translation needed]"


def extract_words_from_phrase(phrase):
    """Extract individual words from a phrase."""
    # Remove punctuation and split
    words = re.findall(r"[a-zàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿœ']+", phrase.lower())
    return [w for w in words if len(w) > 1 or w in ['a', 'à', 'e', 'é', 'i', 'o', 'u', 'y']]


def process_phrase_file(phrase_file, lang_code, lang_config):
    """Extract words from a phrase file."""
    words_set = set()
    
    with open(phrase_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Extract phrase part (before first |)
            parts = line.split('|')
            if parts:
                phrase = parts[0].strip()
                words = extract_words_from_phrase(phrase)
                words_set.update(words)
    
    return sorted(words_set)


def create_word_file(words, output_file, level, source_file, lang_code, lang_config):
    """Create a word file with translations and IPA."""
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write(f"# {lang_config['name']} words from {source_file}\n")
        f.write(f"# Level: {level}\n")
        f.write(f"# Total unique words: {len(words)}\n")
        f.write("#\n")
        f.write("# Format: word | translation | [ipa]\n")
        f.write("# One word per line\n")
        f.write("#\n\n")
        
        # Write words with translations and IPA
        for word in words:
            translation = get_translation(word, lang_code, lang_config)
            ipa = get_espeak_ipa(word, lang_config)
            f.write(f"{word} | {translation} | {ipa}\n")
            print(f"    ✓ {word}: {translation} | {ipa}")


def populate_word_file(word_file, lang_code, lang_config):
    """Update existing word file with translations and IPA."""
    lines = []
    updates_count = 0
    
    with open(word_file, 'r', encoding='utf-8') as f:
        for line in f:
            original_line = line
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                lines.append(original_line)
                continue
            
            # Parse line
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 3:
                lines.append(original_line)
                continue
            
            word = parts[0]
            translation = parts[1]
            ipa = parts[2]
            
            # Update if needed
            needs_update = False
            
            if '[translation needed]' in translation:
                translation = get_translation(word, lang_code, lang_config)
                needs_update = True
            
            if ipa == '[ipa]':
                ipa = get_espeak_ipa(word, lang_config)
                needs_update = True
            
            if needs_update:
                updates_count += 1
                print(f"    ✓ {word}: {translation} | {ipa}")
            
            lines.append(f"{word} | {translation} | {ipa}\n")
    
    # Write back
    with open(word_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return updates_count


def process_language(lang_code):
    """Process all materials for a given language."""
    if lang_code not in LANGUAGES:
        print(f"❌ Unknown language code: {lang_code}")
        return
    
    lang_config = LANGUAGES[lang_code]
    lang_dir = Path(lang_code)
    
    if not lang_dir.exists():
        print(f"❌ Language directory not found: {lang_dir}")
        return
    
    print(f"\n{'='*50}")
    print(f"Processing {lang_config['name']} ({lang_code})")
    print(f"{'='*50}\n")
    
    total_updates = 0
    
    # Process each level (A, B, C, D)
    for level in ['A', 'B', 'C', 'D']:
        phrases_dir = lang_dir / f'phrases-{level}'
        words_dir = lang_dir / f'words-{level}'
        
        if not phrases_dir.exists():
            continue
        
        words_dir.mkdir(exist_ok=True)
        
        # Process phrase files
        for phrase_file in sorted(phrases_dir.glob('phr-*.txt')):
            print(f"\n{phrases_dir.name}/{phrase_file.name}:")
            
            # Extract words
            words = process_phrase_file(phrase_file, lang_code, lang_config)
            
            if not words:
                print("  (no words found)")
                continue
            
            # Create corresponding word file
            word_file = words_dir / f"words-{phrase_file.stem.split('-')[1]}.txt"
            
            if word_file.exists():
                # Update existing file
                updates = populate_word_file(word_file, lang_code, lang_config)
                total_updates += updates
            else:
                # Create new file
                create_word_file(
                    words,
                    word_file,
                    level,
                    phrase_file.name,
                    lang_code,
                    lang_config
                )
                total_updates += len(words)
            
            print(f"  ✓ {phrase_file.name} → {word_file.name} ({len(words)} words)")
    
    print(f"\n{'='*50}")
    print(f"✓ Complete! Processed {total_updates} words for {lang_config['name']}")
    print(f"{'='*50}\n")


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1:
        # Process specific languages
        for lang_code in sys.argv[1:]:
            process_language(lang_code)
    else:
        # Process all languages
        for lang_code in LANGUAGES:
            process_language(lang_code)


if __name__ == '__main__':
    main()
