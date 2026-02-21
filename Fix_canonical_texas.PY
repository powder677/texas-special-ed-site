#!/usr/bin/env python3
# texasspecialed.com - Canonical Fix Script v2
# Run from your site root (texas-special-ed-site folder)
# python Fix_canonical_texas_v2.py
#
# Pass your CSV path as argument if needed:
# python Fix_canonical_texas_v2.py "C:\path\to\your.csv"

import re, os, glob, sys
from datetime import datetime

BACKUP = f"_canonical_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def rread(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def wwrite(path, text):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

# ─────────────────────────────────────────────────────────────────────────────
# CSV PARSER - handles UTF-16, tab-delimited, quoted headers
# ─────────────────────────────────────────────────────────────────────────────
def parse_screaming_frog_csv(csv_path):
    for encoding in ("utf-16", "utf-8-sig", "utf-8", "latin-1"):
        try:
            with open(csv_path, encoding=encoding) as f:
                content = f.read()

            lines = [l for l in content.strip().split("\n") if l.strip()]
            if not lines:
                continue

            # Try tab split first, then comma
            for sep in ("\t", ","):
                headers = [h.strip().strip('"') for h in lines[0].split(sep)]
                if len(headers) > 3:
                    break

            rows = []
            for line in lines[1:]:
                vals = [v.strip().strip('"') for v in line.split(sep)]
                if len(vals) >= len(headers):
                    rows.append(dict(zip(headers, vals)))

            if rows and ("URL" in rows[0] or "Address" in rows[0]):
                # Normalize "Address" -> "URL" (Screaming Frog uses Address)
                if "Address" in rows[0] and "URL" not in rows[0]:
                    rows = [{("URL" if k == "Address" else k): v for k, v in r.items()} for r in rows]
                print(f"  Parsed {len(rows)} rows (encoding: {encoding}, sep: {'tab' if sep == chr(9) else 'comma'})")
                return rows

        except Exception as e:
            continue

    return []


# ─────────────────────────────────────────────────────────────────────────────
# FIND THE CSV
# ─────────────────────────────────────────────────────────────────────────────
def find_csv():
    # Check command line argument first
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.exists(path):
            return path
        print(f"  ⚠️  Argument path not found: {path}")

    # Search current dir and subdirs
    candidates = glob.glob("*.csv") + glob.glob("**/*.csv", recursive=True)
    # Prefer canonical-related CSVs
    preferred = [f for f in candidates if any(x in f.lower() for x in ["canonical", "texas", "screaming"])]
    if preferred:
        return preferred[0]
    if candidates:
        return candidates[0]
    return None


# ─────────────────────────────────────────────────────────────────────────────
# GENERATE REDIRECT RULES
# ─────────────────────────────────────────────────────────────────────────────
def generate_redirect_rules():
    print("\n── Generating redirect rules ────────────────────────────────")

    # Vercel
    vercel = '''{
  "redirects": [
    {
      "source": "/:path*",
      "has": [
        {
          "type": "host",
          "value": "www.texasspecialed.com"
        }
      ],
      "destination": "https://texasspecialed.com/:path*",
      "permanent": true
    }
  ]
}
'''
    wwrite("fix_www_vercel.json", vercel)
    print("  ✅ fix_www_vercel.json  (merge into vercel.json)")

    # Netlify
    netlify = "https://www.texasspecialed.com/* https://texasspecialed.com/:splat 301!\n"
    wwrite("fix_www_netlify_redirects.txt", netlify)
    print("  ✅ fix_www_netlify_redirects.txt")

    # htaccess
    htaccess = """RewriteEngine On
RewriteCond %{HTTP_HOST} ^www\\.texasspecialed\\.com [NC]
RewriteRule ^(.*)$ https://texasspecialed.com/$1 [R=301,L]
"""
    wwrite("fix_www_redirect.htaccess", htaccess)
    print("  ✅ fix_www_redirect.htaccess")


