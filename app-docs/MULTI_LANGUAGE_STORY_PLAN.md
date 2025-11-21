# Multi-Language Story Expansion Plan


## Overview
Expand the Sophie & Lucas story to all 6 supported languages with culturally adapted settings while maintaining the narrative structure.


## Story Settings by Language

| Language | Code | Setting | Story Title |
|----------|------|---------|-------------|
| Portuguese | pt | Brazilian countryside/mountains | Sophie & Lucas: Uma Jornada aos Alpes |
| French | fr | French Alps | Sophie & Lucas: A Journey to the Alps |
| Dutch | nl | Netherlands countryside | Sophie & Lucas: Een Reis naar de Alpen |
| German | de | Black Forest or Bavarian Alps | Sophie & Lucas: Eine Reise in die Alpen |
| Italian | it | Italian Dolomites | Sophie & Lucas: Un Viaggio sulle Alpi |
| Spanish | es | Sierra Nevada, Spain | Sophie & Lucas: Un Viaje a Sierra Nevada |


## Implementation Phases


### Phase 1: Story Translation & Adaptation ⏳
**Status:** Planning
**Objective:** Create culturally adapted full stories for each language

**Tasks:**
1. **Portuguese (pt-BR):**
   - Translate Sophie & Lucas story to Portuguese
   - Adapt setting to Brazilian context (countryside/mountains)
   - Create `language_materials/pt/story.md`
   - Maintain 16-scene structure

2. **Dutch (nl-NL):**
   - Translate to Dutch
   - Adapt setting to Netherlands countryside
   - Create `language_materials/nl/story.md`

3. **German (de-DE):**
   - Translate to German
   - Adapt setting to Black Forest or Bavarian Alps
   - Create `language_materials/de/story.md`

4. **Italian (it-IT):**
   - Translate to Italian
   - Adapt setting to Italian Dolomites
   - Create `language_materials/it/story.md`

5. **Spanish (es-ES):**
   - Translate to Spanish
   - Adapt setting to Sierra Nevada, Spain
   - Create `language_materials/es/story.md`

**Translation Approach:**
- Use LLM for full story translation with cultural adaptation instructions
- Maintain character names (Sophie & Lucas) for consistency
- Adapt place names, cultural references, and local details
- Keep scene structure (16 scenes) for consistency

**Deliverables:**
- 5 new `story.md` files (French already complete)
- Cultural adaptation notes in comments
- Consistent scene numbering and structure

---


### Phase 2: Phrase Extraction to JSON ⏳
**Status:** Planning
**Objective:** Extract individual sentences/phrases from stories into structured JSON files

**Tasks:**
1. For each language (pt, nl, de, it, es):
   - Parse `story.md` and extract phrases by scene
   - Create 16 JSON files: `scene-01-title.json` through `scene-16-title.json`
   - Store in `language_materials/{lang_code}/story-scenes-json/`
   - Initial format: `{"french": "text", "english": "[TO TRANSLATE]", "ipa": "[TO GENERATE]"}`

