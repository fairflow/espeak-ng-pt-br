#!/usr/bin/env python3
"""
Generate story scenes for Spanish, German, Dutch, and Italian.

This script:
1. Adapts the Portuguese story for each language
2. Extracts phrases from each scene
3. Translates to English (batch processing)
4. Generates IPA transcriptions
5. Creates Format 2 JSON files

Uses Claude API for batch translation to save time.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
import anthropic
import os

# Configuration
BASE_DIR = Path(__file__).parent.parent
MATERIALS_DIR = BASE_DIR / "language_materials"
PT_STORY_PATH = MATERIALS_DIR / "pt" / "story.md"
PT_SCENES_DIR = MATERIALS_DIR / "pt" / "story-scenes-json"

# Language configurations
LANGUAGES = {
    'es': {
        'name': 'Spanish',
        'city': 'Madrid',
        'neighborhood': 'Malasaña',
        'espeak_voice': 'es',
        'lang_code': 'es'
    },
    'de': {
        'name': 'German',
        'city': 'Berlin',
        'neighborhood': 'Kreuzberg',
        'espeak_voice': 'de',
        'lang_code': 'de'
    },
    'nl': {
        'name': 'Dutch',
        'city': 'Amsterdam',
        'neighborhood': 'De Pijp',
        'espeak_voice': 'nl',
        'lang_code': 'nl'
    },
    'it': {
        'name': 'Italian',
        'city': 'Rome',
        'neighborhood': 'Trastevere',
        'espeak_voice': 'it',
        'lang_code': 'it'
    }
}

# Scene titles (same across all languages conceptually)
SCENE_TITLES = [
    "The Breakfast",
    "Shopping in the City",
    "Conversation about the Dream",
    "The Decision",
    "At the Bus Station",
    "On the Bus",
    "Arrival in the Village",
    "Meetings and Discoveries",
    "The Difficult Trail",
    "The Involuntary Separation",
    "Sophie's Challenge - The Four Elements",
    "Lucas's Challenge - The Unexpected Guide",
    "The Rescue",
    "Sophie's Reflection",
    "The Discovery",
    "The Reunion"
]


def extract_scene_content(story_md: str, scene_num: int) -> str:
    """Extract a specific scene's content from the story markdown."""
    # Pattern: ### CENA N: Title ... content until next ### or end
    pattern = rf'### CENA {scene_num}:.*?\n\n(.*?)(?=\n### CENA|\Z)'
    match = re.search(pattern, story_md, re.DOTALL)
    return match.group(1).strip() if match else ""


def extract_phrases_from_scene(scene_content: str) -> List[str]:
    """Extract dialogue and key narrative phrases from scene content."""
    phrases = []
    
    # Extract dialogue (text between «» or ")
    dialogue_pattern = r'[«"]([^»"]+)[»"]'
    dialogues = re.findall(dialogue_pattern, scene_content)
    phrases.extend(dialogues)
    
    # Extract narrative sentences (split by period, keep substantial ones)
    # Remove dialogue markers first
    narrative = re.sub(r'[«"][^»"]+[»"]', '', scene_content)
    sentences = [s.strip() for s in narrative.split('.') if s.strip()]
    
    # Filter: keep sentences with 4+ words
    narrative_phrases = [s + '.' for s in sentences if len(s.split()) >= 4]
    phrases.extend(narrative_phrases)
    
    return phrases


def create_translation_prompt(lang_config: Dict, all_phrases: List[Tuple[int, str]]) -> str:
    """Create a comprehensive prompt for batch translation."""
    lang_name = lang_config['name']
    city = lang_config['city']
    neighborhood = lang_config['neighborhood']
    
    phrases_text = "\n".join([f"{idx}. {phrase}" for idx, phrase in all_phrases])
    
    return f"""You are translating a story about Sophie and Lucas from Portuguese to {lang_name}.

CONTEXT:
- Story setting: {city}, {neighborhood} neighborhood
- Characters: Sophie Moreira and Lucas Duarte (young adults, friends considering adventure)
- 16 scenes: from daily routine → mountain adventure → self-discovery

TASK: Translate each numbered phrase below to natural, colloquial {lang_name}. 
- Maintain cultural authenticity for {city}
- Use conversational register for dialogue
- Keep narrative sentences clear and engaging
- Preserve emotional tone

Return ONLY a JSON array with this exact structure:
[
  {{"number": 1, "translated": "phrase in {lang_name}"}},
  {{"number": 2, "translated": "phrase in {lang_name}"}},
  ...
]

PHRASES TO TRANSLATE:
{phrases_text}

Respond with ONLY the JSON array, no explanation."""


def create_ipa_prompt(lang_config: Dict, phrases_with_translations: List[Dict]) -> str:
    """Create prompt for IPA generation."""
    lang_name = lang_config['name']
    lang_code = lang_config['lang_code']
    
    phrases_text = "\n".join([
        f"{p['number']}. {p['translated']}"
        for p in phrases_with_translations
    ])
    
    return f"""Generate IPA (International Phonetic Alphabet) transcriptions for these {lang_name} phrases.

REQUIREMENTS:
- Use standard {lang_name} pronunciation
- Enclose each IPA in square brackets: [ipa]
- Be precise with {lang_name} phonemes
- Include stress marks and syllable boundaries

Return ONLY a JSON array:
[
  {{"number": 1, "ipa": "[ipa transcription]"}},
  {{"number": 2, "ipa": "[ipa transcription]"}},
  ...
]

PHRASES:
{phrases_text}

Respond with ONLY the JSON array."""


