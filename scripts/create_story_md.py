#!/usr/bin/env python3
"""
Generate story.md from story-scenes-json files.
Converts JSON scene phrases into a narrative markdown format.
"""

import json
from pathlib import Path
import sys

def create_story_md(lang_code: str):
    """Create story.md from scene JSON files for a given language."""
    
    # Paths
    base_dir = Path(__file__).parent.parent
    scenes_dir = base_dir / "language_materials" / lang_code / "story-scenes-json"
    output_file = base_dir / "language_materials" / lang_code / "story.md"
    
    if not scenes_dir.exists():
        print(f"❌ Error: Scenes directory not found: {scenes_dir}")
        return
    
    # Get all scene files
    scene_files = sorted(scenes_dir.glob("scene-*.json"))
    
    if not scene_files:
        print(f"❌ Error: No scene files found in {scenes_dir}")
        return
    
    # Language-specific titles
    titles = {
        'es': ('Una Aventura en los Pirineos', 'ESCENAS', 'ESCENA'),
        'de': ('Ein Abenteuer in den Alpen', 'SZENEN', 'SZENE'),
        'nl': ('Een Avontuur in de Ardennen', 'SCÈNES', 'SCÈNE'),
        'it': ('Un\'Avventura nelle Alpi', 'SCENE', 'SCENA'),
        'pt': ('Uma Aventura nas Montanhas', 'CENAS', 'CENA'),
        'fr': ('Une Aventure dans les Alpes', 'SCÈNES', 'SCÈNE')
    }
    
    main_title, scenes_heading, scene_label = titles.get(lang_code, ('Story', 'SCENES', 'SCENE'))
    
    # Start building the story
    story_lines = [
        f"# {main_title}",
        "",
        f"## {scenes_heading}",
        ""
    ]
    
    print(f"📚 Creating story.md for {lang_code.upper()}...")
    print(f"   Processing {len(scene_files)} scenes...")
    
    # Process each scene
    for scene_file in scene_files:
        try:
            with open(scene_file, 'r', encoding='utf-8') as f:
                scene_data = json.load(f)
            
            # Get scene metadata
            scene_num = scene_data.get('scene_number', 0)
            scene_title = scene_data.get('scene_title', 'Untitled')
            phrases = scene_data.get(lang_code, [])
            
            if not phrases:
                print(f"   ⚠️  Scene {scene_num} has no phrases, skipping...")
                continue
            
            # Add scene header
            story_lines.append(f"### {scene_label} {scene_num}: {scene_title}")
            story_lines.append("")
            
            # Build narrative from phrases
            # Group phrases into paragraphs (dialogue vs narrative)
            current_paragraph = []
            
            for phrase_obj in phrases:
                text = phrase_obj.get(lang_code, '').strip()
                
                if not text:
                    continue
                
                # Check if this is dialogue (starts with « or ")
                is_dialogue = text.startswith('«') or text.startswith('"') or text.startswith('¿') or text.startswith('—')
                
                # If transitioning between dialogue and narrative, start new paragraph
                if current_paragraph:
                    last_text = current_paragraph[-1]
                    last_is_dialogue = last_text.startswith('«') or last_text.startswith('"') or last_text.startswith('¿') or last_text.startswith('—')
                    
                    if is_dialogue != last_is_dialogue:
                        # Flush current paragraph
                        story_lines.append(' '.join(current_paragraph))
                        story_lines.append("")
                        current_paragraph = []
                
                current_paragraph.append(text)
                
                # For dialogue, end paragraph after each line
                if is_dialogue:
                    story_lines.append(' '.join(current_paragraph))
                    story_lines.append("")
                    current_paragraph = []
            
            # Flush any remaining paragraph
            if current_paragraph:
                story_lines.append(' '.join(current_paragraph))
                story_lines.append("")
            
            print(f"   ✓ Scene {scene_num}: {scene_title} ({len(phrases)} phrases)")
            
        except Exception as e:
            print(f"   ❌ Error processing {scene_file.name}: {e}")
            continue
    
    # Write the story file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(story_lines))
        
        print(f"\n✅ Story created successfully!")
        print(f"   📁 Output: {output_file}")
        print(f"   📊 Total lines: {len(story_lines)}")
        
    except Exception as e:
        print(f"\n❌ Error writing story file: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_story_md.py <lang_code>")
        print("Example: python create_story_md.py es")
        sys.exit(1)
    
    lang_code = sys.argv[1]
    create_story_md(lang_code)
