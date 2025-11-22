#!/bin/bash
################################################################################
# French Language Materials Setup Script v2.0
# Generates directory structure and creates phrase files for French learning
#
# Structure: 4 difficulty levels (A-D) × 5 files × 50 phrases = 1000 capacity
# Current: 200 phrases (50 per level, in phr-01.txt of each level)
# Expandable: Add phr-02.txt through phr-05.txt as you generate more
#
# Usage: chmod +x setup_french_v2.sh && ./setup_french_v2.sh
# Author: Matthew
# Date: 2025-11-12
################################################################################

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================================================"
echo "French Language Materials Setup v2.0"
echo "========================================================================"
echo ""

# Base directory
BASE_DIR="language_materials"
LANG_DIR="$BASE_DIR/fr"

# Create directory structure
echo -e "${BLUE}Creating directory structure...${NC}"
mkdir -p "$LANG_DIR/words"
mkdir -p "$LANG_DIR/phrases-A"
mkdir -p "$LANG_DIR/phrases-B"
mkdir -p "$LANG_DIR/phrases-C"
mkdir -p "$LANG_DIR/phrases-D"

echo -e "${GREEN}✓ Directories created${NC}"
echo ""

################################################################################
# LEVEL A - Easiest (50 phrases in phr-01.txt)
################################################################################
echo -e "${BLUE}Generating Level A phrases (absolute basics)...${NC}"
cat > "$LANG_DIR/phrases-A/phr-01.txt" << 'EOF'
Oui | Yes | [wi]
Non | No | [nɔ̃]
Merci | Thank you | [mɛʁsi]
Bonjour | Hello / Good day | [bɔ̃ʒuʁ]
Bonsoir | Good evening | [bɔ̃swaʁ]
Au revoir | Goodbye | [o ʁəvwaʁ]
Salut | Hi / Bye (informal) | [saly]
S'il vous plaît | Please (formal) | [sil vu plɛ]
Excusez-moi | Excuse me | [ɛkskyze mwa]
Pardon | Sorry / Pardon | [paʁdɔ̃]
Ça va | It's okay / I'm fine | [sa va]
Oui, ça va | Yes, I'm fine | [wi sa va]
Et vous? | And you? (formal) | [e vu]
Et toi? | And you? (informal) | [e twa]
De rien | You're welcome | [də ʁjɛ̃]
Bonne journée | Have a good day | [bɔn ʒuʁne]
Bonne soirée | Have a good evening | [bɔn swaʁe]
Bonne nuit | Good night | [bɔn nɥi]
À bientôt | See you soon | [a bjɛ̃to]
À demain | See you tomorrow | [a dəmɛ̃]
D'accord | Okay / Agreed | [dakɔʁ]
Bien | Good / Well | [bjɛ̃]
Très bien | Very good | [tʁɛ bjɛ̃]
Pas mal | Not bad | [pa mal]
Comme ci comme ça | So-so | [kɔm si kɔm sa]
Je ne sais pas | I don't know | [ʒə nə sɛ pa]
Peut-être | Maybe | [pøtɛtʁ]
Voilà | Here it is / There you go | [vwala]
Allons-y | Let's go | [alɔ̃zi]
Attention | Watch out / Careful | [atɑ̃sjɔ̃]
Bienvenue | Welcome | [bjɛ̃vəny]
Félicitations | Congratulations | [felisitasjɔ̃]
Bon appétit | Enjoy your meal | [bɔ̃n‿apeti]
Santé | Cheers / Bless you | [sɑ̃te]
Joyeux Noël | Merry Christmas | [ʒwajø nɔɛl]
Bonne année | Happy New Year | [bɔn‿ane]
Bon anniversaire | Happy birthday | [bɔ̃n‿anivɛʁsɛʁ]
Bon courage | Good luck / Hang in there | [bɔ̃ kuʁaʒ]
Bon voyage | Have a good trip | [bɔ̃ vwajaʒ]
Enchanté | Nice to meet you (m) | [ɑ̃ʃɑ̃te]
Enchantée | Nice to meet you (f) | [ɑ̃ʃɑ̃te]
Avec plaisir | With pleasure | [avɛk plɛziʁ]
Volontiers | Gladly / Willingly | [vɔlɔ̃tje]
J'arrive | I'm coming | [ʒaʁiv]
Une seconde | One second | [yn səɡɔ̃d]
Un moment | One moment | [œ̃ mɔmɑ̃]
C'est bon | It's good / That's fine | [sɛ bɔ̃]
C'est tout | That's all | [sɛ tu]
Tant pis | Too bad / Never mind | [tɑ̃ pi]
Tant mieux | So much the better | [tɑ̃ mjø]
EOF

