# Update Newsletter Popup to Use Cloud Run URL
# This script updates all HTML files to point to your Cloud Run backend

import os
import re

PROJECT_PATH = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site"
CLOUD_RUN_URL = "https://ard-intake-bot-831148457361.us-central1.run.app"

# Backup folder
BACKUP_FOLDER = os.path.join(PROJECT_PATH, "_backups_cloud_run_update")

def update_html_file(filepath):
    """Update fetch URL in HTML file to point to Cloud Run"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if this file has the newsletter popup
    if 'newsletterPopup' not in content:
        return "SKIP", "No newsletter popup found"
    
    # Check if already updated
    if CLOUD_RUN_URL in content:
        return "SKIP", "Already updated"
    
    # Create backup
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)
    
    rel_path = os.path.relpath(filepath, PROJECT_PATH)
    backup_path = os.path.join(BACKUP_FOLDER, rel_path)
    backup_dir = os.path.dirname(backup_path)
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    import shutil
    shutil.copy2(filepath, backup_path)
    
    # Replace the fetch URL
    # OLD: fetch('/api/newsletter-signup',
    # NEW: fetch('https://ard-intake-bot-831148457361.us-central1.run.app/api/newsletter-signup',
    
    old_pattern = r"fetch\s*\(\s*['\"]\/api\/newsletter-signup['\"]"
    new_url = f"fetch('{CLOUD_RUN_URL}/api/newsletter-signup'"
    
    content_updated = re.sub(old_pattern, new_url, content)
    
    if content_updated == content:
        return "SKIP", "No fetch URL found to update"
    
    # Write updated content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_updated)
    
    return "SUCCESS", "Updated Cloud Run URL"

def main():
    print("=" * 80)
    print("UPDATING NEWSLETTER POPUP TO USE CLOUD RUN")
    print("=" * 80)
    print(f"\nProject: {PROJECT_PATH}")
    print(f"Cloud Run URL: {CLOUD_RUN_URL}")
    print(f"Backup folder: {BACKUP_FOLDER}")
    
    # Find all HTML files
    html_files = []
    for root, dirs, files in os.walk(PROJECT_PATH):
        if '_backups_' in root:
            continue
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print(f"\nFound {len(html_files)} HTML files")
    print("\nUpdating files...\n")
    
    results = {"SUCCESS": [], "SKIP": []}
    
    for i, filepath in enumerate(html_files, 1):
        rel_path = os.path.relpath(filepath, PROJECT_PATH)
        status, message = update_html_file(filepath)
        
        results[status].append((rel_path, message))
        
        if status == "SUCCESS":
            print(f"[{i}/{len(html_files)}] ✓ {rel_path}")
        else:
            print(f"[{i}/{len(html_files)}] ⊘ {rel_path} - {message}")
    
    print("\n" + "=" * 80)
    print("UPDATE SUMMARY")
    print("=" * 80)
    print(f"\n✓ Successfully updated: {len(results['SUCCESS'])} files")
    print(f"⊘ Skipped: {len(results['SKIP'])} files")
    
    if results['SUCCESS']:
        print("\nSUCCESSFULLY UPDATED FILES:")
        for rel_path, message in results['SUCCESS'][:10]:
            print(f"  • {rel_path}")
        if len(results['SUCCESS']) > 10:
            print(f"  ... and {len(results['SUCCESS']) - 10} more")
    
    print(f"\n💾 Backups saved to: {BACKUP_FOLDER}")
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\n1. Test locally: Open any HTML file in browser")
    print("2. Wait 10 seconds for popup")
    print("3. Submit email - should work now!")
    print("4. Deploy to Vercel (push to GitHub)")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    if not os.path.exists(PROJECT_PATH):
        print("\nERROR: Project path not found!")
        print(PROJECT_PATH)
    else:
        main()