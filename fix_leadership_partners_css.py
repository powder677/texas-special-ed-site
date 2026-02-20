#!/usr/bin/env python3
"""
fix_leadership_partners_css.py
===============================
Injects missing CSS into all leadership-directory.html and partners.html
pages across every district folder.

FIXES:
  leadership-directory.html:
    - .info-box, .contact-bar (verification banner + phone bar)
    - table, thead, tbody styles (staff directory table)
    - .badge-ok / .badge-no (Verified / Not Found pills)
    - Full offer box CSS (.stacked-card, .btn-premium, .topic-tag, etc.)
    - Dropdown hover fix (display:none → display:block)

  partners.html:
    - .authority-header (dark hero section)
    - .featured-partner-hero + .ribbon + .sponsored-badge (ad slot)
    - .contact-table-section / .contact-grid (Who Do I Call box)
    - .directory-filters (category badge row)
    - .process-card / .process-grid (3-step cards)
    - .service-category / .category-featured (provider listings)
    - .trust-section (Why Partner CTA)
    - Fixes broken ../../contact-us/index.html links
    - Dropdown hover fix

USAGE:
  Dry run:
    python fix_leadership_partners_css.py --districts-dir "C:\\...\\districts" --dry-run

  Live run:
    python fix_leadership_partners_css.py --districts-dir "C:\\...\\districts"

  One page type only:
    python fix_leadership_partners_css.py --districts-dir "C:\\...\\districts" --page leadership
    python fix_leadership_partners_css.py --districts-dir "C:\\...\\districts" --page partners
"""

import re
import shutil
import argparse
from pathlib import Path


# ── LEADERSHIP CSS ─────────────────────────────────────────────────────────────

LEADERSHIP_CSS = """
  /* ── Info Box & Contact Bar ── */
  .info-box { background: #f0f9ff; border-left: 4px solid #2563eb; padding: 12px 18px; border-radius: 4px; font-size: 0.9rem; color: #1e40af; margin-bottom: 16px; }
  .contact-bar { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 14px 20px; margin-bottom: 24px; display: flex; gap: 30px; flex-wrap: wrap; font-size: 0.9rem; }
  .contact-bar p { margin: 0; color: #374151; }

  /* ── Staff Directory Table ── */
  table { width: 100%; border-collapse: collapse; margin: 20px 0 30px; font-size: 0.9rem; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; }
  thead { background: #0f172a; color: #fff; }
  thead th { padding: 12px 16px; text-align: left; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
  tbody tr { border-bottom: 1px solid #e2e8f0; }
  tbody tr:last-child { border-bottom: none; }
  tbody tr:hover { background: #f8fafc; }
  tbody td { padding: 14px 16px; vertical-align: top; line-height: 1.5; }

  /* ── Status Badges ── */
  .badge-ok { display: inline-block; background: #dcfce7; color: #166534; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 700; }
  .badge-no { display: inline-block; background: #fee2e2; color: #991b1b; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 700; }

  /* ── Offer Box CSS ── */
  .premium-offers-container { margin: 30px 0 35px; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; background: #f8fafc; }
  .offers-header-badge { background: #0f172a; color: #d4af37; text-align: center; padding: 8px 16px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.12em; }
  .premium-offers-header { text-align: center; padding: 20px 20px 8px; }
  .premium-offers-header h2 { font-size: 1.3rem; color: #0f172a; margin-bottom: 6px; margin-top: 0; }
  .premium-offers-header p { color: #64748b; font-size: 0.9rem; margin: 0; }
  .stacked-card { background: #fff; border-top: 1px solid #e2e8f0; padding: 20px 24px; }
  .card-inner { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
  .card-main-content { flex: 1; min-width: 200px; }
  .card-checkout-zone { min-width: 150px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; border-left: 1px solid #e2e8f0; padding-left: 20px; }
  .topic-tag { display: inline-block; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 3px 10px; border-radius: 4px; margin-bottom: 8px; }
  .tag-gold   { background: #fdf4e3; color: #8a6914; }
  .tag-blue   { background: #e8edf5; color: #002868; }
  .tag-red    { background: #fde8eb; color: #c8102e; }
  .tag-purple { background: #ede6f6; color: #5b3e96; }
  .tag-teal   { background: #e6f5f5; color: #0e7c7b; }
  .tag-slate  { background: #eef0f4; color: #475569; }
  .card-title   { font-size: 1.05rem; color: #0f172a; margin: 0 0 4px; }
  .card-tagline { font-size: 0.85rem; color: #c8102e; font-style: italic; font-weight: 600; margin-bottom: 8px; }
  .card-desc    { font-size: 0.87rem; color: #475569; line-height: 1.6; margin-bottom: 10px; }
  .card-bullets { list-style: none; padding: 0; margin: 0; }
  .card-bullets li { font-size: 0.82rem; color: #475569; padding: 3px 0 3px 18px; position: relative; }
  .card-bullets li::before { content: "✓"; position: absolute; left: 0; color: #0e7c7b; font-weight: 700; }
  .price-block  { text-align: center; }
  .price-label  { display: block; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; font-weight: 600; margin-bottom: 2px; }
  .price-amount { display: block; font-size: 1.5rem; font-weight: 700; color: #0f172a; }
  .btn-premium  { display: inline-block; background: #2563eb; color: #fff !important; padding: 10px 18px; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 0.85rem; transition: background 0.2s; white-space: nowrap; margin-top: 4px; }
  .btn-premium:hover { background: #1d4ed8; }
  .border-gold   { border-left: 4px solid #d4af37; }
  .border-blue   { border-left: 4px solid #2563eb; }
  .border-red    { border-left: 4px solid #ef4444; }
  .border-purple { border-left: 4px solid #5b3e96; }
  .border-teal   { border-left: 4px solid #0e7c7b; }
  .border-slate  { border-left: 4px solid #475569; }
"""

