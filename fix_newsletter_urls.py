#!/usr/bin/env python3
"""
Newsletter Popup Diagnostic Script
Run this from your texas-special-ed-site directory:
  python diagnose_newsletter.py
"""

import os
import re
import glob
import json
import urllib.request
import urllib.error

CLOUD_RUN_URL = "https://ard-intake-bot-831148457361.us-central1.run.app"
ENDPOINT = f"{CLOUD_RUN_URL}/api/newsletter-signup"

# ─────────────────────────────────────────────
# STEP 1: Check HTML files for URL issues
# ─────────────────────────────────────────────
def check_html_files():
    print("\n" + "="*60)
    print("STEP 1: Scanning HTML files for URL issues")
    print("="*60)

    html_files = glob.glob("**/*.html", recursive=True)
    if not html_files:
        html_files = glob.glob("*.html")

    if not html_files:
        print("❌ No HTML files found. Are you in the right directory?")
        print(f"   Current directory: {os.getcwd()}")
        return False

    print(f"✅ Found {len(html_files)} HTML files")

    files_with_popup = 0
    files_with_bad_url = 0
    files_with_good_url = 0
    bad_url_examples = []

    for filepath in html_files:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if "newsletter" not in content.lower():
                continue

            files_with_popup += 1

            # Check for malformed URLs (common issues from the deploy script)
            bad_patterns = [
                r'https://https://',
                r'http://https://',
                r'https://ard-intake-bot.*https://',
                r'newsletter-signup.*newsletter-signup',  # doubled endpoint
                r'run\.app/api/newsletter-signupapi',    # missing slash
                r'run\.appapi',                           # missing slash before api
            ]

            found_bad = False
            for pattern in bad_patterns:
                if re.search(pattern, content):
                    files_with_bad_url += 1
                    found_bad = True
                    if len(bad_url_examples) < 3:
                        # Extract the bad URL for display
                        match = re.search(r'(https?://[^\s"\']+newsletter[^\s"\']*)', content)
                        if match:
                            bad_url_examples.append((filepath, match.group(1)[:80]))
                    break

            if not found_bad:
                # Check if the correct URL is present
                if CLOUD_RUN_URL in content and "newsletter-signup" in content:
                    files_with_good_url += 1
                elif "newsletter-signup" in content:
                    # Has endpoint reference but check the URL
                    match = re.search(r'fetch\(["\']([^"\']+newsletter[^"\']*)["\']', content)
                    if match:
                        url = match.group(1)
                        if url != ENDPOINT:
                            files_with_bad_url += 1
                            if len(bad_url_examples) < 3:
                                bad_url_examples.append((filepath, url[:80]))

        except Exception as e:
            pass

    print(f"\n📋 Results:")
    print(f"   Files with newsletter popup : {files_with_popup}")
    print(f"   Files with ✅ correct URL   : {files_with_good_url}")
    print(f"   Files with ❌ malformed URL : {files_with_bad_url}")

    if bad_url_examples:
        print(f"\n⚠️  Example malformed URLs found:")
        for filepath, url in bad_url_examples:
            print(f"   File: {filepath}")
            print(f"   URL:  {url}")

    if files_with_bad_url > 0:
        print(f"\n🔧 ACTION NEEDED: Run fix_newsletter_urls.py to fix {files_with_bad_url} files")
        return False
    elif files_with_popup == 0:
        print("\n❌ No popup code found in any HTML files — popup may not be deployed yet")
        return False
    else:
        print("\n✅ URLs look correct in HTML files")
        return True

