# Bump Script Usage Guide

The `bump_app.py` script automates version bumping across all project files.

## Configuration Files

- **bump_program_files.txt** - Core program files with version numbers
- **bump_doc_files.txt** - Documentation files with version numbers

Edit these files to add/remove files from version bumping.

## Usage Examples

**Important:** Always activate the virtual environment first:
```bash
source venv/bin/activate
```

### Just bump version (no commit/tag)
```bash
bump_app.py major   # 1.2.3 → 2.0.0
bump_app.py minor   # 1.2.3 → 1.3.0
bump_app.py patch   # 1.2.3 → 1.2.4
```

### Bump + commit + tag
```bash
bump_app.py major tag
bump_app.py minor tag
bump_app.py patch tag
```

### Bump + commit + tag + push
```bash
bump_app.py major tag push
bump_app.py minor tag push
bump_app.py patch tag push
```

## Typical Workflow

1. **During development**: Use plain `bump patch` to update version numbers
   ```bash
   source venv/bin/activate
   bump_app.py patch
   # Review changes
   git add -A
   git commit -m "Fix bug XYZ"
   ```

2. **For releases**: Use `bump tag` or `bump tag push`
   ```bash
   source venv/bin/activate
   bump_app.py minor tag push
   # This will:
   # - Bump 2.2.3 → 2.3.0 in all files
   # - Commit with message "v2.3.0: Version bump"
   # - Create tag v2.3.0
   # - Push to remote
   ```

3. **For hotfixes**:
   ```bash
   source venv/bin/activate
   # Fix the bug first, commit it
   git commit -m "Fix critical bug"
   
   # Then bump and release
   bump_app.py patch tag push
   ```

## What It Does

The script automatically:

- Finds current version in any tracked file
- Updates version in all configured files:
  - Python: `__version__ = "1.2.3"`
  - Markdown: `**Version 1.2.3**`
  - Changelog: Adds new entry with date
- Commits with standardized message
- Creates annotated git tag
- Optionally pushes to remote

## Supported Version Patterns

The script recognizes these patterns:

```python
__version__ = "1.2.3"                    # Python files
```

```markdown
**Version 1.2.3**                        # Markdown
**Current Version:** 1.2.3               # Markdown variant
## [1.2.3] - 2025-11-24                  # Changelog
```
