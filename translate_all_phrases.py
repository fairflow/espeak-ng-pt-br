#!/usr/bin/env python3
"""
Translate all French phrases to English based on narrative context
"""
import json

# Load phrases
data = json.load(open('phrases_organized_fr.json'))

# Comprehensive translation dictionary
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
    "J'ai des tomates d'hier. Deux euros le kilo.": "I have yesterday's tomatoes. Two euros per kilo.",
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
    
    # Scene 5: At the station
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
    
    # Scene 6: On the train
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
    "Le paysage change constamment.": "The landscape keeps changing.",
    "Chaque vue est plus belle que la précédente.": "Each view is more beautiful than the last.",
    "Nous serons bientôt là.": "We'll be there soon.",
    
    # Scene 7: Arrival
    "Nous voilà!": "Here we are!",
    "Quel beau village!": "What a beautiful village!",
    "L'air est frais ici.": "The air is fresh here.",
    "Et tellement pur!": "And so pure!",
    "Où est l'auberge?": "Where is the inn?",
    "Là-bas, je crois.": "Over there, I think.",
    "Demandons à quelqu'un.": "Let's ask someone.",
    "Excusez-moi, où est l'auberge du village?": "Excuse me, where is the village inn?",
    "C'est par là, après la place.": "It's that way, after the square.",
    "Merci beaucoup!": "Thank you very much!",
    "De rien. Bonne journée!": "You're welcome. Have a good day!",
    "Cette auberge est charmante.": "This inn is charming.",
    "Oui, elle est très jolie.": "Yes, it's very pretty.",
    "Installons-nous et puis allons explorer.": "Let's settle in and then go explore.",
    "Excellente idée!": "Excellent idea!",
    
    # Scene 8: Village exploration
    "Quelle belle vue depuis ici!": "What a beautiful view from here!",
    "Les montagnes sont majestueuses.": "The mountains are majestic.",
    "Je n'ai jamais rien vu de si beau.": "I've never seen anything so beautiful.",
    "Demain, nous commençons notre randonnée.": "Tomorrow, we start our hike.",
    "Oui, je suis impatient.": "Yes, I'm impatient.",
    "Nous devons nous coucher tôt.": "We need to go to bed early.",
    "D'accord. Bonne nuit, Lucas.": "Okay. Good night, Lucas.",
    "Bonne nuit, Sophie.": "Good night, Sophie.",
    
    # Scene 9: The hike begins
    "Prêt pour l'aventure?": "Ready for the adventure?",
    "Absolument! Allons-y.": "Absolutely! Let's go.",
    "Le sentier monte beaucoup.": "The trail goes up a lot.",
    "Oui, c'est difficile mais magnifique.": "Yes, it's difficult but magnificent.",
    "Faisons une pause.": "Let's take a break.",
    "Bonne idée. Buvons un peu d'eau.": "Good idea. Let's drink some water.",
    "Regarde ces fleurs sauvages!": "Look at these wild flowers!",
    "Elles sont magnifiques.": "They're magnificent.",
    "La nature est incroyable ici.": "Nature is incredible here.",
    "Je suis tellement content d'être venu.": "I'm so glad I came.",
    "Moi aussi. C'était la bonne décision.": "Me too. It was the right decision.",
    
    # Scene 10: Fog and separation
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
    
    # Scene 11: Sophie's survival
    "Je suis seule maintenant.": "I'm alone now.",
    "Il fait froid.": "It's cold.",
    "Je dois trouver un abri.": "I must find shelter.",
    "Voilà une cabane!": "There's a cabin!",
    "Dieu merci, je suis sauvée.": "Thank God, I'm saved.",
    "Il faut allumer un feu.": "I need to light a fire.",
    "J'ai des allumettes dans mon sac.": "I have matches in my bag.",
    "Le bois est humide, mais quelques brindilles sèches feront l'affaire.": "The wood is damp, but a few dry twigs will do.",
    "Enfin, le feu prend!": "Finally, the fire catches!",
    "C'est si réconfortant.": "It's so comforting.",
    "Qu'est-ce que c'est? Des orties?": "What's this? Nettles?",
    "Elles sont comestibles. Je peux faire une soupe.": "They're edible. I can make soup.",
    "J'ai aussi trouvé une source d'eau fraîche.": "I also found a spring of fresh water.",
    "Au moins, je ne mourrai pas de faim ou de soif.": "At least I won't die of hunger or thirst.",
    "Mais où est Lucas?": "But where is Lucas?",
    "J'espère qu'il va bien.": "I hope he's okay.",
    "Demain, je dois le chercher.": "Tomorrow, I must look for him.",
    "Pour l'instant, je dois me reposer.": "For now, I must rest.",
    
    # Scene 12: Lucas's journey
    "Où suis-je?": "Where am I?",
    "Sophie a disparu.": "Sophie has disappeared.",
    "Je dois la retrouver.": "I must find her.",
    "Mais par où aller?": "But which way to go?",
    "Le brouillard est si épais.": "The fog is so thick.",
    "Qu'est-ce que c'est? Une chèvre?": "What's that? A goat?",
    "Elle me regarde fixement.": "It's staring at me.",
    "Peut-être qu'elle connaît le chemin.": "Maybe it knows the way.",
    "Je vais la suivre.": "I'm going to follow it.",
    "La chèvre me guide vers un sentier.": "The goat is guiding me toward a path.",
    "Ce sentier descend vers la vallée.": "This path goes down to the valley.",
    "Je peux voir des lumières en bas.": "I can see lights below.",
    "Un village! Je suis sauvé!": "A village! I'm saved!",
    "Maintenant je peux organiser des secours pour Sophie.": "Now I can organize rescue for Sophie.",
    
    # Scene 13: Rescue
    "Nous avons trouvé Sophie!": "We found Sophie!",
    "Elle va bien!": "She's okay!",
    "Oh Lucas! Tu es sain et sauf!": "Oh Lucas! You're safe and sound!",
    "J'avais tellement peur de te perdre.": "I was so afraid of losing you.",
    "Moi aussi. Mais nous sommes ensemble maintenant.": "Me too. But we're together now.",
    "L'important, c'est que nous soyons tous les deux sains et saufs.": "The important thing is that we're both safe and sound.",
    "Cette expérience nous a changés.": "This experience has changed us.",
    "Oui, nous sommes plus forts maintenant.": "Yes, we're stronger now.",
    
    # Scene 14: Reflection
    "Je n'oublierai jamais cette aventure.": "I'll never forget this adventure.",
    "Moi non plus. C'était terrifiant mais aussi magnifique.": "Me neither. It was terrifying but also magnificent.",
    "La nature nous a appris beaucoup de choses.": "Nature taught us many things.",
    "La survie, la résilience, l'espoir.": "Survival, resilience, hope.",
    "Et l'importance de l'amitié.": "And the importance of friendship.",
    "Tu es mon meilleur ami, Lucas.": "You're my best friend, Lucas.",
    "Et toi le mien, Sophie.": "And you're mine, Sophie.",
    
    # Scene 15: Helicopter arrival
    "L'hélicoptère arrive!": "The helicopter is coming!",
    "Ils vont nous ramener en sécurité.": "They're going to take us back to safety.",
    "Je suis soulagé.": "I'm relieved.",
    "Moi aussi. Mais je suis aussi triste de partir.": "Me too. But I'm also sad to leave.",
    "Nous reviendrons un jour.": "We'll come back one day.",
    "Oui, mais mieux préparés!": "Yes, but better prepared!",
    "Cette fois, avec un GPS et une radio.": "This time, with a GPS and a radio.",
    "Et de meilleures cartes.": "And better maps.",
    "Montez dans l'hélicoptère!": "Get in the helicopter!",
    "Adieu, belle montagne!": "Goodbye, beautiful mountain!",
    
    # Scene 16: Return
    "Nous sommes de retour à Paris.": "We're back in Paris.",
    "Tout semble différent maintenant.": "Everything seems different now.",
    "Oui, nous avons changé.": "Yes, we've changed.",
    "Cette expérience restera avec nous pour toujours.": "This experience will stay with us forever.",
    "Que faisons-nous maintenant?": "What do we do now?",
    "Nous continuons à vivre, mais avec une nouvelle perspective.": "We continue living, but with a new perspective.",
    "Nous apprécions chaque moment.": "We appreciate every moment.",
    "Et nous n'oublions jamais d'être reconnaissants.": "And we never forget to be grateful.",
    "À la prochaine aventure?": "To the next adventure?",
    "À la prochaine aventure!": "To the next adventure!",
    
    # Scene 17: Literary critique
    "Votre récit suit une linéarité classique, mais l'épreuve de Sophie dans la cabane—cette longue nuit de l'âme—pourrait bénéficier d'une fragmentation temporelle.": "Your narrative follows a classic linearity, but Sophie's ordeal in the cabin—this long dark night of the soul—could benefit from temporal fragmentation.",
    "Pensez à la technique de Stendhal dans La Chartreuse de Parme, où la bataille est vécue dans une confusion sensorielle.": "Think of Stendhal's technique in The Charterhouse of Parma, where the battle is experienced in sensory confusion.",
    "La dialectique entre civilisation et nature sauvage évoque certes Rousseau, mais elle manque peut-être de la complexité ontologique qu'on trouve chez Philip Pullman.": "The dialectic between civilization and wild nature certainly evokes Rousseau, but it perhaps lacks the ontological complexity found in Philip Pullman.",
    "Dans His Dark Materials, les épreuves physiques deviennent des questionnements métaphysiques.": "In His Dark Materials, physical ordeals become metaphysical questionings.",
    "Votre chèvre-guide pourrait-elle porter une signification plus profonde? Un symbole d'autonomie morale plutôt qu'un simple deus ex machina?": "Could your goat-guide carry a deeper significance? A symbol of moral autonomy rather than a simple deus ex machina?",
    
    # Scene 18: Advanced subjunctive
    "Il aurait fallu que Sophie comprît plus tôt les dangers de la montagne.": "Sophie should have understood the dangers of the mountain earlier.",
    "Lucas regrette qu'ils n'eussent pas vérifié la météo avant de partir.": "Lucas regrets that they hadn't checked the weather before leaving.",
    "Il est peu probable que Lucas oublie la terreur de cette nuit où il croyait avoir perdu sa compagne.": "It's unlikely that Lucas will forget the terror of that night when he thought he had lost his companion.",
    "Ils regrettent que leur aventure ait pris une tournure si dangereuse, bien que ce fût précisément cette dangerosité qui les ait transformés.": "They regret that their adventure took such a dangerous turn, although it was precisely this danger that transformed them.",
    "Afin que chacun puisse s'épanouir pleinement, il est nécessaire qu'ils acceptent l'autonomie de l'autre.": "So that each can flourish fully, it's necessary that they accept each other's autonomy.",
}

