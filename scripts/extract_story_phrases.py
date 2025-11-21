#!/usr/bin/env python3
"""
Extract story phrases from markdown file into JSON scene files.
Usage: python extract_story_phrases.py <lang_code>
Example: python extract_story_phrases.py pt
"""

import json
import re
import sys
from pathlib import Path


def extract_phrases_from_story(story_path, output_dir, lang_code):
    """Extract phrases from story markdown and create JSON files per scene."""
    
    # Read the story
    with open(story_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into scenes
    scenes = re.split(r'### (CENA|SCÈNE|SCENE) (\d+): (.+?)\n', content)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    scene_data = []
    for i in range(1, len(scenes), 4):  # Every 4 items: marker, number, title, content
        if i + 3 > len(scenes):
            break
            
        scene_marker = scenes[i]
        scene_num = scenes[i+1]
        scene_title = scenes[i+2].strip()
        scene_content = scenes[i+3].strip()
        
        # Extract phrases (sentences) from scene content
        # Split by periods, exclamation marks, question marks, and dialogue markers
        phrases = []
        
        # Split into paragraphs first
        paragraphs = scene_content.split('\n\n')
        
        for para in paragraphs:
            para = para.strip()
            if not para or para.startswith('#') or para == '---':
                continue
            
            # Remove dialogue markers
            para = para.replace('«', '').replace('»', '')
            
            # Split into sentences
            sentences = re.split(r'([.!?]+\s+|[.!?]+$)', para)
            
            current_sentence = ''
            for part in sentences:
                if re.match(r'[.!?]+', part):
                    current_sentence += part.strip()
                    if current_sentence:
                        clean_sentence = current_sentence.strip()
                        if clean_sentence and len(clean_sentence) > 3:
                            phrases.append(clean_sentence)
                    current_sentence = ''
                else:
                    current_sentence += part
            
            # Add any remaining sentence
            if current_sentence.strip() and len(current_sentence.strip()) > 3:
                phrases.append(current_sentence.strip())
        
        # Create JSON structure
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
        
        # Create filename
        filename = f"scene-{scene_num.zfill(2)}-{scene_title.lower().replace(' ', '-').replace(',', '').replace(':', '')}.json"
        filename = re.sub(r'[^a-z0-9\-.]', '', filename)
        
        output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(scene_obj, f, ensure_ascii=False, indent=2)
        
        print(f"Created {filename} with {len(phrases)} phrases")
        scene_data.append({
            'scene': int(scene_num),
            'title': scene_title,
            'filename': filename,
            'phrase_count': len(phrases)
        })
    
    return scene_data


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_story_phrases.py <lang_code>")
        print("Example: python extract_story_phrases.py pt")
        sys.exit(1)
    
    lang_code = sys.argv[1]
    
    # Paths
    story_path = Path(f"language_materials/{lang_code}/story.md")
    output_dir = Path(f"language_materials/{lang_code}/story-scenes-json")
    
    if not story_path.exists():
        print(f"Error: Story file not found: {story_path}")
        sys.exit(1)
    
    print(f"Extracting phrases from {story_path}...")
    scene_data = extract_phrases_from_story(story_path, output_dir, lang_code)
    
    # Summary
    total_phrases = sum(s['phrase_count'] for s in scene_data)
    print(f"\n✓ Created {len(scene_data)} scene files")
    print(f"✓ Total phrases extracted: {total_phrases}")
    print(f"✓ Output directory: {output_dir}")
    
    # Show scene breakdown
    print("\nScene breakdown:")
    for scene in scene_data:
        print(f"  Scene {scene['scene']:2d}: {scene['phrase_count']:3d} phrases - {scene['title']}")


if __name__ == "__main__":
    main()
