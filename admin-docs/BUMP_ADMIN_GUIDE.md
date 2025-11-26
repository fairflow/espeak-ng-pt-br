# Admin Bump Script Usage

Quick reference for bumping the admin dashboard version.

## Files

- `bump_admin.py` - Version bump script for admin dashboard
- `bump_admin_program_files.txt` - List of admin program files
- `bump_admin_doc_files.txt` - List of admin documentation files

## Usage

Always activate virtual environment first:
```bash
source venv/bin/activate
```

### Bump version only (no commit)
```bash
bump_admin.py patch
bump_admin.py minor
bump_admin.py major
```

### Bump + commit + tag
```bash
bump_admin.py patch tag
bump_admin.py minor tag
bump_admin.py major tag
```

### Bump + commit + tag + push
```bash
bump_admin.py patch tag push
bump_admin.py minor tag push
bump_admin.py major tag push
```

## Tags

Admin versions are tagged separately from app versions:
- App tags: `v2.2.3`
- Admin tags: `admin-v1.6.0`

## Files Updated

The script updates versions in:
- `miolingo-admin.py` (footer caption)
- `admin-docs/ADMIN_GUIDE.md`
- `admin-docs/ADMIN_CHANGELOG.md`

## Version Location

Admin version is in the footer:
```python
st.caption("Miolingo Admin Dashboard v1.6.0 | Local monitoring interface")
```

## Shorthand Commands

When working with me (GitHub Copilot), you can use:
- `bump_admin patch` - I'll execute immediately
- `bump_admin minor tag` - I'll execute immediately
- `bump_admin patch tag push` - I'll confirm first, then execute
