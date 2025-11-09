## CCS-Based Testing Framework for Streamlit App

### Overview

This testing framework applies principles from **Calculus of Communicating Systems (CCS)** developed by Robin Milner to model and test the interaction between a user and a Streamlit web application as two communicating agents.

### The Problem

Traditional Streamlit app state management suffers from:

1. **State Fragmentation**: Boolean flags (`edit_mode`, `phrase_list`, etc.) scattered across `session_state`
2. **View-State Desynchronization**: UI elements don't reliably reflect internal state
   - Phrase sometimes appears in bold, sometimes doesn't
   - Target text gets out of sync with displayed phrase
   - Dropdown selection doesn't match current phrase
3. **No Intent Model**: We track what the app *is*, but not what the user *wants to do*
4. **Lack of Testing Oracle**: No systematic way to validate UI correctness

### The CCS Solution

#### Two Agent Model

**App Agent (Input Ports)**
- Offers capabilities: "I can accept a recording", "I can show phrase #5"
- Represents what the application is prepared to handle

**User Agent (Output Ports)**
- Expresses desires: "I want to record", "I want to see phrase #5"  
- Represents user intent

#### Complementary Ports

In CCS, agents communicate through **complementary ports**:
- **Satisfied Interaction**: User wants to record (output) AND app can accept recording (input) → ✓
- **Unsatisfied User Intent**: User wants to jump to phrase but no dropdown visible → ✗ Bug!
- **Unused App Capability**: App offers "Previous" button but user has no intent to navigate → ? (Not necessarily a bug, but indicates unused complexity)

#### Testing Oracle

At each state transition, the user validates:
- **"Do I see what the model says I should see?"**
- If **NO** → Bug recorded with description
- If **YES** → Model validated, continue testing

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Streamlit App (Actual)                     │
│  - session_state variables                                  │
│  - UI widgets (buttons, inputs, displays)                   │
│  - Current rendering                                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ State Extraction
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              CCS Testing Framework                          │
│                                                             │
│  ┌─────────────────┐         ┌─────────────────┐          │
│  │   App State     │         │   User State    │          │
│  │                 │         │                 │          │
│  │ - Mode          │         │ - Intents       │          │
│  │ - Data          │         │ - Expectations  │          │
│  │ - Visible       │         │ - Perception    │          │
│  │ - Capabilities  │         │                 │          │
│  └────────┬────────┘         └────────┬────────┘          │
│           │                           │                    │
│           └──────────┬────────────────┘                    │
│                      │                                     │
│                      ▼                                     │
│           ┌─────────────────────┐                         │
│           │  Port Matching      │                         │
│           │  (CCS Logic)        │                         │
│           └──────────┬──────────┘                         │
│                      │                                     │
│                      ▼                                     │
│           ┌─────────────────────┐                         │
│           │  - Satisfied        │                         │
│           │  - Unsatisfied      │                         │
│           │  - Unused           │                         │
│           └──────────┬──────────┘                         │
│                      │                                     │
│                      ▼                                     │
│           ┌─────────────────────┐                         │
│           │ User Validation     │                         │
│           │ (Testing Oracle)    │                         │
│           └──────────┬──────────┘                         │
│                      │                                     │
│                      ▼                                     │
│           ┌─────────────────────┐                         │
│           │  Bug Reports        │                         │
│           └─────────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### Files

#### `ccs_test_framework.py`
Core CCS testing logic:
- **Data Structures**: `AppState`, `UserState`, `CCSInteractionState`
- **Enums**: `PracticeMode`, `UIElement`, `AppCapability`, `UserIntent`
- **CCS Logic**: `compute_port_matching()` - matches user intents with app capabilities
- **Testing Oracle**: `CCSTestOracle` - tracks state transitions and validates consistency
- **Logging**: JSON export of complete test sessions

#### `ccs_test_integration.py`
Integration with Streamlit app:
- **State Extraction**: `extract_app_state_from_streamlit()` - bridges actual app to model
- **Inference**: `_infer_visible_elements()`, `_infer_capabilities()` - encode expectations
- **UI Components**: `render_validation_ui()` - testing interface in sidebar
- **Session Management**: `CCSTestSession` - manages testing within Streamlit lifecycle

### Usage

#### 1. Enable Testing Mode

In `streamlit_app_v2.py`, add to imports:
```python
from ccs_test_integration import CCSTestSession
```

Initialize in `initialize_session_state()`:
```python
if 'ccs_test' not in st.session_state:
    st.session_state.ccs_test = CCSTestSession(enabled=False)
```

Add to sidebar:
```python
st.session_state.ccs_test.render_toggle_ui()
if st.session_state.ccs_test.enabled:
    st.session_state.ccs_test.render_validation_ui()
```

