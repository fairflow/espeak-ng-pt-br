# Language Materials Integration Plan

## Executive Summary

This document outlines the implementation plan for integrating the new `language_materials/` directory structure into the Streamlit app, providing users with both built-in curated phrase files and the ability to upload custom files.

---

## Current State Analysis

### What We Have
- ✅ `language_materials/` directory with structured content:
  - `fr/` - French: 200 phrases + 428 words (A/B/C/D levels)
  - `pt/` - Portuguese: 83 phrases + 172 words (A/B/C/D levels)
- ✅ Existing file upload functionality (`st.file_uploader`)
- ✅ File format parser (supports both simple and `phrase | translation | [ipa]` format)
- ✅ Automated translation/IPA generation scripts

### Current Limitations
- ❌ Users cannot access built-in language materials
- ❌ No distinction between "Browse Library" vs "Upload Custom"
- ❌ No way to preview available materials
- ⚠️ User must manually create/find files to practice

---

## Technical Approach

### 1. File Access on Streamlit Cloud

**Verified:** All repository files are accessible when deployed to Streamlit Cloud.

```python
from pathlib import Path

# This works both locally and on Streamlit Cloud
DATA_DIR = Path(__file__).parent / "language_materials"
```

**Key Points:**
- Working directory is always the repository root
- All committed files are cloned and available
- Use `Path` objects for cross-platform compatibility
- File I/O should be cached with `@st.cache_data`

---

## Implementation Plan

### Phase 1: Core Infrastructure (v1.2.0)

#### A. Add Language Materials Module

Create `app_language_materials.py`:

```python
"""Language materials discovery and loading."""

from pathlib import Path
from typing import Dict, List, Optional
import streamlit as st

DATA_DIR = Path(__file__).parent / "language_materials"

@st.cache_data
def get_available_languages() -> List[str]:
    """Get list of languages with available materials."""
    if not DATA_DIR.exists():
        return []
    return [d.name for d in DATA_DIR.iterdir() if d.is_dir()]

@st.cache_data
def get_language_structure(language: str) -> Dict:
    """Get complete directory structure for a language.
    
    Returns:
        {
            'phrases-A': ['phr-01.txt', 'phr-02.txt'],
            'words-A': ['words-01.txt'],
            ...
        }
    """
    lang_dir = DATA_DIR / language
    if not lang_dir.exists():
        return {}
    
    structure = {}
    for category_dir in sorted(lang_dir.iterdir()):
        if category_dir.is_dir():
            files = sorted([f.name for f in category_dir.glob("*.txt")])
            if files:
                structure[category_dir.name] = files
    
    return structure

@st.cache_data
def get_file_metadata(language: str, category: str, filename: str) -> Dict:
    """Get metadata about a phrase/word file.
    
    Returns:
        {
            'path': Path object,
            'line_count': 50,
            'has_translations': True,
            'has_ipa': True,
            'preview': ['first', 'few', 'lines']
        }
    """
    file_path = DATA_DIR / language / category / filename
    
    if not file_path.exists():
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
    
    # Analyze format
    sample = lines[0] if lines else ""
    has_translations = '|' in sample
    has_ipa = '[' in sample and ']' in sample
    
    return {
        'path': file_path,
        'line_count': len(lines),
        'has_translations': has_translations,
        'has_ipa': has_ipa,
        'preview': lines[:3]
    }

@st.cache_data
def load_phrase_file(file_path: Path) -> List[Dict]:
    """Load and parse a phrase/word file.
    
    Returns:
        [
            {'text': 'bonjour', 'translation': 'hello', 'ipa': '[bɔ̃ʒuʁ]'},
            ...
        ]
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    phrases = []
    for line in content.split('\n'):
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            continue
        
        # Parse format: "phrase | translation | [ipa]"
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            phrases.append({
                'text': parts[0],
                'translation': parts[1] if len(parts) > 1 else None,
                'ipa': parts[2] if len(parts) > 2 else None
            })
        else:
            # Simple format
            phrases.append({
                'text': line,
                'translation': None,
                'ipa': None
            })
    
    return phrases
```

#### B. Update UI in `app.py`

Replace current file upload section with hybrid interface:

