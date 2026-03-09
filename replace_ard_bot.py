"""
replace_ard_bot.py
==================
Finds every HTML file in your site directory that contains the ARD chatbot
iframe and replaces it (along with its wrapper div) with the card snippet
that links to the dedicated /tools/ard-rights-scan/index.html page.

USAGE
-----
  python replace_ard_bot.py --dir "C:/Users/elisa/OneDrive/Documents/texas-special-ed-site"

OPTIONS
  --dir       Root folder to scan (searches all subdirectories)
  --dry-run   Preview what would change without touching any files
  --backup    Save a .bak copy of each file before editing

REQUIREMENTS
  pip install beautifulsoup4
"""

import os
import re
import shutil
import argparse
from pathlib import Path

try:
    from bs4 import BeautifulSoup, NavigableString
except ImportError:
    print("ERROR: beautifulsoup4 is not installed.")
    print("Run:  pip install beautifulsoup4")
    exit(1)

# ── The iframe src we're hunting for ──────────────────────────────────────────
BOT_URL = "ard-chatbot-831148457361.us-central1.run.app"

# ── Replacement card HTML (sidebar style, matches your existing dark cards) ───
CARD_HTML = """<div style="
  background: linear-gradient(145deg, #0f172a 0%, #1e3a8a 100%);
  border-radius: 16px;
  box-shadow: 0 12px 35px rgba(30, 58, 138, 0.25);
  padding: 28px 24px 24px;
  border: 1px solid #2a4382;
  text-align: center;
">
  <span style="
    display: inline-block;
    background: #d4af37;
    color: #0f172a;
    padding: 4px 12px;
    border-radius: 50px;
    font-size: 0.75rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 14px;
    font-family: 'DM Sans', sans-serif;
  ">Free AI Tool</span>

  <h3 style="
    margin: 0 0 10px;
    color: #ffffff;
    font-family: 'Lora', serif;
    font-size: 1.35rem;
    line-height: 1.3;
  ">Free ARD Rights Scan</h3>

  <p style="
    font-size: 14px;
    color: #cbd5e1;
    margin: 0 0 22px;
    line-height: 1.55;
    font-family: 'Source Sans 3', sans-serif;
  ">
    Wondering if the school violated your rights? Answer a few questions for an instant analysis based on Texas law.
  </p>

  <a href="/tools/ard-rights-scan/index.html" style="
    display: block;
    background: #d4af37;
    color: #0f172a;
    padding: 14px 20px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 800;
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    transition: background 0.2s;
  ">Run My Free ARD Scan &#8594;</a>

  <p style="
    font-size: 11px;
    color: #64748b;
    margin: 12px 0 0;
    font-family: 'Source Sans 3', sans-serif;
  ">&#128274; Free &nbsp;&middot;&nbsp; No account needed</p>
</div>"""


def find_wrapper_div(iframe_tag):
    """
    Walk up the DOM from the iframe to find the outermost wrapper div
    that exists solely to contain / style the bot.
    We stop climbing when the parent contains meaningful sibling content
    (e.g. other text, headings, links) — that means we've gone too far.
    """
    candidate = iframe_tag.parent
    while candidate and candidate.name not in ("body", "main", "section", "article", "aside"):
        parent = candidate.parent
        if parent is None:
            break
        # If the parent has multiple meaningful children, stop here —
        # replacing it would nuke surrounding content.
        meaningful_siblings = [
            c for c in parent.children
            if not isinstance(c, NavigableString) or c.strip()
        ]
        if len(meaningful_siblings) > 2:
            break
        candidate = parent

    return candidate if candidate and candidate.name == "div" else iframe_tag


def process_file(filepath: Path, dry_run: bool, backup: bool) -> bool:
    """
    Returns True if the file was (or would be) modified.
    """
    html = filepath.read_text(encoding="utf-8", errors="replace")

    # Quick check before full parse
    if BOT_URL not in html:
        return False

    soup = BeautifulSoup(html, "html.parser")
    iframes = soup.find_all("iframe", src=re.compile(re.escape(BOT_URL)))

    if not iframes:
        return False

    for iframe in iframes:
        target = find_wrapper_div(iframe)
        replacement = BeautifulSoup(CARD_HTML, "html.parser")
        target.replace_with(replacement)

    new_html = str(soup)

    if dry_run:
        print(f"  [DRY RUN] Would update: {filepath}")
        return True

    if backup:
        shutil.copy2(filepath, filepath.with_suffix(filepath.suffix + ".bak"))

    filepath.write_text(new_html, encoding="utf-8")
    print(f"  ✅ Updated: {filepath}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Replace ARD bot iframes with card links.")
    parser.add_argument("--dir",     required=True, help="Root directory of your site")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes, don't write files")
    parser.add_argument("--backup",  action="store_true", help="Save .bak copy before editing each file")
    args = parser.parse_args()

    root = Path(args.dir)
    if not root.exists():
        print(f"ERROR: Directory not found: {root}")
        exit(1)

    html_files = list(root.rglob("*.html"))
    print(f"\n🔍 Scanning {len(html_files)} HTML files in: {root}")
    if args.dry_run:
        print("   (DRY RUN — no files will be changed)\n")
    if args.backup:
        print("   (BACKUP mode — .bak copies will be saved)\n")

    changed = []
    skipped = []

    for f in html_files:
        try:
            modified = process_file(f, dry_run=args.dry_run, backup=args.backup)
            if modified:
                changed.append(f)
            else:
                skipped.append(f)
        except Exception as e:
            print(f"  ⚠️  ERROR processing {f}: {e}")

    print(f"\n{'─'*55}")
    print(f"  Files scanned : {len(html_files)}")
    print(f"  Files {'to update' if args.dry_run else 'updated'}  : {len(changed)}")
    print(f"  Files skipped : {len(skipped)} (no bot found)")
    if args.backup and changed and not args.dry_run:
        print(f"  Backups saved : yes (.bak alongside each file)")
    print(f"{'─'*55}\n")

    if changed and not args.dry_run:
        print("✅ All done! Remember to:")
        print("   1. Deploy /tools/ard-rights-scan/index.html to your site")
        print("   2. Spot-check a few pages in your browser")
        print("   3. Delete .bak files once you're happy\n")


if __name__ == "__main__":
    main()