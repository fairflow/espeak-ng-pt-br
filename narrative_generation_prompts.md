# French Narrative Generation Prompts
## For Miolingo Language Learning Materials

This document contains prompts for generating the French narrative using Claude Sonnet 4.5.
The narrative should be 5000-8000 words based on `story_framework_fr.md`.

---

## Primary Generation Prompt

```
Create a French language learning narrative (5000-8000 words) following this framework:

# STORY: Sophie et Lucas - Une Aventure Alpine

## CHARACTERS
- **Sophie Moreau** (27, graphiste): Creative, anxious → confident, emotionally open
- **Lucas Dubois** (29, développeur): Optimistic, organized → resilient, accepting uncertainty

## STRUCTURE (4 Acts with Linguistic Progression)

### ACT 1: Vie Quotidienne (A-level, 50 phrases)
**Scenes:** Café du Matin, Achats en Ville, Conversation sur le Rêve, La Décision
**Linguistic Focus:** Present tense, simple SVO sentences, basic vocabulary
**Key Elements:**
- Scene 1: Morning café routine, ordering, greetings
- Scene 2: Shopping for travel gear, prices, directions
- Scene 3: Discussing dreams and travel plans
- Scene 4: Making the decision to go to the Alps

### ACT 2: Le Voyage (B-level, 60 phrases)
**Scenes:** À la Gare, Dans le Train, Arrivée au Village, Rencontres
**Linguistic Focus:** Futur proche, passé composé, travel vocabulary
**Key Elements:**
- Scene 5: Train station logistics and excitement
- Scene 6: Journey conversations about future plans
- Scene 7: Arrival in alpine village, first impressions
- Scene 8: Meeting locals and other travelers

### ACT 3: Les Défis (C-level, 50 phrases)
**Scenes:** Randonnée Difficile, Séparation, Défi de Sophie, Défi de Lucas
**Linguistic Focus:** Imparfait, conditionnel, nature/survival vocabulary
**Key Elements:**
- Scene 9: Challenging mountain hike, weather changes
- Scene 10: Sudden separation due to weather/terrain
- Scene 11: Sophie's challenge (navigation, fear)
- Scene 12: Lucas's challenge (injury, problem-solving)

### ACT 4: La Réunion (D-level, 40 phrases)
**Scenes:** Les Secours, Réflexion, Découverte, Réunion
**Linguistic Focus:** Subjonctif, abstract concepts, emotional vocabulary
**Key Elements:**
- Scene 13: Rescue operation and coordination
- Scene 14: Reflection on personal growth
- Scene 15: Discovery about themselves and relationship
- Scene 16: Reunion with new perspectives

## WRITING REQUIREMENTS

### Language Requirements:
1. **60% dialogue, 40% narrative**
2. **Scene markers:** Use `### SCENE N: Title` format for extraction
3. **Dialogue:** Use French quotation marks («guillemets»)
4. **Natural progression:** Grammar/vocabulary complexity increases naturally with story
5. **Cultural authenticity:** French customs, places, attitudes

### Linguistic Specifications:
- **Act 1 vocabulary:** 300-400 unique words (top 1500 frequency)
- **Act 2 vocabulary:** 400-500 words (introduce travel terms)
- **Act 3 vocabulary:** 450-550 words (nature, emotions, problem-solving)
- **Act 4 vocabulary:** 500-600 words (abstract concepts, reflection)

### Sentence Length by Act:
- Act 1: Average 6-10 words
- Act 2: Average 8-12 words
- Act 3: Average 10-15 words
- Act 4: Average 12-18 words

### Verb Tenses by Act:
- Act 1: Present (80%), near future with "aller" (20%)
- Act 2: Present (40%), futur proche (30%), passé composé (30%)
- Act 3: Imparfait (40%), passé composé (30%), conditionnel (20%), present (10%)
- Act 4: Subjonctif (30%), passé composé (30%), present (20%), other (20%)