# ── PARTNERS CSS ───────────────────────────────────────────────────────────────

PARTNERS_CSS = """
  /* ── Authority Header ── */
  .authority-header { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: white; padding: 40px 0 30px; }
  .authority-header h1 { color: white; font-size: 2rem; margin-bottom: 10px; }
  .authority-subtitle { color: #94a3b8; font-size: 1rem; margin-bottom: 20px; }
  .district-quick-stats { display: flex; gap: 20px; flex-wrap: wrap; margin-top: 16px; }
  .stat-item { background: rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 20px; font-size: 0.85rem; color: #e2e8f0; display: flex; align-items: center; gap: 8px; }
  .stat-item a { color: #93c5fd; }

  /* ── Featured Partner Hero ── */
  .featured-partner-hero { position: relative; display: flex; gap: 24px; align-items: center; background: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 12px; padding: 28px; margin: 28px 0; flex-wrap: wrap; }
  .ribbon-wrapper { position: absolute; top: 0; right: 0; overflow: hidden; width: 80px; height: 80px; }
  .ribbon { background: #16a34a; color: white; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; padding: 4px 20px; transform: rotate(45deg) translate(14px, -4px); display: block; text-align: center; letter-spacing: 0.05em; }
  .sponsored-badge { position: absolute; top: 12px; left: 12px; background: #1d4ed8; color: white; font-size: 0.65rem; font-weight: 700; padding: 3px 10px; border-radius: 10px; text-transform: uppercase; letter-spacing: 0.08em; }
  .hero-logo-box { width: 80px; height: 80px; background: #e2e8f0; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #64748b; flex-shrink: 0; }
  .hero-content { flex: 1; min-width: 200px; }
  .hero-content h3 { color: #0f172a; font-size: 1.2rem; margin-bottom: 8px; }
  .hero-content p { color: #475569; font-size: 0.9rem; margin-bottom: 12px; }
  .hero-cta { display: inline-block; background: #16a34a; color: white !important; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 0.9rem; transition: background 0.2s; }
  .hero-cta:hover { background: #15803d; }

  /* ── Contact Table Section ── */
  .contact-table-section { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; margin: 24px 0; }
  .contact-table-header { background: #0f172a; color: #d4af37; padding: 12px 20px; font-weight: 700; font-size: 0.9rem; display: flex; align-items: center; }
  .contact-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
  .contact-item { padding: 16px 20px; border-right: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; }
  .contact-item:last-child { border-right: none; }
  .contact-role { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #94a3b8; margin-bottom: 4px; }
  .contact-name { font-size: 0.88rem; color: #1e293b; font-weight: 600; margin-bottom: 4px; min-height: 20px; }
  .contact-phone a { font-size: 0.85rem; color: #2563eb; text-decoration: none; }

  /* ── Directory Filters ── */
  .directory-filters { display: flex; gap: 10px; flex-wrap: wrap; margin: 20px 0; }
  .filter-badge { background: #f1f5f9; border: 1px solid #e2e8f0; color: #475569; padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: flex; align-items: center; gap: 6px; }

  /* ── Process Grid ── */
  .process-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-top: 16px; }
  .process-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; text-align: center; transition: all 0.2s; }
  .process-card:hover { border-color: #2563eb; transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.06); }
  .process-icon { font-size: 1.6rem; color: #2563eb; margin-bottom: 10px; }
  .process-card h4 { color: #0f172a; font-size: 0.95rem; margin-bottom: 6px; }

  /* ── Service Categories ── */
  .service-category { margin-bottom: 32px; }
  .category-header { display: flex; align-items: baseline; justify-content: space-between; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 16px; }
  .category-header h2 { font-size: 1.2rem; color: #0f172a; margin: 0; }
  .category-featured { display: flex; gap: 16px; align-items: center; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px 20px; position: relative; }
  .category-featured.ad-slot-available { border-style: dashed; }
  .cat-feat-logo { width: 48px; height: 48px; background: #e2e8f0; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #64748b; flex-shrink: 0; }

  /* ── Trust Section ── */
  .trust-section { background: linear-gradient(135deg, #0f172a, #1e3a8a); color: white; padding: 50px 20px; text-align: center; margin-top: 40px; }
  .trust-section h2 { color: white; }
  .trust-section p { color: rgba(255,255,255,0.8); }

  /* ── Offer Box CSS (shared) ── */
  .premium-offers-container { margin: 30px 0 35px; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; background: #f8fafc; }
  .offers-header-badge { background: #0f172a; color: #d4af37; text-align: center; padding: 8px 16px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.12em; }
  .premium-offers-header { text-align: center; padding: 20px 20px 8px; }
  .premium-offers-header h2 { font-size: 1.3rem; color: #0f172a; margin-bottom: 6px; margin-top: 0; }
  .stacked-card { background: #fff; border-top: 1px solid #e2e8f0; padding: 20px 24px; }
  .card-inner { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
  .card-main-content { flex: 1; min-width: 200px; }
  .card-checkout-zone { min-width: 150px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; border-left: 1px solid #e2e8f0; padding-left: 20px; }
  .topic-tag { display: inline-block; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 3px 10px; border-radius: 4px; margin-bottom: 8px; }
  .tag-gold   { background: #fdf4e3; color: #8a6914; }
  .tag-blue   { background: #e8edf5; color: #002868; }
  .tag-red    { background: #fde8eb; color: #c8102e; }
  .tag-purple { background: #ede6f6; color: #5b3e96; }
  .tag-teal   { background: #e6f5f5; color: #0e7c7b; }
  .tag-slate  { background: #eef0f4; color: #475569; }
  .card-title   { font-size: 1.05rem; color: #0f172a; margin: 0 0 4px; }
  .card-tagline { font-size: 0.85rem; color: #c8102e; font-style: italic; font-weight: 600; margin-bottom: 8px; }
  .card-desc    { font-size: 0.87rem; color: #475569; line-height: 1.6; margin-bottom: 10px; }
  .card-bullets { list-style: none; padding: 0; margin: 0; }
  .card-bullets li { font-size: 0.82rem; color: #475569; padding: 3px 0 3px 18px; position: relative; }
  .card-bullets li::before { content: "✓"; position: absolute; left: 0; color: #0e7c7b; font-weight: 700; }
  .price-block  { text-align: center; }
  .price-label  { display: block; font-size: 0.65rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; margin-bottom: 2px; }
  .price-amount { display: block; font-size: 1.5rem; font-weight: 700; color: #0f172a; }
  .btn-premium  { display: inline-block; background: #2563eb; color: #fff !important; padding: 10px 18px; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 0.85rem; transition: background 0.2s; white-space: nowrap; margin-top: 4px; }
  .btn-premium:hover { background: #1d4ed8; }
  .border-gold   { border-left: 4px solid #d4af37; }
  .border-blue   { border-left: 4px solid #2563eb; }
  .border-red    { border-left: 4px solid #ef4444; }
  .border-purple { border-left: 4px solid #5b3e96; }
  .border-teal   { border-left: 4px solid #0e7c7b; }
  .border-slate  { border-left: 4px solid #475569; }
"""