```python
# In main() function, replace current expander with:

with st.expander("📚 Load Practice Materials"):
    source_tab1, source_tab2 = st.tabs(["📦 Built-in Library", "📁 Upload File"])
    
    # TAB 1: Built-in materials
    with source_tab1:
        from app_language_materials import (
            get_available_languages,
            get_language_structure,
            get_file_metadata,
            load_phrase_file
        )
        
        languages = get_available_languages()
        
        if not languages:
            st.warning("No built-in materials found")
        else:
            # Language selection (can be different from practice language)
            material_lang = st.selectbox(
                "Material Language",
                languages,
                format_func=lambda x: {
                    'fr': '🇫🇷 French',
                    'pt': '🇵🇹 Portuguese',
                    'nl': '🇳🇱 Dutch'
                }.get(x, x),
                help="Choose language of practice materials"
            )
            
            structure = get_language_structure(material_lang)
            
            if structure:
                # Category selection (phrases vs words, level)
                categories = list(structure.keys())
                category = st.selectbox(
                    "Category",
                    categories,
                    format_func=lambda x: {
                        'phrases-A': '📝 Phrases - Level A (Beginner)',
                        'phrases-B': '📝 Phrases - Level B (Intermediate)',
                        'phrases-C': '📝 Phrases - Level C (Advanced)',
                        'phrases-D': '📝 Phrases - Level D (Expert)',
                        'words-A': '📖 Words - Level A (Beginner)',
                        'words-B': '📖 Words - Level B (Intermediate)',
                        'words-C': '📖 Words - Level C (Advanced)',
                        'words-D': '📖 Words - Level D (Expert)',
                    }.get(x, x),
                    help="Beginner → Expert progression"
                )
                
                # File selection within category
                files = structure[category]
                selected_file = st.selectbox("File", files)
                
                # Show metadata preview
                metadata = get_file_metadata(material_lang, category, selected_file)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Items", metadata.get('line_count', 0))
                with col2:
                    st.metric("Translations", "✓" if metadata.get('has_translations') else "✗")
                with col3:
                    st.metric("IPA", "✓" if metadata.get('has_ipa') else "✗")
                
                # Preview
                with st.expander("Preview"):
                    for line in metadata.get('preview', []):
                        st.text(line)
                
                # Load button
                if st.button("📂 Load This File", type="primary"):
                    phrases = load_phrase_file(metadata['path'])
                    st.session_state.phrase_list = phrases
                    st.session_state.current_phrase_index = 0
                    st.session_state.last_result = None
                    st.session_state.material_source = f"{material_lang}/{category}/{selected_file}"
                    st.success(f"✓ Loaded {len(phrases)} items from built-in library")
                    st.rerun()
            else:
                st.info(f"No materials found for {material_lang}")
    
    # TAB 2: User upload (existing functionality)
    with source_tab2:
        st.write("Upload your own phrase/word list")
        uploaded_file = st.file_uploader(
            "Choose a text file",
            type=['txt'],
            help="Format: one phrase per line, or 'phrase | translation | [ipa]'"
        )
        
        if uploaded_file is not None:
            try:
                content = uploaded_file.read().decode('utf-8')
                raw_lines = [line.strip() for line in content.split('\n') if line.strip()]
                
                phrases = []
                for line in raw_lines:
                    if '|' in line:
                        parts = [p.strip() for p in line.split('|')]
                        phrases.append({
                            'text': parts[0],
                            'translation': parts[1] if len(parts) > 1 else None,
                            'ipa': parts[2] if len(parts) > 2 else None
                        })
                    else:
                        phrases.append({'text': line, 'translation': None, 'ipa': None})
                
                st.success(f"✓ Loaded {len(phrases)} items from upload")
                
                if st.button("✅ Use This File", type="primary"):
                    st.session_state.phrase_list = phrases
                    st.session_state.current_phrase_index = 0
                    st.session_state.last_result = None
                    st.session_state.material_source = f"Uploaded: {uploaded_file.name}"
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error reading file: {e}")

# Show current material source
if 'phrase_list' in st.session_state and st.session_state.phrase_list:
    st.info(f"📚 Current material: {st.session_state.get('material_source', 'Unknown')}")
    
    if st.button("🗑️ Clear Material"):
        st.session_state.phrase_list = []
        st.session_state.current_phrase_index = 0
        st.session_state.last_result = None
        st.session_state.material_source = None
        st.rerun()
```

---

### Phase 2: Enhanced Features (v1.3.0)

#### A. Browse Mode

Add a "Browse Library" page showing all available materials:

