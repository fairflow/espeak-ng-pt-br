#!/usr/bin/env python3
"""
Extract practice phrases from the French story, organized by scene.

Creates one file per scene with phrases in chronological order,
preserving context and natural repetitions for effective learning.
"""

import re
import json
from pathlib import Path

STORY_FILE = Path(__file__).parent / "language_materials" / "fr" / "story.md"
OUTPUT_DIR = Path(__file__).parent / "language_materials" / "fr" / "story-scenes"

def extract_scenes_from_story(story_text):
    """Extract individual scenes from the story markdown."""
    # Split by scene headers
    scene_pattern = r'### SCÈNE (\d+): (.+?)\n'
    scenes = re.split(scene_pattern, story_text)
    
    # Group: [intro, num1, title1, content1, num2, title2, content2, ...]
    scene_list = []
    for i in range(1, len(scenes), 3):
        if i+2 <= len(scenes):
            scene_num = scenes[i].zfill(2)
            scene_title = scenes[i+1].strip()
            scene_content = scenes[i+2]
            scene_list.append({
                'num': scene_num,
                'title': scene_title,
                'content': scene_content
            })
    
    return scene_list

def extract_dialogue_phrases(content):
    """Extract French dialogue phrases with context."""
    phrases = []
    
    # Find all quoted dialogue (French uses « » or " ")
    dialogue_pattern = r'[«"]([^»"]+)[»"]'
    matches = re.finditer(dialogue_pattern, content)
    
    for match in matches:
        phrase = match.group(1).strip()
        # Skip very short phrases (just interjections)
        if len(phrase) > 3 and not phrase.endswith('?'):  # Keep questions separate
            phrases.append(phrase)
        elif '?' in phrase:
            phrases.append(phrase)
    
    return phrases

def extract_narrative_phrases(content):
    """Extract key narrative phrases (descriptive sentences)."""
    phrases = []
    
    # Remove dialogue first
    content_no_dialogue = re.sub(r'[«"]([^»"]+)[»"]', '', content)
    
    # Split into sentences
    sentences = re.split(r'[.!?]\s+', content_no_dialogue)
    
    for sentence in sentences:
        sentence = sentence.strip()
        # Keep medium-length sentences that are descriptive
        if 20 < len(sentence) < 150:
            # Skip markdown headers and empty lines
            if not sentence.startswith('#') and sentence:
                phrases.append(sentence + '.')
    
    return phrases

def create_scene_practice_file(scene, phrases):
    """Create a practice text file for one scene."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Create filename from scene number and title slug
    title_slug = re.sub(r'[^\w\s-]', '', scene['title'].lower())
    title_slug = re.sub(r'[-\s]+', '-', title_slug)
    filename = f"scene-{scene['num']}-{title_slug}.txt"
    
    filepath = OUTPUT_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# French Story - Scene {scene['num']}: {scene['title']}\n")
        f.write(f"# Extracted phrases in chronological order\n")
        f.write(f"# Format: french_phrase\n\n")
        
        for phrase in phrases:
            f.write(f"{phrase}\n")
    
    print(f"✓ Created {filename} ({len(phrases)} phrases)")
    return len(phrases)

def main():
    """Extract and organize story phrases by scene."""
    print("Extracting phrases from French story...")
    
    if not STORY_FILE.exists():
        print(f"Error: Story file not found at {STORY_FILE}")
        return
    
    story_text = STORY_FILE.read_text(encoding='utf-8')
    scenes = extract_scenes_from_story(story_text)
    
    print(f"Found {len(scenes)} scenes")
    
    total_phrases = 0
    for scene in scenes:
        # Extract both dialogue and narrative
        dialogue = extract_dialogue_phrases(scene['content'])
        narrative = extract_narrative_phrases(scene['content'])
        
        # Combine in order they appear
        all_phrases = []
        content = scene['content']
        
        # Simple approach: extract in order from content
        for phrase in dialogue + narrative:
            if phrase in content:
                all_phrases.append(phrase)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_phrases = []
        for p in all_phrases:
            if p not in seen:
                seen.add(p)
                unique_phrases.append(p)
        
        if unique_phrases:
            count = create_scene_practice_file(scene, unique_phrases)
            total_phrases += count
    
    print(f"\n✓ Extraction complete!")
    print(f"✓ {len(scenes)} scene files created")
    print(f"✓ {total_phrases} total practice phrases")
    print(f"✓ Output directory: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
