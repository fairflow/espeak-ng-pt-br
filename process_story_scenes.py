#!/usr/bin/env python3
"""
Process story scene files into JSON format with translations and IPA.
Splits longer phrases at full stops and dashes for better practice.
"""

import os
import re
import json
import subprocess

def get_ipa_transcription(text, language_code):
    """Get IPA transcription using espeak."""
    try:
        # Use local build of espeak-ng to generate IPA
        espeak_bin = './src/.libs/espeak-ng'
        result = subprocess.run(
            [espeak_bin, '-v', language_code, '-q', '--ipa', text],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        if result.returncode == 0:
            # Clean up the IPA output
            ipa = result.stdout.strip()
            # Remove the underscore markers and extra spaces
            ipa = re.sub(r'_:', '', ipa)
            ipa = re.sub(r'\s+', ' ', ipa)
            return ipa
        else:
            print(f"Warning: Could not generate IPA for: {text[:50]}")
            return ""
    except Exception as e:
        print(f"Error generating IPA: {e}")
        return ""

def split_phrase_at_punctuation(phrase):
    """
    Split longer phrases at full stops and dashes.
    Returns list of smaller phrases.
    """
    # Skip if already short
    if len(phrase) < 60:
        return [phrase]
    
    parts = []
    
    # Split at periods followed by space (sentence boundaries)
    sentence_parts = re.split(r'\.\s+', phrase)
    
    for part in sentence_parts:
        if not part.strip():
            continue
            
        # Split at em dashes or double hyphens
        dash_parts = re.split(r'—|--', part)
        
        for dash_part in dash_parts:
            dash_part = dash_part.strip()
            if dash_part:
                # Add back period if it was at the end
                if part == sentence_parts[-1] and phrase.rstrip().endswith('.'):
                    dash_part = dash_part.rstrip('.') + '.'
                parts.append(dash_part)
    
    return parts if parts else [phrase]

def translate_to_english(french_text):
    """
    Manual translations for common story phrases.
    For now, returns placeholder - will be filled in by hand.
    """
    # Common translations we can do automatically
    translations = {
        "Bonjour": "Hello",
        "Merci": "Thank you",
        "Oui": "Yes",
        "Non": "No",
        "Bonne idée!": "Good idea!",
        "Parfait": "Perfect",
        "D'accord": "Okay",
        "Pourquoi pas?": "Why not?",
        "Tu as raison!": "You're right!",
        "Salut!": "Hi!",
        "Bon appétit!": "Enjoy your meal!",
        "Attention!": "Watch out!",
        "Pardon": "Sorry",
        "Excusez-moi": "Excuse me",
        "S'il vous plaît": "Please",
    }
    
    # Check for exact matches
    if french_text in translations:
        return translations[french_text]
    
    # Return placeholder for manual translation
    return "[TO TRANSLATE]"

def process_scene_file(scene_path):
    """Process a scene file into JSON format."""
    with open(scene_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract scene info from header
    scene_match = re.search(r'# French Story - Scene (\d+): (.+)', content)
    if not scene_match:
        return None
    
    scene_num = scene_match.group(1)
    scene_title = scene_match.group(2)
    
    # Extract phrases (skip header lines)
    lines = content.split('\n')
    phrases = []
    
    for line in lines:
        line = line.strip()
        # Skip headers and empty lines
        if line.startswith('#') or not line:
            continue
        
        # Split long phrases at punctuation
        sub_phrases = split_phrase_at_punctuation(line)
        
        for phrase in sub_phrases:
            phrase = phrase.strip()
            if phrase:
                phrases.append(phrase)
    
    print(f"Scene {scene_num}: {len(phrases)} phrases extracted")
    return {
        'scene_number': scene_num,
        'scene_title': scene_title,
        'phrases': phrases
    }

def create_json_practice_file(scene_data, output_path):
    """Create JSON practice file with translations and IPA."""
    practice_data = []
    
    print(f"\nGenerating IPA for Scene {scene_data['scene_number']}...")
    
    for idx, french_phrase in enumerate(scene_data['phrases'], 1):
        # Get IPA transcription
        ipa = get_ipa_transcription(french_phrase, 'fr-fr')
        
        # Get or prepare translation
        english = translate_to_english(french_phrase)
        
        entry = {
            "french": french_phrase,
            "english": english,
            "ipa": ipa
        }
        
        practice_data.append(entry)
        
        # Progress indicator
        if idx % 10 == 0:
            print(f"  Processed {idx}/{len(scene_data['phrases'])} phrases...")
    
    # Write JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(practice_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Created: {output_path}")
    return len(practice_data)

def main():
    # Paths
    scenes_dir = 'language_materials/fr/story-scenes'
    output_dir = 'language_materials/fr/story-scenes-json'
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all scene files
    scene_files = sorted([f for f in os.listdir(scenes_dir) if f.endswith('.txt')])
    
    total_phrases = 0
    
    for scene_file in scene_files:
        print(f"\n{'='*60}")
        print(f"Processing: {scene_file}")
        print('='*60)
        
        scene_path = os.path.join(scenes_dir, scene_file)
        scene_data = process_scene_file(scene_path)
        
        if scene_data:
            # Create output filename
            output_file = scene_file.replace('.txt', '.json')
            output_path = os.path.join(output_dir, output_file)
            
            # Generate JSON with IPA
            num_phrases = create_json_practice_file(scene_data, output_path)
            total_phrases += num_phrases
    
    print(f"\n{'='*60}")
    print(f"✓ All scenes processed!")
    print(f"✓ Total phrases: {total_phrases}")
    print(f"✓ Output directory: {output_dir}")
    print(f"\nNext steps:")
    print(f"1. Review JSON files and add English translations where marked [TO TRANSLATE]")
    print(f"2. Verify IPA transcriptions are correct")
    print(f"3. Use split_phrasebook.py to create topic files")
    print('='*60)

if __name__ == '__main__':
    main()
