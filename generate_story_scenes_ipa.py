#!/usr/bin/env python3
"""
Generate IPA transcriptions and English translations for story scene JSON files using eSpeak.

Usage:
    python3 generate_story_scenes_ipa.py

Requirements:
    - espeak command (not espeak-ng)
    - Run in venv: source venv/bin/activate
"""
import json
import sys
import subprocess
from pathlib import Path

# Language configuration
LANG_CODE = 'fr'
LANG_NAME = 'French'
LANG_KEY = 'french'
VOICE = 'fr-fr'

# English translations for common French phrases
TRANSLATIONS = {
    # Greetings
    "Bonjour": "Hello",
    "Bonjour Sophie, ça va?": "Hello Sophie, how are you?",
    "Bonjour Lucas!": "Hello Lucas!",
    "Salut!": "Hi!",
    "Salut! Tu as bien dormi?": "Hi! Did you sleep well?",
    "Bonsoir": "Good evening",
    
    # Responses
    "Oui": "Yes",
    "Non": "No",
    "Oui, bien merci. Et toi?": "Yes, well thank you. And you?",
    "Non, pas très bien. J'ai fait des rêves étranges.": "No, not very well. I had strange dreams.",
    "Ça va. Qu'est-ce que tu prends ce matin?": "I'm fine. What are you having this morning?",
    
    # Polite expressions
    "Merci": "Thank you",
    "Merci,": "Thank you,",
    "S'il vous plaît": "Please",
    "s'il vous plaît.": "please.",
    "Pardon": "Sorry",
    "Excusez-moi": "Excuse me",
    "Bon appétit!": "Enjoy your meal!",
    "Voilà pour vous. Bon appétit!": "Here you are. Enjoy your meal!",
    
    # Common phrases
    "Bonne idée!": "Good idea!",
    "Parfait": "Perfect",
    "Parfait, prenons une bouteille.": "Perfect, let's take a bottle.",
    "D'accord": "Okay",
    "D'accord, nous prenons un kilo.": "Okay, we'll take a kilo.",
    "Pourquoi pas?": "Why not?",
    "Tu as raison!": "You're right!",
    "On devrait partir en voyage,": "We should go on a trip,",
    "Tu as raison! Pourquoi pas?": "You're right! Why not?",
    "Attention!": "Watch out!",
    
    # Questions
    "Qu'est-ce que je peux faire pour vous?": "What can I do for you?",
    "Où est la boulangerie?": "Where is the bakery?",
    "Le fromage est frais?": "Is the cheese fresh?",
    "Et combien coûtent les tomates?": "And how much do the tomatoes cost?",
    "On achète du vin?": "Shall we buy some wine?",
    "Quel vin tu préfères?": "Which wine do you prefer?",
    "Tu veux du sucre dans ton café?": "Do you want sugar in your coffee?",
    
    # Food and drink
    "Un café et un croissant, s'il vous plaît.": "A coffee and a croissant, please.",
    "Un café au lait et un pain au chocolat, s'il vous plaît.": "A coffee with milk and a chocolate croissant, please.",
    "Nous avons besoin de pain,": "We need bread,",
    "Le pain est là-bas, près de l'entrée.": "The bread is over there, near the entrance.",
    "Trois euros le kilo.": "Three euros per kilo.",
    "Deux euros le kilo.": "Two euros per kilo.",
    "Le rouge, toujours le rouge.": "Red, always red.",
    "Non merci, je le prends noir.": "No thanks, I take it black.",
    
    # Observations
    "Oui, c'est une belle journée.": "Yes, it's a beautiful day.",
    "Il fait beau aujourd'hui,": "It's nice today,",
    "C'est trop cher pour moi.": "That's too expensive for me.",
    "Oui, il est très bon. Je l'ai reçu ce matin.": "Yes, it's very good. I received it this morning.",
    "J'aime ce quartier.": "I like this neighborhood.",
    "Moi aussi, c'est très joli. Les vieux bâtiments ont du charme.": "Me too, it's very pretty. The old buildings have charm.",
    
    # Life and philosophy
    "Tu sais, Lucas, la vie est si monotone ici.": "You know, Lucas, life is so monotonous here.",
    "Je suis d'accord avec toi. Chaque jour est pareil.": "I agree with you. Every day is the same.",
}


