"""
Run this from your texas-special-ed-site directory:
  python fix_popup_urls.py
"""

import os
import glob

def fix_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        original = f.read()

    if "GOOGLE_SCRIPT_URL" not in original:
        return False

    updated = original

    # Step 1: replace the full Google Script URL with new Cloud Run URL
    gs_start = updated.find("const GOOGLE_SCRIPT_URL = 'https://script.google.com")
    if gs_start != -1:
        gs_end = updated.find("'", gs_start + len("const GOOGLE_SCRIPT_URL = '"))
        if gs_end != -1:
            old_line = updated[gs_start:gs_end + 1]
            new_line = "const GOOGLE_SCRIPT_URL = 'https://email-capture-api-831148457361.us-central1.run.app/api/signup'"
            updated = updated.replace(old_line, new_line, 1)

    # Step 2: remove 'mode: no-cors' — it blocks reading the response
    updated = updated.replace("      mode: 'no-cors',\n", "")
    updated = updated.replace("      mode: \"no-cors\",\n", "")

    # Step 3: inject site + language into POST body if not already there
    if '"site":' not in updated and 'site:' not in updated:
        for snippet in ['body: JSON.stringify({', "body: JSON.stringify({"]:
            if snippet in updated:
                updated = updated.replace(
                    snippet,
                    snippet + '\n        site: "texas_special_ed",\n        language: "en",',
                    1
                )
                break

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
        print("\nNext — push to Vercel:")
        print('  git add .')
        print('  git commit -m "Switch popup from Google Script to email-capture-api"')
        print('  git push')
    else:
        print("\nNo files updated.")
        print("Run this to inspect what URL is in your files:")
        print('  python -c "f=open(\'how-to-disagree-at-ard-meeting.html\',encoding=\'utf-8\').read(); idx=f.find(\'GOOGLE_SCRIPT_URL\'); print(f[idx:idx+200])"')

if __name__ == "__main__":
    main()