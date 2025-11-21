#!/usr/bin/env python3
"""
Translate story.md from French to other languages using OpenAI.
Preserves markdown structure and applies cultural adaptations.
"""

import os
import sys
from pathlib import Path
from openai import OpenAI

# Language configurations with cultural context
LANGUAGE_CONFIGS = {
    'es': {
        'name': 'Spanish',
        'native_name': 'Español',
        'city': 'Madrid',
        'neighborhood': 'Malasaña',
        'surnames': ['Moreno', 'Ruiz'],
        'breakfast_item': 'churro',
        'greeting': '¿Qué tal?',
        'mountains': 'Pirineos',
        'title': 'Una Aventura en los Pirineos',
        'scenes_heading': 'ESCENAS',
        'scene_label': 'ESCENA'
    },
    'de': {
        'name': 'German',
        'native_name': 'Deutsch',
        'city': 'Berlin',
        'neighborhood': 'Kreuzberg',
        'surnames': ['Schmidt', 'Müller'],
        'breakfast_item': 'Brötchen',
        'greeting': 'Wie geht\'s?',
        'mountains': 'Alpen',
        'title': 'Ein Abenteuer in den Alpen',
        'scenes_heading': 'SZENEN',
        'scene_label': 'SZENE'
    },
    'nl': {
        'name': 'Dutch',
        'native_name': 'Nederlands',
        'city': 'Amsterdam',
        'neighborhood': 'De Pijp',
        'surnames': ['de Vries', 'van der Berg'],
        'breakfast_item': 'stroopwafel',
        'greeting': 'Hoe gaat het?',
        'mountains': 'Ardennen',
        'title': 'Een Avontuur in de Ardennen',
        'scenes_heading': 'SCÈNES',
        'scene_label': 'SCÈNE'
    },
    'it': {
        'name': 'Italian',
        'native_name': 'Italiano',
        'city': 'Rome',
        'neighborhood': 'Trastevere',
        'surnames': ['Rossi', 'Bianchi'],
        'breakfast_item': 'cornetto',
        'greeting': 'Come va?',
        'mountains': 'Alpi',
        'title': 'Un\'Avventura nelle Alpi',
        'scenes_heading': 'SCENE',
        'scene_label': 'SCENA'
    },
    'pt': {
        'name': 'Portuguese',
        'native_name': 'Português',
        'city': 'São Paulo',
        'neighborhood': 'Vila Madalena',
        'surnames': ['Moreira', 'Duarte'],
        'breakfast_item': 'pão na chapa',
        'greeting': 'Tudo bem?',
        'mountains': 'Serra da Mantiqueira',
        'title': 'Uma Aventura nas Montanhas',
        'scenes_heading': 'CENAS',
        'scene_label': 'CENA'
    }
}

