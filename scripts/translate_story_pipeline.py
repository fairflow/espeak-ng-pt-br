#!/usr/bin/env python3
"""
Complete story translation pipeline for any language.
Handles: story translation, phrase extraction, English translation, IPA generation.

Usage: python translate_story_pipeline.py <source_lang> <target_lang_code> <setting_description>

Examples:
  python translate_story_pipeline.py fr de "Black Forest, Germany"
  python translate_story_pipeline.py fr nl "Netherlands countryside"
  python translate_story_pipeline.py fr it "Italian Dolomites"
  python translate_story_pipeline.py fr es "Sierra Nevada, Spain"
"""

import json
import re
import subprocess
import sys
from pathlib import Path


# Story settings by language
STORY_SETTINGS = {
    'pt': {
        'location': 'São Paulo → Serra da Mantiqueira/Campos do Jordão',
        'country': 'Brazil',
        'cafe_item': 'pão na chapa, pão de queijo',
        'transportation': 'Rodoviária do Tietê',
        'highway': 'Rodovia Dutra'
    },
    'de': {
        'location': 'Munich → Black Forest/Bavarian Alps',
        'country': 'Germany',
        'cafe_item': 'Bretzel, Apfelstrudel',
        'transportation': 'Hauptbahnhof',
        'highway': 'Autobahn'
    },
    'nl': {
        'location': 'Amsterdam → Netherlands countryside/Veluwe',
        'country': 'Netherlands',
        'cafe_item': 'stroopwafel, kroket',
        'transportation': 'Centraal Station',
        'highway': 'snelweg'
    },
    'it': {
        'location': 'Milan → Italian Dolomites',
        'country': 'Italy',
        'cafe_item': 'cornetto, espresso',
        'transportation': 'Stazione Centrale',
        'highway': 'autostrada'
    },
    'es': {
        'location': 'Granada → Sierra Nevada',
        'country': 'Spain',
        'cafe_item': 'churros, tostada',
        'transportation': 'Estación de Autobuses',
        'highway': 'autovía'
    }
}

# Espeak voice codes
ESPEAK_VOICES = {
    'pt': 'pt-br',
    'fr': 'fr-fr',
    'nl': 'nl',
    'de': 'de',
    'it': 'it',
    'es': 'es'
}


