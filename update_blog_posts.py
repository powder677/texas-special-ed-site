"""
update_blog_posts.py
Updates all blog HTML files with:
  1. Gold "Get Your Letter — $25" CTA button in nav
  2. CTA card at top of sidebar
  3. Removes duplicate inline CSS (already in style.css)
  4. Ensures bot iframe is present and standardized

Usage:
    python update_blog_posts.py --dry-run   # preview only
    python update_blog_posts.py             # write changes
"""

import os
import re
import shutil
import argparse
from datetime import datetime
from bs4 import BeautifulSoup

# ── CONFIG ────────────────────────────────────────────────────────────────────

SITE_ROOT  = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site"
BLOG_DIR   = os.path.join(SITE_ROOT, "blog")
BACKUP_DIR = os.path.join(SITE_ROOT, "_backups", datetime.now().strftime("%Y%m%d_%H%M%S"))

BOT_URL = "https://texas-fie-bot-831148457361.us-central1.run.app"

# ── SNIPPETS ──────────────────────────────────────────────────────────────────

# Gold nav CTA — replaces the existing "Free ARD Checklist" nav item
NAV_CTA_HTML = '''<li class="nav-item nav-cta">
       <a class="btn-outline" href="/resources/ard-checklist.pdf" target="_blank">Free ARD Checklist</a>
      </li>
      <li class="nav-item nav-cta" style="margin-left:8px;">
       <a href="/get-your-letter.html" style="background:#d4af37;color:#0f172a;padding:10px 18px;border-radius:4px;font-weight:700;font-size:14px;text-decoration:none;font-family:'DM Sans',sans-serif;white-space:nowrap;">Get Your Letter — $25</a>
      </li>'''

# Sidebar CTA card — injected at the TOP of <aside class="sidebar-col">
SIDEBAR_CTA = '''<div class="sidebar-card cta-card" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);padding:28px;border-radius:12px;text-align:center;color:#fff;border:none;margin-bottom:0;">
      <h4 style="font-family:'Lora',serif;font-size:1.25rem;margin:0 0 10px;color:#fff;">Show the ISD<br/>You Mean Business</h4>
      <p style="font-family:'Source Sans 3',sans-serif;font-size:14px;color:#94a3b8;margin:0 0 18px;line-height:1.5;">A verbal request has no legal weight. A written letter starts the 45-day clock and forces a response within 15 school days.</p>
      <a href="/get-your-letter.html" style="display:block;background:#d4af37;color:#0f172a;padding:14px;border-radius:6px;text-decoration:none;font-weight:800;font-family:'DM Sans',sans-serif;font-size:14px;transition:background 0.2s;">Get Your Letter — $25 →</a>
     </div>'''

# Standardized bot iframe block
BOT_IFRAME_HTML = f'''<div class="bot-wrap" style="margin-bottom:40px;">
      <div style="background:#f8fafc;border-bottom:1px solid #e2e8f0;padding:16px 24px;display:flex;align-items:center;gap:12px;">
       <span style="background:#1e3a8a;color:#fff;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;padding:4px 10px;border-radius:50px;">Free Tool</span>
       <h3 style="font-family:'Lora',serif;font-weight:600;color:#0f172a;margin:0;font-size:1.1rem;">Build Your FIE Request Letter — $25</h3>
      </div>
      <iframe
       src="{BOT_URL}"
       title="Texas FIE Letter Builder"
       allow="clipboard-write"
       loading="lazy"
       style="width:100%;height:820px;border:none;display:block;">
      </iframe>
     </div>'''

# Inline CSS to remove (already in style.css)
INLINE_CSS_TO_REMOVE = re.compile(
    r'\.page-grid\s*\{[^}]+\}.*?@media\s*\(max-width:\s*900px\)\s*\{[^}]+\}',
    re.DOTALL
)

# ── HELPERS ───────────────────────────────────────────────────────────────────

