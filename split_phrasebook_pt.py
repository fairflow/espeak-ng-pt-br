#!/usr/bin/env python3
"""
Split Portuguese phrasebook_complete.json into topic-based text files.
"""
import json
from pathlib import Path
from collections import defaultdict

# Load complete phrasebook
input_file = Path('language_materials/pt/phrasebook_complete.json')
print(f"Loading {input_file}...")

with open(input_file, 'r', encoding='utf-8') as f:
    phrasebook = json.load(f)

# Group phrases by situation
by_situation = defaultdict(list)
for phrase in phrasebook["phrases"]:
    situation = phrase["situation"]
    portuguese = phrase["portuguese"]
    english = phrase["english"]
    ipa = phrase["ipa"]
    level = phrase["level"]
    
    by_situation[situation].append({
        "portuguese": portuguese,
        "english": english,
        "ipa": ipa,
        "level": level
    })

# Topic file mapping (consistent with French structure)
topic_files = {
    "greetings": "01-greetings.txt",
    "farewells": "02-farewells.txt",
    "courtesy": "03-courtesy-basics.txt",
    "introductions": "04-introductions.txt",
    "asking_for_help": "05-asking-for-help.txt",
    "directions": "06-directions.txt",
    "shopping": "07-shopping.txt",
    "restaurant": "08-restaurant.txt",
    "conversation": "09-conversation.txt",
    "feelings": "10-feelings-emotions.txt",
    "exclamations": "11-exclamations.txt",
    "basics": "basics.txt",
}

# Create output directory
output_dir = Path('language_materials/pt/phrasebook-topics')
output_dir.mkdir(parents=True, exist_ok=True)

# Write each topic file
print("\nCreating topic files...")
total_phrases = 0

for situation, filename in topic_files.items():
    if situation not in by_situation:
        print(f"  ⚠️  No phrases for situation: {situation}")
        continue
    
    phrases = by_situation[situation]
    output_file = output_dir / filename
    
    # Sort by level (A, B, C, D)
    phrases.sort(key=lambda p: (p['level'], p['portuguese']))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Portuguese Phrasebook - {situation.replace('_', ' ').title()}\n")
        f.write(f"# Level distribution: {', '.join(set(p['level'] for p in phrases))}\n")
        f.write(f"# Format: portuguese | english | [ipa]\n\n")
        
        for phrase in phrases:
            line = f"{phrase['portuguese']} | {phrase['english']} | [{phrase['ipa']}]\n"
            f.write(line)
    
    total_phrases += len(phrases)
    print(f"  ✓ {filename}: {len(phrases)} phrases")

print(f"\n✅ Complete! {len(topic_files)} topic files created")
print(f"📍 Location: {output_dir}")
print(f"📊 Total phrases: {total_phrases}")
