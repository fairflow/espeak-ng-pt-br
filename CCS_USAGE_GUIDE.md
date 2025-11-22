# CCS Testing Framework - Quick Start Guide

## Overview

The CCS (Calculus of Communicating Systems) testing framework is now integrated into `streamlit_app_v2.py` on the `ccs-testing` branch. This integration is:

- **Non-invasive**: Wrapped in `CCS_AVAILABLE` checks
- **Disabled by default**: No impact on normal app usage
- **Local testing**: Stays on ccs-testing branch for evaluation
- **Optional**: Framework gracefully disabled if imports fail

## How to Use

### 1. Start the App

```bash
cd /Users/matthew/Software/working/adaptive-text/espeak-ng
source venv/bin/activate
streamlit run streamlit_app_v2.py
```

The app runs normally with testing disabled.

### 2. Enable Testing Mode

In the sidebar, you'll see a new section:

```
🧪 CCS Testing
```

Click the **"🧪 Enable CCS Testing"** button to activate testing mode.

### 3. Testing Workflow

Once enabled, the sidebar shows validation controls:

```
🔍 CCS Validation
Current State:
  Mode: [QUICK_PRACTICE or GUIDED_LIST]
  Visible Elements: [list of UI elements]
  Capabilities: [list of app capabilities]

User Perception:
  ✅ Matches    ❌ Mismatch
  [Notes text area]
```

**For each action you take:**

1. **Perform an action** (navigate, record, play audio, etc.)
2. **Check the "Current State"** - does it match what you see?
3. **Validate your perception:**
   - Click **✅ Matches** if UI matches the model
   - Click **❌ Mismatch** if something is wrong (add notes explaining what's wrong)
4. Repeat for each interaction

### 4. What Gets Tracked

The framework tracks:

- **Practice Mode**: Quick Practice vs Guided List
- **UI Elements**: Buttons, text inputs, audio players (7 specific types), dropdowns
- **App Capabilities**: What actions the app offers
- **User Intents**: What actions you want to perform
- **Port Matching**: Which user intents are satisfied by app capabilities

### 5. Example Test Scenario

**Scenario**: Test phrase list navigation

1. Load a phrase list
2. ✅ Validate: "Phrase display visible, Previous disabled, Next enabled"
3. Click Next button
4. ✅ Validate: "Moved to phrase 2, Previous now enabled"
5. Click Previous button
6. ✅ Validate: "Back to phrase 1, Previous disabled again"

If at any point the UI doesn't match expectations, click ❌ and note the issue.

### 6. Export Test Results

The framework automatically tracks all validations. To export:

```python
# In Python console or add to app:
st.session_state.ccs_test.oracle.export_session("test_session_001.json")
```

The JSON file contains:
- Complete state history
- All validation results
- Recorded bugs/mismatches
- Timestamps

### 7. Disable Testing

Click **"🚫 Disable CCS Testing"** to return to normal app usage.

## Understanding the Output

### Current State Display

```
Mode: GUIDED_LIST
Visible Elements: 8
  - PHRASE_DISPLAY_BOLD
  - PREV_BUTTON
  - NEXT_BUTTON
  - PHRASE_DROPDOWN
  - AUDIO_PLAYER_TARGET_PRACTICE
  - RECORD_BUTTON
  - TEXT_INPUT_PHRASE
  - RESULTS_PANEL

Capabilities: 6
  - ACCEPT_NAVIGATION_PREV
  - ACCEPT_NAVIGATION_NEXT
  - ACCEPT_PHRASE_JUMP
  - PROVIDE_TARGET_AUDIO_PRACTICE
  - ACCEPT_RECORDING
  - ACCEPT_TEXT_INPUT
```

This tells you what the **model predicts** should be visible/available.

### Port Matching

After you indicate your intent (e.g., "I want to go next"), the framework shows:

```
✓ Satisfied: WANT_GO_NEXT <-> ACCEPT_NAVIGATION_NEXT
✗ Unsatisfied: WANT_HEAR_TARGET_PRACTICE
```

This reveals:
- **Satisfied ports**: Your intent can be fulfilled
- **Unsatisfied ports**: You want something the app doesn't offer (potential bug!)

## Common Bugs to Look For

1. **Audio player confusion**: Wrong audio type playing
2. **Navigation state**: Buttons enabled/disabled incorrectly
3. **Phrase display**: Current phrase not highlighted
4. **Results visibility**: Results panel appearing when it shouldn't
5. **Recording state**: Record button not responding
6. **Text input sync**: Input field not matching target phrase

## Technical Notes

### Integration Points

The integration adds exactly 3 code blocks to `streamlit_app_v2.py`:

1. **Import** (lines ~30-34):
   ```python
   try:
       from ccs_test_integration import CCSTestSession
       CCS_AVAILABLE = True
   except ImportError:
       CCS_AVAILABLE = False
   ```

2. **Initialize** (lines ~128-130):
   ```python
   if CCS_AVAILABLE and 'ccs_test' not in st.session_state:
       st.session_state.ccs_test = CCSTestSession(enabled=False)
   ```

3. **UI + State Extraction** (sidebar + end of main):
   ```python
   # Sidebar controls
   if CCS_AVAILABLE:
       st.session_state.ccs_test.render_toggle_ui()
       if st.session_state.ccs_test.enabled:
           st.session_state.ccs_test.render_validation_ui()
   
   # State extraction (end of main)
   if CCS_AVAILABLE and st.session_state.ccs_test.enabled:
       st.session_state.ccs_test.extract_app_state_from_streamlit()
   ```

### Performance Impact

- **Disabled**: Zero overhead (conditionals short-circuit)
- **Enabled**: Minimal overhead (state extraction happens once per UI render)
- **No file operations**: All tracking in memory until explicit export

## Next Steps

After local testing:

1. Use the framework to document bugs you find
2. Export test sessions as JSON for analysis
3. If framework proves useful, consider:
   - Refining state inference logic based on findings
   - Adding more UI element types if needed
   - Potentially integrating into main branch (optional)

## Questions or Issues?

If the framework doesn't work as expected:

1. Check that CCS imports work: `python -c "from ccs_test_integration import CCSTestSession"`
2. Look for import errors in Streamlit console
3. Verify `CCS_AVAILABLE` is True in session_state
4. Check that `ccs_test` object exists in session_state

The framework is designed to fail gracefully - if imports fail, the app continues normally without testing features.
