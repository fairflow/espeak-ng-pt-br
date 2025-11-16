# Resource Generation Plan for Miolingo

**Date:** 2025-11-16  
**Goal:** Generate 200-1000 phrases per language with narrative coherence and proper difficulty grading

---

## Phase 1: Narrative Story Generation (French First)

### Step 1.1: Story Framework Design
**Duration:** 1-2 days  
**LLM Recommendation:** **Claude Sonnet 3.5 or 4** (excellent at creative writing with coherent narrative structure)

**Tasks:**
1. Define story arc structure:
   - **Act 1: Modern Urban Life** (A-level phrases)
     - Cafés, shops, daily routines
     - Simple present tense, basic vocabulary
     - ~50 phrases
   
   - **Act 2: The Journey Begins** (B-level phrases)
     - Travel preparations, departures
     - Near future, simple past, more varied vocabulary
     - ~60 phrases
   
   - **Act 3: Challenges & Separation** (C-level phrases)
     - Unexpected events, emotional situations
     - Complex past tenses, conditional, richer vocabulary
     - ~50 phrases
   
   - **Act 4: Individual Journeys & Reunion** (D-level phrases)
     - Reflection, determination, resolution
     - Subjunctive, complex sentences, abstract concepts
     - ~40 phrases

2. Create character profiles for the couple (names, backgrounds, motivations)
3. Outline 20-30 key scenes/situations
4. Map linguistic features to story progression

**Deliverable:** `story_framework_fr.md` with scene outlines and linguistic targets

---

### Step 1.2: AI-Generated Narrative
**Duration:** 2-3 days  
**LLM Recommendation:** **Claude Sonnet 3.5** (best for long-form creative content with consistency)

**Prompt Strategy:**
```
You are a creative writer crafting an engaging story in French for language learners.

Story premise: [Insert from framework]

Requirements:
- 5000-8000 words in French
- Natural dialogue between characters (60% of content)
- Progressive vocabulary complexity (start A1, end B2/C1)
- Include these linguistic elements per act: [list from framework]
- Emotional resonance and authentic cultural references
- Scene transitions that feel natural

Deliver in 4 acts with scene markers.
```

**Alternative Approach:** Use **GPT-4** for initial draft, then **Claude** for refinement and dialogue enhancement

**Deliverable:** `narrative_fr_v1.txt` (raw story)

---

## Phase 2: Phrase Extraction & Analysis

### Step 2.1: Automated Phrase Extraction
**Duration:** 1 day  
**LLM Recommendation:** **Claude Sonnet 3.5** (excellent at nuanced text analysis)

**Script:** `extract_phrases.py`

**Logic:**
1. Parse narrative into dialogue segments
2. Extract sentences/phrases 5-20 words long
3. Filter for:
   - Complete grammatical units
   - Practical/reusable expressions
   - Natural language patterns
4. Tag with context (scene, character, emotion)

**Deliverable:** `extracted_phrases_fr.json` (~400-600 raw phrases)

---

### Step 2.2: Linguistic Difficulty Analysis
**Duration:** 2-3 days  
**LLM Recommendation:** **Claude Sonnet 3.5** (superior at detailed linguistic analysis)

**Script:** `analyze_difficulty.py`

**Criteria Matrix:**

| Factor | Weight | A-level | B-level | C-level | D-level |
|--------|--------|---------|---------|---------|---------|
| Sentence length | 15% | 3-8 words | 8-12 words | 12-18 words | 15-25 words |
| Vocabulary frequency | 25% | Top 500 | Top 1500 | Top 3000 | Top 5000+ |
| Verb tenses | 20% | Present, near future | Simple past, future | Imperfect, conditional | Subjunctive, complex |
| Grammatical structures | 15% | SVO, no subordinates | 1 subordinate | Multiple clauses | Relative pronouns, passive |
| Phonetic complexity | 10% | Common phonemes | Some nasal vowels | Liaisons, r sounds | Complex clusters |
| Idiomatic content | 10% | Literal | Some idioms | Common expressions | Abstract/figurative |
| Cultural references | 5% | Universal | Regional | Cultural-specific | Literary/historical |