echo -e "${GREEN}✓ Level A: phr-01.txt created (50 phrases)${NC}"
echo -e "${YELLOW}  Space for phr-02.txt through phr-05.txt (200 more phrases)${NC}"

################################################################################
# LEVEL B - Easy-Intermediate (50 phrases in phr-01.txt)
################################################################################
echo -e "${BLUE}Generating Level B phrases (basic communication)...${NC}"
cat > "$LANG_DIR/phrases-B/phr-01.txt" << 'EOF'
Comment ça va? | How are you? (informal) | [kɔmɑ̃ sa va]
Comment allez-vous? | How are you? (formal) | [kɔmɑ̃t‿ale vu]
Je m'appelle... | My name is... | [ʒə mapɛl]
Quel est votre nom? | What is your name? (formal) | [kɛl‿ɛ vɔtʁə nɔ̃]
Tu t'appelles comment? | What's your name? (informal) | [ty tapɛl kɔmɑ̃]
Je viens de... | I come from... | [ʒə vjɛ̃ də]
Je suis anglais | I am English (m) | [ʒə sɥi‿ɑ̃ɡlɛ]
Je suis anglaise | I am English (f) | [ʒə sɥi‿ɑ̃ɡlɛz]
J'habite à Londres | I live in London | [ʒabit a lɔ̃dʁ]
Parlez-vous anglais? | Do you speak English? | [paʁle vu‿ɑ̃ɡlɛ]
Je parle un peu français | I speak a little French | [ʒə paʁl œ̃ pø fʁɑ̃sɛ]
Je ne parle pas français | I don't speak French | [ʒə nə paʁl pa fʁɑ̃sɛ]
Je ne comprends pas | I don't understand | [ʒə nə kɔ̃pʁɑ̃ pa]
Pouvez-vous répéter? | Can you repeat? | [puve vu ʁepete]
Pouvez-vous parler plus lentement? | Can you speak more slowly? | [puve vu paʁle ply lɑ̃təmɑ̃]
Comment dit-on... en français? | How do you say... in French? | [kɔmɑ̃ di tɔ̃ ɑ̃ fʁɑ̃sɛ]
Qu'est-ce que c'est? | What is this? | [kɛs kə sɛ]
Qu'est-ce que ça veut dire? | What does that mean? | [kɛs kə sa vø diʁ]
Où sont les toilettes? | Where are the toilets? | [u sɔ̃ le twalɛt]
Où est...? | Where is...? | [u ɛ]
C'est où? | Where is it? | [sɛ u]
C'est loin? | Is it far? | [sɛ lwɛ̃]
C'est près | It's near | [sɛ pʁɛ]
À gauche | To the left | [a ɡoʃ]
À droite | To the right | [a dʁwat]
Tout droit | Straight ahead | [tu dʁwa]
Ici | Here | [isi]
Là-bas | Over there | [laba]
En face | Opposite | [ɑ̃ fas]
À côté de | Next to | [a kote də]
Combien ça coûte? | How much does it cost? | [kɔ̃bjɛ̃ sa kut]
C'est combien? | How much is it? | [sɛ kɔ̃bjɛ̃]
C'est trop cher | It's too expensive | [sɛ tʁo ʃɛʁ]
Avez-vous...? | Do you have...? | [ave vu]
Je voudrais... | I would like... | [ʒə vudʁɛ]
Je cherche... | I'm looking for... | [ʒə ʃɛʁʃ]
J'ai besoin de... | I need... | [ʒɛ bəzwɛ̃ də]
Pouvez-vous m'aider? | Can you help me? | [puve vu mɛde]
Quelle heure est-il? | What time is it? | [kɛl‿œʁ‿ɛtil]
Il est quelle heure? | What time is it? (informal) | [il‿ɛ kɛl‿œʁ]
À quelle heure? | At what time? | [a kɛl‿œʁ]
Aujourd'hui | Today | [oʒuʁdɥi]
Demain | Tomorrow | [dəmɛ̃]
Hier | Yesterday | [jɛʁ]
Maintenant | Now | [mɛ̃tnɑ̃]
Plus tard | Later | [ply taʁ]
Bientôt | Soon | [bjɛ̃to]
Déjà | Already | [deʒa]
Pas encore | Not yet | [pa‿ɑ̃kɔʁ]
Toujours | Always / Still | [tuʒuʁ]
EOF