# ── DETECTION: already fixed? ──────────────────────────────────────────────────

LEADERSHIP_MARKER = ".badge-ok {"
PARTNERS_MARKER   = ".authority-header {"


# ── FIX FUNCTIONS ──────────────────────────────────────────────────────────────

def fix_dropdown_hover(content: str) -> str:
    content = re.sub(
        r'(\.dropdown:hover\s+\.dropdown-menu\s*\{[^}]*?)display:\s*none',
        r'\1display: block', content
    )
    content = re.sub(
        r'(\.dropdown\.active\s+\.dropdown-menu\s*\{[^}]*?)display:\s*none',
        r'\1display: block', content
    )
    return content


def fix_leadership(content: str) -> tuple[str, list[str]]:
    changes = []

    # Skip if already fixed
    if LEADERSHIP_MARKER in content:
        return content, []

    # Inject CSS
    if "</style>" in content:
        content = content.replace("</style>", LEADERSHIP_CSS + "\n</style>", 1)
        changes.append("injected table, badge-ok/no, info-box, contact-bar, offer box CSS")

    # Fix dropdown
    fixed = fix_dropdown_hover(content)
    if fixed != content:
        changes.append("fixed dropdown hover display:block")
        content = fixed

    # Fix back link: resources.html → index.html
    if 'href="resources.html"' in content:
        content = content.replace('href="resources.html"', 'href="index.html"')
        changes.append("fixed back link: resources.html → index.html")

    # Strip any lingering markdown code fences from Vertex
    if "```" in content:
        content = re.sub(r'```html\s*\n?', '', content)
        content = re.sub(r'\n?```\s*\n', '\n', content)
        content = content.replace('```', '')
        changes.append("removed markdown code fences")

    return content, changes


