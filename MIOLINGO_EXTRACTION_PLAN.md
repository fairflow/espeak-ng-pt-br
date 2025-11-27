# Miolingo Repository Extraction Plan

## Objective
Extract miolingo from espeak-ng-pt-br repo into standalone `~/Software/working/miolingo/` repo with preserved git history from commit f38c27bf onward.

## Target Structure

```
~/Software/working/
├── espeak-ng/              # Fresh clone with local config
└── miolingo/               # Extracted with history
    ├── src/                # Python source files
    ├── docs/
    │   ├── app-docs/       # App documentation (separate VC stream)
    │   └── admin-docs/     # Admin documentation (separate VC stream)
    ├── config/             # Configuration templates
    ├── scripts/            # Utility scripts
    ├── language_materials/ # Language content
    ├── articles/           # Miolingo articles
    ├── .streamlit/         # Streamlit config (not secrets)
    ├── requirements.txt
    ├── configure           # Setup script
    ├── Makefile           # Build automation
    └── README.md          # Miolingo-focused
```

## Files to Extract (with git history from f38c27bf)

### Core Python Applications
```
src/app.py                          # Main app
src/miolingo-admin.py              # Admin dashboard
src/app_mysql.py                   # Database connection
src/app_language_materials.py      # Language materials
src/api_usage_logger.py            # API logging
src/cost_monitor.py                # Cost tracking
```

### Python Utilities & Tools
```
src/add_ipa_to_scenes.py
src/analyze_difficulty.py
src/analyze_difficulty_local.py
src/apply_translations.py
src/complete_all_story_translations.py
src/complete_story_translations.py
src/complete_story_translations_full.py
src/extract_french_words.py
src/extract_phrases.py
src/extract_story_phrases.py
src/fill_ipa_tags.py
src/generate_phrasebook_ipa.py
src/generate_story_scenes_ipa.py
src/populate_french_translations.py
src/practice_app.py
src/practice_sentences.py
src/process_story_scenes.py
src/pronunciation_trainer.py
src/record_audio.py
src/split_phrasebook.py
src/streamlit_app.py
src/streamlit_app_v2.py
src/test_audio.py
src/test_google_cloud_tts.py
src/test_gtts_simple.py
src/test_isso.py
src/translate_all_phrases.py
src/update_version.py
```

### Testing Framework
```
src/ccs_test_framework.py
src/ccs_test_integration.py
ccs_test_logs/                     # Directory
```

### Version Management Scripts
```
scripts/bump_app.py
scripts/bump_admin.py
scripts/bump_admin_doc_files.txt
scripts/bump_admin_program_files.txt
scripts/bump_doc_files.txt
scripts/bump_program_files.txt
```

### eSpeak-NG Integration Tools
```
scripts/speak_phonemes.py
scripts/ipa_to_espeak.py
scripts/configure-macos.sh         # Also stays in espeak-ng
```

### Configuration Files
```
requirements.txt
requirements-wav2vec2.txt
runtime.txt
packages.txt
.gitignore
.python-version
config/practice_config.json        # Template (not actual data)
config/.miolingo.config            # NEW: espeak-ng path config
```

### Streamlit Configuration
```
.streamlit/config.toml             # If exists
.streamlit/secrets_template.toml   # Template only
# NOT: .streamlit/secrets.toml (user must copy manually)
```

### Documentation - App (docs/app-docs/)
```
docs/app-docs/USER_GUIDE.md
docs/app-docs/TESTING_GUIDE.md
docs/app-docs/DEVELOPER_GUIDE.md
docs/app-docs/DEPLOYMENT.md
# ... all files from app-docs/
```

### Documentation - Admin (docs/admin-docs/)
```
docs/admin-docs/ADMIN_GUIDE.md
docs/admin-docs/ADMIN_CHANGELOG.md
docs/admin-docs/BUMP_ADMIN_GUIDE.md
docs/admin-docs/EMAIL_MONITORING.md
# ... all files from admin-docs/
```

### Documentation - Admin Sources (docs/admin-docs/sources/)
```
docs/admin-docs/sources/email_monitor.py
docs/admin-docs/sources/email_secrets_template.toml
# ... all files from admin-sources/
```

### Documentation - Root Level (Miolingo-specific)
```
README.md                          # REWRITE for miolingo
APP_CHANGELOG.md
VERSION_WORKFLOW.md
VERSION_CHECKLIST.md
BUMP_GUIDE.md
AUTOMATION_REFERENCE.md
MIOLINGO_DESCRIPTION.md

# Implementation & Planning
IMPLEMENTATION_SUMMARY.md
MULTI_USER_IMPLEMENTATION_PLAN.md
PRACTICE_MODE_IMPLEMENTATION.md
LANGUAGE_MATERIALS_INTEGRATION_PLAN.md
JSON_FORMAT_STANDARDIZATION_PROPOSAL.md

# Technical Guides
PYTHON-SETUP.md
STREAMLIT-FIXES.md
STREAMLIT_CLOUD_DATABASE_ISSUE.md
KRYSTAL_DATABASE_SETUP_GUIDE.md
SECURITY_HARDENING.md

# Testing & Quality
CCS_TESTING_README.md
CCS_USAGE_GUIDE.md
PROJECT_STATS.md

# API & Cost
API_COST_TRACKING.md
AUDIO_TRACKING.md

# Feature Documentation
PHRASE_LIST_FORMAT.md
APP-GUIDE.md
pronunciationVowels.md

# Historical/Session Notes
CHAT_SUMMARY_2025-11-10.md
DOCUMENTATION_SUMMARY.md
NEW-APP-SUMMARY.md
```

