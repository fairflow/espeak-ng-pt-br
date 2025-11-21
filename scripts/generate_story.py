#!/usr/bin/env python3
"""
Generate story scenes for any language using OpenAI API.

Adapts French story with cultural localization for the target language.
Processes all 16 scenes in batches for efficiency.

Usage:
    python generate_story.py <lang_code>
    
Examples:
    python generate_story.py es
    python generate_story.py de
    python generate_story.py nl
    python generate_story.py it
"""

import json
import re
import sys
import subprocess
from pathlib import Path
from typing import List, Dict
import os

try:
    from openai import OpenAI
except ImportError:
    print("❌ Error: openai package not installed")
    print("   Install with: pip install openai")
    exit(1)

# Configuration
BASE_DIR = Path(__file__).parent.parent
MATERIALS_DIR = BASE_DIR / "language_materials"
FR_STORY_PATH = MATERIALS_DIR / "fr" / "story.md"
FR_SCENES_DIR = MATERIALS_DIR / "fr" / "story-scenes-json"

# Language-specific cultural contexts
LANGUAGE_CONFIGS = {
    'es': {
        'name': 'Spanish',
        'native_name': 'Español (España)',
        'city': 'Madrid',
        'neighborhood': 'Malasaña',
        'breakfast_item': 'churro con chocolate',
        'greeting': '¿Qué tal?',
        'mountains': 'los Pirineos',
        'surnames': ['Moreno', 'Ruiz'],
        'dialect_note': 'Use Peninsular Spanish (Spain), informal tú form'
    },
    'de': {
        'name': 'German',
        'native_name': 'Deutsch',
        'city': 'Berlin',
        'neighborhood': 'Kreuzberg',
        'breakfast_item': 'Brötchen',
        'greeting': 'Wie geht\'s?',
        'mountains': 'die Alpen',
        'surnames': ['Müller', 'Schmidt'],
        'dialect_note': 'Use standard High German, informal du form'
    },
    'nl': {
        'name': 'Dutch',
        'native_name': 'Nederlands',
        'city': 'Amsterdam',
        'neighborhood': 'De Pijp',
        'breakfast_item': 'stroopwafel',
        'greeting': 'Hoe gaat het?',
        'mountains': 'de Ardennen',
        'surnames': ['de Vries', 'van der Berg'],
        'dialect_note': 'Use standard Dutch (Netherlands), informal jij/je form'
    },
    'it': {
        'name': 'Italian',
        'native_name': 'Italiano',
        'city': 'Rome',
        'neighborhood': 'Trastevere',
        'breakfast_item': 'cornetto',
        'greeting': 'Come va?',
        'mountains': 'le Alpi',
        'surnames': ['Romano', 'Conti'],
        'dialect_note': 'Use standard Italian, informal tu form'
    }
}


