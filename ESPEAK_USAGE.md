# eSpeak-NG Usage in Portuguese Pronunciation Trainer

## Overview

This project uses **eSpeak-NG** for phoneme extraction only. We do NOT use it for audio generation in production.

## What We Use From eSpeak-NG

### 1. Phoneme Extraction (Critical - Used Always)

**Function:** `get_phonemes(text, voice="pt-br")`
- **Command:** `espeak-ng -v pt-br -x -q "text"`
- **Returns:** eSpeak phoneme codes (e.g., `bˈom dˈiə`)
- **Purpose:** Core pronunciation comparison algorithm
- **Works:** Local AND deployed (via `packages.txt`)

**Function:** `get_ipa(text, voice="pt-br")`
- **Command:** `espeak-ng -v pt-br --ipa -q "text"`
- **Returns:** IPA transcription (e.g., `bõ dʒiə`)
- **Purpose:** Display to user, linguistic analysis
- **Works:** Local AND deployed (via `packages.txt`)

**Why This Works Everywhere:**
- eSpeak-NG is specified in `packages.txt`
- Streamlit Cloud installs it automatically
- Pure command-line tool, no audio device needed
- Fast, deterministic, reproducible

### 2. Audio Playback (Optional - Local Development Only)

**Function:** `speak_text(text, voice, speed, pitch)`
- **Command:** `espeak-ng -v pt-br -s 160 -p 40 "text"`
- **Returns:** Nothing (plays audio directly to system speakers)
- **Purpose:** Debugging phoneme sounds during development
- **Works:** Local ONLY (requires audio device)

**UI Location:** Results panel → "Compare Phoneme Sounds (eSpeak)" section

**Feature Gating:**
```python
# Lines ~1017-1019 in streamlit_app_v2.py
if IS_LOCAL_DEV and not result["exact_match"]:
    st.markdown("---")
    st.subheader("Compare Phoneme Sounds (eSpeak)")
    st.caption("� Development feature - requires local audio device")
    # ... buttons here ...
```

**Result:**
- Local development: Buttons visible and functional
- Streamlit Cloud: Entire section hidden (not just disabled)

**Why These Buttons Are Hidden in Deployment:**
```python
try:
    subprocess.run([get_espeak_path(), "-v", voice, "-s", str(speed), "-p", str(pitch), text], check=True)
except (subprocess.CalledProcessError, FileNotFoundError):
    pass  # Silently fail if espeak not available
```
- Streamlit Cloud has NO audio device
- `subprocess.run()` with audio output fails silently
- Buttons appear but do nothing when clicked
- This is INTENTIONAL - graceful degradation

## What We Use For Audio Generation

### Production: Google Text-to-Speech (gTTS)

**Function:** `speak_text_gtts(text, voice="pt-br")`
- **Library:** `gtts` (Google Text-to-Speech)
- **Returns:** MP3 audio bytes
- **Purpose:** High-quality target audio for practice
- **Works:** Local AND deployed (internet-based, no dependencies)

**Advantages:**
- ✅ Natural, human-like voice
- ✅ Works on Streamlit Cloud (no audio device needed)
- ✅ Returns audio bytes → can use `st.audio()` widget
- ✅ Better for language learning (more realistic pronunciation)

**Trade-offs:**
- ❌ Requires internet connection
- ❌ Slower than eSpeak (API calls)
- ❌ No direct phoneme control

## Deployment Configuration

### Environment Detection

The app automatically detects whether it's running locally or deployed:

```python
# In streamlit_app_v2.py (lines ~18-19)
IS_LOCAL_DEV = os.path.exists('./local/bin/run-espeak-ng')
```

**How it works:**
- If local eSpeak build exists → `IS_LOCAL_DEV = True` → Show eSpeak sound buttons
- If not (Streamlit Cloud) → `IS_LOCAL_DEV = False` → Hide eSpeak sound buttons

**Why this approach:**
- No manual config needed
- No branch divergence
- Safe for both environments
- Automatic feature gating

