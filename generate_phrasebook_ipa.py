#!/usr/bin/env python3
import json
import subprocess
import os
from pathlib import Path

# Set eSpeak NG data path
os.environ['ESPEAK_DATA_PATH'] = '/Users/matthew/Software/working/adaptive-text/espeak-ng/espeak-ng-data'

# Load phrasebook
with open('language_materials/fr/phrasebook_raw.json', 'r', encoding='utf-8') as f:
    phrasebook = json.load(f)

# Common French translations
translations = {
    "Bonjour": "Hello",
    "Bonsoir": "Good evening",
    "Salut": "Hi",
    "Au revoir": "Goodbye",
    "À bientôt": "See you soon",
    "À demain": "See you tomorrow",
    "Bonne journée": "Have a good day",
    "Bonne soirée": "Have a good evening",
    "Bonne nuit": "Good night",
    "Merci": "Thank you",
    "Merci beaucoup": "Thank you very much",
    "De rien": "You're welcome",
    "S'il vous plaît": "Please",
    "S'il te plaît": "Please",
    "Excusez-moi": "Excuse me",
    "Pardon": "Pardon",
    "Désolé": "Sorry",
    "Oui": "Yes",
    "Non": "No",
    "Comment allez-vous?": "How are you?",
    "Comment ça va?": "How are you?",
    "Ça va": "I'm fine",
    "Ça va bien": "I'm doing well",
    "Je vais bien, merci": "I'm fine, thank you",
    "Et vous?": "And you?",
    "Je m'appelle...": "My name is...",
    "Comment vous appelez-vous?": "What is your name?",
    "Enchanté": "Nice to meet you",
    "Enchantée": "Nice to meet you",
    "Ravi de faire votre connaissance": "Pleased to meet you",
    "D'où venez-vous?": "Where are you from?",
    "Je viens de...": "I come from...",
    "Je ne comprends pas": "I don't understand",
    "Je ne parle pas français": "I don't speak French",
    "Je parle un peu français": "I speak a little French",
    "Parlez-vous anglais?": "Do you speak English?",
    "Plus lentement, s'il vous plaît": "Slower, please",
    "Pouvez-vous répéter?": "Can you repeat?",
    "Comment dit-on... en français?": "How do you say... in French?",
    "Qu'est-ce que ça veut dire?": "What does that mean?",
    "J'ai besoin d'aide": "I need help",
    "Pouvez-vous m'aider?": "Can you help me?",
    "Où est...?": "Where is...?",
    "Où se trouve...?": "Where is...?",
    "Où sont les toilettes?": "Where is the bathroom?",
    "C'est loin d'ici?": "Is it far from here?",
    "C'est près d'ici?": "Is it near here?",
    "À gauche": "To the left",
    "À droite": "To the right",
    "Tout droit": "Straight ahead",
    "Je cherche...": "I'm looking for...",
    "Combien ça coûte?": "How much does it cost?",
    "C'est combien?": "How much is it?",
    "C'est trop cher": "It's too expensive",
    "Je voudrais...": "I would like...",
    "Avez-vous...?": "Do you have...?",
    "Quelle taille?": "What size?",
    "Puis-je essayer?": "Can I try it?",
    "Je vais prendre ça": "I'll take this",
    "Puis-je payer par carte?": "Can I pay by card?",
    "Une table pour deux, s'il vous plaît": "A table for two, please",
    "Le menu, s'il vous plaît": "The menu, please",
    "L'addition, s'il vous plaît": "The bill, please",
    "C'était délicieux": "It was delicious",
    "Qu'est-ce que vous recommandez?": "What do you recommend?",
    "Je suis végétarien": "I'm vegetarian",
    "Je suis allergique à...": "I'm allergic to...",
    "Un café, s'il vous plaît": "A coffee, please",
    "Une carafe d'eau, s'il vous plaît": "A carafe of water, please",
    "Comment vas-tu?": "How are you?",
    "Qu'est-ce que tu fais?": "What are you doing?",
    "Tu fais quoi?": "What are you doing?",
    "Ça te dit?": "How about it?",
    "J'ai envie de...": "I feel like...",
    "Tu veux prendre un verre?": "Want to get a drink?",
    "Comment va le travail?": "How's work?",
    "Comment va ta famille?": "How's your family?",
    "Tiens-moi au courant": "Keep me updated",
    "Tu t'en sors?": "Are you managing?",
    "Je suis content": "I'm happy",
    "Je suis contente": "I'm happy",
    "Je suis fatigué": "I'm tired",
    "Je suis fatiguée": "I'm tired",
    "J'ai faim": "I'm hungry",
    "J'ai soif": "I'm thirsty",
    "J'ai chaud": "I'm hot",
    "J'ai froid": "I'm cold",
    "Je suis crevé": "I'm exhausted",
    "J'ai le cafard": "I'm feeling down",
    "J'ai hâte": "I can't wait",
    "Je m'ennuie": "I'm bored",
    "Ah bon!": "Oh really!",
    "N'importe quoi!": "Whatever!",
    "C'est n'importe quoi!": "That's nonsense!",
    "Laisse tomber": "Forget it",
    "Bref": "Anyway",
    "Dis donc!": "Wow!",
    "La vache!": "Holy cow!",
    "C'est nul": "That sucks",
    "Allez!": "Come on!",
    "Bof": "Meh",
}

def get_ipa(text):
    try:
        result = subprocess.run(
            ['espeak', '-v', 'fr-fr', '-q', '--ipa', text],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip().replace('_', '').replace('\n', ' ')
        return ""
    except:
        return ""

# Process phrases
print("Generating translations and IPA...")
for i, phrase in enumerate(phrasebook["phrases"], 1):
    french = phrase["french"]
    phrase["english"] = translations.get(french, "[NEEDS TRANSLATION]")
    phrase["ipa"] = get_ipa(french)
    
    if i % 20 == 0:
        print(f"  {i}/{len(phrasebook['phrases'])} processed")

# Save
output_path = Path('language_materials/fr/phrasebook_complete.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(phrasebook, f, ensure_ascii=False, indent=2)

missing = sum(1 for p in phrasebook["phrases"] if p["english"] == "[NEEDS TRANSLATION]")
print(f"\n✅ Complete! {len(phrasebook['phrases'])} phrases with IPA")
print(f"📍 Location: {output_path}")
print(f"📊 Translated: {len(phrasebook['phrases']) - missing}/{len(phrasebook['phrases'])}")
