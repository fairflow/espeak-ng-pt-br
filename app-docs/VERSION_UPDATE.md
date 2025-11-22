# Version Update Workflow

This guide documents the process for updating version numbers across the Miolingo codebase.

## Quick Start

```bash
# Update to new version
./update_version.py 1.6.7

# Review changes
git diff

# Commit with changelog
git add -A
git commit -m "v1.6.7: <Brief description>

- <Change 1>
- <Change 2>
- <Change 3>

Fixes: #<issue_number> (if applicable)"

# Tag the release
git tag -a v1.6.7 -m "v1.6.7: <Brief description>"

# Push to remote
git push myfork main --tags
```

## update_version.py Script

The `update_version.py` script automates version number updates across all project files.

### Features

- ✅ Automatically finds and updates version numbers (no need to know current version)
- ✅ Updates `__version__` in Python files
- ✅ Updates `Version:` in markdown documentation
- ✅ Updates `Date:` to current date
- ✅ Shows clear summary of all changes

### Files Updated

**Python Files**:
- `app.py` - Main application
- `miolingo-admin.py` - Admin dashboard

**Documentation**:
- `README.md` - Project readme
- `app-docs/USER_GUIDE.md` - User documentation
- `app-docs/TESTING_GUIDE.md` - Testing guide
- `app-docs/DEVELOPER_GUIDE.md` - Developer documentation

### Usage

```bash
# Make executable (first time only)
chmod +x update_version.py

# Run with new version number
./update_version.py 1.6.7
```

### What It Does

1. **Validates version format**: Ensures format is `X.Y.Z`
2. **Updates Python files**: Searches for `__version__ = "X.Y.Z"` pattern
3. **Updates documentation**: Searches for `Version: X.Y.Z` and `Date: YYYY-MM-DD` patterns
4. **Shows summary**: Displays all changes made
5. **Provides next steps**: Shows git commands for committing and tagging

### Example Output

```
🔄 Updating to version 1.6.7
📅 Date: 2025-11-16

📝 Updating app files...
  ✓ app.py: 1.5.1 → 1.6.7
  ✓ miolingo-admin.py: 1.5.1 → 1.6.7

📚 Updating documentation...
  ✓ README.md:
      Version: 1.5.1 → 1.6.7
      Date: 2025-11-15 → 2025-11-16
  ✓ app-docs/USER_GUIDE.md:
      Version: 1.5.1 → 1.6.7
      Date: 2025-11-15 → 2025-11-16

✅ Version update complete!

📋 Next steps:
   1. Review changes: git diff
   2. Commit: git add -A && git commit -m 'v1.6.7: <description>'
   3. Tag: git tag -a v1.6.7 -m 'v1.6.7: <description>'
   4. Push: git push myfork main --tags
```

## Semantic Versioning

