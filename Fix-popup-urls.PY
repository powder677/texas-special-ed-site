"""
Run this from your texas-special-ed-site directory:
  python fix_popup_urls.py

Updates all HTML files to point to the new email-capture-api service.
"""

import os
import glob
import re

OLD_URL      = "https://ard-intake-bot-831148457361.us-central1.run.app/api/newsletter-signup"
NEW_URL      = "https://email-capture-api-831148457361.us-central1.run.app/api/signup"

# The new API also needs site + language in the payload.
# We'll inject them into the existing fetch body.
OLD_PAYLOAD_SNIPPET = '"source":'
NEW_PAYLOAD_SNIPPET = '"site": "texas_special_ed", "language": "en", "source":'

def fix_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        original = f.read()

    if OLD_URL not in original:
        return False  # nothing to fix in this file

    updated = original.replace(OLD_URL, NEW_URL)

    # Only inject site/language if not already there
    if '"site":' not in updated and OLD_PAYLOAD_SNIPPET in updated:
        updated = updated.replace(OLD_PAYLOAD_SNIPPET, NEW_PAYLOAD_SNIPPET, 1)

    if updated != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(updated)
        return True

    return False

def main():
    html_files = glob.glob("**/*.html", recursive=True)
    if not html_files:
        html_files = glob.glob("*.html")

    if not html_files:
        print("No HTML files found. Are you in the right directory?")
        print(f"Current directory: {os.getcwd()}")
        return

    print(f"Scanning {len(html_files)} HTML files...")

    fixed = 0
    for filepath in html_files:
        if fix_file(filepath):
            fixed += 1
            if fixed <= 5:
                print(f"  ✓ {filepath}")

    if fixed > 5:
        print(f"  ... and {fixed - 5} more files")

    print(f"\nDone. Fixed {fixed} / {len(html_files)} files.")

    if fixed > 0:
        print("\nNext step — push to Vercel:")
        print('  git add .')
        print('  git commit -m "Point popup to new email-capture-api"')
        print('  git push')
    else:
        print("\nNo files needed updating.")
        print("Check that you're running this from your texas-special-ed-site folder.")

if __name__ == "__main__":
    main()