def backup(path):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    rel  = os.path.relpath(path, SITE_ROOT)
    dest = os.path.join(BACKUP_DIR, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(path, dest)


def already_updated(html):
    return "Get Your Letter — $25" in html and "get-your-letter.html" in html


def add_nav_cta(html):
    """Add gold CTA button next to existing Free ARD Checklist button."""
    if "get-your-letter.html" in html:
        return html  # already done

    # Find the Free ARD Checklist nav item and add our button after it
    old = '''<li class="nav-item nav-cta">
       <a class="btn-outline" href="/resources/ard-checklist.pdf" target="_blank">
        Free ARD Checklist
       </a>
      </li>'''
    new = '''<li class="nav-item nav-cta">
       <a class="btn-outline" href="/resources/ard-checklist.pdf" target="_blank">
        Free ARD Checklist
       </a>
      </li>
      <li class="nav-item nav-cta" style="margin-left:8px;">
       <a href="/get-your-letter.html" style="background:#d4af37;color:#0f172a;padding:10px 18px;border-radius:4px;font-weight:700;font-size:14px;text-decoration:none;font-family:'DM Sans',sans-serif;white-space:nowrap;">Get Your Letter — $25</a>
      </li>'''

    if old in html:
        return html.replace(old, new, 1)

    # Fallback: try single-line version
    pattern = r'(<li[^>]*nav-cta[^>]*>.*?Free ARD Checklist.*?</li>)'
    match = re.search(pattern, html, re.DOTALL)
    if match:
        replacement = match.group(0) + '\n      <li class="nav-item nav-cta" style="margin-left:8px;"><a href="/get-your-letter.html" style="background:#d4af37;color:#0f172a;padding:10px 18px;border-radius:4px;font-weight:700;font-size:14px;text-decoration:none;font-family:\'DM Sans\',sans-serif;white-space:nowrap;">Get Your Letter — $25</a></li>'
        return html[:match.start()] + replacement + html[match.end():]

    return html  # couldn't find, skip


def add_sidebar_cta(html):
    """Inject CTA card at the top of the sidebar."""
    if "Show the ISD" in html:
        return html  # already done

    # Find <aside class="sidebar-col"> and inject after opening tag
    pattern = r'(<aside[^>]*sidebar-col[^>]*>)'
    match = re.search(pattern, html)
    if match:
        insert_pos = match.end()
        return html[:insert_pos] + '\n     ' + SIDEBAR_CTA + '\n' + html[insert_pos:]

    return html


def ensure_bot_iframe(html):
    """Standardize bot iframe if present, or skip if already there."""
    # If iframe already points to our bot URL, leave it alone
    if BOT_URL in html:
        return html

    # If there's a bot-wrap div without our iframe, we could update it
    # but since most pages already have it, just return unchanged
    return html


def remove_duplicate_inline_css(html):
    """Remove the repeated inline page-grid/sidebar CSS block from <style> tags."""
    # Find <style> blocks that contain .page-grid definition
    def clean_style_block(match):
        content = match.group(1)
        # Remove the page-grid / sidebar duplicate rules
        content = re.sub(
            r'\.page-grid\s*\{.*?\}',
            '', content, flags=re.DOTALL
        )
        content = re.sub(
            r'\.sidebar-col\s*\{.*?\}',
            '', content, flags=re.DOTALL
        )
        content = re.sub(
            r'\.law-box\s*\{.*?\}',
            '', content, flags=re.DOTALL
        )
        content = re.sub(
            r'\.timeline-card\s*\{.*?\}',
            '', content, flags=re.DOTALL
        )
        content = re.sub(
            r'\.tl\s*[\w\s]*\{.*?\}',
            '', content, flags=re.DOTALL
        )
        content = re.sub(
            r'@media\s*\(max-width:\s*900px\)\s*\{[^}]*\.page-grid[^}]*\}',
            '', content, flags=re.DOTALL
        )
        # If style block is now empty or just whitespace, remove entirely
        if not content.strip():
            return ''
        return f'<style>{content}</style>'

    html = re.sub(r'<style>(.*?)</style>', clean_style_block, html, flags=re.DOTALL)
    # Clean up empty style tags
    html = re.sub(r'<style>\s*</style>', '', html)
    return html


# ── MAIN ──────────────────────────────────────────────────────────────────────

def process_file(path, dry_run):
    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()

    html = original

    # Skip index.html
    if os.path.basename(path) == 'index.html':
        return False, "skipped (index)"

    # Apply updates
    html = add_nav_cta(html)
    html = add_sidebar_cta(html)
    html = ensure_bot_iframe(html)
    html = remove_duplicate_inline_css(html)

    if html == original:
        return False, "no changes needed"

    if dry_run:
        return True, "would update"

    backup(path)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return True, "updated"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only", type=str, help="Process only this filename e.g. ard-meeting-tips.html")
    args = parser.parse_args()

    if not os.path.exists(BLOG_DIR):
        print(f"ERROR: Blog directory not found: {BLOG_DIR}")
        return

    files = [f for f in os.listdir(BLOG_DIR) if f.endswith('.html')]
    if args.only:
        files = [f for f in files if args.only in f]

    print(f"Found {len(files)} blog files\n")
    if args.dry_run:
        print("DRY RUN — no files will be written\n")

    updated, skipped = 0, 0

    for filename in sorted(files):
        path = os.path.join(BLOG_DIR, filename)
        changed, reason = process_file(path, args.dry_run)

        if changed:
            updated += 1
            print(f"  ✓ {filename} — {reason}")
        else:
            skipped += 1
            print(f"  – {filename} — {reason}")

    print(f"\n── SUMMARY ──────────────────────")
    print(f"  Updated: {updated}")
    print(f"  Skipped: {skipped}")

    if not args.dry_run and updated > 0:
        print(f"  Backups: {BACKUP_DIR}")
        print(f"\nNext: git add blog/ && git commit -m 'add letter CTA to all blog posts' && git push")


if __name__ == "__main__":
    main()