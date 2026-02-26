import os
import re

# Set the root directory of your site
root_dir = '.'

# The Trust Badge HTML to inject
trust_badge_html = """
<div class="trust-anchor" style="background-color: #f8fbff; border-left: 5px solid #004085; padding: 16px; margin: 20px 0; border-radius: 4px;">
    <p style="margin: 0; font-size: 16px; color: #333; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
        <strong>Hi, I'm a Texas parent of a 2e child.</strong> When I watched the school system fail her, I realized how broken the process is. I built this resource to help parents like you get the support your child deserves. You are not alone.
    </p>
</div>
"""

def update_html_files():
    files_modified = 0
    
    for subdir, dirs, files in os.walk(root_dir):
        # Normalize the path for Windows (\) vs Mac/Linux (/)
        normalized_dir = subdir.replace('\\', '/')
        
        # Skip backup directories and git to prevent massive bloat
        if 'backup' in normalized_dir.lower() or '.git' in normalized_dir:
            continue
            
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(subdir, file)
                normalized_path = filepath.replace('\\', '/')
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                original_content = content

                # --- FIX 1: NAVIGATION REFRAMING ---
                # A more robust regex to catch "Store" anywhere inside an anchor/span tag without disturbing links
                content = re.sub(r'>\s*Store\s*<', '>Parent Toolkits<', content, flags=re.IGNORECASE)
                
                # --- FIX 2: TRUST INJECTOR ---
                # Only inject if it hasn't been injected yet
                if "UX FIX: Founder Trust Anchor" not in content:
                    # Target district pages and blogs using the normalized path
                    if 'districts/' in normalized_path or 'blog/' in normalized_path or 'generated_pages/' in normalized_path:
                        # Find the first </h1> and insert the badge right after it
                        content = re.sub(r'(</h1>)', r'\1\n' + trust_badge_html, content, count=1, flags=re.IGNORECASE)

                # Write back if changes were made
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    files_modified += 1

    print(f"✅ UX Fix Complete. Modified {files_modified} HTML files.")
    print("- 'Store' navigation elements changed to 'Parent Toolkits'")
    print("- 2e Parent Trust Anchor injected below H1s on SEO landing pages")

if __name__ == '__main__':
    update_html_files()