def generate_ipa_with_espeak(text: str, lang_code: str) -> str:
    """Generate IPA transcription using eSpeak NG."""
    try:
        # Map language codes to eSpeak voice codes
        voice_map = {
            'es': 'es',
            'de': 'de',
            'nl': 'nl',
            'it': 'it',
            'fr': 'fr',
            'pt': 'pt'
        }
        
        voice = voice_map.get(lang_code, lang_code)
        
        # Run espeak with IPA output
        result = subprocess.run(
            ['espeak', '-v', voice, '-q', '--ipa', text],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            ipa = result.stdout.strip()
            # Clean up the IPA output
            ipa = ipa.replace('_:', ' ').replace('_', ' ').strip()
            return f"[{ipa}]" if ipa else "[unavailable]"
        else:
            return "[unavailable]"
            
    except Exception as e:
        print(f"    ⚠️  eSpeak IPA generation failed: {e}")
        return "[unavailable]"


def extract_french_scene_phrases(scene_file: Path) -> List[Dict]:
    """Extract phrases from French scene JSON."""
    with open(scene_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get('fr', [])


def create_translation_prompt(scene_num: int, french_phrases: List[Dict], lang_code: str, config: Dict) -> str:
    """Create prompt for OpenAI to translate and adapt scene."""
    
    phrases_text = "\n".join([
        f"{i+1}. {p['fr']}"
        for i, p in enumerate(french_phrases)
    ])
    
    return f"""You are adapting a story from French (Paris) to {config['name']} ({config['city']}, {config['neighborhood']}).

SCENE {scene_num} CONTEXT:
- Original: Paris, Le Marais
- Adapted: {config['city']}, {config['neighborhood']}
- Characters: Sophie {config['surnames'][0]} & Lucas {config['surnames'][1]} (young adults, friends)
- Cultural shifts: French items → {config['name']} equivalents (e.g., croissant → {config['breakfast_item']})

LANGUAGE STYLE:
{config['dialect_note']}

TASK: For each numbered French phrase, provide:
1. Natural {config['name']} translation (conversational, culturally adapted)
2. English translation

CULTURAL ADAPTATION:
- Use {config['name']} greetings: "{config['greeting']}" instead of "Ça va?"
- Replace French food/places with {config['city']} equivalents naturally
- Replace "les Alpes" with "{config['mountains']}"
- Keep emotional tone and character personality
- Make dialogue sound natural for native speakers in {config['city']}

OUTPUT FORMAT (JSON array):
[
  {{
    "{lang_code}": "{config['name']} translation here",
    "english": "English translation here"
  }},
  ...
]

CRITICAL JSON RULES:
- Escape ALL quotation marks in text with backslash: \\"
- Example: "Ella dijo \\"hola\\" a María"
- Do NOT escape apostrophes in contractions (l'eau, qu'il)
- Preserve ellipsis (...) as-is without escaping
- Ensure valid JSON syntax - test mentally before returning

FRENCH PHRASES TO ADAPT:
{phrases_text}

Return ONLY the JSON array, no explanation or markdown."""


def translate_phrases_chunk(client: OpenAI, scene_num: int, french_phrases: List[Dict], 
                           lang_code: str, config: Dict, chunk_label: str = "", output_dir: Path = None) -> List[Dict]:
    """Translate a chunk of phrases (handles large scenes by splitting)."""
    prompt = create_translation_prompt(scene_num, french_phrases, lang_code, config)
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": f"You are an expert translator specializing in {config['name']} ({config['native_name']}) with deep knowledge of {config['city']} culture and conversational language."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=4096
    )
    
    result_text = response.choices[0].message.content.strip()
    result_text = re.sub(r'```json\n?|\n?```', '', result_text)
    
    try:
        phrases = json.loads(result_text)
        
        # Add IPA using eSpeak NG for each phrase
        for phrase in phrases:
            if lang_code in phrase:
                phrase['ipa'] = generate_ipa_with_espeak(phrase[lang_code], lang_code)
        
        return phrases
    except json.JSONDecodeError as e:
        print(f"    ❌ JSON parsing error{chunk_label}: {e}")
        if output_dir:
            debug_file = output_dir / f"debug_scene_{scene_num}{chunk_label.replace(' ', '_')}_response.txt"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(result_text)
            print(f"    💾 Debug saved: {debug_file.name}")
        raise


def process_scene(scene_num: int, client: OpenAI, lang_code: str, config: Dict, output_dir: Path) -> Dict:
    """Process a single scene: translate and adapt from French."""
    print(f"  📄 Processing Scene {scene_num}...")
    
    # Find French scene file
    fr_files = list(FR_SCENES_DIR.glob(f"scene-{scene_num:02d}-*.json"))
    if not fr_files:
        print(f"    ⚠️  French scene {scene_num} not found!")
        return None
    
    fr_scene_file = fr_files[0]
    french_phrases = extract_french_scene_phrases(fr_scene_file)
    
    print(f"    → {len(french_phrases)} phrases to translate")
    
    # Get scene metadata
    with open(fr_scene_file, 'r', encoding='utf-8') as f:
        fr_data = json.load(f)
    scene_title_en = fr_data.get('scene_title', f'Scene {scene_num}')
    
    # Handle large scenes by chunking (over 40 phrases)
    CHUNK_SIZE = 30
    if len(french_phrases) > 40:
        print(f"    ⚠️  Large scene ({len(french_phrases)} phrases) - splitting into chunks...")
        target_phrases = []
        for i in range(0, len(french_phrases), CHUNK_SIZE):
            chunk = french_phrases[i:i+CHUNK_SIZE]
            chunk_num = i // CHUNK_SIZE + 1
            total_chunks = (len(french_phrases) + CHUNK_SIZE - 1) // CHUNK_SIZE
            print(f"    → Translating chunk {chunk_num}/{total_chunks} ({len(chunk)} phrases)...")
            chunk_result = translate_phrases_chunk(client, scene_num, chunk, lang_code, config, f" (chunk {chunk_num})", output_dir)
            target_phrases.extend(chunk_result)
        print(f"    ✓ Translated {len(target_phrases)} phrases total")
    else:
        # Normal single-call translation
        target_phrases = translate_phrases_chunk(client, scene_num, french_phrases, lang_code, config, "", output_dir)
        print(f"    ✓ Translated {len(target_phrases)} phrases")
    
    # Translate scene title
    try:
        title_response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": f"Translate to {config['name']} ({config['native_name']})."},
                {"role": "user", "content": f"Translate this scene title to natural {config['name']}: '{scene_title_en}'.\nRespond with ONLY the {config['name']} translation, nothing else."}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        scene_title_target = title_response.choices[0].message.content.strip()
        
        # Build scene data
        scene_data = {
            lang_code: target_phrases,
            "scene_number": scene_num,
            "scene_title": scene_title_target
        }
        
        return scene_data
        
    except Exception as e:
        print(f"    ❌ Error translating scene {scene_num}: {e}")
        return None


def scene_exists(scene_num: int, output_dir: Path) -> bool:
    """Check if a scene file already exists."""
    # Look for any file matching scene-NN-*.json
    existing = list(output_dir.glob(f"scene-{scene_num:02d}-*.json"))
    return len(existing) > 0


def save_scene(scene_num: int, scene_data: Dict, lang_code: str, output_dir: Path) -> None:
    """Save scene data to JSON file."""
    # Create filename from title
    title_slug = scene_data['scene_title'].lower()
    # Remove special characters and normalize
    title_slug = re.sub(r'[^\w\s-]', '', title_slug)
    title_slug = re.sub(r'[-\s]+', '-', title_slug)
    
    filename = f"scene-{scene_num:02d}-{title_slug}.json"
    output_path = output_dir / filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(scene_data, f, ensure_ascii=False, indent=2)
    
    print(f"    💾 Saved: {filename}")


def main():
    """Main execution."""
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python generate_story.py <lang_code>")
        print("\nAvailable languages:")
        for code, config in LANGUAGE_CONFIGS.items():
            print(f"  {code} - {config['name']} ({config['city']})")
        sys.exit(1)
    
    lang_code = sys.argv[1].lower()
    
    if lang_code not in LANGUAGE_CONFIGS:
        print(f"❌ Error: Unknown language code '{lang_code}'")
        print("\nAvailable languages:")
        for code, config in LANGUAGE_CONFIGS.items():
            print(f"  {code} - {config['name']} ({config['city']})")
        sys.exit(1)
    
    config = LANGUAGE_CONFIGS[lang_code]
    output_dir = MATERIALS_DIR / lang_code / "story-scenes-json"
    
    print("=" * 60)
    print(f"🌍 {config['name']} Story Generation (OpenAI)")
    print("=" * 60)
    print(f"\nLanguage: {config['native_name']}")
    print(f"Setting: {config['city']}, {config['neighborhood']}")
    print(f"Source: {FR_SCENES_DIR}")
    print(f"Output: {output_dir}\n")
    
    # Check API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("   Set it with: export OPENAI_API_KEY='sk-...'")
        return
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process all 16 scenes
    print("📚 Processing 16 scenes...\n")
    
    successful = 0
    failed = 0
    skipped = 0
    
    for scene_num in range(1, 17):
        try:
            # Skip if scene already exists
            if scene_exists(scene_num, output_dir):
                print(f"  ⏭️  Scene {scene_num} already exists, skipping...")
                skipped += 1
                continue
            
            scene_data = process_scene(scene_num, client, lang_code, config, output_dir)
            
            if scene_data:
                save_scene(scene_num, scene_data, lang_code, output_dir)
                successful += 1
            else:
                failed += 1
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            break
        except Exception as e:
            print(f"    ❌ Unexpected error: {e}")
            failed += 1
            continue
    
    # Summary
    print("\n" + "=" * 60)
    print(f"✅ {config['name']} Story Generation Complete!")
    print("=" * 60)
    print(f"\n📊 Results:")
    print(f"   ✓ Successful: {successful} scenes")
    if skipped > 0:
        print(f"   ⏭️  Skipped: {skipped} scenes (already exist)")
    if failed > 0:
        print(f"   ✗ Failed: {failed} scenes")
    
    print(f"\n📁 Output: {output_dir}")
    print("\n📋 Next steps:")
    print(f"   1. Review generated files for {config['name']}")
    print(f"   2. Test in Story Reader (select {config['name']})")
    print("   3. Verify cultural adaptations are natural")
    print("   4. Check IPA transcriptions")
    if successful == 16:
        print(f"   5. Run for another language: python generate_story.py <code>")


if __name__ == '__main__':
    main()
