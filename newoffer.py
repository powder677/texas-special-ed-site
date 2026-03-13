#!/usr/bin/env python3
"""
Comprehensive ARD Offer Replacement Script
Finds and replaces ALL variations of ARD scan offers with the standardized version
"""

import re
import sys
from pathlib import Path

# The new standardized ARD scan offer (links to index page)
NEW_ARD_OFFER = '''<!-- AI Tool Section -->
<div style="
  background: linear-gradient(145deg, #0f172a 0%, #1e3a8a 100%);
  border-radius: 16px;
  box-shadow: 0 12px 35px rgba(30, 58, 138, 0.25);
  padding: 28px 24px 24px;
  border: 1px solid #2a4382;
  text-align: center;
  margin: 2.5rem 0;
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
<a href="/" style="
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
  ">Run My Free ARD Scan →</a>
<p style="
    font-size: 11px;
    color: #64748b;
    margin: 12px 0 0;
    font-family: 'Source Sans 3', sans-serif;
  ">🔒 Free  ·  No account needed</p>
</div>'''


def replace_ard_offers(content):
    """
    Replace all variations of ARD offers with the standardized version.
    Returns (modified_content, number_of_replacements)
    """
    replacements_made = 0
    
    # Pattern 1: Tailwind gradient box with openRightsScan button
    pattern1 = re.compile(
        r'<!-- AI Tool Section -->.*?<div class="bg-gradient-to-br from-slate-900.*?</div>\s*</div>',
        re.DOTALL | re.IGNORECASE
    )
    
    matches = pattern1.findall(content)
    if matches:
        replacements_made += len(matches)
        content = pattern1.sub(NEW_ARD_OFFER, content)
    
    # Pattern 2: Alternative inline styles version
    pattern2 = re.compile(
        r'<div class="ai-tool-banner">.*?</div>',
        re.DOTALL | re.IGNORECASE
    )
    
    matches = pattern2.findall(content)
    if matches:
        replacements_made += len(matches)
        content = pattern2.sub(NEW_ARD_OFFER, content)
    
    # Remove modal overlay if present
    modal_pattern = re.compile(
        r'<!-- MODAL FOR AI SCAN -->.*?</div>\s*</div>\s*</div>',
        re.DOTALL
    )
    
    if modal_pattern.search(content):
        content = modal_pattern.sub('', content)
    
    # Remove JavaScript for modal if present
    js_pattern = re.compile(
        r'<script>\s*const apiKey.*?</script>',
        re.DOTALL
    )
    
    if js_pattern.search(content):
        content = js_pattern.sub('', content)
    
    # Alternative JS pattern (without const apiKey)
    js_pattern2 = re.compile(
        r'<script>.*?function openRightsScan.*?</script>',
        re.DOTALL
    )
    
    if js_pattern2.search(content):
        content = js_pattern2.sub('', content)
    
    return content, replacements_made


def process_file(file_path):
    """Process a single HTML file."""
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Check if this file has any ARD offer code
        has_old_offer = (
            'openRightsScan' in original_content or
            'bg-gradient-to-br from-slate-900' in original_content or
            'ai-tool-banner' in original_content
        )
        
        if not has_old_offer:
            return False, "No ARD offer found"
        
        # Replace ARD offers
        new_content, num_replacements = replace_ard_offers(original_content)
        
        # Only write if changes were made
        if new_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True, f"Replaced {num_replacements} ARD offer(s)"
        else:
            return False, "Already has correct format"
            
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Main function to process files or directories."""
    
    if len(sys.argv) < 2:
        print("=" * 70)
        print("ARD OFFER REPLACEMENT SCRIPT")
        print("=" * 70)
        print("\nUsage:")
        print("  python replace_ard_offers_comprehensive.py <file.html>")
        print("  python replace_ard_offers_comprehensive.py <directory>")
        print("\nExamples:")
        print("  python replace_ard_offers_comprehensive.py anna-isd/ard-guide.html")
        print("  python replace_ard_offers_comprehensive.py anna-isd")
        print("  python replace_ard_offers_comprehensive.py districts")
        print("=" * 70)
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    
    if not input_path.exists():
        print(f"❌ Error: {input_path} does not exist")
        sys.exit(1)
    
    # Process directory
    if input_path.is_dir():
        html_files = list(input_path.rglob('*.html'))
        
        if not html_files:
            print(f"❌ No HTML files found in {input_path}")
            sys.exit(1)
        
        print(f"Found {len(html_files)} HTML files in {input_path}")
        print("=" * 70)
        
        processed = 0
        skipped = 0
        errors = 0
        
        for html_file in html_files:
            success, message = process_file(html_file)
            
            if success:
                processed += 1
                print(f"✓ {html_file.relative_to(input_path)}: {message}")
            else:
                skipped += 1
                # Only show errors, not "no offer found" messages
                if message.startswith("Error"):
                    errors += 1
                    print(f"✗ {html_file.relative_to(input_path)}: {message}")
        
        print("=" * 70)
        print(f"\n✓ Processed: {processed} files")
        print(f"○ Skipped: {skipped} files (no changes needed)")
        if errors > 0:
            print(f"✗ Errors: {errors} files")
        print("\nDone!")
    
    # Process single file
    elif input_path.is_file():
        print(f"Processing: {input_path.name}")
        print("=" * 70)
        
        success, message = process_file(input_path)
        
        if success:
            print(f"✓ Success: {message}")
        else:
            print(f"○ {message}")
        
        print("=" * 70)
    
    else:
        print(f"❌ Error: {input_path} is neither a file nor a directory")
        sys.exit(1)


if __name__ == '__main__':
    main()