def fix_partners(content: str) -> tuple[str, list[str]]:
    changes = []

    # Skip if already fixed
    if PARTNERS_MARKER in content:
        return content, []

    # Inject CSS
    if "</style>" in content:
        content = content.replace("</style>", PARTNERS_CSS + "\n</style>", 1)
        changes.append("injected full partners component CSS")

    # Fix dropdown
    fixed = fix_dropdown_hover(content)
    if fixed != content:
        changes.append("fixed dropdown hover display:block")
        content = fixed

    # Fix broken relative contact-us links
    if "../../contact-us/index.html" in content:
        content = content.replace("../../contact-us/index.html", "/contact/index.html")
        changes.append("fixed ../../contact-us links → /contact/index.html")

    # Fix any other deep relative paths
    if "../contact-us/index.html" in content:
        content = content.replace("../contact-us/index.html", "/contact/index.html")
        changes.append("fixed ../contact-us links → /contact/index.html")

    return content, changes


# ── MAIN ───────────────────────────────────────────────────────────────────────

def run(districts_dir: str, dry_run: bool, no_backup: bool, page_filter: str):
    root = Path(districts_dir).resolve()

    if not root.exists():
        print(f"\nERROR: Directory not found: {root}\n")
        return

    print(f"\n{'='*64}")
    print(f"  Leadership & Partners CSS Fixer")
    print(f'{"="*64}')
    print(f"  Root   : {root}")
    print(f"  Mode   : {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"  Filter : {page_filter}")
    print(f'{"="*64}\n')

    # Collect target files
    targets = []
    if page_filter in ("all", "leadership"):
        targets += [(f, "leadership") for f in sorted(root.rglob("leadership-directory.html"))]
    if page_filter in ("all", "partners"):
        targets += [(f, "partners")   for f in sorted(root.rglob("partners.html"))]

    if not targets:
        print("  No matching files found.\n")
        return

    print(f"  Found {len(targets)} file(s) to process...\n")

    fixed = skipped = errors = 0

    for f, page_type in targets:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"  ERROR reading {f.name}: {e}")
            errors += 1
            continue

        if page_type == "leadership":
            new_content, changes = fix_leadership(content)
        else:
            new_content, changes = fix_partners(content)

        if not changes:
            skipped += 1
            continue

        rel = f.relative_to(root)
        print(f"  {rel}")
        for c in changes:
            print(f"    ✓ {c}")

        fixed += 1

        if dry_run:
            continue

        try:
            if not no_backup:
                shutil.copy2(f, f.with_suffix(".html.bak"))
            f.write_text(new_content, encoding="utf-8")
        except Exception as e:
            print(f"    ✗ Write failed: {e}")
            errors += 1

    print(f'\n{"="*64}')
    print(f"  SUMMARY")
    print(f'{"="*64}')
    print(f"  Files processed : {len(targets)}")
    print(f"  Fixed           : {fixed}")
    print(f"  Already OK      : {skipped}")
    if errors:
        print(f"  Errors          : {errors}")
    print()
    if dry_run:
        print("  ℹ️  Dry run. Run without --dry-run to apply.")
    elif fixed:
        print(f"  ✅ Done. {fixed} files updated.")
        if not no_backup:
            print("  💾 Originals backed up as .html.bak")
    print(f'{"="*64}\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fix missing CSS in leadership-directory.html and partners.html across all districts."
    )
    parser.add_argument("--districts-dir", required=True,
                        help="Path to your districts/ folder")
    parser.add_argument("--dry-run",   action="store_true",
                        help="Preview changes without writing files")
    parser.add_argument("--no-backup", action="store_true",
                        help="Skip .html.bak backup files")
    parser.add_argument("--page",      default="all",
                        choices=["all", "leadership", "partners"],
                        help="Which page type to fix (default: all)")
    args = parser.parse_args()
    run(args.districts_dir, args.dry_run, args.no_backup, args.page)