print(f"📖 Translation dictionary: {len(translations)} entries\n")
print("🔄 Applying translations to all phrases...\n")

# Apply translations
translated = 0
still_need = 0

for level in ['A', 'B', 'C', 'D']:
    books = data['books'][level]
    for book in books:
        for phrase in book:
            french = phrase['french']
            # Try exact match
            if french in translations:
                phrase['english'] = translations[french]
                translated += 1
            else:
                # Try without trailing punctuation
                base = french.rstrip('.,!?;:')
                if base in translations:
                    eng = translations[base]
                    if french != base and french[-1] in '.,!?;:':
                        eng += french[-1]
                    phrase['english'] = eng
                    translated += 1
                else:
                    still_need += 1

print(f"📊 Translation Status:")
print(f"   ✅ Translated: {translated}/{translated + still_need}")
print(f"   ⚠️  Need review: {still_need}\n")

# Save progress
with open('phrases_organized_fr.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"💾 Saved to phrases_organized_fr.json")

if still_need > 0:
    # Show first few untranslated for context
    print(f"\n📝 Sample untranslated phrases (first 5):")
    count = 0
    for level in ['A', 'B', 'C', 'D']:
        for book in data['books'][level]:
            for phrase in book:
                if phrase['english'].startswith('[TRANSLATE:'):
                    print(f"   {phrase['french'][:70]}...")
                    count += 1
                    if count >= 5:
                        break
            if count >= 5:
                break
        if count >= 5:
            break