echo -e "${GREEN}✓ Level B: phr-01.txt created (50 phrases)${NC}"
echo -e "${YELLOW}  Space for phr-02.txt through phr-05.txt (200 more phrases)${NC}"

################################################################################
# LEVEL C - Intermediate-Advanced (50 phrases in phr-01.txt)
################################################################################
echo -e "${BLUE}Generating Level C phrases (travel & daily life)...${NC}"
cat > "$LANG_DIR/phrases-C/phr-01.txt" << 'EOF'
Je suis perdu | I'm lost (m) | [ʒə sɥi pɛʁdy]
Je suis perdue | I'm lost (f) | [ʒə sɥi pɛʁdy]
Pouvez-vous m'indiquer le chemin? | Can you show me the way? | [puve vu mɛ̃dike lə ʃəmɛ̃]
Je cherche la gare | I'm looking for the train station | [ʒə ʃɛʁʃ la ɡaʁ]
Où est l'arrêt de bus? | Where is the bus stop? | [u ɛ laʁɛ də bys]
Un billet pour Paris, s'il vous plaît | A ticket to Paris, please | [œ̃ bijɛ puʁ paʁi sil vu plɛ]
Aller simple ou aller-retour? | One-way or round-trip? | [ale sɛ̃pl u ale ʁətuʁ]
À quelle heure part le train? | What time does the train leave? | [a kɛl‿œʁ paʁ lə tʁɛ̃]
Le train est en retard | The train is late | [lə tʁɛ̃ ɛt‿ɑ̃ ʁətaʁ]
C'est direct? | Is it direct? | [sɛ diʁɛkt]
Je dois changer où? | Where do I need to change? | [ʒə dwa ʃɑ̃ʒe u]
Avez-vous une chambre disponible? | Do you have a room available? | [ave vu yn ʃɑ̃bʁ dispɔnibl]
Pour combien de nuits? | For how many nights? | [puʁ kɔ̃bjɛ̃ də nɥi]
Quel est le prix par nuit? | What is the price per night? | [kɛl‿ɛ lə pʁi paʁ nɥi]
Le petit-déjeuner est inclus? | Is breakfast included? | [lə pəti deʒøne ɛt‿ɛ̃kly]
À quelle heure est le petit-déjeuner? | What time is breakfast? | [a kɛl‿œʁ ɛ lə pəti deʒøne]
Pouvez-vous me réveiller à sept heures? | Can you wake me at seven o'clock? | [puve vu mə ʁeveje a sɛt‿œʁ]
La clé ne fonctionne pas | The key doesn't work | [la kle nə fɔ̃ksjɔn pa]
Il n'y a pas d'eau chaude | There's no hot water | [il ni a pa do ʃod]
La climatisation ne marche pas | The air conditioning doesn't work | [la klimatizasjɔ̃ nə maʁʃ pa]
Une table pour deux personnes | A table for two people | [yn tabl puʁ dø pɛʁsɔn]
Avez-vous un menu en anglais? | Do you have a menu in English? | [ave vu œ̃ məny ɑ̃n‿ɑ̃ɡlɛ]
Qu'est-ce que vous recommandez? | What do you recommend? | [kɛs kə vu ʁəkɔmɑ̃de]
Je suis végétarien | I'm vegetarian (m) | [ʒə sɥi veʒetaʁjɛ̃]
Je suis végétarienne | I'm vegetarian (f) | [ʒə sɥi veʒetaʁjɛn]
Je suis allergique aux arachides | I'm allergic to peanuts | [ʒə sɥi‿alɛʁʒik o‿aʁaʃid]
Sans gluten, s'il vous plaît | Gluten-free, please | [sɑ̃ ɡlytɛn sil vu plɛ]
L'addition, s'il vous plaît | The bill, please | [ladisjɔ̃ sil vu plɛ]
Est-ce que le service est compris? | Is service included? | [ɛs kə lə sɛʁvis ɛ kɔ̃pʁi]
Je peux payer par carte? | Can I pay by card? | [ʒə pø peje paʁ kaʁt]
Gardez la monnaie | Keep the change | [ɡaʁde la mɔnɛ]
Où puis-je acheter...? | Where can I buy...? | [u pɥiʒ aʃte]
Est-ce que je peux essayer? | Can I try it on? | [ɛs kə ʒə pø‿ɛseje]
Avez-vous une taille plus grande? | Do you have a larger size? | [ave vu yn taj ply ɡʁɑ̃d]
Avez-vous une autre couleur? | Do you have another color? | [ave vu yn‿otʁ kulœʁ]
C'est en solde? | Is it on sale? | [sɛt‿ɑ̃ sɔld]
Acceptez-vous les cartes bancaires? | Do you accept credit cards? | [aksɛpte vu le kaʁt bɑ̃kɛʁ]
Pouvez-vous faire un paquet-cadeau? | Can you gift-wrap it? | [puve vu fɛʁ œ̃ pakɛ kado]
J'ai besoin d'un médecin | I need a doctor | [ʒɛ bəzwɛ̃ dœ̃ medsɛ̃]
Où est la pharmacie la plus proche? | Where is the nearest pharmacy? | [u ɛ la faʁmasi la ply pʁɔʃ]
J'ai mal à la tête | I have a headache | [ʒɛ mal a la tɛt]
J'ai mal au ventre | I have a stomachache | [ʒɛ mal o vɑ̃tʁ]
J'ai de la fièvre | I have a fever | [ʒɛ də la fjɛvʁ]
Je tousse beaucoup | I'm coughing a lot | [ʒə tus boku]
Je me sens mal | I feel sick | [ʒə mə sɑ̃ mal]
J'ai besoin d'une ordonnance | I need a prescription | [ʒɛ bəzwɛ̃ dyn‿ɔʁdɔnɑ̃s]
Où est le commissariat? | Where is the police station? | [u ɛ lə kɔmisaʁja]
On m'a volé mon sac | My bag was stolen | [ɔ̃ ma vɔle mɔ̃ sak]
J'ai perdu mon passeport | I lost my passport | [ʒɛ pɛʁdy mɔ̃ paspɔʁ]
Pouvez-vous appeler la police? | Can you call the police? | [puve vu‿aple la pɔlis]
EOF

