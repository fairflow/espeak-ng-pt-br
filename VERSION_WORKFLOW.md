# Version Management & Git Workflow

## Quick Reference

**Current Version:** 0.9.0
**App File:** `app.py`
**Versioning:** Semantic Versioning (MAJOR.MINOR.PATCH)
**Git Tags:** Match versions (`v0.9.0`, `v1.0.0`, etc.)

## Version Number Rules

```
0.9.0 → 0.9.1 → 0.9.2 → ... → 0.9.9 → 1.0.0 → 1.0.1 → 1.1.0 → 2.0.0
```

- **PATCH** (0.9.0 → 0.9.1): Bug fixes only, no new features
- **MINOR** (1.0.0 → 1.1.0): New features, backward compatible  
- **MAJOR** (0.9.9 → 1.0.0): Breaking changes OR first stable release

## Git Workflow

### Main Branch
- **main** - Always production-ready, deployed to Streamlit Cloud
- Never commit broken code to main
- Never merge without explicit permission

### Feature Development

```bash
# Start new feature
git checkout main
git pull myfork main
git checkout -b feature/feature-name

# Work on feature
# ... make changes ...
git add .
git commit -m "Descriptive commit message"

# Push feature branch
git push myfork feature/feature-name

# When ready to test/integrate
git checkout main
git merge feature/feature-name
# Test locally before pushing!

# If tests pass, update version and push
# (see "Releasing a New Version" below)
```

### Bug Fixes

```bash
# For bugs in production
git checkout main
git checkout -b bugfix/bug-description

# Fix bug
# ... make changes ...
git add .
git commit -m "Fix: description of bug fix"

# Merge and release patch version
git checkout main
git merge bugfix/bug-description
# Bump PATCH version (0.9.0 → 0.9.1)
```

### Hotfixes

```bash
# For critical production issues
git checkout main
git checkout -b hotfix/critical-issue

# Fix immediately
# ... make changes ...
git add .
git commit -m "Hotfix: critical issue description"

# Merge and release
git checkout main
git merge hotfix/critical-issue
# Bump PATCH version immediately
```

## Releasing a New Version

### 1. Update Version Number

Edit `app.py`:
```python
__version__ = "0.9.1"  # Increment appropriately
```

### 2. Update Changelog

Edit `APP_CHANGELOG.md`:
```markdown
## [0.9.1] - 2025-11-XX

### Added
- New feature descriptions

### Fixed
- Bug fix descriptions

### Changed
- Changes to existing features
```

### 3. Commit Version Bump

```bash
git add app.py APP_CHANGELOG.md
git commit -m "Bump version to 0.9.1

- Summary of main changes
- Key bug fixes
- Important notes"
```

### 4. Create Git Tag

```bash
# Tag must match version in app.py
git tag -a v0.9.1 -m "Version 0.9.1

- Feature/fix summary
- Important changes
- Known issues (if any)"
```

### 5. Push Everything

```bash
# Push main branch AND tags together
git push myfork main --follow-tags
```

### 6. Verify Deployment

- Check Streamlit Cloud picks up changes
- Reboot app if needed via Streamlit dashboard
- Verify version number shows in sidebar

## Version Display

The app automatically shows version info in the sidebar:
```
Portuguese Pronunciation Trainer
Version 0.9.0
```

This is pulled from `__version__` in `app.py`.

## Rollback Procedure

If a release has critical issues:

```bash
# Identify last working version
git tag -l  # List all tags

# Rollback to previous version
git checkout v0.9.0  # or previous working version

# Create hotfix branch from that point
git checkout -b hotfix/rollback-v0.9.1

# Or hard reset main (DANGEROUS - use with caution)
git reset --hard v0.9.0
git push myfork main --force  # Only if necessary!
```

## Best Practices

1. **Never push directly to main** - Always use branches
2. **Test locally first** - Run app before pushing
3. **Keep versions in sync** - Tag = version in app.py
4. **Document changes** - Update APP_CHANGELOG.md
5. **Meaningful commits** - Clear, descriptive messages
6. **Small increments** - Patch versions for fixes, minor for features
7. **Wait for permission** - Don't merge to main without approval

## When to Release 1.0.0

Version 1.0.0 should be released when:
- All major features are stable
- No critical bugs remain
- App has been tested on multiple devices/platforms
- Documentation is complete
- You're confident it's production-ready

Until then, stay in 0.x.x versions:
- 0.9.x = beta/pre-release
- 1.0.0 = first stable release
- 1.x.x = stable with new features
- 2.0.0 = major breaking changes

## Viewing Version History

```bash
# List all versions
git tag -l

# Show specific version details
git show v0.9.0

# View changelog
cat APP_CHANGELOG.md

# Check current version
git describe --tags
```

## Remote Repository

- **myfork**: `fairflow/espeak-ng-pt-br` (your fork)
- **origin**: `espeak-ng/espeak-ng` (upstream, read-only)

Always push to `myfork`, never `origin`.