### Key Phrase Targets (200 total, pre-identified in framework):
Each scene should incorporate the key phrases from `story_framework_fr.md`:
- Scene 1: "Bonjour, ça va?", "Un café, s'il vous plaît", etc. (12 phrases)
- Scene 2: "Combien ça coûte?", "C'est trop cher", etc. (15 phrases)
- [Continue for all 16 scenes]

## OUTPUT FORMAT

Please structure your output like this:

```
### SCENE 1: Café du Matin

[Narrative paragraph establishing setting]

«Dialogue line one,» dit Sophie.
«Dialogue line two,» répondit Lucas.

[More narrative and dialogue, natural flow]

### SCENE 2: Achats en Ville

[Continue with next scene...]
```

## QUALITY CRITERIA

1. **Narrative coherence:** Story should flow naturally, not feel like a language textbook
2. **Character authenticity:** Sophie and Lucas should feel like real people with motivations
3. **Emotional engagement:** Reader should care about the outcome
4. **Cultural details:** Include French-specific details (café culture, train system, alpine customs)
5. **Pedagogical value:** Phrases should be useful for real-world conversation
6. **Extractability:** Dialogue and sentences should be clear and self-contained enough to extract

Begin writing the narrative now, starting with Scene 1.
```

---

## Alternative: Act-by-Act Generation

If the full narrative is too long for one prompt, use this iterative approach:

### Prompt 1: Act 1 (Scenes 1-4)

```
Generate Act 1 (Scenes 1-4) of the French narrative "Sophie et Lucas - Une Aventure Alpine".

Target: 1500-2000 words, A-level difficulty (beginner)

[Include full character descriptions, Act 1 specifications, and requirements from primary prompt]

Focus on establishing characters, setting, and their decision to travel. Use simple present tense (80%) and futur proche with aller (20%). Vocabulary should be top 1500 most common French words.

Start now with Scene 1: Café du Matin.
```

### Prompt 2: Act 2 (Scenes 5-8)

```
Continue the narrative "Sophie et Lucas - Une Aventure Alpine" with Act 2 (Scenes 5-8).

Target: 1800-2200 words, B-level difficulty (elementary)

[Previous context: Act 1 summary]
Sophie and Lucas have decided to travel to the Alps. They're excited but also nervous.

[Include Act 2 specifications and requirements]

Begin with Scene 5: À la Gare, where they arrive at the train station.
```

### Prompt 3: Act 3 (Scenes 9-12)

```
Continue the narrative "Sophie et Lucas - Une Aventure Alpine" with Act 3 (Scenes 9-12).

Target: 1500-2000 words, C-level difficulty (intermediate)

[Previous context: Acts 1-2 summary]
Sophie and Lucas have arrived in the alpine village and begun their hiking adventure.

[Include Act 3 specifications and requirements]

This act should introduce real challenges and the separation. Begin with Scene 9: Randonnée Difficile.
```

### Prompt 4: Act 4 (Scenes 13-16)

```
Complete the narrative "Sophie et Lucas - Une Aventure Alpine" with Act 4 (Scenes 13-16).

Target: 1200-1600 words, D-level difficulty (advanced)

[Previous context: Acts 1-3 summary]
Sophie and Lucas have been separated in the mountains. Each has faced their own challenge.

[Include Act 4 specifications and requirements]

This final act should bring resolution, growth, and emotional depth. Begin with Scene 13: Les Secours.
```

---

## Post-Generation Review Prompt

After generating the narrative, use this prompt to review and improve:

```
Review this French narrative for language learning suitability:

[Paste generated narrative]

Check for:
1. **Scene markers:** Are all 16 scenes clearly marked with `### SCENE N: Title`?
2. **Dialogue ratio:** Is approximately 60% dialogue vs 40% narrative?
3. **Linguistic progression:** Does complexity increase naturally across acts?
4. **Extractable phrases:** Are sentences clear and complete enough to extract?
5. **Cultural authenticity:** Are French cultural details accurate and natural?
6. **Character consistency:** Do Sophie and Lucas behave consistently?
7. **Emotional engagement:** Is the story interesting and believable?

