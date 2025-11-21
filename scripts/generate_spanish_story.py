#!/usr/bin/env python3
"""
Generate Spanish story scenes using OpenAI API.

Adapts French story to Madrid/Malasaña context with cultural localization.
Processes all 16 scenes in batches for efficiency.
"""

import json
import re
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
ES_OUTPUT_DIR = MATERIALS_DIR / "es" / "story-scenes-json"

# Spanish cultural context
SPANISH_CONTEXT = {
    'city': 'Madrid',
    'neighborhood': 'Malasaña',
    'breakfast_item': 'churro',  # instead of croissant
    'greeting': '¿Qué tal?',  # instead of 'Ça va?'
    'mountains': 'los Pirineos',  # instead of 'les Alpes'
}


def extract_french_scene_phrases(scene_file: Path) -> List[Dict]:
    """Extract phrases from French scene JSON."""
    with open(scene_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get('fr', [])


def create_translation_prompt(scene_num: int, french_phrases: List[Dict]) -> str:
    """Create prompt for OpenAI to translate and adapt scene."""
    
    phrases_text = "\n".join([
        f"{i+1}. {p['fr']}"
        for i, p in enumerate(french_phrases)
    ])
    
    return f"""You are adapting a story from Paris to Madrid (Malasaña neighborhood).

SCENE {scene_num} CONTEXT:
- Original: Paris, Le Marais
- Adapted: Madrid, Malasaña  
- Characters: Sophie Moreno & Lucas Ruiz (young Spanish adults)
- Cultural shifts: croissant→churro, métro→metro, Paris landmarks→Madrid landmarks

TASK: For each numbered French phrase, provide:
1. Natural Spanish translation (Madrid dialect, informal/conversational)
2. English translation
3. IPA transcription (Spanish phonemes)

CULTURAL ADAPTATION RULES:
- Use "tú" form (they're friends)
- Spanish greetings: "¿Qué tal?" not "Ça va?"
- Food: churros, tostada, café con leche (Spanish items)
- Replace French places with Madrid equivalents naturally
- Keep emotional tone and character personality

OUTPUT FORMAT (JSON array):
[
  {{
    "es": "Spanish translation here",
    "english": "English translation here", 
    "ipa": "[Spanish IPA transcription]"
  }},
  ...
]

FRENCH PHRASES TO ADAPT:
{phrases_text}

Return ONLY the JSON array, no explanation or markdown."""


def process_scene(scene_num: int, client: OpenAI) -> Dict:
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
    
    # Create prompt
    prompt = create_translation_prompt(scene_num, french_phrases)
    
    # Call OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # Using GPT-4 Turbo
            messages=[
                {"role": "system", "content": "You are an expert translator specializing in Spanish (Spain) with deep knowledge of Madrid culture and IPA phonetic transcription."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Clean up markdown code blocks if present
        result_text = re.sub(r'```json\n?|\n?```', '', result_text)
        
        # Parse JSON
        spanish_phrases = json.loads(result_text)
        
        print(f"    ✓ Translated {len(spanish_phrases)} phrases")
        
        # Translate scene title
        title_response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Translate to Spanish (Spain)."},
                {"role": "user", "content": f"Translate this scene title to natural Spanish: '{scene_title_en}'.\nRespond with ONLY the Spanish translation, nothing else."}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        scene_title_es = title_response.choices[0].message.content.strip()
        
        # Build scene data
        scene_data = {
            "es": spanish_phrases,
            "scene_number": scene_num,
            "scene_title": scene_title_es
        }
        
        return scene_data
        
    except Exception as e:
        print(f"    ❌ Error translating scene {scene_num}: {e}")
        return None


def save_scene(scene_num: int, scene_data: Dict) -> None:
    """Save scene data to JSON file."""
    # Create filename from title
    title_slug = scene_data['scene_title'].lower()
    title_slug = re.sub(r'[^\w\s-]', '', title_slug)
    title_slug = re.sub(r'[-\s]+', '-', title_slug)
    
    filename = f"scene-{scene_num:02d}-{title_slug}.json"
    output_path = ES_OUTPUT_DIR / filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(scene_data, f, ensure_ascii=False, indent=2)
    
    print(f"    💾 Saved: {filename}")


def main():
    """Main execution."""
    print("=" * 60)
    print("🇪🇸 Spanish Story Generation (OpenAI)")
    print("=" * 60)
    print(f"\nSource: {FR_SCENES_DIR}")
    print(f"Output: {ES_OUTPUT_DIR}\n")
    
    # Check API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("   Set it with: export OPENAI_API_KEY='sk-...'")
        return
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Create output directory
    ES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process all 16 scenes
    print("📚 Processing 16 scenes...\n")
    
    successful = 0
    failed = 0
    
    for scene_num in range(1, 17):
        try:
            scene_data = process_scene(scene_num, client)
            
            if scene_data:
                save_scene(scene_num, scene_data)
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
    print("✅ Spanish Story Generation Complete!")
    print("=" * 60)
    print(f"\n📊 Results:")
    print(f"   ✓ Successful: {successful} scenes")
    if failed > 0:
        print(f"   ✗ Failed: {failed} scenes")
    
    print(f"\n📁 Output: {ES_OUTPUT_DIR}")
    print("\n📋 Next steps:")
    print("   1. Review generated files")
    print("   2. Test in Story Reader (select Spanish)")
    print("   3. Verify cultural adaptations are natural")
    print("   4. Check IPA transcriptions")
    print("   5. If good, run for German/Dutch/Italian!")


if __name__ == '__main__':
    main()
