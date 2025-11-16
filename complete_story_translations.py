#!/usr/bin/env python3
"""
Complete English translations for story scene JSON files using comprehensive translation dictionary.
"""
import json
import sys
from pathlib import Path

# Comprehensive translation dictionary from translate_all_phrases.py
translations = {
    # Scene 1: Café
    "Bonjour Sophie, ça va?": "Hello Sophie, how are you?",
    "Oui, bien merci. Et toi?": "Yes, fine thanks. And you?",
    "Ça va. Qu'est-ce que tu prends ce matin?": "I'm fine. What are you having this morning?",
    "Un café et un croissant, s'il vous plaît.": "A coffee and a croissant, please.",
    "Bonjour Lucas!": "Hello Lucas!",
    "Salut! Tu as bien dormi?": "Hi! Did you sleep well?",
    "Non, pas très bien. J'ai fait des rêves étranges.": "No, not very well. I had strange dreams.",
    "Un café au lait et un pain au chocolat, s'il vous plaît.": "A latte and a pain au chocolat, please.",
    "Voilà pour vous. Bon appétit!": "Here you are. Enjoy your meal!",
    "Merci,": "Thank you,",
    "Tu veux du sucre dans ton café?": "Do you want sugar in your coffee?",
    "Non merci, je le prends noir.": "No thanks, I take it black.",
    "Il fait beau aujourd'hui,": "The weather is nice today,",
    "Oui, c'est une belle journée.": "Yes, it's a beautiful day.",
    "Tu sais, Lucas, la vie est si monotone ici.": "You know, Lucas, life is so monotonous here.",
    "Je suis d'accord avec toi. Chaque jour est pareil.": "I agree with you. Every day is the same.",
    "On devrait partir en voyage,": "We should go on a trip,",
    "Tu as raison! Pourquoi pas?": "You're right! Why not?",
    
    # Narrative descriptions - generic translations
    "Le soleil se lève doucement sur Paris.": "The sun rises gently over Paris.",
    "Les rues du Marais commencent à s'animer.": "The streets of the Marais begin to come alive.",
    "Sophie Moreau entre dans son café préféré, un petit endroit chaleureux au coin de la rue des Rosiers.": "Sophie Moreau enters her favorite café, a small cozy place on the corner of Rue des Rosiers.",
    "demande Marc, le serveur qui la connaît bien.": "asks Marc, the waiter who knows her well.",
    "répond Sophie avec un sourire fatigué.": "Sophie replies with a tired smile.",
    "Sophie s'assoit près de la fenêtre.": "Sophie sits near the window.",
    "Elle regarde les gens qui passent dans la rue.": "She watches people passing in the street.",
    "Quelques minutes plus tard, Lucas Dubois arrive, son sac à dos sur l'épaule.": "A few minutes later, Lucas Dubois arrives, his backpack on his shoulder.",
    "Lucas commande au comptoir.": "Lucas orders at the counter.",
    "Il vient s'asseoir en face de Sophie.": "He comes to sit across from Sophie.",
    "Marc apporte leurs commandes.": "Marc brings their orders.",
    "Lucas regarde Sophie attentivement.": "Lucas looks at Sophie attentively.",
    "remarque Lucas en regardant par la fenêtre.": "Lucas notes, looking out the window.",
    "Ils boivent leur café en silence pendant quelques instants.": "They drink their coffee in silence for a few moments.",
    "Sophie soupire profondément.": "Sophie sighs deeply.",
    "dit Sophie spontanément.": "Sophie says spontaneously.",
    "Lucas la regarde avec surprise, puis un sourire apparaît sur son visage.": "Lucas looks at her with surprise, then a smile appears on his face.",
    
    # Scene 2: Shopping
    "Bonjour,": "Hello,",
    "Qu'est-ce que je peux faire pour vous?": "What can I do for you?",
    "Nous avons besoin de pain,": "We need bread,",
    "Le pain est là-bas, près de l'entrée.": "The bread is over there, near the entrance.",
    "Le fromage est frais?": "Is the cheese fresh?",
    "Oui, il est très bon. Je l'ai reçu ce matin.": "Yes, it's very good. I received it this morning.",
    "Parfait. Et combien coûtent les tomates?": "Perfect. And how much are the tomatoes?",
    "Trois euros le kilo.": "Three euros per kilo.",
    "C'est trop cher pour moi.": "That's too expensive for me.",
    "Regardez,": "Look,",
    "j'ai des tomates d'hier. Deux euros le kilo.": "I have yesterday's tomatoes. Two euros per kilo.",
    "D'accord, nous prenons un kilo.": "Okay, we'll take a kilo.",
    "Où est la boulangerie?": "Where is the bakery?",
    "Elle est au coin de la rue, après l'église.": "It's on the corner of the street, after the church.",
    "J'aime ce quartier.": "I love this neighborhood.",
    "Moi aussi, c'est très joli. Les vieux bâtiments ont du charme.": "Me too, it's very pretty. The old buildings have charm.",
    "On achète du vin?": "Should we buy some wine?",
    "Bonne idée! On peut prendre une bouteille pour ce soir.": "Good idea! We can get a bottle for tonight.",
    "Quel vin tu préfères?": "What wine do you prefer?",
    "Le rouge, toujours le rouge.": "Red, always red.",
    "Parfait, prenons une bouteille.": "Perfect, let's get a bottle.",
    "L'après-midi, Sophie et Lucas se promènent dans les rues du Marais.": "In the afternoon, Sophie and Lucas walk through the streets of the Marais.",
    "Ils entrent dans une petite épicerie.": "They enter a small grocery store.",
    "Lucas examine les fromages sur le comptoir.": "Lucas examines the cheeses on the counter.",
    "Sophie fait la grimace.": "Sophie makes a face.",
    "Ils marchent vers la boulangerie.": "They walk toward the bakery.",
    "Ils entrent dans un petit magasin de vins.": "They enter a small wine shop.",
    "Le propriétaire les conseille et ils repartent avec un bon bordeaux.": "The owner advises them and they leave with a good Bordeaux.",
    
    # Scene 3: Travel planning
    "Tu sais, Lucas, je suis fatigué de cette vie,": "You know, Lucas, I'm tired of this life,",
    "Moi aussi, tout est pareil chaque jour. Métro, boulot, dodo.": "Me too, everything is the same every day. Metro, work, sleep.",
    "On pourrait voyager quelque part. Pour de vrai, pas juste en parler.": "We could travel somewhere. For real, not just talk about it.",
    "Où veux-tu aller?": "Where do you want to go?",
    "Je ne sais pas. Quelque chose de différent. La montagne, peut-être?": "I don't know. Something different. The mountains, maybe?",
    "La montagne! Excellente idée. Les Alpes!": "The mountains! Excellent idea. The Alps!",
    "Tu aimes les montagnes?": "Do you like mountains?",
    "Oui, j'adore. L'air est si pur là-haut.": "Yes, I love them. The air is so pure up there.",
    "Et les paysages sont magnifiques.": "And the landscapes are magnificent.",
    "Exactement. On peut marcher pendant des heures.": "Exactly. We can walk for hours.",
    "D'accord, c'est décidé. On part dans les Alpes.": "Okay, it's decided. We're going to the Alps.",
    "Quand partons-nous?": "When are we leaving?",
    "Le plus tôt possible. Ce week-end?": "As soon as possible. This weekend?",
    "Oui! Préparons nos affaires ce soir.": "Yes! Let's pack our things tonight.",
    
    # Scene 4: Preparation
    "Nous devons faire une liste.": "We need to make a list.",
    "Oui, qu'est-ce qu'on prend?": "Yes, what should we take?",
    "Des vêtements chauds, certainement.": "Warm clothes, certainly.",
    "Et de bonnes chaussures pour marcher.": "And good walking shoes.",
    "N'oublie pas ton appareil photo.": "Don't forget your camera.",
    "Jamais! Je veux prendre beaucoup de photos.": "Never! I want to take lots of photos.",
    "Il faut aussi des provisions.": "We also need supplies.",
    "Du chocolat, des fruits secs, de l'eau.": "Chocolate, dried fruit, water.",
    "Tu as un sac à dos?": "Do you have a backpack?",
    "Oui, j'en ai un grand.": "Yes, I have a big one.",
    "Parfait. Et moi aussi.": "Perfect. Me too.",
    "On part demain matin, d'accord?": "We're leaving tomorrow morning, okay?",
    "D'accord! Je suis tellement excité!": "Okay! I'm so excited!",
    "Moi aussi. Ce sera une aventure.": "Me too. It will be an adventure.",
    "Le soir, Sophie et Lucas font leurs bagages.": "In the evening, Sophie and Lucas pack their bags.",
    "Ils vérifient la météo.": "They check the weather.",
    
    # Additional common phrases and narratives
    "Voici la gare de Lyon.": "Here's Lyon station.",
    "Elle est immense!": "It's huge!",
    "Oui, c'est impressionnant.": "Yes, it's impressive.",
    "Nous avons nos billets?": "Do we have our tickets?",
    "Oui, tout est prêt.": "Yes, everything is ready.",
    "Le train part dans vingt minutes.": "The train leaves in twenty minutes.",
    "Parfait, nous avons le temps.": "Perfect, we have time.",
    "Tu veux quelque chose à boire?": "Do you want something to drink?",
    "Oui, de l'eau, s'il te plaît.": "Yes, water, please.",
    "Prends aussi des sandwichs pour le voyage.": "Get some sandwiches for the journey too.",
    "Bonne idée.": "Good idea.",
    "Le quai est là-bas.": "The platform is over there.",
    "Allons-y!": "Let's go!",
    "Le train arrive!": "The train is coming!",
    "Monte vite!": "Get on quickly!",
    
    # Continue with more translations...
    "Voilà nos places.": "Here are our seats.",
    "Près de la fenêtre, parfait!": "By the window, perfect!",
    "Regarde le paysage!": "Look at the scenery!",
    "C'est magnifique!": "It's magnificent!",
    "Les montagnes deviennent plus grandes.": "The mountains are getting bigger.",
    "Nous approchons.": "We're getting closer.",
    "J'ai hâte d'arriver.": "I can't wait to arrive.",
    "Moi aussi.": "Me too.",
    "Le voyage est long.": "The journey is long.",
    "Oui, mais ça vaut la peine.": "Yes, but it's worth it.",
    "Tu as faim?": "Are you hungry?",
    "Un peu. Et toi?": "A little. And you?",
    "Oui, mangeons nos sandwichs.": "Yes, let's eat our sandwiches.",
}