```python
# New sidebar page
def show_library_browser():
    st.title("📚 Language Materials Library")
    
    from app_language_materials import get_available_languages, get_language_structure
    
    for lang in get_available_languages():
        st.header(f"🌍 {lang.upper()}")
        
        structure = get_language_structure(lang)
        
        for category, files in structure.items():
            with st.expander(f"{category} ({len(files)} files)"):
                for file in files:
                    metadata = get_file_metadata(lang, category, file)
                    
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{file}**")
                    with col2:
                        st.caption(f"{metadata['line_count']} items")
                    with col3:
                        if st.button("Load", key=f"{lang}_{category}_{file}"):
                            # Load logic
                            pass
```

#### B. GitHub URL Loading (Optional)

For advanced users or community sharing:

```python
with st.expander("🌐 Load from URL (Advanced)"):
    url = st.text_input(
        "GitHub Raw URL",
        placeholder="https://raw.githubusercontent.com/user/repo/main/file.txt"
    )
    
    if url and st.button("Load from URL"):
        try:
            import requests
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            content = response.text
            phrases = parse_phrases(content)
            
            st.session_state.phrase_list = phrases
            st.session_state.material_source = f"URL: {url}"
            st.success(f"✓ Loaded {len(phrases)} items")
            
        except Exception as e:
            st.error(f"Failed to load URL: {e}")
```

---

## Performance Optimization

### Caching Strategy

```python
# Cache all file operations
@st.cache_data
def get_available_languages() -> List[str]:
    # Scans filesystem once, caches result
    pass

@st.cache_data
def load_phrase_file(file_path: Path) -> List[Dict]:
    # Reads file once, caches parsed result
    pass

# Session state for user selections
if 'phrase_list' not in st.session_state:
    st.session_state.phrase_list = []
    st.session_state.current_phrase_index = 0
    st.session_state.material_source = None
```

### Benefits
- ⚡ File scanning happens once at startup
- ⚡ File loading cached until app restarts
- ⚡ No repeated disk I/O during user interaction
- 💾 Session state persists user choices across reruns

---

## User Experience Flow

### Scenario 1: New User (Built-in Materials)
1. Opens app
2. Sees "📚 Load Practice Materials" expander
3. Opens "Built-in Library" tab
4. Selects: French → Phrases-A → phr-01.txt
5. Sees preview: 50 phrases, translations ✓, IPA ✓
6. Clicks "Load This File"
7. Starts practicing immediately

### Scenario 2: Advanced User (Custom Materials)
1. Opens app
2. Goes to "Upload File" tab
3. Uploads `my_vocab_list.txt`
4. App parses and shows count
5. Clicks "Use This File"
6. Starts practicing

### Scenario 3: Returning User
1. Opens app
2. Sees "Current material: fr/phrases-A/phr-01.txt"
3. Continues from last phrase index
4. Can click "Clear Material" to start over

---

## File Format Documentation

Update user guide to explain formats:

```markdown
### Built-in Materials Format

All built-in phrase and word files follow this format:

```
phrase | translation | [ipa]
```

**Example:**
```
bonjour | hello / good day | [bɔ̃ʒuʁ]
merci | thank you | [mɛʁsi]
```

**Simple format also supported:**
```
bonjour
merci
au revoir
```

### Custom File Requirements

- **Encoding:** UTF-8
- **Format:** One phrase per line
- **Comments:** Lines starting with `#` are ignored
- **Empty lines:** Ignored automatically
- **Translations:** Optional, use `|` separator
- **IPA:** Optional, use `[brackets]`
```

---

## Testing Plan

### Unit Tests

```python
# test_language_materials.py

def test_get_available_languages():
    langs = get_available_languages()
    assert 'fr' in langs
    assert 'pt' in langs

def test_load_phrase_file():
    file_path = Path("language_materials/fr/phrases-A/phr-01.txt")
    phrases = load_phrase_file(file_path)
    
    assert len(phrases) == 50
    assert phrases[0]['text'] == 'bonjour'
    assert phrases[0]['translation'] == 'hello / good day'
    assert '[' in phrases[0]['ipa']

def test_parse_formats():
    # Test enhanced format
    content = "hello | bonjour | [hɛˈloʊ]"
    phrases = parse_phrases(content)
    assert phrases[0]['translation'] == 'bonjour'
    
    # Test simple format
    content = "hello\nworld"
    phrases = parse_phrases(content)
    assert len(phrases) == 2
    assert phrases[0]['translation'] is None