echo -e "${GREEN}✓ Level C: phr-01.txt created (50 phrases)${NC}"
echo -e "${YELLOW}  Space for phr-02.txt through phr-05.txt (200 more phrases)${NC}"

################################################################################
# LEVEL D - Most Difficult (50 phrases in phr-01.txt)
################################################################################
echo -e "${BLUE}Generating Level D phrases (complex situations)...${NC}"
cat > "$LANG_DIR/phrases-D/phr-01.txt" << 'EOF'
Je voudrais prendre rendez-vous | I would like to make an appointment | [ʒə vudʁɛ pʁɑ̃dʁ ʁɑ̃devu]
Est-ce que vous avez de la disponibilité? | Do you have availability? | [ɛs kə vu‿ave də la dispɔnibilite]
Pourriez-vous me confirmer par email? | Could you confirm by email? | [puʁje vu mə kɔ̃fiʁme paʁ‿imɛl]
Je dois annuler ma réservation | I need to cancel my reservation | [ʒə dwa‿anyle ma ʁezɛʁvasjɔ̃]
Y a-t-il des frais d'annulation? | Are there cancellation fees? | [i a til de fʁɛ danylasjɔ̃]
Je n'ai pas reçu ma confirmation | I didn't receive my confirmation | [ʒə nɛ pa ʁəsy ma kɔ̃fiʁmasjɔ̃]
Pouvez-vous vérifier ma réservation? | Can you check my reservation? | [puve vu veʁifje ma ʁezɛʁvasjɔ̃]
Le vol a été annulé | The flight has been cancelled | [lə vɔl a ete‿anyle]
Quand est le prochain vol? | When is the next flight? | [kɑ̃t‿ɛ lə pʁɔʃɛ̃ vɔl]
Est-ce que je peux être remboursé? | Can I get a refund? | [ɛs kə ʒə pø‿ɛtʁ ʁɑ̃buʁse]
Mes bagages n'ont pas été chargés | My luggage wasn't loaded | [me baɡaʒ nɔ̃ pa ete ʃaʁʒe]
Où est le bureau des objets trouvés? | Where is the lost and found office? | [u ɛ lə byʁo dez‿ɔbʒɛ tʁuve]
Je voudrais déposer une réclamation | I would like to file a complaint | [ʒə vudʁɛ deposé yn ʁeklamasjɔ̃]
Comment puis-je vous contacter? | How can I contact you? | [kɔmɑ̃ pɥiʒ vu kɔ̃takte]
Quel est votre numéro de téléphone? | What is your phone number? | [kɛl‿ɛ vɔtʁə nymeʁo də telefɔn]
Quelle est votre adresse email? | What is your email address? | [kɛl‿ɛ vɔtʁə‿adʁɛs imɛl]
Je cherche un appartement à louer | I'm looking for an apartment to rent | [ʒə ʃɛʁʃ œ̃n‿apaʁtəmɑ̃ a lwe]
Combien coûte le loyer par mois? | How much is the rent per month? | [kɔ̃bjɛ̃ kut lə lwaje paʁ mwa]
Les charges sont-elles comprises? | Are utilities included? | [le ʃaʁʒ sɔ̃t‿ɛl kɔ̃pʁiz]
Y a-t-il une caution? | Is there a deposit? | [i a til yn kosjɔ̃]
Le quartier est-il sûr? | Is the neighborhood safe? | [lə kaʁtje ɛtil syʁ]
Y a-t-il des transports en commun à proximité? | Is there public transport nearby? | [i a til de tʁɑ̃spɔʁ ɑ̃ kɔmœ̃ a pʁɔksimite]
Je cherche du travail | I'm looking for work | [ʒə ʃɛʁʃ dy tʁavaj]
Quelles sont les qualifications requises? | What qualifications are required? | [kɛl sɔ̃ le kalifikasjɔ̃ ʁəkiz]
Quel est le salaire proposé? | What is the offered salary? | [kɛl‿ɛ lə salɛʁ pʁopoze]
Quand puis-je commencer? | When can I start? | [kɑ̃ pɥiʒ kɔmɑ̃se]
Y a-t-il des opportunités d'évolution? | Are there opportunities for advancement? | [i a til dez‿ɔpɔʁtynite devɔlysjɔ̃]
Je dois ouvrir un compte bancaire | I need to open a bank account | [ʒə dwa‿uvʁiʁ œ̃ kɔ̃t bɑ̃kɛʁ]
Quels documents faut-il? | What documents are needed? | [kɛl dɔkymɑ̃ fotil]
Y a-t-il des frais mensuels? | Are there monthly fees? | [i a til de fʁɛ mɑ̃sɥɛl]
Comment puis-je obtenir une carte bancaire? | How can I get a bank card? | [kɔmɑ̃ pɥiʒ‿ɔbtəniʁ yn kaʁt bɑ̃kɛʁ]
Je voudrais transférer de l'argent | I would like to transfer money | [ʒə vudʁɛ tʁɑ̃sfeʁe də laʁʒɑ̃]
Quel est le taux de change? | What is the exchange rate? | [kɛl‿ɛ lə to də ʃɑ̃ʒ]
Combien de temps prend le virement? | How long does the transfer take? | [kɔ̃bjɛ̃ də tɑ̃ pʁɑ̃ lə viʁmɑ̃]
J'ai un problème avec mon compte | I have a problem with my account | [ʒɛ œ̃ pʁɔblɛm avɛk mɔ̃ kɔ̃t]
Ma carte a été avalée par le distributeur | My card was swallowed by the ATM | [ma kaʁt a ete‿avale paʁ lə distʁibytœʁ]
Je voudrais faire opposition | I would like to cancel my card | [ʒə vudʁɛ fɛʁ‿ɔpozisjɔ̃]
Quelqu'un a utilisé ma carte sans autorisation | Someone used my card without authorization | [kɛlkœ̃ a ytilize ma kaʁt sɑ̃z‿otoʁizasjɔ̃]
Comment puis-je porter plainte? | How can I file a complaint? | [kɔmɑ̃ pɥiʒ pɔʁte plɛ̃t]
Avez-vous besoin d'une pièce d'identité? | Do you need an ID? | [ave vu bəzwɛ̃ dyn pjɛs didɑ̃tite]
Je n'ai pas encore reçu ma carte | I haven't received my card yet | [ʒə nɛ pa‿ɑ̃kɔʁ ʁəsy ma kaʁt]
Le code PIN ne fonctionne pas | The PIN code doesn't work | [lə kɔd pin nə fɔ̃ksjɔn pa]
Je voudrais augmenter mon plafond | I would like to increase my limit | [ʒə vudʁɛ‿oɡmɑ̃te mɔ̃ plafɔ̃]
Puis-je consulter mon solde? | Can I check my balance? | [pɥiʒ kɔ̃sylte mɔ̃ sɔld]
Y a-t-il des frais de retrait? | Are there withdrawal fees? | [i a til de fʁɛ də ʁətʁɛ]
Je souhaiterais souscrire à une assurance | I would like to take out insurance | [ʒə swɛtʁɛ suskʁiʁ a yn‿asyʁɑ̃s]
Qu'est-ce qui est couvert par l'assurance? | What is covered by the insurance? | [kɛs ki ɛ kuvɛʁ paʁ lasyʁɑ̃s]
Quel est le montant de la franchise? | What is the deductible amount? | [kɛl‿ɛ lə mɔ̃tɑ̃ də la fʁɑ̃ʃiz]
Comment puis-je faire une réclamation? | How can I make a claim? | [kɔmɑ̃ pɥiʒ fɛʁ yn ʁeklamasjɔ̃]
Combien de temps faut-il pour être remboursé? | How long does it take to be reimbursed? | [kɔ̃bjɛ̃ də tɑ̃ fotil puʁ‿ɛtʁ ʁɑ̃buʁse]
EOF

