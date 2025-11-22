# Story Practice Integration Proposal

## Problem Statement

Currently, the Story Reader and Quick Practice tabs are disconnected:
- **Story Reader Tab**: Users can read stories scene-by-scene with translations/IPA, but cannot practice pronunciation
- **Quick Practice Tab**: Users can practice pronunciation with audio playback and recording, but must manually load story scenes from the Built-in Library
- **No integration**: Users see a message "Ready to practice? Go to the Quick Practice tab..." but this requires manual navigation and file selection

## Proposed Solution: Interactive Practice Mode in Story Reader

### Core Design Principles
1. **No code duplication**: Reuse existing `practice_word_from_audio()` function and practice UI components
2. **Seamless UX**: Practice directly from Story Reader without switching tabs
3. **Progressive disclosure**: Show practice options only when user wants them
4. **Mobile-friendly**: Maintain compact, touch-friendly interface

---

## Detailed Design

### 1. Story Reader Enhancement: Three Reading Modes

```
Story Reader Tab Layout:
┌─────────────────────────────────────────────────┐
│ 📖 Sophie & Lucas: Uma Jornada aos Alpes       │
├─────────────────────────────────────────────────┤
│ Reading Mode: [ 📄 Full Story | 🎬 Scene by Scene | 🎙️ Practice Mode ]
└─────────────────────────────────────────────────┘
```

**New "🎙️ Practice Mode"** would be added alongside existing modes.

### 2. Practice Mode Interface

```
Practice Mode Layout:
┌────────────────────────────────────────────────────────────┐
│ Select Scene: [Dropdown: Scene 01: O Café da Manhã ▼]     │
├────────────────────────────────────────────────────────────┤
│ Phrase Progress: [=========>         ] 5 / 40              │
├────────────────────────────────────────────────────────────┤
│ ⬅️ Previous  |  Next ➡️  |  [☐ Show Translation] [☐ IPA]   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ 🎯 Current Phrase:                                         │
│    "O sol nasce suavemente sobre São Paulo."              │
│                                                            │
│ [📖 Show Translation]  [📚 Show IPA]                       │
│                                                            │
│ 🎯 Target pronunciation:                                   │
│    ▶️ [Audio Player]                                       │
│                                                            │
│ 🎙️ Record your pronunciation:                             │
│    🔴 [Record Button]                                      │
│                                                            │
│ [▶️ Your recording:]                                       │
│    ▶️ [Audio Player]                                       │
│                                                            │
│    [✅ Check Pronunciation]  [🗑️ Remove Recording]         │
│                                                            │
│ ─────────────────────────────────────────────────────────  │
│ 📊 Results: 95% - Excellent!                               │
│ [...comparison details...]                                 │
└────────────────────────────────────────────────────────────┘
```

### 3. Implementation Structure

#### A. New Function: `render_scene_practice_mode(scenes_dir)`

```python
def render_scene_practice_mode(scenes_dir):
    """
    Practice mode: Navigate through story phrases with audio + recording
    Reuses practice_word_from_audio() logic from Quick Practice
    """
    # Scene selection
    scene_files = sorted(scenes_dir.glob("scene-*.json"))
    selected_scene_file = st.selectbox("Select scene", scene_options)
    
    # Load scene data
    with open(selected_scene_file, 'r') as f:
        scene_data = json.load(f)
    
    # Initialize phrase index in session state
    if 'story_practice_index' not in st.session_state:
        st.session_state.story_practice_index = 0
    
    # Progress bar
    current_idx = st.session_state.story_practice_index
    total_phrases = len(scene_data[lang_code])
    st.progress(current_idx / total_phrases)
    st.caption(f"Phrase {current_idx + 1} of {total_phrases}")
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("⬅️ Previous", disabled=(current_idx == 0)):
            st.session_state.story_practice_index -= 1
            st.session_state.last_result = None  # Clear results
            st.rerun()
    with col2:
        if st.button("Next ➡️", disabled=(current_idx >= total_phrases - 1)):
            st.session_state.story_practice_index += 1
            st.session_state.last_result = None
            st.rerun()
    
    # Get current phrase
    phrase_obj = scene_data[lang_code][current_idx]
    text = phrase_obj[lang_code]
    translation = phrase_obj.get('english', '')
    ipa = phrase_obj.get('ipa', '').strip('[]')  # Remove brackets for display
    
    # Display phrase
    st.markdown(f"#### 🎯 **{text}**")
    
    # Optional translation/IPA (collapsible)
    with st.expander("📖 Translation & Reference"):
        if translation:
            st.markdown(f"**🇬🇧 English:** {translation}")
        if ipa:
            st.markdown(f"**📚 IPA:** {ipa}")
    
    # === PRACTICE INTERFACE (reused from Quick Practice) ===
    render_practice_interface(text)
```

