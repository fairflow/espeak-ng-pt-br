#!/usr/bin/env python3
"""
Complete materials generation for all 6 languages.
Generates phrases (with IPA) and dictionaries (with translations and IPA) for all languages.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from collections import defaultdict
from openai import OpenAI
import re

LANGUAGE_CONFIGS = {
    'fr': {'name': 'French', 'native': 'Français', 'espeak_voice': 'fr', 'source': True},
    'pt': {'name': 'Portuguese', 'native': 'Português', 'espeak_voice': 'pt-br', 'source': True},
    'es': {'name': 'Spanish', 'native': 'Español', 'espeak_voice': 'es', 'source': False},
    'de': {'name': 'German', 'native': 'Deutsch', 'espeak_voice': 'de', 'source': False},
    'nl': {'name': 'Dutch', 'native': 'Nederlands', 'espeak_voice': 'nl', 'source': False},
    'it': {'name': 'Italian', 'native': 'Italiano', 'espeak_voice': 'it', 'source': False}
}

def get_ipa_with_espeak(text: str, lang_code: str) -> str:
    """Generate IPA using espeak."""
    try:
        voice = LANGUAGE_CONFIGS[lang_code]['espeak_voice']
        result = subprocess.run(
            ['espeak', '-v', voice, '-q', '--ipa', text],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            ipa = result.stdout.strip()
            return f"[{ipa}]" if ipa else ""
        return ""
    except Exception as e:
        return ""


def translate_phrases(client: OpenAI, lang_code: str, fr_phrases_dir: Path, output_dir: Path):
    """Translate French phrase files to target language with IPA."""
    
    config = LANGUAGE_CONFIGS[lang_code]
    fr_files = sorted(fr_phrases_dir.glob('phrases-*.txt'))
    
    if not fr_files:
        print(f"   ⚠️  No French phrase files found")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📝 Translating phrase files to {config['name']}...")
    
    for fr_file in fr_files:
        output_file = output_dir / fr_file.name
        
        if output_file.exists():
            print(f"   ⏭️  {fr_file.name} already exists, skipping...")
            continue
        
        # Read French phrases
        with open(fr_file, 'r', encoding='utf-8') as f:
            fr_content = f.read()
        
        # Check if file has actual content
        actual_lines = [line for line in fr_content.split('\n') 
                       if line.strip() and not line.strip().startswith('#')]
        if not actual_lines:
            print(f"   ⏭️  {fr_file.name} is empty (placeholder), skipping...")
            continue
        
        print(f"   → Translating {fr_file.name}...")
        
        # Translate
        prompt = f"""Translate these French phrases to {config['name']}.

CRITICAL FORMAT:
Input format: French phrase | English translation | [IPA]
Output format: {config['name']} phrase | English translation

RULES:
- Only translate the FIRST column (French → {config['name']})
- Keep the SECOND column (English) EXACTLY as-is
- Remove the THIRD column (IPA) - we'll regenerate it locally
- One phrase per line
- Use natural, conversational {config['name']}

Example:
Input:  Bonjour | Hello | [bɔ̃ʒuʁ]
Output: Hola | Hello

FRENCH PHRASES:
{fr_content}

Return ONLY the translated phrases in format: {config['name']} | English"""

        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": f"Expert {config['name']} translator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            translated = response.choices[0].message.content.strip()
            
            # Add IPA to each line
            print(f"      → Generating IPA...")
            lines_with_ipa = []
            for line in translated.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('|')
                    if len(parts) >= 2:
                        target_phrase = parts[0].strip()
                        english = parts[1].strip()
                        ipa = get_ipa_with_espeak(target_phrase, lang_code)
                        if ipa:
                            lines_with_ipa.append(f"{target_phrase} | {english} | {ipa}")
                        else:
                            lines_with_ipa.append(f"{target_phrase} | {english}")
                    else:
                        lines_with_ipa.append(line)
                else:
                    lines_with_ipa.append(line)
            
            # Write output
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines_with_ipa))
            
            print(f"      ✓ {fr_file.name} complete")
            
        except Exception as e:
            print(f"      ❌ Error: {e}")
            continue


def add_ipa_to_existing_phrases(lang_code: str, phrases_dir: Path):
    """Add IPA to existing phrase files that may be missing it."""
    
    config = LANGUAGE_CONFIGS[lang_code]
    phrase_files = sorted(phrases_dir.glob('phrases-*.txt'))
    
    if not phrase_files:
        return
    
    print(f"\n📝 Checking IPA in {config['name']} phrase files...")
    
    for phrase_file in phrase_files:
        needs_update = False
        updated_lines = []
        
        with open(phrase_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n')
                if line.strip() and not line.startswith('#'):
                    parts = line.split('|')
                    if len(parts) == 2:
                        # Missing IPA
                        needs_update = True
                        target_phrase = parts[0].strip()
                        english = parts[1].strip()
                        ipa = get_ipa_with_espeak(target_phrase, lang_code)
                        if ipa:
                            updated_lines.append(f"{target_phrase} | {english} | {ipa}")
                        else:
                            updated_lines.append(line)
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)
        
        if needs_update:
            print(f"   → Adding IPA to {phrase_file.name}...")
            with open(phrase_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(updated_lines))
            print(f"      ✓ {phrase_file.name} updated")


def extract_words_from_text(text: str) -> set:
    """Extract unique words from text, removing punctuation and numbers."""
    words = re.findall(r'\b[\w\'-]+\b', text.lower())
    return set(w for w in words if len(w) > 1 and not w.isdigit())


def translate_words_batch(client: OpenAI, words: list, lang_code: str) -> dict:
    """Translate a batch of words to English."""
    config = LANGUAGE_CONFIGS[lang_code]
    words_text = '\n'.join(words)
    
    prompt = f"""Translate these {config['name']} words to English. Return one translation per line in same order.