# ─────────────────────────────────────────────
# STEP 2: Test Cloud Run endpoint directly
# ─────────────────────────────────────────────
def test_cloud_run_endpoint():
    print("\n" + "="*60)
    print("STEP 2: Testing Cloud Run endpoint directly")
    print("="*60)
    print(f"   Endpoint: {ENDPOINT}")

    # Test 1: Check if Cloud Run is reachable at all
    try:
        req = urllib.request.Request(
            CLOUD_RUN_URL,
            headers={"User-Agent": "DiagnosticScript/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"✅ Cloud Run is reachable (status {resp.status})")
    except urllib.error.HTTPError as e:
        if e.code < 500:
            print(f"✅ Cloud Run is reachable (status {e.code})")
        else:
            print(f"❌ Cloud Run returned server error: {e.code}")
            return False
    except urllib.error.URLError as e:
        print(f"❌ Cannot reach Cloud Run: {e.reason}")
        print("   → Check your internet connection or if Cloud Run service is running")
        return False

    # Test 2: POST to newsletter endpoint
    print(f"\n   Sending test POST to {ENDPOINT}...")
    test_payload = json.dumps({
        "email": "diagnostic_test@test.com",
        "source": "diagnostic_script",
        "district": "test"
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            ENDPOINT,
            data=test_payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "DiagnosticScript/1.0",
                "Origin": "https://texasspecialed.com"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            print(f"✅ Endpoint responded: status {resp.status}")
            print(f"   Response: {body[:200]}")
            return True

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if hasattr(e, 'read') else ""
        print(f"❌ Endpoint error: HTTP {e.code}")
        print(f"   Response: {body[:300]}")

        if e.code == 404:
            print("\n   🔧 FIX: The /api/newsletter-signup endpoint doesn't exist on Cloud Run")
            print("      → Make sure newsletter_signup_endpoint.py code is added to app.py")
            print("      → Re-deploy to Cloud Run with: gcloud run deploy")
        elif e.code == 405:
            print("\n   🔧 FIX: Method not allowed — endpoint may not accept POST requests")
        elif e.code == 500:
            print("\n   🔧 FIX: Server error — check Cloud Run logs:")
            print("      gcloud logging read 'resource.type=cloud_run_revision' --limit=20")
        return False

    except urllib.error.URLError as e:
        print(f"❌ Network error reaching endpoint: {e.reason}")
        return False

# ─────────────────────────────────────────────
# STEP 3: Check CORS headers
# ─────────────────────────────────────────────
def check_cors():
    print("\n" + "="*60)
    print("STEP 3: Checking CORS headers")
    print("="*60)
    print("   (CORS errors are a common cause of silent form failures)")

    try:
        req = urllib.request.Request(
            ENDPOINT,
            headers={
                "Origin": "https://texasspecialed.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
            method="OPTIONS"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            headers = dict(resp.headers)
            acao = headers.get("Access-Control-Allow-Origin", "NOT SET")
            acam = headers.get("Access-Control-Allow-Methods", "NOT SET")
            print(f"   Access-Control-Allow-Origin  : {acao}")
            print(f"   Access-Control-Allow-Methods : {acam}")

            if acao in ("*", "https://texasspecialed.com"):
                print("✅ CORS is configured correctly")
            else:
                print("❌ CORS may be blocking requests from texasspecialed.com")
                print("   🔧 FIX: Add to your Flask app.py:")
                print('      from flask_cors import CORS')
                print('      CORS(app, origins=["https://texasspecialed.com", "*"])')

    except urllib.error.HTTPError as e:
        if e.code == 405:
            print("⚠️  OPTIONS method not supported (CORS preflight may fail)")
            print("   🔧 Add flask-cors to your Flask app")
        else:
            print(f"⚠️  Could not check CORS (HTTP {e.code}) — manual check recommended")
    except Exception as e:
        print(f"⚠️  Could not check CORS: {e}")

# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────
def print_summary(html_ok, endpoint_ok):
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)

    issues = []
    if not html_ok:
        issues.append("❌ Malformed URLs in HTML files → run fix_newsletter_urls.py")
    if not endpoint_ok:
        issues.append("❌ Cloud Run endpoint not responding → check app.py + redeploy")

    if not issues:
        print("✅ Everything looks good! Try submitting the form again.")
        print("   If it still fails, open browser DevTools (F12) → Network tab")
        print("   and watch for the failed request when you submit.")
    else:
        print("Issues found:")
        for issue in issues:
            print(f"  {issue}")

        print("\n📋 Recommended fix order:")
        if not html_ok:
            print("  1. python fix_newsletter_urls.py")
            print("  2. Open an HTML file, check the fetch URL looks like:")
            print(f"     {ENDPOINT}")
        if not endpoint_ok:
            print("  3. Verify newsletter endpoint is in app.py")
            print("  4. gcloud run deploy ard-intake-bot --region us-central1")
        print("  5. git add . && git commit -m 'Fix newsletter URLs' && git push")

if __name__ == "__main__":
    print("🔍 Texas Special Ed — Newsletter Popup Diagnostic")
    print(f"   Running from: {os.getcwd()}")

    html_ok = check_html_files()
    endpoint_ok = test_cloud_run_endpoint()
    check_cors()
    print_summary(html_ok, endpoint_ok)