#### B. Extract Reusable Component: `render_practice_interface(text)`

```python
def render_practice_interface(text):
    """
    Reusable practice interface for any phrase
    Used by both Quick Practice and Story Practice Mode
    
    Shows:
    - Target audio playback
    - Recording interface
    - Results comparison
    
    This eliminates code duplication between tabs
    """
    # Target audio
    st.write("🎯 **Target pronunciation:**")
    audio_bytes, audio_format = generate_target_audio(text, st.session_state.settings)
    st.audio(audio_bytes, format=audio_format)
    
    # Recording interface
    st.write("🎙️ **Record your pronunciation:**")
    audio_data = st.audio_input("Click to record", 
                                 key=f"audio_input_{st.session_state.audio_input_key}")
    
    if audio_data:
        st.write("▶️ **Your recording:**")
        st.audio(audio_data, format='audio/wav')
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("✅ Check Pronunciation", key="check_btn", type="primary"):
                with st.spinner("Processing..."):
                    result = practice_word_from_audio(
                        text, 
                        audio_data.getvalue(), 
                        st.session_state.settings
                    )
                    st.session_state.last_result = result
                    st.rerun()
        
        with col2:
            if st.button("🗑️ Remove Recording", key="clear_btn"):
                st.session_state.last_result = None
                st.session_state.audio_input_key += 1
                st.rerun()
    
    # Show results (if any)
    if st.session_state.last_result:
        render_practice_results(st.session_state.last_result)
```

#### C. Extract Results Component: `render_practice_results(result)`

```python
def render_practice_results(result):
    """
    Reusable results display for pronunciation practice
    Shows comparison, scores, audio playback
    """
    st.markdown("---")
    st.header("Results")
    
    # Score display with celebration sounds
    if result["exact_match"]:
        st.success("🎉 PERFECT MATCH!")
        # [play celebration sound]
    elif result['similarity'] >= 0.90:
        st.success(f"✨ Excellent! {result['similarity']:.1%}")
        # [play success sound]
    else:
        st.info(f"📊 Score: {result['similarity']:.1%}")
    
    # Side-by-side comparison
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Target")
        st.write(f"**Text:** {result['target']}")
        st.write(f"**Phonemes:** {result['correct_phonemes']}")
        # [audio playback]
    
    with col2:
        st.subheader("Your Pronunciation")
        st.write(f"**Recognized:** {result['recognized']}")
        st.write(f"**Phonemes:** {result['user_phonemes']}")
        # [warning if text differs]
    
    # Detailed analysis (optional)
    if st.checkbox("🔍 Show detailed analysis"):
        # [phoneme-by-phoneme breakdown]
```

### 4. Modified Story Reader Structure

```python
def render_story_reader():
    """Story Reader with three modes"""
    lang_code = st.session_state.get('material_language', 'fr')
    story_md_path = Path(f"language_materials/{lang_code}/story.md")
    story_scenes_dir = Path(f"language_materials/{lang_code}/story-scenes-json")
    
    st.header(f"📖 {story_config[lang_code]['title']}")
    
    # Three-way mode selector
    story_mode = st.radio(
        "Choose mode:",
        ["📄 Full Story", "🎬 Scene by Scene", "🎙️ Practice Mode"],
        horizontal=True
    )
    
    if story_mode == "📄 Full Story":
        render_full_story(story_md_path)
    elif story_mode == "🎬 Scene by Scene":
        render_scene_by_scene(story_scenes_dir)
    elif story_mode == "🎙️ Practice Mode":
        render_scene_practice_mode(story_scenes_dir)  # NEW!
```

---

## Implementation Benefits

### ✅ Advantages
1. **Zero code duplication**: Reuses `practice_word_from_audio()`, audio generation, results display
2. **Consistent UX**: Same practice interface in both Quick Practice and Story Reader
3. **Seamless workflow**: Practice immediately without switching tabs or loading files
4. **Progress tracking**: Built-in progress bar shows position in scene
5. **Context preservation**: Users stay immersed in the story context
6. **Easy testing**: Can test Portuguese story immediately before translating other languages