**Extraction Script Requirements:**
- Automated phrase detection (by sentence boundaries)
- Scene boundary detection (## headings in markdown)
- Preserve narrative order
- Handle dialogue and narrative text
- Generate friendly filenames from scene titles

**Script Name:** `scripts/extract_story_phrases.py`
**Usage:** `python scripts/extract_story_phrases.py <lang_code>`

**Deliverables:**
- 80 JSON files total (5 languages × 16 scenes)
- Extraction script for reusability
- Phrase count validation per scene

---


### Phase 3: English Translation ✅ (French) / ⏳ (Others)
**Status:** French complete, others planning
**Objective:** Translate all phrases to English for learner reference

**Lessons Learned from French Translation:**
- ❌ Avoid: External LLM tools lose context and sync
- ❌ Avoid: Scripts with manual [TO TRANSLATE] markers (436 phrases left)
- ✅ Effective: Direct LLM translation in-session with file reading
- ✅ Effective: VS Code TAB autocomplete for rapid manual translation

**Recommended Approach:**
1. **Batch LLM Translation (Preferred):**
   - Read JSON file directly in agent session
   - Translate all phrases in single pass with full story context
   - Replace [TO TRANSLATE] markers inline
   - Process scene-by-scene to maintain context
   - Validate JSON structure after translation

2. **Quality Assurance:**
   - Cross-check translations for consistency
   - Ensure character/place names match across scenes
   - Verify cultural adaptations are preserved

**Script Name:** `scripts/translate_story_phrases.py`
**Usage:** `python scripts/translate_story_phrases.py <lang_code> <scene_number>`
**Alternate:** Agent-driven direct translation in conversation

**Deliverables:**
- All story-scenes-json files with English translations
- Translation quality report (consistency check)
- No [TO TRANSLATE] markers remaining

---


### Phase 4: IPA Generation ✅ (French) / ⏳ (Others)
**Status:** French complete, others planning
**Objective:** Generate IPA transcriptions for pronunciation reference

**Technical Requirements:**
- Use `espeak` command (NOT espeak-ng) for IPA generation
- Command format: `espeak -q -v {voice_code} --ipa "text"`
- Voice codes per language:
  - pt-BR: `pt-br`
  - fr-FR: `fr-fr`
  - nl-NL: `nl`
  - de-DE: `de`
  - it-IT: `it`
  - es-ES: `es`

**Approach:**
1. Iterate through all JSON files for a language
2. For each phrase, run espeak command
3. Clean and normalize IPA output
4. Insert into JSON file
5. Validate IPA encoding (UTF-8)

**Script Name:** `scripts/generate_ipa_for_language.py`
**Usage:** `python scripts/generate_ipa_for_language.py <lang_code>`

**Deliverables:**
- All story-scenes-json files with IPA transcriptions
- IPA validation report
- No [TO GENERATE] markers remaining

---


### Phase 5: Metadata Enhancement ⏳
**Status:** Planning
**Objective:** Add difficulty levels, tags, and educational metadata to phrases

**Metadata Schema:**
```json
{
  "metadata": {
    "title": "Scene Title",
    "scene_number": 1,
    "total_phrases": 30,
    "setting": "Location description",
    "difficulty": "beginner|intermediate|advanced"
  },
  "phrases": [
    {
      "id": 1,
      "french": "Bonjour!",
      "english": "Hello!",
      "ipa": "bɔ̃ʒuʁ",
      "difficulty": "beginner",
      "tags": ["greeting", "essential"],
      "type": "dialogue|narrative",
      "speaker": "Sophie|Lucas|narrator"
    }
  ]
}
```

**Metadata Categories:**
- **Difficulty:** beginner, intermediate, advanced
- **Tags:** greeting, food, travel, emotion, question, command, description, etc.
- **Type:** dialogue vs narrative
- **Speaker:** Character attribution for dialogue

**Implementation:**
1. Add metadata to existing French JSON files first
2. Replicate metadata structure for other languages
3. Use LLM to suggest difficulty and tags
4. Manual review and adjustment

**Deliverables:**
- Enhanced JSON schema documentation
- All story-scenes-json files with metadata
- Filtering capability in Story Reader

---


### Phase 6: Scene Mode Practice Integration ⏳
**Status:** Planning
**Objective:** Allow practicing story phrases directly from Scene by Scene mode

**Current State:**
- Story Reader displays phrases with optional English/IPA
- No direct practice integration
- User must manually navigate to Practice tab

**Proposed Enhancements:**

#### 6.1: Audio Playback in Story Reader
- Add 🔊 button next to each phrase in Scene by Scene mode
- Use existing TTS logic (`generate_audio_file()`)
- Play phrase audio inline without leaving Story Reader
- Respect current TTS engine and voice settings

#### 6.2: Practice Mode Integration
- Add "Practice this phrase" button/checkbox per phrase
- Collect selected phrases for practice session
- Transition to Practice tab with selected phrases pre-loaded
- Maintain scene context in practice session

**UI Design Considerations:**
- Keep modular design for easy refactoring
- Add practice controls without cluttering reading experience
- Consider collapsible "Practice Mode" section
- Show visual feedback for selected phrases

**Implementation Steps:**
1. Add audio playback first (simpler, no state changes)
2. Add phrase selection UI (checkboxes or buttons)
3. Create "Start Practice" action button
4. Integrate with existing practice workflow in tab1
5. Test transitions and state management

**Code Locations:**
- `render_scene_by_scene()` in app.py (lines ~1272-1363)
- `generate_audio_file()` for TTS (existing)
- Practice tab session state management

**Deliverables:**
- Audio playback in Story Reader
- Practice phrase selection UI
- Seamless transition to Practice tab
- State management for selected phrases

---


## Project Timeline Estimate

| Phase | Estimated Time | Dependencies |
|-------|----------------|--------------|
| Phase 1: Translation | 4-6 hours | None |
| Phase 2: Extraction | 2-3 hours | Phase 1 |
| Phase 3: English Translation | 3-4 hours | Phase 2 |
| Phase 4: IPA Generation | 1-2 hours | Phase 2 |
| Phase 5: Metadata | 3-4 hours | Phases 3-4 |
| Phase 6: Practice Integration | 4-5 hours | Phases 1-5 |
| **Total** | **17-24 hours** | Sequential |

**Notes:**
- Phases 3 and 4 can run in parallel after Phase 2
- Phase 5 can start incrementally during Phases 3-4
- Phase 6 can begin with French while others complete
- User testing and iteration adds 20-30% to estimates

---


## Priority Ordering


### High Priority (Core Functionality)
1. **Phase 1:** Portuguese and Spanish translations (highest user demand)
2. **Phase 2:** Phrase extraction (enables all other phases)
3. **Phase 3:** English translations (learning prerequisite)


### Medium Priority (User Experience)
4. **Phase 4:** IPA generation (pronunciation reference)
5. **Phase 6.1:** Audio playback in Story Reader


### Lower Priority (Enhancements)
6. **Phase 5:** Metadata enhancement
7. **Phase 6.2:** Practice mode integration

---


## Technical Considerations


### File Structure
```
language_materials/
├── pt/
│   ├── story.md
│   └── story-scenes-json/
│       ├── scene-01-title.json
│       └── ... (16 scenes)
├── fr/ (✅ COMPLETE)
│   ├── story.md
│   └── story-scenes-json/ (505 phrases)
├── nl/
├── de/
├── it/
└── es/
```


### App Integration Points
- **Story Reader:** `render_story_reader()` - Already language-aware ✅
- **Sidebar Links:** Language-specific story links ✅
- **Materials Browser:** Auto-discover new languages ✅
- **Practice Tab:** Load story-scenes-json files (existing)


### Quality Assurance Checklist
- [ ] All stories maintain 16-scene structure
- [ ] Character names consistent across languages
- [ ] Cultural adaptations appropriate and respectful
- [ ] All phrases have English translations
- [ ] All phrases have IPA transcriptions
- [ ] JSON files valid and UTF-8 encoded
- [ ] Story Reader displays correctly for all languages
- [ ] Audio generation works for all languages
- [ ] Practice integration seamless

---


## Next Actions


### Immediate (Ready to Start)
1. ✅ Restructure tabs (Story Reader as second tab) - **COMPLETE**
2. ✅ Add language-aware sidebar links - **COMPLETE**
3. ⏳ Begin Phase 1: Translate Portuguese story with Brazilian setting


### Short Term (After Phase 1)
4. Create phrase extraction script
5. Run extraction on French (validation) and Portuguese


### Medium Term
6. Translate remaining languages (nl, de, it, es)
7. Generate IPA for all languages
8. Add audio playback to Story Reader

---


## Success Metrics
- All 6 languages have complete story.md files
- All languages have 16 scenes × JSON files with translations
- IPA transcriptions complete for all phrases
- Story Reader accessible and functional for all languages
- User can practice story phrases directly from reading interface
- Zero manual [TO TRANSLATE] markers in final state

---

**Last Updated:** 2025-11-20
**Status:** Phase 0 (Planning and Restructuring) Complete ✅
**Next Phase:** Phase 1 - Portuguese Story Translation