def translate_phrase(french_text):
    """Get English translation with fallback logic."""
    # Try exact match
    if french_text in translations:
        return translations[french_text]
    
    # Try without trailing punctuation
    base = french_text.rstrip('.,!?;:')
    if base in translations:
        eng = translations[base]
        if french_text != base and french_text[-1] in '.,!?;:':
            eng += french_text[-1]
        return eng
    
    # Keep original placeholder
    return "[TO TRANSLATE]"

def complete_translations(scenes_dir):
    """Complete all translations in scene JSON files."""
    scene_files = sorted(scenes_dir.glob('scene-*.json'))
    
    total_updated = 0
    still_need = 0
    
    for scene_file in scene_files:
        print(f"\n📄 {scene_file.name}")
        
        with open(scene_file, 'r', encoding='utf-8') as f:
            phrases = json.load(f)
        
        updated_count = 0
        for phrase_obj in phrases:
            english = phrase_obj.get('english', '')
            if not english or english == '[TO TRANSLATE]':
                french_text = phrase_obj.get('french', '')
                translation = translate_phrase(french_text)
                phrase_obj['english'] = translation
                
                if translation != '[TO TRANSLATE]':
                    updated_count += 1
                else:
                    still_need += 1
        
        # Save updated file
        with open(scene_file, 'w', encoding='utf-8') as f:
            json.dump(phrases, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Updated {updated_count} translations")
        if still_need > 0:
            print(f"  ℹ️  {still_need} entries still need manual translation")
        
        total_updated += updated_count
    
    return total_updated, still_need

def main():
    scenes_dir = Path('language_materials/fr/story-scenes-json')
    
    if not scenes_dir.exists():
        print(f"❌ Directory not found: {scenes_dir}")
        sys.exit(1)
    
    print("🔄 Completing English translations for story scenes...")
    print(f"📂 Directory: {scenes_dir}\n")
    
    total_updated, still_need = complete_translations(scenes_dir)
    
    print(f"\n{'='*70}")
    print(f"✅ Complete! Updated {total_updated} translations")
    if still_need > 0:
        print(f"⚠️  {still_need} entries still marked [TO TRANSLATE] for manual completion")
    print(f"{'='*70}")

if __name__ == '__main__':
    sys.exit(main())