def translate_story(lang_code: str):
    """Translate French story.md to target language."""
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("   Set it with: export OPENAI_API_KEY='sk-...'")
        return
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Get language config
    if lang_code not in LANGUAGE_CONFIGS:
        print(f"❌ Error: Language '{lang_code}' not supported")
        print(f"   Supported: {', '.join(LANGUAGE_CONFIGS.keys())}")
        return
    
    config = LANGUAGE_CONFIGS[lang_code]
    
    # Paths
    base_dir = Path(__file__).parent.parent
    fr_story = base_dir / "language_materials" / "fr" / "story.md"
    target_story = base_dir / "language_materials" / lang_code / "story.md"
    
    if not fr_story.exists():
        print(f"❌ Error: French story not found: {fr_story}")
        return
    
    # Read French story
    print(f"\n{'='*60}")
    print(f"📖 Story Translation: French → {config['name']}")
    print(f"{'='*60}\n")
    print(f"Source: {fr_story}")
    print(f"Target: {target_story}")
    print(f"Setting: {config['city']}, {config['neighborhood']}")
    
    with open(fr_story, 'r', encoding='utf-8') as f:
        french_text = f.read()
    
    # Count sections
    scene_count = french_text.count('### SCÈNE')
    print(f"\n📚 Processing story with {scene_count} scenes...")
    
    # Create translation prompt
    prompt = f"""You are translating a French language learning story into {config['name']} for learners.

STORY CONTEXT:
- Original: Paris, Le Marais neighborhood
- Characters: Sophie Moreau & Lucas Dubois (young adults, friends)
- Target: {config['city']}, {config['neighborhood']} neighborhood
- New surnames: Sophie {config['surnames'][0]} & Lucas {config['surnames'][1]}

CULTURAL ADAPTATION REQUIRED:
1. Replace Paris/Le Marais with {config['city']}/{config['neighborhood']}
2. Change character surnames: Moreau → {config['surnames'][0]}, Dubois → {config['surnames'][1]}
3. Replace French cultural items:
   - "croissant" → "{config['breakfast_item']}"
   - "Ça va?" / "Bonjour" → "{config['greeting']}" and natural {config['name']} greetings
   - "les Alpes" → "{config['mountains']}"
4. Use informal, conversational {config['name']} (tú/du/jij/tu form)
5. Keep emotional tone and narrative style

MARKDOWN STRUCTURE:
- Title: # {config['title']}
- Section: ## {config['scenes_heading']}
- Scene headers: ### {config['scene_label']} [number]: [Scene Title in {config['name']}]
- Preserve all paragraph breaks and dialogue formatting
- Keep guillemets (« ») or use {config['name']} quote style

TRANSLATION GUIDELINES:
- Natural, conversational {config['name']} that sounds authentic
- Maintain story flow and emotional beats
- Adapt idioms and expressions culturally
- Keep proper names where appropriate (Marc the waiter can stay Marc)
- Translate scene titles naturally

Return ONLY the translated markdown text. No explanations or commentary.

FRENCH STORY TO TRANSLATE:

{french_text}"""
    
    # Split story into scenes for manageable chunks
    scenes = french_text.split('### SCÈNE ')
    header = scenes[0]  # Title and introduction
    scene_parts = scenes[1:]  # Individual scenes
    
    print(f"🤖 Translating story in chunks...")
    
    translated_parts = []
    
    # Translate header
    print(f"   → Translating header...")
    try:
        header_prompt = f"""Translate this French story header to {config['name']}.

ADAPTATIONS:
- Title should be: {config['title']}
- Replace "SCÈNES" with "{config['scenes_heading']}"
- Keep markdown formatting

FRENCH TEXT:
{header}

Return ONLY the translated text."""

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": f"Expert {config['name']} translator."},
                {"role": "user", "content": header_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        translated_header = response.choices[0].message.content.strip()
        translated_parts.append(translated_header)
        print(f"      ✓ Header translated")
        
    except Exception as e:
        print(f"      ❌ Header translation failed: {e}")
        return
    
    # Translate scenes in batches of 2
    batch_size = 2
    for i in range(0, len(scene_parts), batch_size):
        batch = scene_parts[i:i+batch_size]
        batch_text = '### SCÈNE ' + '\n### SCÈNE '.join(batch)
        scene_nums = f"{i+1}-{min(i+batch_size, len(scene_parts))}"
        
        print(f"   → Translating scenes {scene_nums}/{len(scene_parts)}...")
        
        try:
            scene_prompt = f"""Translate these French story scenes to {config['name']}.

ADAPTATIONS:
- Paris/Le Marais → {config['city']}/{config['neighborhood']}
- Moreau → {config['surnames'][0]}, Dubois → {config['surnames'][1]}
- croissant → {config['breakfast_item']}
- "Ça va?" → "{config['greeting']}"
- les Alpes → {config['mountains']}
- Use "### {config['scene_label']}" for scene headers
- Keep conversational, informal {config['name']}
- Preserve paragraph breaks and dialogue formatting

FRENCH SCENES:
{batch_text}

Return ONLY the translated scenes."""

            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": f"Expert {config['name']} translator with {config['city']} cultural knowledge."},
                    {"role": "user", "content": scene_prompt}
                ],
                temperature=0.7,
                max_tokens=4096
            )
            
            translated_batch = response.choices[0].message.content.strip()
            translated_parts.append(translated_batch)
            print(f"      ✓ Scenes {scene_nums} translated")
            
        except Exception as e:
            print(f"      ❌ Scenes {scene_nums} failed: {e}")
            return
    
    # Combine all parts
    try:
        translated_text = '\n\n'.join(translated_parts)
        
        # Clean up any markdown code blocks if present
        import re
        translated_text = re.sub(r'^```markdown\n?', '', translated_text)
        translated_text = re.sub(r'\n?```$', '', translated_text)
        
        # Write output
        target_story.parent.mkdir(parents=True, exist_ok=True)
        with open(target_story, 'w', encoding='utf-8') as f:
            f.write(translated_text)
        
        # Count output
        target_scenes = translated_text.count(f'### {config["scene_label"]}')
        lines = len(translated_text.split('\n'))
        
        print(f"\n{'='*60}")
        print(f"✅ Translation Complete!")
        print(f"{'='*60}")
        print(f"\n📊 Results:")
        print(f"   ✓ Scenes translated: {target_scenes}")
        print(f"   ✓ Total lines: {lines}")
        print(f"   📁 Output: {target_story}")
        print(f"\n💡 Next steps:")
        print(f"   1. Review {target_story} for quality")
        print(f"   2. Test in Story Reader (select {config['name']})")
        print(f"   3. Verify cultural adaptations are natural")
        
    except Exception as e:
        print(f"\n❌ Error during translation: {e}")
        return


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python translate_story_md.py <lang_code>")
        print("Example: python translate_story_md.py es")
        print(f"Supported: {', '.join(LANGUAGE_CONFIGS.keys())}")
        sys.exit(1)
    
    lang_code = sys.argv[1]
    translate_story(lang_code)
