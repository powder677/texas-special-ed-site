"""
check_spanish_pages.py
----------------------
Scans all como-solicitar-una-evaluacion-fie-en-*.html pages and reports
formatting issues. No API needed.

Issues checked:
  1. Truncated inline-cta block (cut off mid-tag)
  2. Quick Answer box still in English
  3. Silo nav links still in English
  4. FAQ schema still in English
  5. Sidebar card still in English ("Show the ISD")
  6. h1 not updated to Spanish
  7. lang attribute still "en"
  8. Missing Spanish section entirely

Run from your site root:
    python check_spanish_pages.py

Outputs a summary + a detailed report saved to: spanish_page_issues.txt
"""

import os
import glob
import re

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
DISTRICTS_DIR = os.path.join(SCRIPT_DIR, "districts")
REPORT_FILE   = os.path.join(SCRIPT_DIR, "spanish_page_issues.txt")

CHECKS = [
    {
        "id":      "truncated_cta",
        "label":   "❌ Truncated inline-cta block",
        "detect":  lambda h: re.search(r'class="inline-cta"[^>]*style="[^"]*border-radius:\s*\d+\s*\n', h) is not None
                             or ('inline-cta' in h and '</div>\n</section>' not in h and 'Generar mi carta' not in h),
        "fix":     "The CTA block was cut off when the Spanish content was injected. Needs the full CTA re-added."
    },
    {
        "id":      "english_quick_answer",
        "label":   "❌ Quick Answer box in English",
        "detect":  lambda h: 'What is an FIE in' in h and 'Respuesta Rápida' in h,
        "fix":     "The Quick Answer paragraph text was not translated."
    },
    {
        "id":      "english_silo_nav",
        "label":   "❌ Silo nav in English",
        "detect":  lambda h: 'What Is an FIE?' in h,
        "fix":     "Silo nav link text still says 'What Is an FIE?' instead of Spanish."
    },
    {
        "id":      "english_faq_schema",
        "label":   "❌ FAQ schema in English",
        "detect":  lambda h: '"What is an FIE' in h and 'application/ld+json' in h,
        "fix":     "The FAQPage JSON-LD schema still contains English questions."
    },
    {
        "id":      "english_sidebar_card",
        "label":   "❌ Sidebar card in English",
        "detect":  lambda h: 'Show the ISD' in h,
        "fix":     "Sidebar CTA card still says 'Show the ISD You Mean Business'."
    },
    {
        "id":      "english_h1",
        "label":   "❌ H1 not translated",
        "detect":  lambda h: re.search(r'<h1>What Is an FIE', h) is not None,
        "fix":     "The <h1> tag was not updated to Spanish."
    },
    {
        "id":      "wrong_lang",
        "label":   "❌ lang attribute still English",
        "detect":  lambda h: '<html lang="en">' in h,
        "fix":     "The <html lang> attribute was not changed to 'es'."
    },
    {
        "id":      "missing_spanish_section",
        "label":   "❌ No Spanish section found",
        "detect":  lambda h: 'id="seccion-espanol"' not in h and 'Cómo solicitar' not in h,
        "fix":     "The Spanish content section is missing entirely."
    },
    {
        "id":      "english_letter_link",
        "label":   "⚠️  Letter CTA links to English page",
        "detect":  lambda h: '/resources/Iep-letter' in h or ('iep-letter"' in h and 'iep-letter-spanish' not in h),
        "fix":     "Some CTA links still point to the English letter page instead of /resources/iep-letter-spanish/."
    },
]

def check_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    issues = []
    for check in CHECKS:
        try:
            if check["detect"](html):
                issues.append(check)
        except Exception as e:
            issues.append({"id": "check_error", "label": f"⚠️  Check error: {e}", "fix": ""})

    return issues


def main():
    files = sorted(set(
        glob.glob(os.path.join(DISTRICTS_DIR, "**", "como-solicitar-una-evaluacion-fie-en-*.html"), recursive=True)
    ))
    total = len(files)

    print(f"Checking {total} Spanish FIE pages...\n")

    issue_counts  = {c["id"]: 0 for c in CHECKS}
    perfect_pages = []
    problem_pages = []

    report_lines = [f"Spanish FIE Page Audit — {total} pages checked\n", "=" * 60 + "\n"]

    for filepath in files:
        slug   = os.path.basename(os.path.dirname(filepath))
        fname  = os.path.basename(filepath)
        issues = check_file(filepath)

        if not issues:
            perfect_pages.append(slug)
            print(f"  ✅  {slug}")
        else:
            problem_pages.append((slug, issues))
            labels = ", ".join(c["id"] for c in issues)
            print(f"  ❌  {slug}  [{labels}]")
            report_lines.append(f"\n{slug}/{fname}")
            for issue in issues:
                report_lines.append(f"  {issue['label']}")
                report_lines.append(f"     → {issue['fix']}")
            for c in issues:
                issue_counts[c["id"]] = issue_counts.get(c["id"], 0) + 1

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total pages checked : {total}
  ✅  Clean pages     : {len(perfect_pages)}
  ❌  Pages with issues: {len(problem_pages)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue breakdown:""")

    for check in CHECKS:
        count = issue_counts.get(check["id"], 0)
        if count:
            print(f"  {check['label']:<45} {count} pages")

    # ── Write report file ─────────────────────────────────────────────────────
    report_lines.append(f"\n{'='*60}")
    report_lines.append(f"SUMMARY: {len(perfect_pages)} clean, {len(problem_pages)} with issues\n")
    for check in CHECKS:
        count = issue_counts.get(check["id"], 0)
        if count:
            report_lines.append(f"  {check['label']}: {count} pages")

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\n📄 Full report saved to: spanish_page_issues.txt")
    print(f"   Share that file and I can write a targeted fix script for each issue.\n")


if __name__ == "__main__":
    main()