#### 2. Testing Workflow

1. **Enable Testing**: Check "Enable CCS Testing" in sidebar
2. **Perform Action**: Click button, enter text, navigate, etc.
3. **Capture State**: (Optional) Click "📊 Show Current State" to see internal model
4. **Validate UI**: 
   - Does the UI match what you expect?
   - ✅ **Matches**: Click green button
   - ❌ **Mismatch**: Click red button, describe what's wrong
5. **Review Bugs**: Expand "View Bugs" to see all recorded issues
6. **Save Session**: Click "💾 Save Test Session" to export JSON report

#### 3. Example Test Session

**Scenario**: Load phrase list and navigate

```
STEP 1: Free Text Mode
- User Intent: WANT_ENTER_TEXT
- App Capability: ACCEPT_TEXT_INPUT
- Port Match: ✓ SATISFIED
- UI Check: Text input visible? YES ✅

STEP 2: Upload phrase list → Guided Mode
- User Intent: WANT_GO_NEXT, WANT_HEAR_TARGET
- App Capabilities: ACCEPT_NAVIGATION_NEXT, PROVIDE_TARGET_AUDIO
- Port Match: ✓ SATISFIED (both)
- UI Check: Phrase "Bom dia" in bold? NO ❌
  → BUG RECORDED: "Phrase not displaying in bold"

STEP 3: Click Next
- User Intent: WANT_SEE_RESULTS
- App Capabilities: ACCEPT_NAVIGATION_NEXT
- Port Match: ✗ UNSATISFIED (WANT_SEE_RESULTS has no matching capability)
  → Indicates missing feature or user expectation mismatch

STEP 4: Fix applied, retest
- UI Check: Phrase "Obrigado" in bold? YES ✅
- Port Match: All satisfied
```

### Key Concepts

#### State vs. Intent Separation

**Traditional approach** (problematic):
```python
if st.button("Record"):
    # What if button isn't visible? What if user didn't want to record?
    record_audio()
```

**CCS approach** (explicit):
```python
# App offers capability
app_state.active_capabilities.add(AppCapability.ACCEPT_AUDIO_RECORDING)

# User expresses intent
user_state.active_intents.add(UserIntent.WANT_RECORD_AUDIO)

# Framework checks if they align
if intent_satisfied:
    # Safe to proceed
    record_audio()
else:
    # Bug: Button visible but user didn't want it, or vice versa
```

#### Port Matching as Contract

The port matching logic encodes the **contract** between user and app:

```python
port_pairs = {
    UserIntent.WANT_ENTER_TEXT: AppCapability.ACCEPT_TEXT_INPUT,
    UserIntent.WANT_RECORD_AUDIO: AppCapability.ACCEPT_AUDIO_RECORDING,
    # ... etc
}
```

This makes expectations **explicit** and **testable**.

#### Unsatisfied Ports as Bugs

- **Unsatisfied User Intent**: User wants something app doesn't offer → Missing feature or hidden UI element
- **Unused App Capability**: App offers something user doesn't want → Unnecessary complexity or poor UX

### Benefits

1. **Explicit State Model**: Internal representation separate from UI rendering
2. **Intent Tracking**: Know what user wants to do, not just what they can do
3. **Systematic Testing**: Oracle provides clear validation process
4. **Bug Documentation**: Automatic recording of mismatches with context
5. **Regression Prevention**: Test sessions can be replayed
6. **Complexity Management**: Parallel composition (if needed) for complex interactions

### Advanced: Parallel Composition

For more complex scenarios, CCS supports **parallel composition**:

```
App = RecordingAgent | AudioPlayerAgent | NavigationAgent
User = PracticeIntent | ReviewIntent
System = App || User
```

Each agent can have its own state and ports. The framework computes which combinations satisfy the user's compound intent.

### Limitations & Future Work

**Current Limitations**:
- State extraction relies on inference (not instrumented)
- Manual validation (user must click buttons)
- Single-user model (no multi-user testing)

**Future Enhancements**:
- Automated UI scraping to verify actual visibility
- Hypothesis-based property testing
- Multi-agent composition for complex workflows
- Mutation testing: deliberately break app, verify bugs caught

### References

- Milner, R. (1989). *Communication and Concurrency*. Prentice Hall.
- CCS Workbench: http://www.dcs.ed.ac.uk/home/perdita/cwb/
- Process Calculi: https://en.wikipedia.org/wiki/Process_calculus

### Contributing

To extend the framework:

1. Add new `UIElement` types to `ccs_test_framework.py`
2. Add corresponding capabilities/intents
3. Update port matching pairs
4. Update inference logic in `ccs_test_integration.py`
5. Document expected behavior

The framework is designed to grow with the application!