We follow [Semantic Versioning 2.0.0](https://semver.org/):

### Version Format: MAJOR.MINOR.PATCH

- **MAJOR** (1.x.x): Breaking changes, incompatible API changes
- **MINOR** (x.1.x): New features, backwards-compatible
- **PATCH** (x.x.1): Bug fixes, backwards-compatible

### When to Bump Each Number

**MAJOR version** (1.0.0 → 2.0.0):
- Breaking changes to user interface
- Incompatible database schema changes
- Major feature rewrites
- Removal of supported features

**MINOR version** (1.5.0 → 1.6.0):
- New language support added
- New features (phrasebook topics, admin dashboard)
- New TTS/STT providers
- Backwards-compatible improvements

**PATCH version** (1.5.1 → 1.5.2):
- Bug fixes
- Performance improvements
- Documentation updates
- Minor UI tweaks

### Examples from Project History

- **v1.3.5**: Bug fix - Fixed Google Cloud TTS secrets access (PATCH)
- **v1.4.0**: New feature - Added celebration sounds and session tracking (MINOR)
- **v1.5.0**: New feature - Added French phrasebook with topics (MINOR)
- **v1.5.1**: Bug fix - Fixed TTS fallback priority (PATCH)

## Commit Message Format

Use this format for version commits:

```
v1.6.7: <Brief one-line summary>

<Detailed description of changes>

Changes:
- <Change 1>
- <Change 2>
- <Change 3>

Fixes: #<issue_number>
Breaking Changes: <if any>
```

### Good Examples

```
v1.6.0: Add Spanish phrasebook with 103 phrases

Added full Spanish language support with translated phrasebook.

Changes:
- Translated all 103 French phrases to Spanish
- Generated IPA using eSpeak es voice
- Created 12 topic files in phrasebook-topics/
- Updated language selector to include Spanish

Files:
- language_materials/es/phrasebook_complete.json
- language_materials/es/phrasebook-topics/*.txt
```

```
v1.5.2: Fix audio playback on iOS Safari

Fixed audio format compatibility issues on iOS devices.

Changes:
- Convert MP3 to WAV format before playback
- Add iOS-specific audio handling
- Improve error messages for unsupported formats

Fixes: #42
```

## Git Tag Format

Tags should match version numbers and include a brief description:

```bash
# Annotated tag (recommended)
git tag -a v1.6.7 -m "v1.6.7: Add Spanish phrasebook support"

# Tag with detailed message
git tag -a v1.6.7 -m "v1.6.7: Add Spanish phrasebook support

- 103 phrases translated
- 12 topic files created
- Full IPA transcriptions"
```

## Complete Workflow Example

Here's a complete example of releasing version 1.6.0 with Spanish support:

```bash
# 1. Make your changes to the code
# ... code changes ...

# 2. Update version numbers
./update_version.py 1.6.0

# 3. Review the changes
git diff

# 4. Stage all changes
git add -A

# 5. Commit with detailed message
git commit -m "v1.6.0: Add Spanish phrasebook with 103 phrases

Added complete Spanish language support with phrasebook.

Changes:
- Translated all 103 French phrases to Spanish
- Generated IPA transcriptions using eSpeak es voice
- Created 12 topic-based phrasebook files
- Updated split_phrasebook.py to support Spanish
- Updated generate_phrasebook_ipa.py with es voice

Files:
- language_materials/es/phrasebook_complete.json
- language_materials/es/phrasebook-topics/*.txt
- Documentation updated to v1.6.0

Testing:
- Verified all 12 topic files load correctly
- Tested IPA pronunciation playback
- Confirmed Spanish appears in language selector"

# 6. Create annotated tag
git tag -a v1.6.0 -m "v1.6.0: Add Spanish phrasebook support"

# 7. Push to remote with tags
git push myfork main --tags

# 8. Verify on GitHub
# Check that tag appears: https://github.com/<user>/<repo>/tags
```

## Pre-Release Checklist

Before committing a version update:

- [ ] All tests pass (if you have automated tests)
- [ ] Documentation is up to date
- [ ] README.md reflects new features
- [ ] Changelog entries are accurate
- [ ] Version number follows semantic versioning
- [ ] Date is current in all docs
- [ ] No debugging code or temporary files included
- [ ] Feature works in production environment

## Hotfix Workflow

For urgent bug fixes that need immediate release:

```bash
# 1. Create hotfix branch (optional)
git checkout -b hotfix/1.5.2

# 2. Make the fix
# ... fix code ...

# 3. Update version (PATCH bump)
./update_version.py 1.5.2

# 4. Commit
git add -A
git commit -m "v1.5.2: Fix critical audio playback bug

Fixes: #123"

# 5. Tag
git tag -a v1.5.2 -m "v1.5.2: Critical audio fix"

# 6. Merge to main and push
git checkout main
git merge hotfix/1.5.2
git push myfork main --tags

# 7. Delete hotfix branch
git branch -d hotfix/1.5.2
```

## Rollback

If you need to rollback to a previous version:

```bash
# View available tags
git tag -l

# Checkout specific version
git checkout v1.5.0

# Or reset to previous version (CAREFUL!)
git reset --hard v1.5.0
git push myfork main --force  # Only if absolutely necessary
```

## Troubleshooting

### update_version.py not found
```bash
# Check if file exists
ls -l update_version.py

# Make executable
chmod +x update_version.py
```

### Version pattern not found
- Check that files contain `__version__ = "X.Y.Z"` format
- Check that docs contain `Version: X.Y.Z` format
- Update script patterns if needed

### Git push rejected
```bash
# Pull latest changes first
git pull myfork main

# Then push again
git push myfork main --tags
```

### Tag already exists
```bash
# Delete local tag
git tag -d v1.6.7

# Delete remote tag (if needed)
git push myfork --delete v1.6.7

# Create tag again
git tag -a v1.6.7 -m "v1.6.7: <description>"
```

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Tagging](https://git-scm.com/book/en/v2/Git-Basics-Tagging)

---

**Version**: 1.5.1  
**Last Updated**: 2025-11-16  
**Maintainer**: Matthew & Contributors
