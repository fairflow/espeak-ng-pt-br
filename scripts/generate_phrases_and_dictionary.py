#!/usr/bin/env python3
"""
Generate phrase files and comprehensive dictionaries for all languages.
- Translates French phrase files to target languages
- Creates sorted dictionary from all story and phrase content
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict
from openai import OpenAI
import re

LANGUAGE_CONFIGS = {
    'es': {'name': 'Spanish', 'native': 'Español'},
    'de': {'name': 'German', 'native': 'Deutsch'},
    'nl': {'name': 'Dutch', 'native': 'Nederlands'},
    'it': {'name': 'Italian', 'native': 'Italiano'},
    'pt': {'name': 'Portuguese', 'native': 'Português'},
    'fr': {'name': 'French', 'native': 'Français'}
}

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
        
        print(f"   → Translating {fr_file.name}...")
        
        # Translate
        prompt = f"""Translate these French phrases to {config['name']}.

Keep the same format: one phrase per line.
Use natural, conversational {config['name']}.
Maintain the same meaning and tone.

FRENCH PHRASES:
{fr_content}

Return ONLY the translated phrases, one per line."""

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
            
            # Write output
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(translated)
            
            print(f"      ✓ {fr_file.name} translated")
            
        except Exception as e:
            print(f"      ❌ Error: {e}")
            continue


def extract_words_from_text(text: str) -> set:
    """Extract unique words from text, removing punctuation."""
    # Remove punctuation and split into words
    words = re.findall(r'\b[\w\'-]+\b', text.lower())
    return set(w for w in words if len(w) > 1)  # Filter very short words


def generate_dictionary(lang_code: str, materials_dir: Path):
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
    
    # Sort and write dictionary
    sorted_words = sorted(all_words)
    
    output_file = materials_dir / "words" / "dictionary-complete.txt"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Complete {config['name']} Dictionary\n")
        f.write(f"# Generated from story and phrases\n")
        f.write(f"# Total words: {len(sorted_words)}\n\n")
        
        for word in sorted_words:
            f.write(f"{word}\n")
    
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
        materials_dir = base_dir / "language_materials" / lang_code
        generate_dictionary(lang_code, materials_dir)
    
    print(f"\n{'='*60}")
    print(f"✅ {config['name']} Materials Complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
