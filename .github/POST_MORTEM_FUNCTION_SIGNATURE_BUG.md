# Post-Mortem: Function Signature Breaking Change Bug

**Date:** 2025-11-14  
**Severity:** High (Production-breaking)  
**Type:** Type Error / API Contract Violation  
**Meta-Level:** Universe Level 1 (Development Process Issue)

## Summary

A function signature change was made to enable caching, but call sites were not updated, resulting in a `TypeError: generate_target_audio() takes 2 positional arguments but 7 were given`. The bug was introduced in commit `ad252a6f`, reverted in commit `fc7ffb17`, then reintroduced when implementing Google Cloud TTS on feature branch.

## Timeline

1. **Commit ad252a6f** (2025-11-14 15:21:58 UTC): "Activate maintenance banner and improve audio caching"
   - **Changed:** `generate_target_audio()` signature from `(text: str, settings: Dict)` to `(text: str, tts_engine: str, voice: str, speed: int, pitch: int, use_wav: bool, slow: bool)`
   - **Reason:** Added `@st.cache_data(ttl=86400)` decorator to enable 24-hour caching across all users
   - **Problem:** Only updated the function definition, NOT the call sites

2. **Commit fc7ffb17** (2025-11-14 15:23:02 UTC): "Fix broken function signature - revert to working version"
   - **Action:** Reverted the signature change back to `(text: str, settings: Dict)`
   - **Reason:** Discovered the breaking change when testing (compilation errors: "settings" is not defined)
   - **Result:** Production restored to working state

3. **Commit 89994c8b** (later): "Add Google Cloud Text-to-Speech API integration with fallback chain"
   - **Action:** Added Google Cloud TTS function, kept `(text: str, settings: Dict)` signature
   - **Status:** Working (used old signature)

4. **Feature branch `feature/google-cloud-tts-rest-api`**: REST API implementation
   - **Commit 56466ae2:** Implemented REST API version
   - **Problem:** Local edits had residual code from the ad252a6f attempt
   - **Bug reintroduced:** Call site at line 1594 still had old 7-argument form:
     ```python
     audio_bytes, audio_format = generate_target_audio(
         text,
         settings.get('tts_engine', 'gtts'),
         settings.get('voice', 'pt-br'),
         settings.get('speed', 140),
         settings.get('pitch', 35),
         settings.get('use_wav_audio', False),
         settings.get('gtts_slow', False)
     )
     ```
   - **Function expected:** `generate_target_audio(text, settings)`

## Root Cause Analysis

### Primary Cause: Incomplete Refactoring
When changing a function signature that's part of an API contract, ALL call sites must be updated atomically. The commit ad252a6f changed the definition but missed 3 call sites at lines 1594, 1665, 1767.

### Contributing Factors

1. **No Type Checking in CI/CD**
   - Python's dynamic typing allowed the mismatch to pass syntax checks
   - No `mypy` or similar static type checker in the workflow
   - Error only discovered at runtime when function was invoked