Keep it simple - just the most common English meaning.

{config['name']} words:
{words_text}

Return ONLY the English translations, one per line."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": f"Expert {config['name']}-English translator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        translations = response.choices[0].message.content.strip().split('\n')
        word_map = {}
        for i, word in enumerate(words):
            if i < len(translations):
                word_map[word] = translations[i].strip()
            else:
                word_map[word] = ""
        return word_map
    except Exception as e:
        print(f"      ⚠️  Translation error: {e}")
        return {word: "" for word in words}


def generate_dictionary(lang_code: str, materials_dir: Path, client: OpenAI):
    """Generate comprehensive dictionary with translations and IPA."""
    
    config = LANGUAGE_CONFIGS[lang_code]
    print(f"\n📚 Generating dictionary for {config['name']}...")
    
    all_words = set()
    
    # Extract from story.md
    story_file = materials_dir / "story.md"
    if story_file.exists():
        with open(story_file, 'r', encoding='utf-8') as f:
            story_words = extract_words_from_text(f.read())
        all_words.update(story_words)
        print(f"   → Extracted {len(story_words)} words from story.md")
    
    # Extract from phrase files
    phrases_dir = materials_dir / "phrases"
    if phrases_dir.exists():
        phrase_count = 0
        for phrase_file in phrases_dir.glob('phrases-*.txt'):
            with open(phrase_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        all_words.update(extract_words_from_text(line))
                        phrase_count += 1
        print(f"   → Extracted words from {phrase_count} phrases")
    
    # Extract from story scenes
    scenes_dir = materials_dir / "story-scenes-json"
    if scenes_dir.exists():
        scene_count = 0
        for scene_file in scenes_dir.glob('scene-*.json'):
            try:
                with open(scene_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if lang_code in data and isinstance(data[lang_code], list):
                    for item in data[lang_code]:
                        text = item.get(lang_code, '')
                        if text:
                            all_words.update(extract_words_from_text(text))
                    scene_count += 1
            except Exception:
                pass
        print(f"   → Extracted words from {scene_count} story scenes")
    
    # Sort words
    sorted_words = sorted(all_words)
    print(f"   → Total unique words: {len(sorted_words)}")
    
    # Translate words in batches
    print(f"   → Translating words to English...")
    word_translations = {}
    batch_size = 50
    
    for i in range(0, len(sorted_words), batch_size):
        batch = sorted_words[i:i + batch_size]
        batch_trans = translate_words_batch(client, batch, lang_code)
        word_translations.update(batch_trans)
        if (i + batch_size) % 200 == 0 or i + batch_size >= len(sorted_words):
            print(f"      {min(i + batch_size, len(sorted_words))}/{len(sorted_words)} words translated...")
    
    # Generate IPA
    print(f"   → Generating IPA...")
    
    output_file = materials_dir / "words" / "dictionary-complete.txt"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Complete {config['name']} Dictionary\n")
        f.write(f"# Generated from story and phrases\n")
        f.write(f"# Format: word | English | [IPA]\n")
        f.write(f"# Total words: {len(sorted_words)}\n\n")
        
        for i, word in enumerate(sorted_words, 1):
            english = word_translations.get(word, "")
            ipa = get_ipa_with_espeak(word, lang_code)
            
            if english and ipa:
                f.write(f"{word} | {english} | {ipa}\n")
            elif english:
                f.write(f"{word} | {english}\n")
            elif ipa:
                f.write(f"{word} | {ipa}\n")
            else:
                f.write(f"{word}\n")
            
            if i % 200 == 0:
                print(f"      {i}/{len(sorted_words)} IPA generated...")
    
    print(f"   ✓ Dictionary complete: {len(sorted_words)} words")
    print(f"   📁 {output_file}")


def main():
    base_dir = Path(__file__).parent.parent
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not set")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    
    print("="*60)
    print("🌍 Complete Materials Generation for All Languages")
    print("="*60)
    
    # Process all languages
    for lang_code, config in LANGUAGE_CONFIGS.items():
        print(f"\n{'='*60}")
        print(f"Processing: {config['name']} ({config['native']})")
        print(f"{'='*60}")
        
        materials_dir = base_dir / "language_materials" / lang_code
        
        # 1. Handle phrases
        if config['source']:
            # Source languages (FR, PT) - just add IPA if missing
            phrases_dir = materials_dir / "phrases"
            if phrases_dir.exists():
                add_ipa_to_existing_phrases(lang_code, phrases_dir)
        else:
            # Target languages (ES, DE, NL, IT) - translate from French
            fr_phrases_dir = base_dir / "language_materials" / "fr" / "phrases"
            output_dir = materials_dir / "phrases"
            translate_phrases(client, lang_code, fr_phrases_dir, output_dir)
        
        # 2. Generate dictionary with translations and IPA
        generate_dictionary(lang_code, materials_dir, client)
    
    print(f"\n{'='*60}")
    print("✅ All Materials Complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