Provide:
- Overall assessment
- List of specific improvements needed
- Any problematic scenes that should be rewritten
```

---

## Usage Instructions

### Option A: Single Generation (Recommended for Claude with extended context)
1. Use the **Primary Generation Prompt**
2. Copy the entire prompt into Claude
3. Review output for completeness (should be 5000-8000 words)
4. Use **Post-Generation Review Prompt** if revisions needed
5. Save as `narrative_fr.txt`

### Option B: Iterative Generation (If hitting token limits)
1. Use **Act-by-Act prompts** (Prompts 1-4)
2. Generate each act separately
3. Concatenate all acts into single file
4. Use **Post-Generation Review Prompt** for final polish
5. Save as `narrative_fr.txt`

### Testing with extract_phrases.py
After generation, test extraction:
```bash
python3 extract_phrases.py narrative_fr.txt --output extracted_phrases_fr.json
```

Expected output: 400-600 phrases (narrative is longer than 200 target phrases to allow selection)

---

## Prompt Optimization Tips

If Claude's output doesn't meet requirements:

### Problem: Not enough dialogue
**Solution:** Add to prompt:
```
CRITICAL: Aim for 60% dialogue. Each scene should have at least 8-12 lines of dialogue between Sophie and Lucas or with other characters.
```

### Problem: Grammar doesn't progress
**Solution:** Add to prompt:
```
CRITICAL: Consciously shift verb tenses by act:
- Act 1: Only present + futur proche
- Act 2: Introduce passé composé for completed actions
- Act 3: Use imparfait for descriptions + conditionnel for hypotheticals
- Act 4: Include subjonctif when expressing wishes, doubts, emotions
```

### Problem: Sentences too complex for extraction
**Solution:** Add to prompt:
```
CRITICAL: Keep individual sentences complete but concise. Avoid run-on sentences with multiple subordinate clauses. Each phrase should be extractable and understandable in isolation.
```

### Problem: Story feels like a textbook
**Solution:** Add to prompt:
```
CRITICAL: This is a real story first, language tool second. Focus on authentic human emotions, realistic conflicts, and natural dialogue. Sophie and Lucas should feel like real people having a genuine experience.
```

---

## Example Output Format

```markdown
### SCENE 1: Café du Matin

Le soleil se lève sur Paris. Sophie entre dans son café préféré, un petit endroit chaleureux près de son appartement.

«Bonjour, ça va?» dit le serveur avec un sourire.

«Ça va bien, merci,» répond Sophie. «Un café, s'il vous plaît.»

Elle s'assoit près de la fenêtre. Lucas arrive quelques minutes plus tard.

«Salut Sophie!» dit-il joyeusement.

«Salut Lucas! Tu es en retard,» elle sourit.

«Désolé, le métro...» Lucas commande son café. «Un café au lait, s'il vous plaît.»

Ils s'assoient ensemble. Le serveur apporte les cafés.

«Merci,» disent-ils ensemble.

### SCENE 2: Achats en Ville

[Continue with next scene...]
```

---

## Cost Estimate

Based on Claude Sonnet 4.5 pricing:
- Full narrative (8000 words ≈ 10,000 tokens output): ~$0.30
- Review/revision (5000 tokens): ~$0.15
- Total per narrative: ~$0.45

For 3 languages: ~$1.35 total for narrative generation

---

## Next Steps After Generation

1. ✅ Generate narrative using prompts above
2. Save as `narrative_fr.txt` with scene markers
3. Run `extract_phrases.py` to extract phrases
4. Run `analyze_difficulty.py` to grade phrases
5. Manual curation: Review, select best 50+ per level
6. Run `fill_ipa_tags.py --lang fr` to add IPA
7. Integrate into `language_materials/fr/` directory structure

---

**Document Version:** 1.0  
**Created:** 2025-01-XX  
**Purpose:** Guide Claude narrative generation for Miolingo French materials  
**Related:** `story_framework_fr.md`, `RESOURCE_GENERATION_PLAN.md`