# ─────────────────────────────────────────────────────────────────────────────
# FIX CANONICAL TAGS IN LOCAL HTML FILES
# ─────────────────────────────────────────────────────────────────────────────
def fix_canonical_tags():
    print("\n── Fixing canonical tags in local HTML files ───────────────")
    import shutil

    html_files = glob.glob("**/*.html", recursive=True) + glob.glob("**/*.htm", recursive=True)
    html_files = [f for f in html_files if not any(
        x in f for x in ["node_modules", ".next", "build", ".git", "dist", "_backup", "_canonical_backup"]
    )]

    fixed = 0
    for filepath in sorted(html_files):
        original = rread(filepath)
        content = original

        # Fix www in canonical
        content = re.sub(
            r'<link rel="canonical" href="https://www\.texasspecialed\.com([^"]*)"',
            r'<link rel="canonical" href="https://texasspecialed.com\1"',
            content
        )
        # Fix www in og:url
        content = re.sub(
            r'<meta property="og:url" content="https://www\.texasspecialed\.com([^"]*)"',
            r'<meta property="og:url" content="https://texasspecialed.com\1"',
            content
        )

        if content != original:
            os.makedirs(BACKUP, exist_ok=True)
            dest = os.path.join(BACKUP, filepath.replace(":", "_"))
            os.makedirs(os.path.dirname(dest) if os.path.dirname(dest) else BACKUP, exist_ok=True)
            shutil.copy2(filepath, dest)
            wwrite(filepath, content)
            fixed += 1
            print(f"  ✅ {filepath}")

    if fixed == 0:
        print("  No HTML files with www canonicals found")
        print("  (Canonical fix may be in your framework config, not HTML files)")
    else:
        print(f"\n  Fixed {fixed} files")


# ─────────────────────────────────────────────────────────────────────────────
# GENERATE URL REPORT
# ─────────────────────────────────────────────────────────────────────────────
def generate_url_report(csv_path):
    print("\n── Generating URL report ────────────────────────────────────")

    rows = parse_screaming_frog_csv(csv_path)
    if not rows:
        print(f"  Could not parse: {csv_path}")
        print("  Headers in file:", end=" ")
        try:
            with open(csv_path, encoding="utf-16") as f:
                print(f.readline()[:200])
        except:
            print("(unreadable)")
        return

    all_urls     = [r["URL"] for r in rows]
    canonical    = [r.get("Canonical URL", "") for r in rows]

    district_pages = [r for r in rows if r["URL"].count("/") == 4]
    subpages       = [r for r in rows if r["URL"].count("/") == 5]

    report = f"""texasspecialed.com - Canonical Fix Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
==========================================

DIAGNOSIS
---------
Total non-indexable pages:  {len(rows)}
Root cause:                 www vs non-www canonical mismatch (100%)

Google crawls:    https://www.texasspecialed.com/...
Canonical points: https://texasspecialed.com/...

Fix: one redirect rule (www -> non-www 301)
See: fix_www_vercel.json  (already generated)

BREAKDOWN
---------
District index pages:  {len(district_pages)}
District subpages:     {len(subpages)}
  - /evaluation-child-find  (~112 pages)
  - /ard-process-guide      (~112 pages)

AFTER FIX — CHECKLIST
----------------------
[ ] Merge fix_www_vercel.json redirects into your vercel.json
[ ] git commit + push (Vercel auto-deploys)
[ ] Verify: https://www.texasspecialed.com/ redirects to non-www
[ ] Google Search Console > Sitemaps > Resubmit
[ ] GSC > URL Inspection > Request indexing on 10 key pages
[ ] Rerun Screaming Frog in 2-4 weeks

ALL {len(rows)} AFFECTED URLs
{'='*50}
"""
    for url, can in zip(all_urls, canonical):
        report += f"{url}\n  -> {can}\n"

    wwrite("texasspecialed_affected_urls.txt", report)
    print(f"  ✅ texasspecialed_affected_urls.txt ({len(rows)} URLs)")

    # Priority list — first 20 districts for GSC manual indexing
    priority = [r["URL"] for r in district_pages[:20]]
    wwrite("texasspecialed_priority_reindex.txt", "\n".join(priority))
    print(f"  ✅ texasspecialed_priority_reindex.txt (top 20 pages for GSC)")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("texasspecialed.com - Canonical Fix Script v2")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Running from: {os.getcwd()}")
    print("=" * 60)

    generate_redirect_rules()
    fix_canonical_tags()

    csv_path = find_csv()
    if csv_path:
        print(f"\n  Found CSV: {csv_path}")
        generate_url_report(csv_path)
    else:
        print("\n  No CSV found — skipping URL report")
        print("  Pass path as argument: python Fix_canonical_texas_v2.py path/to/file.csv")

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    print("""
NEXT STEPS:
  1. Open fix_www_vercel.json
  2. Merge its "redirects" block into your vercel.json
  3. git add vercel.json
  4. git commit -m "Fix: www to non-www redirect"
  5. git push  (Vercel auto-deploys)
  6. Test: visit https://www.texasspecialed.com in browser
     Should redirect to https://texasspecialed.com
""")

if __name__ == "__main__":
    main()