def process_language(lang_code: str, client: anthropic.Anthropic) -> None:
    """Process complete story generation for one language."""
    lang_config = LANGUAGES[lang_code]
    print(f"\n{'='*60}")
    print(f"🌍 Processing {lang_config['name']} ({lang_code})")
    print(f"{'='*60}")
    
    # Read Portuguese story
    with open(PT_STORY_PATH, 'r', encoding='utf-8') as f:
        pt_story = f.read()
    
    # Extract all phrases from all scenes
    all_phrases = []
    scene_phrase_map = {}  # {scene_num: [(phrase_idx, phrase_text), ...]}
    
    phrase_counter = 1
    for scene_num in range(1, 17):
        print(f"  📄 Extracting Scene {scene_num}...")
        scene_content = extract_scene_content(pt_story, scene_num)
        phrases = extract_phrases_from_scene(scene_content)
        
        scene_phrases = []
        for phrase in phrases:
            all_phrases.append((phrase_counter, phrase))
            scene_phrases.append(phrase_counter)
            phrase_counter += 1
        
        scene_phrase_map[scene_num] = scene_phrases
    
    print(f"  ✅ Extracted {len(all_phrases)} total phrases across 16 scenes")
    
    # STEP 1: Batch translate all phrases
    print(f"\n  🔄 Batch translating to {lang_config['name']}...")
    translation_prompt = create_translation_prompt(lang_config, all_phrases)
    
    translation_response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=16000,
        messages=[{"role": "user", "content": translation_prompt}]
    )
    
    translations_json = translation_response.content[0].text.strip()
    # Remove markdown code blocks if present
    translations_json = re.sub(r'```json\n?|\n?```', '', translations_json)
    translations = json.loads(translations_json)
    
    print(f"  ✅ Translated {len(translations)} phrases")
    
    # STEP 2: Batch translate to English
    print(f"  🔄 Translating to English...")
    english_prompt = f"""Translate these {lang_config['name']} phrases to natural English.

Return ONLY a JSON array:
[
  {{"number": 1, "english": "translation"}},
  ...
]

PHRASES:
{chr(10).join([f"{t['number']}. {t['translated']}" for t in translations])}

Respond with ONLY the JSON array."""
    
    english_response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=12000,
        messages=[{"role": "user", "content": english_prompt}]
    )
    
    english_json = english_response.content[0].text.strip()
    english_json = re.sub(r'```json\n?|\n?```', '', english_json)
    english_translations = json.loads(english_json)
    
    print(f"  ✅ English translations complete")
    
    # STEP 3: Generate IPA
    print(f"  🔄 Generating IPA transcriptions...")
    ipa_prompt = create_ipa_prompt(lang_config, translations)
    
    ipa_response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=12000,
        messages=[{"role": "user", "content": ipa_prompt}]
    )
    
    ipa_json = ipa_response.content[0].text.strip()
    ipa_json = re.sub(r'```json\n?|\n?```', '', ipa_json)
    ipa_transcriptions = json.loads(ipa_json)
    
    print(f"  ✅ IPA transcriptions complete")
    
    # Combine all data
    phrase_data = {}
    for t in translations:
        phrase_data[t['number']] = {'translated': t['translated']}
    for e in english_translations:
        phrase_data[e['number']]['english'] = e['english']
    for i in ipa_transcriptions:
        phrase_data[i['number']]['ipa'] = i['ipa']
    
    # STEP 4: Create scene JSON files
    print(f"  📝 Creating scene JSON files...")
    output_dir = MATERIALS_DIR / lang_code / "story-scenes-json"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for scene_num in range(1, 17):
        phrase_indices = scene_phrase_map[scene_num]
        
        scene_phrases = []
        for idx in phrase_indices:
            if idx in phrase_data:
                pd = phrase_data[idx]
                scene_phrases.append({
                    lang_code: pd['translated'],
                    'english': pd['english'],
                    'ipa': pd['ipa']
                })
        
        scene_data = {
            lang_code: scene_phrases,
            "scene_number": scene_num,
            "scene_title": SCENE_TITLES[scene_num - 1]
        }
        
        # Create filename (sanitized scene title)
        title_slug = SCENE_TITLES[scene_num - 1].lower().replace(' ', '-').replace("'", '')
        filename = f"scene-{scene_num:02d}-{title_slug}.json"
        
        output_path = output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(scene_data, f, ensure_ascii=False, indent=2)
        
        print(f"    ✓ {filename} ({len(scene_phrases)} phrases)")
    
    print(f"  ✅ {lang_config['name']} complete! ({len(all_phrases)} phrases, 16 scenes)")


def main():
    """Main execution."""
    print("="*60)
    print("🌍 Multi-Language Story Generation")
    print("="*60)
    print("\nGenerating stories for:")
    for code, config in LANGUAGES.items():
        print(f"  - {config['name']} ({code})")
    
    # Initialize Anthropic client
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("\n❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("   Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Process each language
    for lang_code in LANGUAGES.keys():
        try:
            process_language(lang_code, client)
        except Exception as e:
            print(f"\n❌ Error processing {lang_code}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "="*60)
    print("✅ All languages processed!")
    print("="*60)
    print("\n📋 Next steps:")
    print("  1. Review generated files in language_materials/*/story-scenes-json/")
    print("  2. Test in app (Story Reader tab)")
    print("  3. Verify translations and IPA accuracy")
    print("  4. Commit changes to git")


if __name__ == '__main__':
    main()