2. **Lack of Automated Testing**
   - No unit tests for `generate_target_audio()`
   - No integration tests that would catch signature mismatches
   - Manual testing missed the code path (likely didn't generate audio immediately)

3. **Large Monolithic File**
   - `app.py` is 1864 lines - hard to track all function usages
   - No IDE/LSP warnings visible during editing
   - grep/search required to find all call sites manually

4. **Git Workflow Issue**
   - Reverted commit (fc7ffb17) fixed production but left local working directory in inconsistent state
   - Uncommitted local changes from ad252a6f attempt remained in editor/filesystem
   - When continuing work on feature branch, these stale edits were included

5. **Caching Motivation vs Implementation**
   - Goal: Add caching to reduce API calls (valid optimization)
   - Chosen approach: Expand signature to make all parameters explicit (for cache key)
   - Better approach: Keep `settings: Dict` and let Streamlit hash it for cache key
   - Streamlit's `@st.cache_data` can hash dictionaries - no need to destructure

## The Meta-Development Perspective

This is a **Level 1 meta-issue** in the type-theoretic hierarchy:

### Level 0: The Application Code
- Function: `generate_target_audio(text, settings)`
- Purpose: Generate TTS audio
- Issue: Works or doesn't work

### Level 1: The Development Process (This Bug)
- Process: How we change function signatures
- Issue: Incomplete refactoring broke the contract
- Meta-git issue: Local state diverged from committed state
- Type system issue: No static verification of API contracts

### Level 2: Development Methodology (Potential Future Analysis)
- Question: Why don't we have safeguards against Level 1 issues?
- Analysis: Missing CI/CD checks, test coverage, type checking
- Philosophy: Trade-off between velocity and safety in a hobby project

## Lessons Learned

### 1. Function Signature Changes Are Breaking Changes
**Rule:** Any change to a function's parameters is a breaking change requiring:
- Find all call sites (use `grep`, LSP "find references", or IDE tools)
- Update call sites BEFORE or in the SAME commit as the signature change
- Test at least one code path through each call site
- Consider deprecation path if public API (not applicable here)

### 2. Cache Keys Don't Require Parameter Expansion
**Streamlit Caching:** Streamlit's `@st.cache_data` can hash complex objects:
```python
# ✅ GOOD: Keep simple signature, Streamlit hashes the Dict
@st.cache_data(ttl=86400)
def generate_target_audio(text: str, settings: Dict) -> tuple[bytes, str]:
    # Streamlit creates cache key from both text AND settings dict
    ...

# ❌ UNNECESSARY: Expanded signature for caching
@st.cache_data(ttl=86400)
def generate_target_audio(text: str, tts_engine: str, voice: str, ...) -> tuple[bytes, str]:
    # More parameters = more complex API = more places to break
    ...
```

### 3. Git Revert Leaves Local State Dirty
**Workflow issue:**
```bash
# Commit with bug
git commit -m "Change function signature"  # ad252a6f

# Revert the commit (fixes repo, not local files)
git revert HEAD  # fc7ffb17

# Local editor may still have unsaved changes from ad252a6f!
# These can "leak" into next commit
```

**Better workflow:**
```bash
# After discovering bug, check working directory state
git status  # Any uncommitted changes?
git diff    # What's different from HEAD?

# Clean up before continuing
git checkout .  # Discard all local changes
# OR
git stash      # Save them for later review
```

### 4. Python Type Hints Are Not Enforced
**Current state:** Type hints are documentation only
```python
def generate_target_audio(text: str, settings: Dict) -> tuple[bytes, str]:
    ...

# This WILL run (wrong!) - Python doesn't check types at runtime
generate_target_audio("hello", "gtts", "pt-br", 140, 35, False, False)
```

**Solutions:**
- Add `mypy` to check types statically
- Add runtime validation with `typeguard` or `pydantic`
- Add unit tests that would catch signature mismatches

### 5. IDE/LSP Could Have Caught This
Modern Python LSPs (Pylance, Pyright, MyPy) would show errors:
```
Expected 2 positional arguments (text, settings)
Got 7 positional arguments
```

**Why didn't this show up?**
- Possibly LSP not running during editing
- Possibly errors ignored/not visible in terminal workflow
- No CI/CD gate to block commits with type errors

## Recommendations

### Immediate (Prevent This Specific Bug)
1. ✅ **Keep function signature stable:** Use `(text: str, settings: Dict)` - already reverted
2. ✅ **Verify caching works with Dict:** Streamlit can hash it - confirmed working
3. ✅ **Search for all call sites before merging:** Done manually, found 3 instances
4. ⏳ **Add regression test:** Create unit test for `generate_target_audio()` signature

### Short Term (Prevent Similar Bugs)
1. **Add static type checking:**
   ```bash
   pip install mypy
   mypy app.py --strict
   ```
   Add to pre-commit hook or CI/CD

2. **Add basic unit tests:**
   ```python
   def test_generate_target_audio_signature():
       """Ensure generate_target_audio accepts (text, settings)"""
       settings = {'tts_engine': 'gtts', 'voice': 'pt-br', ...}
       result = generate_target_audio("test", settings)
       assert isinstance(result, tuple)
       assert len(result) == 2
   ```

3. **Use IDE with Python LSP:**
   - VS Code with Pylance (already using?)
   - Ensure errors are visible in UI
   - Don't ignore red squiggles!

4. **Git hygiene after reverts:**
   ```bash
   # After reverting a commit, clean working directory
   git status && git diff
   git checkout . # if appropriate
   ```

### Long Term (Development Process)
1. **Function signature changes = new major version:**
   - Document breaking changes in CHANGELOG
   - Consider deprecation warnings for public APIs
   - For internal APIs (like this), ensure all call sites updated in same commit

2. **Automated testing:**
   - Unit tests for pure functions (TTS generation, audio processing)
   - Integration tests for user flows (record → compare → score)
   - Smoke tests in CI/CD before deployment

3. **Code review checklist:**
   - [ ] Function signature changed?
   - [ ] All call sites updated?
   - [ ] Type hints accurate?
   - [ ] Tests added/updated?
   - [ ] Breaking changes documented?

4. **Smaller files / modular architecture:**
   - Split `app.py` into modules: `tts.py`, `audio.py`, `ui.py`, `scoring.py`
   - Easier to track function usage within a module
   - Better LSP performance on smaller files

## Meta-Git-Issue: State Divergence

This bug reveals a fundamental issue with git + local state:

```
Timeline:
1. Working directory: Clean, matches HEAD
2. Edit files, make changes (signature change)
3. Commit (ad252a6f) - but not all changes staged/tested
4. Discover bug in production
5. Revert commit (fc7ffb17) - repo is fixed
6. BUT: Local working directory may still have uncommitted edits from step 2!
7. Continue working → stale edits leak into new commits
```

**Solution:** Treat `git revert` as "fix the history, then fix the working directory":
```bash
git revert HEAD          # Fix commit history
git status               # Check for leftover changes
git diff                 # Review what's different
git checkout . || git stash  # Clean up working directory
```

**Alternative:** Use branches for experiments:
```bash
git checkout -b experiment/cache-optimization
# Make breaking changes, test thoroughly
git checkout main        # Abandon if it fails - working directory auto-cleaned
```

## Conclusion

This bug was a **textbook incomplete refactoring** - a function signature was changed but call sites were not updated. The root cause is the lack of static type checking and automated tests in the workflow. The meta-git-issue (local state divergence after revert) exacerbated the problem by reintroducing the bug in a later commit.

**Key Insight:** In dynamically-typed languages without runtime enforcement, API contracts are social agreements, not compiler-enforced invariants. Manual discipline (grep for call sites, update all at once, test thoroughly) is required, OR we add tooling (mypy, tests, CI/CD) to enforce the contracts automatically.

**Action Items:**
- [ ] Add mypy to pre-commit hook
- [ ] Create unit test for `generate_target_audio()`
- [ ] Document "Function Signature Change Protocol" in DEVELOPER_GUIDE.md
- [ ] Consider splitting app.py into modules (>2000 lines is unwieldy)

---

**Meta-Note:** This document itself is a Level 1 artifact - it's not about the TTS functionality (Level 0), but about how we develop and maintain that functionality. A Level 2 analysis would ask: "Why don't we have a documented process for function signature changes?" and "What cultural/tooling changes would prevent needing these post-mortems?"