**Process:**
1. Use spaCy or similar for automatic tagging (POS, dependency parsing)
2. LLM analyzes each phrase against criteria
3. Assign difficulty score 0-100
4. Bin into A (0-25), B (26-50), C (51-75), D (76-100)
5. Manual review of edge cases

**Prompt Template:**
```
Analyze this French phrase for language learning difficulty:

Phrase: "[phrase]"
Context: [scene description]

Rate 0-100 on these factors:
1. Vocabulary frequency (25%)
2. Grammar complexity (20%)
3. Sentence length (15%)
4. Verb tense difficulty (20%)
...

Provide:
- Overall score
- Difficulty level (A/B/C/D)
- Key challenging elements
- Suggested prerequisite knowledge
```

**Deliverable:** `graded_phrases_fr.json` with scores and justifications

---

### Step 2.3: Curation & Progression Design
**Duration:** 2-3 days  
**Human + AI:** Review and arrange phrases

**Tasks:**
1. Remove redundant phrases
2. Ensure each level has 50+ phrases
3. Within each level, order by:
   - Internal difficulty progression
   - Narrative coherence (story order)
   - Phonetic feature introduction
4. Add English translations
5. Validate with native speaker (if possible)

**Deliverable:** `curated_phrases_fr_A.txt` through `D.txt`

---

## Phase 3: IPA Generation & File Creation

### Step 3.1: IPA Generation
**Duration:** 1 day  
**Tool:** Existing `fill_ipa_tags.py` script

**Process:**
1. Convert curated phrase files to standard format:
   ```
   phrase | translation | [ipa]
   ```
2. Run: `ESPEAK_DATA_PATH=$PWD python3 fill_ipa_tags.py --lang fr`
3. Manual review of IPA accuracy (sample 20% of phrases)

**Deliverable:** `language_materials/fr/phrases-A/phr-XX.txt` (complete with IPA)

---

### Step 3.2: Metadata & Integration
**Duration:** 1 day

**Tasks:**
1. Update `language_materials/fr/metadata.json`:
   - Total phrase count
   - Difficulty distribution
   - Story theme/description
   - Version info
2. Create phrase set descriptions (for UI display)
3. Test loading in app
4. Verify TTS pronunciation quality

**Deliverable:** Complete French language material set ready for production

---

## Phase 4: Replication for Portuguese & Dutch

### Portuguese Adaptation
**Duration:** 7-10 days  
**Approach:** Translate narrative OR create new culturally-appropriate story

**Option A: Translation** (faster, 7 days)
- Translate French narrative to Portuguese
- Adjust cultural references (Portuguese/Brazilian context)
- Re-analyze difficulty (may shift due to language differences)
- Generate new IPA with eSpeak NG pt-br

**Option B: New Story** (more authentic, 10 days)
- Use Portuguese myths/legends as inspiration
- Follow same framework as French
- More culturally resonant but requires new narrative generation

**Recommendation:** Start with Option A for speed, plan Option B for v2.0

### Dutch Adaptation
**Duration:** 7-10 days  
**Same process as Portuguese**

---

## Phase 5: Grammatical Feature Tracking (Optional Enhancement)

### Step 5.1: Grammatical Annotation
**Duration:** 3-4 days  
**LLM:** Claude Sonnet 3.5 (best for linguistic analysis)

**Add metadata to each phrase:**
```json
{
  "phrase": "Nous partirons demain matin",
  "translation": "We will leave tomorrow morning",
  "ipa": "[nu paʁtiʁɔ̃ dəmɛ̃ matɛ̃]",
  "difficulty": "B",
  "grammar_features": {
    "tenses": ["future_simple"],
    "persons": ["1st_plural"],
    "sentence_type": "declarative",
    "clauses": 1,
    "verb_count": 1,
    "pronoun_types": ["subject"]
  },
  "vocabulary_tags": ["time", "movement"],
  "phonetic_features": ["nasal_vowels", "liaison"]
}
```

