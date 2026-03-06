import os
import re

# The path to your main 'districts' folder
DIRECTORY_PATH = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"

# The EXACT list of files you want to update
TARGET_FILES = [
    "evaluation-child-find.html",
    "grievance-dispute-resolution.html",
    "dyslexia-services.html",
    "ard-process-guide.html"
]

# The NEW high-contrast dark blue and gold HTML for the chatbot iframe
NEW_SIDEBAR_CONTENT = """   <div style="background: linear-gradient(145deg, #0f172a 0%, #1e3a8a 100%); border-radius: 16px; box-shadow: 0 12px 35px rgba(30, 58, 138, 0.25); padding: 24px; position: relative; overflow: hidden; border: 1px solid #2a4382;">
      
      <div style="text-align: center; margin-bottom: 20px;">
         <span style="display: inline-block; background: #d4af37; color: #0f172a; padding: 4px 12px; border-radius: 50px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">Live AI Tool</span>
         <h3 style="margin: 0; color: #ffffff; font-family: 'Lora', serif; font-size: 1.4rem;">Free ARD Rights Scan</h3>
         <p style="font-size: 14px; color: #cbd5e1; margin: 8px 0 0; line-height: 1.5;">Wondering if the school violated your rights? Answer a few questions for an instant analysis.</p>
      </div>
      
      <iframe 
         src="https://ard-rights-scan-831148457361.us-central1.run.app" 
         width="100%" 
         height="500px" 
         style="border: none; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); max-height: 65vh;"
         title="ARD Rights Scan Tool">
      </iframe>
   </div>"""

# The cleaned-up script that keeps your mobile menu AND FAQ dropdowns working
CLEAN_SCRIPT = """<script>
document.addEventListener('DOMContentLoaded', function() {
    // Menu toggle logic
    var toggle = document.querySelector('.mobile-menu-toggle');
    var menu   = document.querySelector('.nav-menu');
    if (toggle && menu) {
        toggle.addEventListener('click', function() {
            menu.classList.toggle('active');
            toggle.setAttribute('aria-expanded', menu.classList.contains('active'));
        });
    }
    
    // FAQ Toggle logic
    const details = document.querySelectorAll('details');
    details.forEach(targetDetail => {
        targetDetail.addEventListener('click', () => {
            details.forEach(detail => {
                if (detail !== targetDetail) {
                    detail.removeAttribute('open');
                }
            });
        });
    });
});
</script>"""

def update_html_files():
    updated_count = 0
    
    # Walk through every folder and subfolder
    for root, dirs, files in os.walk(DIRECTORY_PATH):
        for file in files:
            # Check if the file is exactly one of the ones we want to update
            if file in TARGET_FILES:
                filepath = os.path.join(root, file)
                district_name = os.path.basename(root)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    original_content = content
                    
                    # 1. REMOVE OLD CSS: Strip out the old Sidebar Form CSS
                    css_pattern = re.compile(r'/\*\s*── SIDEBAR FORM STYLES.*?(?=</style>)', re.DOTALL)
                    content = css_pattern.sub('', content)
                    
                    # 2. INJECT NEW IFRAME: Replace everything inside the <aside> tags
                    aside_pattern = re.compile(r'(<aside class="sidebar-column">)(.*?)(</aside>)', re.DOTALL)
                    content = aside_pattern.sub(r'\1\n' + NEW_SIDEBAR_CONTENT + r'\n\3', content)
                    
                    # 3. REMOVE GOOGLE SHEET SCRIPT: Replace the old lead capture script block
                    script_block_pattern = re.compile(
                        r'<!-- =+ -->\s*<!-- THE LEAD CAPTURE SCRIPT.*?-->\s*<!-- =+ -->\s*<script>.*?</script>', 
                        re.DOTALL
                    )
                    
                    if script_block_pattern.search(content):
                        content = script_block_pattern.sub(CLEAN_SCRIPT, content)
                    else:
                        # Fallback: look for the script containing the Google URL
                        fallback_pattern = re.compile(r'<script>[^<]*GOOGLE_SCRIPT_URL.*?</script>', re.DOTALL)
                        content = fallback_pattern.sub(CLEAN_SCRIPT, content)
                        
                    # Only save the file if we actually changed something
                    if content != original_content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"✅ Updated: {district_name} / {file}")
                        updated_count += 1
                        
                except Exception as e:
                    print(f"❌ Error processing {district_name}/{file}: {e}")
                    
    print(f"\n🎉 Done! Successfully updated {updated_count} pages.")

if __name__ == "__main__":
    print(f"Scanning directory: {DIRECTORY_PATH}")
    print(f"Looking for: {', '.join(TARGET_FILES)}\n")
    update_html_files()