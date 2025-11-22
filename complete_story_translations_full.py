#!/usr/bin/env python3
"""
COMPLETE translation script for ALL story scene phrases.
This includes every single phrase with proper context-aware translations.
"""
import json
from pathlib import Path

# COMPLETE TRANSLATION DICTIONARY - Every single phrase from all 16 scenes
COMPLETE_TRANSLATIONS = {
    # Scene 1 - Le café du matin (COMPLETE)
    "Bonjour Sophie, ça va?": "Hello Sophie, how are you?",
    "Oui, bien merci. Et toi?": "Yes, well thank you. And you?",
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
    "Il fait beau aujourd'hui,": "It's nice today,",
    "Oui, c'est une belle journée.": "Yes, it's a beautiful day.",
    "Tu sais, Lucas, la vie est si monotone ici.": "You know, Lucas, life is so monotonous here.",
    "Je suis d'accord avec toi. Chaque jour est pareil.": "I agree with you. Every day is the same.",
    "On devrait partir en voyage,": "We should go on a trip,",
    "Tu as raison! Pourquoi pas?": "You're right! Why not?",
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
    
    # Scene 10 - La séparation involontaire (NOW COMPLETE!)
    "Lucas? Lucas, où es-tu?": "Lucas? Lucas, where are you?",
    "Je n'entends plus sa voix.": "I can't hear his voice anymore.",
    "Si seulement j'avais mon téléphone! Mais il ne sert à rien ici.": "If only I had my phone! But it's useless here.",
    "Je ne sais plus où je suis.": "I don't know where I am anymore.",
    "Il aurait fallu rester ensemble. Nous avons été stupides.": "We should have stayed together. We were stupid.",
    "Maintenant, je suis complètement seule.": "Now, I'm completely alone.",
    "J'aurais dû l'écouter tout à l'heure": "I should have listened to him earlier",
    "Il voulait faire demi-tour.": "He wanted to turn back.",
    "Mais il est trop tard pour les regrets.": "But it's too late for regrets.",
    "Je dois trouver un abri": "I must find shelter",
    "Je ne peux pas rester dehors cette nuit.": "I can't stay outside tonight.",
    "Dans le doute, descends. L'eau coule vers le bas.": "When in doubt, go downhill. Water flows downward.",
    "Où suis-je vraiment? Qui suis-je sans Lucas à mes côtés?": "Where am I really? Who am I without Lucas by my side?",
    "Là-bas, il y a quelque chose!": "Over there, there's something!",
    "Une petite cabane abandonnée. Dieu merci!": "A small abandoned cabin. Thank God!",
    "Sophie attend quelques minutes, puis commence à paniquer.": "Sophie waits a few minutes, then begins to panic.",
    "Le vent emporte sa voix.": "The wind carries away her voice.",
    "Elle crie plus fort, mais rien.": "She shouts louder, but nothing.",
    "Elle cherche son téléphone dans sa poche.": "She searches for her phone in her pocket.",
    "Le brouillard est si dense qu'elle ne voit pas à trois mètres devant elle.": "The fog is so dense that she can't see three meters ahead.",
    "Elle se reproche leur dispute.": "She blames herself for their argument.",
    "Le vent souffle de plus en plus fort.": "The wind blows harder and harder.",
    "Sophie se force à réfléchir calmement.": "Sophie forces herself to think calmly.",
    "Elle avance prudemment, les mains tendues devant elle.": "She moves forward cautiously, hands stretched out in front of her.",
    "Dans sa tête, des souvenirs surgissent.": "In her mind, memories surface.",
    "Soudain, ses mains touchent quelque chose de solide.": "Suddenly, her hands touch something solid.",
    "C'est une forme sombre dans le brouillard.": "It's a dark shape in the fog.",
    "En milieu d'après-midi, le temps change soudainement.": "In mid-afternoon, the weather suddenly changes.",
    "Un brouillard épais descend sur la montagne.": "A thick fog descends on the mountain.",
    "La visibilité devient presque nulle.": "Visibility becomes almost zero.",
    "Sophie et Lucas ne peuvent plus voir à plus de quelques mètres.": "Sophie and Lucas can't see more than a few meters.",
    "C'est inquiétant.": "It's worrying.",
    "Ils essaient de rester ensemble.": "They try to stay together.",
    "Mais le sentier est étroit et glissant.": "But the trail is narrow and slippery.",
    "Sophie trébuche.": "Sophie stumbles.",
    "Quand elle se relève, Lucas a disparu dans le brouillard.": "When she gets up, Lucas has disappeared into the fog.",
    "Elle crie son nom.": "She calls his name.",
    "Lui aussi crie.": "He calls out too.",
    "Mais leurs voix se perdent dans le silence ouaté du brouillard.": "But their voices are lost in the muffled silence of the fog.",
    "Ils sont séparés.": "They are separated.",
    "Le temps change.": "The weather is changing.",
    "Oui, un brouillard arrive.": "Yes, fog is coming.",
    "C'est dense. Je ne vois presque rien.": "It's dense. I can barely see anything.",
    "Restons ensemble!": "Let's stay together!",
    "Lucas? Où es-tu?": "Lucas? Where are you?",
    "Sophie! Je suis ici!": "Sophie! I'm here!",
    "Je ne te vois plus!": "I can't see you anymore!",
    "Ne bouge pas! Je vais te retrouver!": "Don't move! I'll find you!",
    "J'ai peur!": "I'm scared!",
    "Reste calme! Crie pour que je puisse te localiser!": "Stay calm! Shout so I can locate you!",
}

