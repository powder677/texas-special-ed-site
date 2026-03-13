#!/usr/bin/env python3
"""
Replace ARD scan offers in district pages with the standardized external link version.
This script finds and replaces modal-based ARD scan implementations with the 
clean external chatbot link from the index page.
"""

import re
import sys
from pathlib import Path

# The standardized ARD scan offer HTML from index.html
STANDARD_ARD_OFFER = '''<!-- AI Tool Section -->
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


def replace_ard_offer(html_content):
    """Replace modal-based ARD offer with standard external link version."""
    
    # Pattern 1: Find the Tailwind-styled gradient box ARD offer
    # This matches the section from <!-- AI Tool Section --> to the closing </div>
    pattern1 = re.compile(
        r'<!-- AI Tool Section -->.*?<div class="bg-gradient-to-br from-slate-900 to-blue-900.*?</div>\s*</div>',
        re.DOTALL
    )
    
    # Replace with standard offer
    html_content = pattern1.sub(STANDARD_ARD_OFFER, html_content)
    
    # Pattern 2: Remove the modal overlay and modal content
    pattern2 = re.compile(
        r'<!-- MODAL FOR AI SCAN -->.*?</div>\s*</div>\s*</div>',
        re.DOTALL
    )
    html_content = pattern2.sub('', html_content)
    
    # Pattern 3: Remove the JavaScript functions for the modal
    # Find and remove the script block containing openRightsScan, closeRightsScan, runAnalysis
    pattern3 = re.compile(
        r'<script>\s*const apiKey.*?</script>',
        re.DOTALL
    )
    html_content = pattern3.sub('', html_content)
    
    return html_content


def process_file(input_path, output_path=None):
    """Process a single HTML file."""
    
    # Read the file
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file contains modal-based ARD offer
    if 'openRightsScan()' not in content and 'bg-gradient-to-br from-slate-900' not in content:
        print(f"✓ {input_path.name}: No modal-based ARD offer found - skipping")
        return False
    
    # Replace the ARD offers
    new_content = replace_ard_offer(content)
    
    # Write to output file
    if output_path is None:
        output_path = input_path
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ {input_path.name}: Replaced ARD offer successfully")
    return True


def main():
    """Main function to process files."""
    
    if len(sys.argv) < 2:
        print("Usage: python replace_ard_offers.py <file.html> [output.html]")
        print("   or: python replace_ard_offers.py <directory>")
        print("\nExamples:")
        print("  python replace_ard_offers.py district-page.html")
        print("  python replace_ard_offers.py district-page.html updated-page.html")
        print("  python replace_ard_offers.py ./districts/")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    
    # Process directory
    if input_path.is_dir():
        html_files = list(input_path.rglob('*.html'))
        print(f"Found {len(html_files)} HTML files in {input_path}")
        
        processed = 0
        for html_file in html_files:
            if process_file(html_file):
                processed += 1
        
        print(f"\n✓ Processed {processed} files with ARD offer replacements")
    
    # Process single file
    elif input_path.is_file():
        output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        process_file(input_path, output_path)
    
    else:
        print(f"Error: {input_path} not found")
        sys.exit(1)


if __name__ == '__main__':
    main()