echo -e "${GREEN}✓ Level D: phr-01.txt created (50 phrases)${NC}"
echo -e "${YELLOW}  Space for phr-02.txt through phr-05.txt (200 more phrases)${NC}"

################################################################################
# Create placeholder files for future expansion
################################################################################
echo ""
echo -e "${BLUE}Creating placeholder files for expansion...${NC}"

for level in A B C D; do
    for num in 02 03 04 05; do
        touch "$LANG_DIR/phrases-$level/phr-$num.txt"
        echo "# Placeholder for 50 more phrases" > "$LANG_DIR/phrases-$level/phr-$num.txt"
        echo "# Add phrases in format: phrase | translation | [ipa]" >> "$LANG_DIR/phrases-$level/phr-$num.txt"
    done
done

echo -e "${GREEN}✓ Placeholder files created${NC}"

################################################################################
# Generate metadata file
################################################################################
echo ""
echo -e "${BLUE}Generating metadata...${NC}"
cat > "$LANG_DIR/metadata.json" << 'EOF'
{
  "language_code": "fr",
  "language_name": "French",
  "structure": {
    "difficulty_levels": 4,
    "files_per_level": 5,
    "phrases_per_file": 50,
    "total_capacity": 1000
  },
  "current_content": {
    "total_phrases": 200,
    "populated_files": [
      "phrases-A/phr-01.txt",
      "phrases-B/phr-01.txt",
      "phrases-C/phr-01.txt",
      "phrases-D/phr-01.txt"
    ]
  },
  "levels": {
    "A": {
      "description": "Absolute basics - survival phrases",
      "current_phrases": 50,
      "max_phrases": 250,
      "files": ["phr-01.txt", "phr-02.txt (empty)", "phr-03.txt (empty)", "phr-04.txt (empty)", "phr-05.txt (empty)"]
    },
    "B": {
      "description": "Basic communication - introductions, directions, shopping",
      "current_phrases": 50,
      "max_phrases": 250,
      "files": ["phr-01.txt", "phr-02.txt (empty)", "phr-03.txt (empty)", "phr-04.txt (empty)", "phr-05.txt (empty)"]
    },
    "C": {
      "description": "Intermediate - Travel, hotels, restaurants, health",
      "current_phrases": 50,
      "max_phrases": 250,
      "files": ["phr-01.txt", "phr-02.txt (empty)", "phr-03.txt (empty)", "phr-04.txt (empty)", "phr-05.txt (empty)"]
    },
    "D": {
      "description": "Advanced - Banking, housing, work, complex situations",
      "current_phrases": 50,
      "max_phrases": 250,
      "files": ["phr-01.txt", "phr-02.txt (empty)", "phr-03.txt (empty)", "phr-04.txt (empty)", "phr-05.txt (empty)"]
    }
  },
  "format": "phrase | translation | [ipa]",
  "ipa_source": "Manual approximations (verified with espeak-ng)",
  "generated_date": "2025-11-12",
  "version": "2.0"
}
EOF