### Documentation - eSpeak Integration (copy to both repos)
```
LOCAL-BUILD.md
IPA-SOLUTION.md
AUDIO-NOTES.md
PHONEME-REFERENCE.md
QUICKSTART-SPEECH-RECOGNITION.md
ESPEAK_USAGE.md
SPEECH-RECOGNITION.md
RECOGNITION-TIPS.md
README-PT-BR.md                    # Portuguese eSpeak README
```

### Language Materials
```
language_materials/                # Entire directory
```

### Articles
```
articles/                          # Entire directory
```

### Practice/Training Data Files (tracked)
```
practice_flemish_phrases_A.txt
practice_french_phrases_A.txt
practice_phrases_with_translations.txt
practice_phrases1.txt
practice_phrases2.txt
practice_words.txt
practice_words2.txt
sample_phrases.txt
sample_practice.txt
sample_practice2.txt
sample_practice2_english.txt
```

### French Content Files
```
extracted_phrases_fr.json
graded_phrases_fr.json
narrative_fr.txt
narrative_generation_prompts.md
phrases_organized_fr.json
phrases_with_translations_fr.json
story_framework_fr.md
scene-13-les-secours-translated.json
scene-14-la-reflexion-de-sophie-translated.json
scene-15-la-decouverte-translated.json
scene-16-la-reunion-translated.json
```

### Setup Scripts
```
scripts/setup.sh
scripts/setup-french-v2.sh
```

### Other Data Files
```
training_set.txt
```

### VS Code Configuration
```
.vscode/                           # Directory (if miolingo-specific)
```

### GitHub Configuration
```
.github/                           # Directory (workflows, etc)
```

## Files to EXCLUDE (stay with espeak-ng or discard)

### eSpeak-NG Core
- All `phsource/`, `dictsource/`, `espeak-ng-data/`, `src/`, `docs/` (espeak's)
- `tests/`, `tools/`, `vim/`, `m4/`, `cmake/`, `emscripten/`, `android/`, `fastlane/`
- Build system: `configure.ac`, `Makefile.am`, `CMakeLists.txt`, `autogen.sh`
- eSpeak licenses: `COPYING*`
- eSpeak docs: `ChangeLog.md`, `NEWS`, original `README`

### Build Artifacts (not in git anyway)
- `local/`, `venv/`, `__pycache__/`, `nano/`, `scripts/`
- Build files: `config.h`, `config.status`, etc.
- Temporary: `temp_streamlit_recording.wav`, `*.pyc`, `.DS_Store`

### Runtime Data (not in git)
- `practice_config.json` (user's actual file)
- `practice_history.json`
- `.streamlit/secrets.toml`
- Any database dumps or sensitive data

## espeak-ng Local Config to Preserve

When setting up fresh espeak-ng clone, preserve:
1. `configure-macos.sh` (custom configure script)
2. `.gitignore` additions for `local/`
3. `docs/building.md` additions (MacPorts instructions)
4. Any other MacPorts-specific patches

## Git History Split Point

**Start commit**: `f38c27bf` - "Add local build support with Brazilian Portuguese speech recognition tools"

All miolingo development after this commit will be preserved.

## Non-Tracked Essential Files to Document

User must manually copy these:
- `.streamlit/secrets.toml` (contains passwords)
- `practice_config.json` (user's actual config)
- `practice_history.json` (user's practice data)
- Any local data files

## Workflow Steps

1. ✅ Install git-filter-repo: `port install git-filter-repo`
2. ⏳ Commit all current changes
3. ⏳ Create full backup of current directory
4. ⏳ Clone repo to temp location
5. ⏳ Run git-filter-repo to extract miolingo files
6. ⏳ Reorganize into new structure (src/, docs/, scripts/, config/)
7. ⏳ Create configure/Makefile for miolingo
8. ⏳ Update README.md for miolingo
9. ⏳ Create .miolingo.config template
10. ⏳ Test locally
11. ⏳ Move to ~/Software/working/miolingo/
12. ⏳ Create GitHub repo fairflow/miolingo
13. ⏳ Push and verify
14. ⏳ Fresh clone espeak-ng upstream
15. ⏳ Re-apply local config to espeak-ng
16. ⏳ Test espeak-ng build
17. ⏳ Move to ~/Software/working/espeak-ng/
18. ⏳ Verify both repos work independently
19. ⏳ Remove adaptive-text/espeak-ng/

## Safety Measures

- ✅ No deletions until everything tested
- ✅ Full backup before any git operations
- ✅ Local testing before GitHub
- ✅ Verify git history preservation
- ✅ Document all manual steps needed