```

### Manual Testing Checklist

- [ ] Built-in file selector shows all languages
- [ ] File preview displays correct metadata
- [ ] Load button populates session state correctly
- [ ] Upload tab works independently
- [ ] Can switch between built-in and uploaded files
- [ ] Clear button resets state
- [ ] Works on Streamlit Cloud
- [ ] Performance: no lag when browsing files
- [ ] Format parsing handles all variations

---

## Deployment Checklist

### Before v1.2.0 Release

- [ ] Create `app_language_materials.py` module
- [ ] Update `app.py` with new UI
- [ ] Add `requests` to `requirements.txt` (for future URL loading)
- [ ] Update `USER_GUIDE.md` with new file loading instructions
- [ ] Test locally with both French and Portuguese materials
- [ ] Commit all `language_materials/` files to git
- [ ] Update version to 1.2.0 in `app.py`
- [ ] Update `APP_CHANGELOG.md`
- [ ] Create git tag: `v1.2.0`
- [ ] Push to GitHub
- [ ] Test on Streamlit Cloud deployment

### Verification on Cloud

```bash
# After deployment, verify:
1. Built-in library tab shows all materials
2. Can load French phrases-A
3. Can load Portuguese words-B
4. Upload tab still works
5. Performance is acceptable
6. No 404 errors in logs
```

---

## Future Enhancements (v1.4.0+)

### A. Material Statistics

Show usage stats for built-in materials:
- Most practiced files
- User completion rates
- Popular difficulty levels

### B. Favorites System

Allow users to bookmark favorite materials:
```python
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

# Star button next to files
if st.button("⭐", key=f"fav_{file}"):
    st.session_state.favorites.append(file_path)
```

### C. Search/Filter

Add search across all materials:
```python
search = st.text_input("🔍 Search materials")
if search:
    results = search_phrase_files(search)
    # Display matching phrases
```

### D. Community Materials

Integration with GitHub Issues/Discussions:
- Users can request new phrase sets
- Community can contribute materials
- Auto-populate from accepted PRs

---

## Security Considerations

### File Access

```python
# Always validate paths to prevent directory traversal
def load_phrase_file(file_path: Path) -> List[Dict]:
    # Ensure path is within DATA_DIR
    if not str(file_path.resolve()).startswith(str(DATA_DIR.resolve())):
        raise ValueError("Invalid file path")
    
    # Proceed with loading
    ...
```

### User Uploads

```python
# Limit file size
MAX_FILE_SIZE = 1024 * 1024  # 1MB

uploaded_file = st.file_uploader(
    "Choose a file",
    type=['txt'],
    accept_multiple_files=False
)

if uploaded_file:
    if uploaded_file.size > MAX_FILE_SIZE:
        st.error("File too large (max 1MB)")
    else:
        # Process file
        ...
```

---

## Success Metrics

### Quantitative
- ✅ All built-in materials accessible within 3 clicks
- ✅ File loading < 1 second for files up to 500 lines
- ✅ Zero file I/O during practice (all cached)
- ✅ Works on all major browsers
- ✅ Mobile-responsive interface

### Qualitative
- ✅ Clear distinction between built-in vs upload
- ✅ Easy material discovery
- ✅ Preview helps users choose appropriate level
- ✅ Smooth transition from browsing to practicing
- ✅ No confusion about file formats

---

## Rollout Plan

### Week 1: Core Implementation
- Day 1-2: Create `app_language_materials.py`
- Day 3-4: Update UI in `app.py`
- Day 5: Testing and bug fixes

### Week 2: Polish & Deploy
- Day 1-2: Documentation updates
- Day 3: Final testing
- Day 4: Deploy to Streamlit Cloud
- Day 5: Monitor for issues, gather feedback

### Week 3: Iteration
- Address user feedback
- Performance optimization if needed
- Plan v1.3.0 enhancements

---

## Conclusion

This implementation provides:

1. **Zero Friction for New Users** - Built-in materials ready to use
2. **Flexibility for Advanced Users** - Can upload custom files
3. **Scalability** - Easy to add more languages/materials
4. **Performance** - Smart caching prevents slowdowns
5. **Cloud Ready** - Works identically on local and deployed versions

**Estimated Development Time:** 2-3 days
**Risk Level:** Low (existing upload functionality remains unchanged)
**User Impact:** High (significantly improves first-time experience)

---

## Next Steps

1. Review this plan with stakeholders
2. Begin Phase 1 implementation
3. Create feature branch: `feature/language-materials-v1.2.0`
4. Implement and test incrementally
5. Deploy and gather user feedback
