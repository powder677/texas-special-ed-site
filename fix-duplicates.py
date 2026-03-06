import os
import re

# The exact text blocks we want to remove when they are NOT inside the new styled box
ORPHAN_TEXT = [
    "🚨 ARD Meeting in 7 Days? You Need This",
    "Stop going into ARD meetings unprepared. Get the exact scripts Texas advocates charge $200/hr to provide.",
    "⭐⭐⭐⭐⭐ 4.9/5 stars (327 Texas parents)",
    "✅ Email templates (copy & paste)",
    "✅ Response scripts for district pushback",
    "✅ 10-Day Recess Playbook",
    "✅ IEP Red Flag Analyzer",
    "✅ Meeting prep checklist",
    '"Used the eval request template—FIE scheduled in 48 hours!"',
    "- Maria, Round Rock ISD",
    "Get Instant Access — $47",
    "🔒 30-Day Money-Back Guarantee",
    "Get the ARD Toolkit — $47"
]

def clean_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if it doesn't look like it has the ARD ad at all
    if "ARD Meeting in 7 Days?" not in content:
        return False

    original_content = content

    # Use regex to find and remove exact strings wrapped in <p>, <li>, <div>, etc. 
    # ONLY if they are NOT part of the new beautifully styled HTML box.
    # The new box has specific inline styles like 'color: #dc3545;' or 'background-color: #f8f9fa;'
    
    for phrase in ORPHAN_TEXT:
        # Escape the phrase for regex, handling weird spaces or newlines
        escaped_phrase = re.escape(phrase).replace(r'\ ', r'\s+')
        
        # Look for this phrase wrapped in standard tags (p, div, span, li, center, strong, em, h1-h6)
        # But we ensure it DOES NOT have the inline styles we just added in our new box
        pattern = r'<([a-z1-6]+)(?![^>]*style="[^"]*background-color:\s*#f8f9fa|color:\s*#dc3545)[^>]*>\s*' + escaped_phrase + r'\s*<\/\1>'
        
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        # Also catch bare phrases just sitting there outside of tags, avoiding the styled box
        bare_pattern = r'(?<!>)\s*' + escaped_phrase + r'\s*(?!<)'
        # We only remove bare phrases if the whole file has more than one "ARD Meeting in 7 Days?"
        if content.count("ARD Meeting in 7 Days?") > 1:
            content = re.sub(bare_pattern, '', content, flags=re.IGNORECASE)

    # Clean up empty tags left behind (like empty <p></p> or <ul></ul>)
    content = re.sub(r'<p[^>]*>\s*<\/p>', '', content)
    content = re.sub(r'<ul[^>]*>\s*<\/ul>', '', content)
    content = re.sub(r'<div[^>]*>\s*<\/div>', '', content)
    content = re.sub(r'<center[^>]*>\s*<\/center>', '', content)

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def run_cleanup():
    updated_count = 0
    for root, dirs, files in os.walk('.'):
        # Skip certain directories if you want, like node_modules or .git
        if '.git' in root: continue
            
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                try:
                    if clean_file(file_path):
                        updated_count += 1
                        print(f"🧹 Cleaned up duplicates in: {file_path}")
                except Exception as e:
                    print(f"⚠️ Error cleaning {file_path}: {e}")

    print(f"\n✨ Finished! Successfully removed floating duplicates in {updated_count} files.")

if __name__ == "__main__":
    run_cleanup()