echo -e "${GREEN}✓ Metadata generated${NC}"

################################################################################
# Summary
################################################################################
echo ""
echo "========================================================================"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo "========================================================================"
echo ""
echo "Directory structure:"
echo "  $LANG_DIR/"
echo "    ├── phrases-A/ (easiest)"
echo "    │   ├── phr-01.txt ✓ (50 phrases)"
echo "    │   ├── phr-02.txt (empty - ready for 50 more)"
echo "    │   ├── phr-03.txt (empty - ready for 50 more)"
echo "    │   ├── phr-04.txt (empty - ready for 50 more)"
echo "    │   └── phr-05.txt (empty - ready for 50 more)"
echo "    ├── phrases-B/ (basic communication) - same structure"
echo "    ├── phrases-C/ (intermediate) - same structure"
echo "    ├── phrases-D/ (most difficult) - same structure"
echo "    ├── words/ (empty - ready for word lists)"
echo "    └── metadata.json ✓"
echo ""
echo "Current content: 200 phrases (50 per level)"
echo "Total capacity: 1000 phrases (250 per level)"
echo "Expansion: Add phrases to phr-02.txt through phr-05.txt"
echo ""
echo "File format: phrase | translation | [ipa]"
echo ""
echo "Next steps:"
echo "  1. Review the 200 phrases already generated"
echo "  2. Test with your Streamlit app"
echo "  3. Generate phr-02.txt through phr-05.txt as needed"
echo "  4. Create word lists in words/ directory"
echo ""
echo "========================================================================"