### Files That Control eSpeak-NG Installation

**`packages.txt`** (Streamlit Cloud system packages):
```text
espeak-ng
ffmpeg
```

**Why eSpeak-NG is listed:**
- Needed for phoneme extraction (`-x` and `--ipa` flags)
- Command-line only, no audio device required
- Installed via apt-get on Streamlit Cloud

**Why FFmpeg is listed:**
- Audio format conversion for ASR models
- Not related to eSpeak-NG

### Path Detection Logic

```python
def get_espeak_path():
    """Get espeak-ng path (local build or system-wide)"""
    local_path = "./local/bin/run-espeak-ng"
    if Path(local_path).exists():
        return local_path  # Local development build
    return "espeak-ng"     # System-wide (Streamlit Cloud)
```

**Local Development:**
- Uses custom-compiled eSpeak-NG from `./local/bin/`
- Allows testing bleeding-edge features or custom voices

**Streamlit Cloud Deployment:**
- Uses system-wide `espeak-ng` (installed via packages.txt)
- Standard Ubuntu package, stable and tested

## Branch Strategy Issue

### Current Problem

You noted that deployment and testing branches might diverge. The concern:
- **Testing branch (ccs-testing):** Has CCS framework enabled
- **Deployment branch (main):** Should NOT have testing framework in production

### Why This Isn't a Problem Here

The CCS testing framework is **already designed for this**:

```python
# In streamlit_app_v2.py (lines ~30-34)
try:
    from ccs_test_integration import CCSTestSession
    CCS_AVAILABLE = True
except ImportError:
    CCS_AVAILABLE = False

# In sidebar (lines ~675-685)
if CCS_AVAILABLE:
    st.markdown("---")
    st.header("🧪 CCS Testing")
    st.session_state.ccs_test.render_toggle_ui()
```

**The framework is:**
- ✅ **Optional by design** - ImportError gracefully handled
- ✅ **User-controlled** - Checkbox to enable/disable
- ✅ **Non-invasive** - Zero impact when disabled
- ✅ **Safe for production** - Can ship with framework included

### Recommended Strategy

**Option 1: Single Branch (Recommended)**
- Keep CCS framework in production code
- Users enable it via sidebar checkbox only when testing
- No branch divergence issues
- Framework helps catch production bugs too!

**Option 2: Config File (If You Prefer)**
```python
# config.py
ENABLE_CCS_TESTING = True  # False in production

# streamlit_app_v2.py
from config import ENABLE_CCS_TESTING

if ENABLE_CCS_TESTING:
    try:
        from ccs_test_integration import CCSTestSession
        CCS_AVAILABLE = True
    except ImportError:
        CCS_AVAILABLE = False
else:
    CCS_AVAILABLE = False
```

**Option 3: Environment Variable**
```python
import os
CCS_AVAILABLE = os.environ.get('ENABLE_CCS_TESTING', 'false').lower() == 'true'
```

Set in Streamlit Cloud: Settings → Secrets → `ENABLE_CCS_TESTING = false`

## Summary: What Works Where

| Feature | Local Dev | Streamlit Cloud | Purpose |
|---------|-----------|----------------|---------|
| `get_phonemes()` | ✅ | ✅ | **Core feature** - pronunciation comparison |
| `get_ipa()` | ✅ | ✅ | Display IPA to users |
| `speak_text()` (eSpeak buttons) | ✅ | ❌ | Development debugging only |
| `speak_text_gtts()` | ✅ | ✅ | **Production audio** - target pronunciation |
| CCS Testing Framework | ✅ | ✅ (optional) | Quality assurance, user-controlled |

## Key Takeaway

**eSpeak-NG is critical infrastructure for phoneme extraction, but NOT for audio generation.**

The "Compare Phoneme Sounds" buttons failing in deployment is:
- Expected behavior
- Gracefully handled (silent failure)
- Not a bug - feature is development-only
- Production users get better audio from gTTS anyway

**No branch strategy needed** - the code already handles both environments correctly!