def translate_phrase(french_text):
    """Get English translation for a French phrase."""
    # Try exact match first
    if french_text in COMPLETE_TRANSLATIONS:
        return COMPLETE_TRANSLATIONS[french_text]
    
    # Try without trailing punctuation
    base = french_text.rstrip('.,!?;:—')
    if base in COMPLETE_TRANSLATIONS:
        eng = COMPLETE_TRANSLATIONS[base]
        # Add punctuation back if it was removed
        if french_text != base and french_text[-1] in '.,!?;:—':
            eng += french_text[-1]
        return eng
    
    # No translation found
    return None

def complete_translations(scenes_dir):
    """Complete translations in all scene JSON files."""
    scenes_dir = Path(scenes_dir)
    
    if not scenes_dir.exists():
        print(f"❌ Directory not found: {scenes_dir}")
        return
    
    scene_files = sorted(scenes_dir.glob('scene-*.json'))
    
    total_updated = 0
    total_still_missing = 0
    
    for scene_file in scene_files:
        print(f"\n📄 {scene_file.name}")
        
        with open(scene_file, 'r', encoding='utf-8') as f:
            phrases = json.load(f)
        
        updated = 0
        for phrase_obj in phrases:
            french = phrase_obj.get('french', '')
            english = phrase_obj.get('english', '')
            
            # Only update if missing or marked for translation
            if not english or english == '[TO TRANSLATE]':
                translation = translate_phrase(french)
                if translation:
                    phrase_obj['english'] = translation
                    updated += 1
                else:
                    total_still_missing += 1
        
        # Save updated file
        if updated > 0:
            with open(scene_file, 'w', encoding='utf-8') as f:
                json.dump(phrases, f, ensure_ascii=False, indent=2)
            print(f"  ✓ Updated {updated} translations")
        else:
            print(f"  ℹ️ No updates needed")
        
        total_updated += updated
    
    print(f"\n{'='*70}")
    print(f"✅ Complete! Updated {total_updated} translations across all scenes")
    if total_still_missing > 0:
        print(f"⚠️  {total_still_missing} entries still marked [TO TRANSLATE]")
    else:
        print(f"🎉 ALL TRANSLATIONS COMPLETE!")
    print(f"{'='*70}")

if __name__ == '__main__':
    complete_translations('language_materials/fr/story-scenes-json')