def get_ipa(text, voice):
    """Get IPA transcription from eSpeak."""
    try:
        result = subprocess.run(
            ['espeak', '-q', '-v', voice, '--ipa', text],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            ipa = result.stdout.strip()
            # Clean up spacing
            ipa = ' '.join(ipa.split())
            return ipa
        return ""
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  Timeout for: {text}")
        return ""
    except FileNotFoundError:
        print(f"❌ espeak command not found. Please install espeak (not espeak-ng)")
        print(f"   Run in venv: source venv/bin/activate")
        sys.exit(1)
    except Exception as e:
        print(f"  ⚠️  Error for '{text}': {e}")
        return ""


def get_english_translation(french_text):
    """Get English translation, either from dictionary or generate basic one."""
    # Check exact match first
    if french_text in TRANSLATIONS:
        return TRANSLATIONS[french_text]
    
    # Check without punctuation
    text_stripped = french_text.rstrip('.,!?')
    if text_stripped in TRANSLATIONS:
        return TRANSLATIONS[text_stripped]
    
    # For dialogue/narrative descriptions, provide generic translation
    if french_text.startswith("demande "):
        return f"asks {french_text[8:]}"
    if french_text.startswith("répond "):
        return f"replies {french_text[7:]}"
    if french_text.startswith("dit "):
        return f"says {french_text[4:]}"
    
    # Return placeholder for manual translation
    return "[TO TRANSLATE]"


def process_scene_file(scene_file):
    """Process a single scene JSON file to add IPA and English."""
    print(f"\n📄 {scene_file.name}")
    
    try:
        with open(scene_file, 'r', encoding='utf-8') as f:
            phrases = json.load(f)
    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON: {e}")
        return 0
    
    if not isinstance(phrases, list):
        print(f"  ❌ Expected list of phrases")
        return 0
    
    updated_count = 0
    total = len(phrases)
    
    for i, phrase_obj in enumerate(phrases, 1):
        french_text = phrase_obj.get('french', '')
        
        if not french_text:
            print(f"  ⚠️  Entry {i} missing 'french' field")
            continue
        
        # Generate IPA if missing or empty
        if not phrase_obj.get('ipa'):
            ipa = get_ipa(french_text, VOICE)
            if ipa:
                phrase_obj['ipa'] = ipa
                updated_count += 1
        
        # Generate English translation if missing or placeholder
        english = phrase_obj.get('english', '')
        if not english or english == '[TO TRANSLATE]':
            translation = get_english_translation(french_text)
            phrase_obj['english'] = translation
            if translation != '[TO TRANSLATE]':
                updated_count += 1
        
        # Show progress
        if i % 10 == 0:
            print(f"  Progress: {i}/{total} phrases processed")
    
    # Save updated file
    with open(scene_file, 'w', encoding='utf-8') as f:
        json.dump(phrases, f, ensure_ascii=False, indent=2)
    
    # Count entries still needing translation
    needs_translation = sum(1 for p in phrases if p.get('english') == '[TO TRANSLATE]')
    
    print(f"  ✓ Updated {updated_count} entries")
    if needs_translation > 0:
        print(f"  ℹ️  {needs_translation} entries still need manual translation")
    
    return updated_count


def main():
    """Main entry point."""
    scenes_dir = Path('language_materials/fr/story-scenes-json')
    
    if not scenes_dir.exists():
        print(f"❌ Directory not found: {scenes_dir}")
        sys.exit(1)
    
    print(f"🔊 Generating IPA and English translations for {LANG_NAME} story scenes...")
    print(f"📂 Directory: {scenes_dir}")
    print(f"🎤 Voice: {VOICE}")
    print()
    
    # Get all JSON files
    scene_files = sorted(scenes_dir.glob('scene-*.json'))
    
    if not scene_files:
        print(f"❌ No scene JSON files found in {scenes_dir}")
        sys.exit(1)
    
    print(f"Found {len(scene_files)} scene files")
    
    total_updated = 0
    
    for scene_file in scene_files:
        updated = process_scene_file(scene_file)
        total_updated += updated
    
    print(f"\n{'='*70}")
    print(f"✅ Complete! Updated {total_updated} entries across {len(scene_files)} files")
    print(f"💾 Files saved in: {scenes_dir}")
    print(f"\nNext steps:")
    print(f"1. Review files and add English translations where marked [TO TRANSLATE]")
    print(f"2. Verify IPA transcriptions are correct")
    print(f"3. Run split_phrasebook.py if needed to create topic files")
    print(f"{'='*70}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
