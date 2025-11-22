#!/usr/bin/env python3
"""
Generate phrase files and comprehensive dictionaries for all languages.
- Translates French phrase files to target languages
- Creates sorted dictionary from all story and phrase content
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
    'es': {'name': 'Spanish', 'native': 'Español', 'espeak_voice': 'es'},
    'de': {'name': 'German', 'native': 'Deutsch', 'espeak_voice': 'de'},
    'nl': {'name': 'Dutch', 'native': 'Nederlands', 'espeak_voice': 'nl'},
    'it': {'name': 'Italian', 'native': 'Italiano', 'espeak_voice': 'it'},
    'pt': {'name': 'Portuguese', 'native': 'Português', 'espeak_voice': 'pt'},
    'fr': {'name': 'French', 'native': 'Français', 'espeak_voice': 'fr'}
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
        print(f"      ⚠️  IPA generation error: {e}")
        return ""

def translate_phrases(client: OpenAI, lang_code: str, fr_phrases_dir: Path, output_dir: Path):
    """Translate French phrase files to target language."""
    
    config = LANGUAGE_CONFIGS[lang_code]
    fr_files = sorted(fr_phrases_dir.glob('phrases-*.txt'))
    
    if not fr_files:
        print(f"   ⚠️  No French phrase files found")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📝 Translating {len(fr_files)} phrase files to {config['name']}...")
    
    for fr_file in fr_files:
        output_file = output_dir / fr_file.name
        
        if output_file.exists():
            print(f"   ⏭️  {fr_file.name} already exists, skipping...")
            continue
        
        # Read French phrases
        with open(fr_file, 'r', encoding='utf-8') as f:
            fr_content = f.read()
        
        # Check if file has actual content (not just comments/blank lines)
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
            print(f"      → Generating IPA with espeak...")
            lines_with_ipa = []
            for line in translated.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse the phrase
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
            
            print(f"      ✓ {fr_file.name} translated with IPA")
            
        except Exception as e:
            print(f"      ❌ Error: {e}")
            continue


def extract_words_from_text(text: str) -> set:
    """Extract unique words from text, removing punctuation and numbers."""
    # Remove punctuation and split into words
    words = re.findall(r'\b[\w\'-]+\b', text.lower())
    # Filter short words and pure numbers
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
        # Map words to translations
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


def generate_dictionary(lang_code: str, materials_dir: Path, client: OpenAI = None):
    """Generate comprehensive dictionary from story and phrases."""
    
    config = LANGUAGE_CONFIGS[lang_code]
    print(f"\n📚 Generating dictionary for {config['name']}...")
    
    all_words = set()
    word_contexts = defaultdict(list)  # word -> [example sentences]
    
    # 1. Extract from story.md
    story_file = materials_dir / "story.md"
    if story_file.exists():
        with open(story_file, 'r', encoding='utf-8') as f:
            story_text = f.read()
        
        # Extract words
        story_words = extract_words_from_text(story_text)
        all_words.update(story_words)
        print(f"   → Extracted {len(story_words)} unique words from story.md")
    
    # 2. Extract from phrase files
    phrases_dir = materials_dir / "phrases"
    if phrases_dir.exists():
        phrase_count = 0
        for phrase_file in phrases_dir.glob('phrases-*.txt'):
            with open(phrase_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        phrase_words = extract_words_from_text(line)
                        all_words.update(phrase_words)
                        phrase_count += 1
                        
                        # Store example contexts for some words
                        for word in phrase_words:
                            if len(word_contexts[word]) < 3:  # Keep max 3 examples
                                word_contexts[word].append(line[:80])
        
        print(f"   → Extracted words from {phrase_count} phrases")
    
    # 3. Extract from story scenes JSON
    scenes_dir = materials_dir / "story-scenes-json"
    if scenes_dir.exists():
        scene_count = 0
        for scene_file in scenes_dir.glob('scene-*.json'):
            try:
                with open(scene_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Get phrases for this language
                if lang_code in data and isinstance(data[lang_code], list):
                    for item in data[lang_code]:
                        text = item.get(lang_code, '')
                        if text:
                            scene_words = extract_words_from_text(text)
                            all_words.update(scene_words)
                    scene_count += 1
            except Exception as e:
                print(f"      ⚠️  Error reading {scene_file.name}: {e}")
        
        print(f"   → Extracted words from {scene_count} story scenes")
    
    # Sort words
    sorted_words = sorted(all_words)
    
    output_file = materials_dir / "words" / "dictionary-complete.txt"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Translate words in batches
    print(f"   → Translating {len(sorted_words)} words to English...")
    word_translations = {}
    batch_size = 50
    
    if client:
        for i in range(0, len(sorted_words), batch_size):
            batch = sorted_words[i:i + batch_size]
            batch_trans = translate_words_batch(client, batch, lang_code)
            word_translations.update(batch_trans)
            print(f"      {min(i + batch_size, len(sorted_words))}/{len(sorted_words)} words translated...")
    else:
        print(f"      ⚠️  No API client - skipping translations")
    
    # Generate IPA and write dictionary
    print(f"   → Generating IPA for {len(sorted_words)} words...")
    
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
            
            # Progress indicator
            if i % 200 == 0:
                print(f"      {i}/{len(sorted_words)} IPA generated...")
    
    print(f"   ✓ Dictionary created: {len(sorted_words)} words")
    print(f"   📁 {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_phrases_and_dictionary.py <lang_code> [--phrases-only|--dict-only]")
        print(f"Supported: {', '.join(k for k in LANGUAGE_CONFIGS.keys() if k not in ['fr', 'pt'])}")
        sys.exit(1)
    
    lang_code = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else 'both'
    
    if lang_code not in LANGUAGE_CONFIGS:
        print(f"❌ Error: Language '{lang_code}' not supported")
        sys.exit(1)
    
    config = LANGUAGE_CONFIGS[lang_code]
    base_dir = Path(__file__).parent.parent
    
    print(f"\n{'='*60}")
    print(f"🌍 {config['name']} Materials Generation")
    print(f"{'='*60}")
    
    # Phrases translation (only for new languages)
    if mode in ['both', '--phrases-only'] and lang_code in ['es', 'de', 'nl', 'it']:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ Error: OPENAI_API_KEY not set (needed for phrase translation)")
            if mode == '--phrases-only':
                sys.exit(1)
        else:
            client = OpenAI(api_key=api_key)
            fr_phrases_dir = base_dir / "language_materials" / "fr" / "phrases"
            output_dir = base_dir / "language_materials" / lang_code / "phrases"
            translate_phrases(client, lang_code, fr_phrases_dir, output_dir)
    
    # Dictionary generation (all languages)
    if mode in ['both', '--dict-only']:
        # Get API client if available
        api_key = os.getenv('OPENAI_API_KEY')
        dict_client = OpenAI(api_key=api_key) if api_key else None
        
        materials_dir = base_dir / "language_materials" / lang_code
        generate_dictionary(lang_code, materials_dir, dict_client)
    
    print(f"\n{'='*60}")
    print(f"✅ {config['name']} Materials Complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
