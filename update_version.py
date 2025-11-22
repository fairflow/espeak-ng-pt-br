#!/usr/bin/env python3
"""
Update version numbers across the application and documentation.

Usage:
    python3 update_version.py 1.2.3
    python3 update_version.py 1.2.3 --date "14 November 2025"
"""

import sys
import re
from pathlib import Path
from datetime import datetime

def update_version_in_file(file_path, old_pattern, new_value, description):
    """Update version pattern in a file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Try to find and replace the pattern
        new_content, count = re.subn(old_pattern, new_value, content)
        
        if count > 0:
            file_path.write_text(new_content, encoding='utf-8')
            print(f"✓ {file_path.name}: {description} ({count} replacement(s))")
            return True
        else:
            print(f"⚠ {file_path.name}: Pattern not found - {description}")
            return False
    except Exception as e:
        print(f"✗ {file_path.name}: Error - {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 update_version.py <version> [--date <date>]")
        print("Example: python3 update_version.py 1.2.3")
        print("Example: python3 update_version.py 1.2.3 --date '14 November 2025'")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    # Parse optional date argument
    update_date = None
    if len(sys.argv) > 2 and sys.argv[2] == '--date':
        update_date = sys.argv[3] if len(sys.argv) > 3 else datetime.now().strftime("%d %B %Y")
    else:
        update_date = datetime.now().strftime("%d %B %Y")
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print(f"Error: Invalid version format '{new_version}'. Expected format: X.Y.Z (e.g., 1.2.3)")
        sys.exit(1)
    
    # Get script directory and project root
    script_dir = Path(__file__).parent
    
    print(f"Updating version to {new_version}...")
    print(f"Update date: {update_date}")
    print("-" * 50)
    
    success_count = 0
    total_count = 0
    
    # 1. Update app.py - __version__ variable
    app_file = script_dir / "app.py"
    total_count += 1
    if update_version_in_file(
        app_file,
        r'__version__\s*=\s*["\'][0-9]+\.[0-9]+\.[0-9]+["\']',
        f'__version__ = "{new_version}"',
        f"__version__ = \"{new_version}\""
    ):
        success_count += 1
    
    # 2. Update README.md - Version line
    readme_file = script_dir / "README.md"
    total_count += 1
    if update_version_in_file(
        readme_file,
        r'\*\*Version\s+[0-9]+\.[0-9]+\.[0-9]+\*\*',
        f'**Version {new_version}**',
        f"Version badge"
    ):
        success_count += 1
    
    # 3. Update app-docs/README.md - Version and date
    app_docs_readme = script_dir / "app-docs" / "README.md"
    total_count += 1
    if update_version_in_file(
        app_docs_readme,
        r'\*\*Version\s+[0-9]+\.[0-9]+\.[0-9]+\*\*\s*\|\s*Last Updated:.*',
        f'**Version {new_version}** | Last Updated: {update_date}',
        f"Version and date"
    ):
        success_count += 1
    
    # 4. Update app-docs/DEVELOPER_GUIDE.md - Version and date
    dev_guide = script_dir / "app-docs" / "DEVELOPER_GUIDE.md"
    total_count += 1
    if update_version_in_file(
        dev_guide,
        r'\*\*Version\s+[0-9]+\.[0-9]+\.[0-9]+\*\*\s*\|\s*Last Updated:.*',
        f'**Version {new_version}** | Last Updated: {update_date}',
        f"Version and date"
    ):
        success_count += 1
    
    # 5. Update app-docs/TESTING_GUIDE.md - Version at top
    testing_guide = script_dir / "app-docs" / "TESTING_GUIDE.md"
    total_count += 1
    if update_version_in_file(
        testing_guide,
        r'\*\*Version\s+[0-9]+\.[0-9]+\.[0-9]+\*\*',
        f'**Version {new_version}**',
        f"Version badge"
    ):
        success_count += 1
    
    # 6. Update app-docs/USER_GUIDE.md - Version and date
    user_guide = script_dir / "app-docs" / "USER_GUIDE.md"
    total_count += 1
    if update_version_in_file(
        user_guide,
        r'\*\*Version\s+[0-9]+\.[0-9]+\.[0-9]+\*\*\s*\|\s*Last Updated:.*',
        f'**Version {new_version}** | Last Updated: {update_date}',
        f"Version and date"
    ):
        success_count += 1
    
    print("-" * 50)
    print(f"Updated {success_count}/{total_count} files successfully")
    
    if success_count == total_count:
        print("\n✓ All version numbers updated!")
        print("\nNext steps:")
        print(f"1. Update APP_CHANGELOG.md manually with changes for v{new_version}")
        print(f"2. Update version history comment in app.py (around line 47)")
        print(f"3. Test: streamlit run app.py")
        print(f"4. Commit: git add app.py APP_CHANGELOG.md README.md app-docs/")
        print(f"5. Commit: git commit -m 'Bump version to {new_version}'")
        print(f"6. Tag: git tag -a v{new_version} -m 'Release version {new_version}: [description]'")
        print(f"7. Push: git push myfork main --follow-tags")
    else:
        print("\n⚠ Some files were not updated. Please check the warnings above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