def extract_phrases_from_story(story_path, output_dir, lang_code):
    """Extract phrases from story markdown and create JSON files per scene."""
    with open(story_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Detect scene markers (multi-language support)
    scene_markers = {
        'pt': 'CENA',
        'fr': 'SCÈNE',
        'de': 'SZENE',
        'nl': 'SCÈNE',
        'it': 'SCENA',
        'es': 'ESCENA'
    }
    
    marker = scene_markers.get(lang_code, 'SCENE')
    scenes = re.split(rf'### ({marker}) (\d+): (.+?)\n', content)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    scene_data = []
    for i in range(1, len(scenes), 4):
        if i + 3 > len(scenes):
            break
            
        scene_num = scenes[i+1]
        scene_title = scenes[i+2].strip()
        scene_content = scenes[i+3].strip()
        
        phrases = []
        paragraphs = scene_content.split('\n\n')
        
        for para in paragraphs:
            para = para.strip()
            if not para or para.startswith('#') or para == '---':
                continue
            
            para = para.replace('«', '').replace('»', '').replace('"', '').replace('"', '')
            sentences = re.split(r'([.!?]+\s+|[.!?]+$)', para)
            
            current_sentence = ''
            for part in sentences:
                if re.match(r'[.!?]+', part):
                    current_sentence += part.strip()
                    if current_sentence and len(current_sentence) > 3:
                        phrases.append(current_sentence.strip())
                    current_sentence = ''
                else:
                    current_sentence += part
            
            if current_sentence.strip() and len(current_sentence.strip()) > 3:
                phrases.append(current_sentence.strip())
        
        scene_obj = {
            f"{lang_code}": [],
            "scene_number": int(scene_num),
            "scene_title": scene_title
        }
        
        for phrase in phrases:
            scene_obj[lang_code].append({
                f"{lang_code}": phrase,
                "english": "[TO TRANSLATE]",
                "ipa": "[TO GENERATE]"
            })
        
        filename = f"scene-{scene_num.zfill(2)}-{scene_title.lower().replace(' ', '-').replace(',', '').replace(':', '')}.json"
        filename = re.sub(r'[^a-z0-9\-.]', '', filename)
        
        output_path = output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(scene_obj, f, ensure_ascii=False, indent=2)
        
        scene_data.append({
            'scene': int(scene_num),
            'phrase_count': len(phrases),
            'filename': filename
        })
    
    return scene_data


def generate_ipa_for_scene(json_file, lang_code):
    """Generate IPA transcriptions for all phrases in a scene using espeak."""
    voice = ESPEAK_VOICES.get(lang_code, lang_code)
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    generated_count = 0
    for phrase_obj in data[lang_code]:
        if phrase_obj['ipa'] == '[TO GENERATE]':
            text = phrase_obj[lang_code]
            try:
                result = subprocess.run(
                    ['espeak', '-q', '-v', voice, '--ipa', text],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    ipa = result.stdout.strip()
                    phrase_obj['ipa'] = f"[{ipa}]"
                    generated_count += 1
            except Exception as e:
                print(f"Warning: IPA generation failed for phrase: {text[:50]}... ({e})")
                phrase_obj['ipa'] = "[GENERATION_FAILED]"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return generated_count


def generate_ipa_for_all_scenes(lang_code):
    """Generate IPA for all scenes of a language."""
    scenes_dir = Path(f"language_materials/{lang_code}/story-scenes-json")
    
    if not scenes_dir.exists():
        print(f"Error: Directory not found: {scenes_dir}")
        return 0
    
    total_generated = 0
    for json_file in sorted(scenes_dir.glob("scene-*.json")):
        count = generate_ipa_for_scene(json_file, lang_code)
        print(f"  ✓ {json_file.name}: {count} IPA transcriptions generated")
        total_generated += count
    
    return total_generated


def main():
    print("=" * 70)
    print("STORY TRANSLATION PIPELINE")
    print("=" * 70)
    
    if len(sys.argv) < 2:
        print("\nUsage: python translate_story_pipeline.py <lang_code> [--extract-only] [--ipa-only]")
        print("\nExamples:")
        print("  python translate_story_pipeline.py pt --ipa-only")
        print("  python translate_story_pipeline.py de --extract-only")
        sys.exit(1)
    
    lang_code = sys.argv[1]
    
    # Check for flags
    extract_only = '--extract-only' in sys.argv
    ipa_only = '--ipa-only' in sys.argv
    
    if ipa_only:
        print(f"\n📝 Generating IPA transcriptions for {lang_code.upper()}...")
        total = generate_ipa_for_all_scenes(lang_code)
        print(f"\n✅ Total IPA transcriptions generated: {total}")
        return
    
    if extract_only:
        print(f"\n📝 Extracting phrases from {lang_code.upper()} story...")
        story_path = Path(f"language_materials/{lang_code}/story.md")
        output_dir = Path(f"language_materials/{lang_code}/story-scenes-json")
        
        if not story_path.exists():
            print(f"Error: Story file not found: {story_path}")
            sys.exit(1)
        
        scene_data = extract_phrases_from_story(story_path, output_dir, lang_code)
        total_phrases = sum(s['phrase_count'] for s in scene_data)
        print(f"\n✅ Extracted {len(scene_data)} scenes with {total_phrases} phrases")
        return
    
    print("\nFor full pipeline (story translation + extraction + IPA),")
    print("please use the subagent or manual translation workflow.")
    print("\nAvailable commands:")
    print("  --extract-only : Extract phrases from existing story.md")
    print("  --ipa-only     : Generate IPA for existing JSON files")


if __name__ == "__main__":
    main()
