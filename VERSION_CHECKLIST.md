# Version Number Update Checklist

**CURRENT VERSION: 2.0.5** <!-- UPDATE THIS MARKER -->

This document lists all files that contain version numbers and must be updated when releasing a new version.

---

## 🤖 Automated Updates (use `update_version.py`)

Run the script to automatically update these files:

```bash
./update_version.py 2.0.3
# or with custom date:
./update_version.py 2.0.3 --date "22 November 2025"
```

### Files Updated by Script:

1. **`app.py`** (Line ~11)
   - Pattern: `__version__ = "X.Y.Z"`
   - Example: `__version__ = "2.0.2"`

2. **`README.md`** (Line ~3)
   - Pattern: `**Version X.Y.Z**`
   - Example: `**Version 2.0.2** | Web-based...`

3. **`app-docs/README.md`** (Line ~3)
   - Pattern: `**Version X.Y.Z** | Last Updated: DD Month YYYY`
   - Example: `**Version 2.0.2** | Last Updated: 22 November 2025`

4. **`app-docs/DEVELOPER_GUIDE.md`** (Line ~3)
   - Pattern: `**Version X.Y.Z** | Last Updated: DD Month YYYY`
   - Example: `**Version 2.0.2** | Last Updated: 22 November 2025`

5. **`app-docs/TESTING_GUIDE.md`** (Line ~3)
   - Pattern: `**Version X.Y.Z**`
   - Example: `**Version 2.0.2** | For App Users & Testers`

6. **`app-docs/USER_GUIDE.md`** (Line ~3)
   - Pattern: `**Version X.Y.Z** | Last Updated: DD Month YYYY`
   - Example: `**Version 2.0.2** | Last Updated: 22 November 2025`

---

## ✍️ Manual Updates Required

### 1. **`APP_CHANGELOG.md`** (Line ~9)
   - **Action:** Add new version section at the top
   - **Format:**
     ```markdown
     ## [X.Y.Z] - YYYY-MM-DD

     ### Added
     - New feature description

     ### Fixed
     - Bug fix description

     ### Changed
     - Change description
     ```

### 2. **`VERSION_WORKFLOW.md`** (Line ~5)
   - **Action:** Update current version reference
   - **Pattern:** `**Current Version:** X.Y.Z`
   - **Example:** `**Current Version:** 2.0.2`

### 3. **Git Operations**
   - **Commit message:** `vX.Y.Z: Brief description`
   - **Tag creation:** `git tag -a vX.Y.Z -m "Version X.Y.Z: Description"`

---

## 📋 Pre-Release Checklist

Before creating a new version:

- [ ] Run `./update_version.py X.Y.Z`
- [ ] Manually update `APP_CHANGELOG.md` with new version entry
- [ ] Manually update `VERSION_WORKFLOW.md` current version
- [ ] Review and update version history comment in `app.py` (if needed)
- [ ] Test the app: `streamlit run app.py`
- [ ] Verify all version numbers are consistent:
  ```bash
  grep -r "Version [0-9]\.[0-9]\.[0-9]" app.py README.md app-docs/ | grep -v ".git"
  ```
- [ ] Commit changes: `git add -A && git commit -m "vX.Y.Z: Description"`
- [ ] Create tag: `git tag -a vX.Y.Z -m "Version X.Y.Z: Description"`
- [ ] Push to remote: `git push myfork main && git push myfork --tags`

---

## 🔍 Finding Version References

Search for version numbers across the project:

```bash
# Find all version number patterns
grep -rn "Version [0-9]\.[0-9]\.[0-9]" . --include="*.md" --include="*.py" | grep -v ".git" | grep -v "venv"

# Find __version__ declarations
grep -rn "__version__" . --include="*.py" | grep -v ".git"

# Find git tag references
grep -rn "v[0-9]\.[0-9]\.[0-9]" . --include="*.md" | grep -v ".git"
```

---

## 📝 Notes

- **Semantic Versioning:** MAJOR.MINOR.PATCH
  - MAJOR: Breaking changes
  - MINOR: New features (backward compatible)
  - PATCH: Bug fixes (backward compatible)

- **Version markers:** Files should have `<!-- VERSION: X.Y.Z -->` or similar markers near version numbers for easy identification

- **Automation:** The `update_version.py` script handles 6 files automatically. Only 2 files require manual updates (changelog and workflow docs).

---

**Last Updated:** 22 November 2025
