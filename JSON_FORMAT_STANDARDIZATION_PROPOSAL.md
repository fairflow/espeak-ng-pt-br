# JSON Format Standardization Proposal

## Problem Statement

The current implementation has **two incompatible JSON formats** for story scenes:

### Format 1 (French - Legacy)
```json
[
  {
    "french": "Bonjour Sophie, ça va?",
    "english": "Hello Sophie, how are you?",
    "ipa": "bɔ̃ʒˈuʁ sɔfˈi sa vˈa"
  },
  ...
]
```

### Format 2 (Portuguese - New)
```json
{
  "pt": [
    {
      "pt": "O sol nasce suavemente sobre São Paulo.",
      "english": "The sun rises gently over São Paulo.",
      "ipa": "[ʊ sˈɔl nˈasy sˌuavemˈeɪŋtʃy sˈobry sɐ̃ʊ̃ pˈaʊlʊ]"
    },
    ...
  ],
  "scene_number": 1,
  "scene_title": "O Café da Manhã"
}
```

## Impact

This dual-format approach has caused **5 bugs in rapid succession**:
1. `'list' object has no attribute 'keys'` - Practice Mode failed on Portuguese
2. Duplicate key `audio_input_0` - Widget collision between modes
3. `ValueError: not enough values to unpack (expected 5, got 4)` - Phoneme analysis
4. Duplicate key `show_detail` - Checkbox collision
5. `'str' object has no attribute 'get'` - Scene by Scene failed on Portuguese

Every function that loads scene data now needs dual-format handling, increasing complexity and fragility.

## Root Cause

The Portuguese format was designed to:
1. Support multiple languages in one file (language key at top level)
2. Include metadata (scene_number, scene_title)
3. Be more structured and extensible

The French format is simpler but:
1. Language is implicit in key names
2. No metadata support
3. Less structured but more straightforward

## Options

### Option 1: Standardize on Format 2 (Portuguese - Recommended)

**Pros:**
- More structured and extensible
- Supports metadata (scene numbers, titles)
- Language-agnostic (can add multiple languages later)
- Already implemented for Portuguese (438 phrases)
- Better for future multi-language support

**Cons:**
- Requires converting all French scenes (16 files, ~505 phrases)
- More verbose format
- Slightly more complex to parse

**Migration Steps:**
1. Create conversion script `convert_french_scenes_to_format2.py`
2. Convert all 16 French scene files
3. Simplify code - remove dual-format handling
4. Test all three modes (Full Story, Scene by Scene, Practice Mode)
5. Update documentation

**Estimated Effort:** 1-2 hours
**Risk:** Low (can validate before committing)

### Option 2: Standardize on Format 1 (French)

**Pros:**
- Simpler format
- Less verbose
- Already works for French (505 phrases)

**Cons:**
- Requires converting all Portuguese scenes (16 files, 438 phrases)
- Loses metadata (scene_number, scene_title)
- Language name baked into keys (not language-agnostic)
- Less extensible for future features

**Estimated Effort:** 1-2 hours
**Risk:** Low (can validate before committing)

### Option 3: Keep Dual Format (Current Approach)

**Pros:**
- No conversion needed
- Both formats already work

**Cons:**
- ❌ Already caused 5 bugs
- ❌ Every scene-loading function needs dual-format logic
- ❌ Increased complexity and maintenance burden
- ❌ Future bugs likely as code evolves
- ❌ "Heath-Robinsonish" effect (overly complex)

**Estimated Effort:** Ongoing maintenance cost
**Risk:** High (more bugs likely)

## Recommendation

**✅ Option 1: Standardize on Format 2 (Portuguese)**

### Rationale:
1. **Future-proof:** Designed for multi-language expansion (de, nl, it, es coming)
2. **Metadata:** Scene numbers and titles useful for navigation/tracking
3. **Cleaner code:** Remove all dual-format handling = simpler, more maintainable
4. **Portuguese is correct:** It's the newer, better-designed format
5. **One-time cost:** 1-2 hours of conversion vs ongoing bug fixes

### Implementation Plan:

#### Step 1: Create Conversion Script
```python
# scripts/convert_french_to_format2.py
import json
from pathlib import Path

def convert_scene(french_scene_path, scene_number):
    """Convert French Format 1 to Format 2"""
    with open(french_scene_path, 'r', encoding='utf-8') as f:
        old_data = json.load(f)  # List format
    
    # Extract title from filename
    stem = french_scene_path.stem
    parts = stem.split('-', 2)
    scene_title = parts[2] if len(parts) >= 3 else stem
    
    # Convert to new format
    new_data = {
        "fr": [
            {
                "fr": phrase["french"],
                "english": phrase["english"],
                "ipa": phrase["ipa"]
            }
            for phrase in old_data
        ],
        "scene_number": scene_number,
        "scene_title": scene_title
    }
    
    return new_data
```

#### Step 2: Run Conversion
```bash
python scripts/convert_french_to_format2.py
```

#### Step 3: Simplify Code
Remove dual-format handling from:
- `render_scene_by_scene()` (lines ~1708-1740)
- `render_scene_practice_mode()` (lines ~1517-1547)

New simplified code:
```python
with open(scene_file, 'r', encoding='utf-8') as f:
    scene_data = json.load(f)

# Always Format 2 now
lang_keys = [k for k in scene_data.keys() if k not in ['scene_number', 'scene_title']]
lang_key = lang_keys[0]
phrases = scene_data[lang_key]
```

#### Step 4: Test
- ✅ Scene by Scene (French)
- ✅ Practice Mode (French)
- ✅ Scene by Scene (Portuguese)
- ✅ Practice Mode (Portuguese)
- ✅ No errors or warnings

#### Step 5: Document
- Update `STORY_PRACTICE_INTEGRATION_PROPOSAL.md`
- Add note to `PRACTICE_MODE_IMPLEMENTATION.md`
- Update any other relevant docs

## Decision

**Pending user approval.**

Current status: Feature branch `feature/story-practice-mode` has 6 commits, 5 of which are bug fixes related to dual-format handling.

**Recommendation: Convert French to Format 2 before merging to main.**

This will:
1. Eliminate the root cause of bugs
2. Simplify code significantly
3. Make future language additions easier
4. Improve maintainability

**Alternative: If time is critical, merge as-is and standardize later in a separate PR.**

## Questions for User

1. **Approve standardization?** Should we standardize on Format 2 (Portuguese)?
2. **Timeline?** Do it now before merging, or later in a separate PR?
3. **Validation?** How much testing do you want before considering it done?

---

**Note:** The current dual-format code works but is fragile. Five rapid bug fixes suggest this complexity is causing issues. Standardization would eliminate this entire class of bugs.
