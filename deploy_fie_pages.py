"""
deploy_fie_pages.py
-------------------
Moves generated FIE HTML files from ./fie_html_pages/ into their
correct district silo folders.

FROM:  fie_html_pages/what-is-an-fie-katy-isd.html
TO:    districts/katy-isd/what-is-an-fie-katy-isd.html

Usage:
    python deploy_fie_pages.py

Run this from your site root:
    C:\\Users\\elisa\\OneDrive\\Documents\\texas-special-ed-site\\
"""

import os
import shutil

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR   = os.path.join(SCRIPT_DIR, "fie_html_pages")
DISTRICTS_DIR = os.path.join(SCRIPT_DIR, "districts")

if not os.path.exists(SOURCE_DIR):
    raise FileNotFoundError(
        f"\n❌ Source folder not found: {SOURCE_DIR}\n"
        f"   Run assemble_fie_pages.py first to generate the files.\n"
    )

files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".html")]

if not files:
    print("⚠️  No HTML files found in fie_html_pages/. Nothing to deploy.")
    exit()

print(f"Found {len(files)} files to deploy...\n")

moved   = []
skipped = []
errors  = []

for filename in sorted(files):
    # Extract slug from filename: what-is-an-fie-katy-isd.html → katy-isd
    slug = filename.replace("what-is-an-fie-", "").replace(".html", "")

    source      = os.path.join(SOURCE_DIR, filename)
    silo_folder = os.path.join(DISTRICTS_DIR, slug)
    destination = os.path.join(silo_folder, filename)

    # Create the district folder if it doesn't exist yet
    os.makedirs(silo_folder, exist_ok=True)

    if os.path.exists(destination):
        skipped.append(filename)
        print(f"  SKIP   {filename}  (already exists in districts/{slug}/)")
        continue

    try:
        shutil.copy2(source, destination)   # copy2 preserves timestamps
        moved.append(filename)
        print(f"  ✓      {filename}  →  districts/{slug}/")
    except Exception as e:
        errors.append((filename, str(e)))
        print(f"  ✗  ERROR {filename}: {e}")

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅  Deployed : {len(moved)}
  ⏭️   Skipped  : {len(skipped)} (already existed)
  ❌  Errors   : {len(errors)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Files copied to: {DISTRICTS_DIR}
""")

if errors:
    print("Errors:")
    for fname, msg in errors:
        print(f"  {fname}: {msg}")