**Use cases:**
- Filter phrases by grammatical feature
- Create grammar-focused practice sets
- Track learner progress by grammar concept
- Future: Grammar explanations in app

---

## Timeline Summary

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| 1.1 Framework | 1-2 days | None |
| 1.2 Narrative | 2-3 days | 1.1 |
| 2.1 Extraction | 1 day | 1.2 |
| 2.2 Analysis | 2-3 days | 2.1 |
| 2.3 Curation | 2-3 days | 2.2 |
| 3.1 IPA | 1 day | 2.3 |
| 3.2 Integration | 1 day | 3.1 |
| **French Total** | **10-14 days** | - |
| Portuguese | 7-10 days | French complete |
| Dutch | 7-10 days | French complete |
| **Grand Total** | **24-34 days** | - |

---

## LLM Selection Guide

### For Different Tasks:

**Creative Writing (Narrative Generation):**
- **Best:** Claude Sonnet 3.5 or 4
- **Alternative:** GPT-4 Turbo
- **Why:** Claude excels at maintaining narrative coherence over long texts, creates more natural dialogue

**Linguistic Analysis:**
- **Best:** Claude Sonnet 3.5 or 4
- **Alternative:** GPT-4 with linguistic prompting
- **Why:** Claude shows superior understanding of nuanced linguistic concepts, better at following complex criteria

**Translation:**
- **Best:** GPT-4 Turbo or Claude Sonnet 4
- **Alternative:** DeepL API (non-LLM but excellent for European languages)
- **Why:** Both handle idiomatic expressions well, GPT-4 slightly better for cultural adaptation

**Code Generation (Scripts):**
- **Best:** Claude Sonnet 3.5 (current choice is correct!)
- **Alternative:** GPT-4
- **Why:** You're already using the right model for coding tasks

**Batch Processing:**
- **Best:** GPT-3.5 Turbo (cost-effective) or Claude Haiku (fast)
- **Alternative:** Llama 3 70B (if self-hosting)
- **Why:** For analyzing hundreds of phrases, cheaper models with good prompting work well

---

## Recommendation for Your Use Case

**Stay with Claude Sonnet 4.5** for:
- Initial story framework design
- Narrative generation
- Linguistic analysis
- All coding tasks

**Consider switching to:**
- **GPT-4 Turbo** for: Large-scale translation tasks (better API pricing for high volume)
- **Claude Haiku** for: Batch difficulty scoring (100+ phrases at once, much cheaper)
- **DeepL API** for: Portuguese/Dutch translations of French phrases (specialized tool)

---

## Resource Requirements

### Human Effort:
- Story framework: 4-6 hours
- Curation/review: 10-15 hours per language
- Testing/validation: 5-10 hours per language
- **Total: ~40-60 hours across all languages**

### AI/Compute:
- LLM API costs (estimate): $20-50 for French, $15-30 per additional language
- eSpeak NG: Local (free)
- Storage: Minimal (<10MB per language)

### Quality Assurance:
- Native speaker review recommended (outsource via Upwork: ~$50-100 per language)
- Beta testing with 5-10 learners per language
- A/B testing of narrative vs. non-narrative approaches

---

## Success Metrics

1. **Quantity:** 200+ phrases per language (target: 300-500)
2. **Distribution:** 25% A-level, 30% B-level, 25% C-level, 20% D-level
3. **Quality:** >85% native speaker approval rating
4. **Engagement:** Users complete 2x more phrases with narrative vs. random
5. **Difficulty accuracy:** Learner-reported difficulty matches assigned level 80%+ of time

---

## Next Steps (Immediate)

1. **Create story framework document** (2 hours) - Start tomorrow
2. **Generate French narrative** (1 day) - Use Claude Sonnet 3.5 with iterative refinement
3. **Build extraction pipeline** (1 day) - Python script using existing tools
4. **Set up difficulty analysis** (1 day) - Combine spaCy + Claude API

**First milestone:** 50 French A-level phrases with IPA by end of Week 1

Would you like me to:
1. Start drafting the story framework for French now?
2. Create the extraction and analysis scripts?
3. Provide more detailed prompts for each LLM task?