### 🎯 User Flow Comparison

**Before (Current):**
1. Story Reader → Read Scene 1
2. See message: "Go to Quick Practice tab..."
3. Switch to Quick Practice tab
4. Load Practice Materials → Built-in Library → Portuguese → Story Scenes → scene-01
5. Practice phrases
6. ❌ Lost story context, manual navigation

**After (Proposed):**
1. Story Reader → Practice Mode
2. Select Scene 1
3. Practice phrases with ▶️ audio + 🎙️ recording
4. ✅ Seamless, contextual, efficient

---

## Testing Plan

### Phase 1: Portuguese Story (Current State)
1. Implement Practice Mode for Portuguese (all 438 phrases ready)
2. Test navigation, audio playback, recording, results
3. Verify no regressions in Quick Practice tab
4. Mobile testing (key user base)

### Phase 2: Refinement
1. User feedback on UX
2. Performance testing (audio generation speed)
3. Edge case handling (empty scenes, missing IPA)

### Phase 3: Expand to Other Languages
1. Once Portuguese Practice Mode is stable
2. Complete German/Dutch/Italian/Spanish stories
3. Enable Practice Mode for all 6 languages

---

## Technical Considerations

### Session State Management
```python
# New session state keys for Story Practice Mode
st.session_state.story_practice_scene_file = None  # Currently selected scene
st.session_state.story_practice_index = 0  # Current phrase index
st.session_state.audio_input_key = 0  # For recording widget reset
st.session_state.last_result = None  # Practice result
```

### Code Organization
```
app.py structure:
├── Core Functions (unchanged)
│   ├── practice_word_from_audio()
│   ├── generate_target_audio()
│   └── transcribe_audio()
├── NEW: Reusable UI Components
│   ├── render_practice_interface(text)  # Extracted from Quick Practice
│   └── render_practice_results(result)  # Extracted from Quick Practice
├── Story Reader Functions
│   ├── render_story_reader()  # Modified: add Practice Mode option
│   ├── render_full_story()  # Unchanged
│   ├── render_scene_by_scene()  # Unchanged
│   └── render_scene_practice_mode()  # NEW!
└── Main Tabs (unchanged)
    ├── tab1: Quick Practice (now uses render_practice_interface())
    ├── tab2: Story Reader (now has Practice Mode)
    ├── tab3: Statistics
    └── tab4: History
```

---

## Alternative Approaches (Considered & Rejected)

### ❌ Approach A: Duplicate practice code in Story Reader
- **Problem**: Code duplication, maintenance burden
- **Problem**: Inconsistent behavior between tabs

### ❌ Approach B: Add practice button in Scene by Scene mode
- **Problem**: Cluttered UI, unclear which phrase to practice
- **Problem**: Still requires per-phrase selection

### ❌ Approach C: Auto-load story scenes in Quick Practice
- **Problem**: Doesn't solve context switching
- **Problem**: Quick Practice becomes story-specific

---

## Recommendation

**Proceed with Implementation?**

✅ **YES** - This design provides:
- Clean separation of concerns (reading vs. practicing)
- Reusable components (no duplication)
- Excellent user experience (seamless workflow)
- Easy testing with Portuguese (438 phrases ready)
- Scalable to all 6 languages

**Next Steps:**
1. Extract `render_practice_interface()` and `render_practice_results()` from Quick Practice
2. Implement `render_scene_practice_mode()` in Story Reader
3. Add Practice Mode radio button option
4. Test with Portuguese story scenes
5. Gather user feedback before translating remaining languages

---

## Open Questions

1. **Should Practice Mode remember progress?** (e.g., "Resume from Phrase 15")
   - Proposal: Add session state to track last practiced phrase per scene
   
2. **Should we track practice statistics in Practice Mode?**
   - Proposal: Yes, reuse existing statistics tracking from Quick Practice
   
3. **Should we allow random phrase order in Practice Mode?**
   - Proposal: Add toggle "🔀 Random Order" for variety in repeated practice
   
4. **Should Practice Mode show scene narrative context?**
   - Proposal: Show scene title + total phrase count, but not surrounding phrases (focus)

---

**Document Version:** 1.0  
**Date:** 2025-11-21  
**Author:** GitHub Copilot  
**Status:** Awaiting User Approval
