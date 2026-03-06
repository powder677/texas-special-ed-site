import os
import re

# We set the path to your main 'districts' folder so it catches Abilene, Dallas, Houston, etc.
DIRECTORY_PATH = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"

# The new HTML for the chatbot iframe
NEW_SIDEBAR_CONTENT = """   <div style="background: #fff; border: 2px solid #1a56db; border-radius: 16px; box-shadow: 0 10px 30px rgba(26, 86, 219, 0.08); padding: 20px;">
      <h3 style="margin-top: 0; text-align: center; color: #0a2342; font-family: 'Lora', serif; font-size: 1.3rem;">Free ARD Rights Scan</h3>
      <p style="text-align: center; font-size: 14px; margin-bottom: 16px; color: #3a3a5c;">Wondering if the school violated your rights? Answer a few questions and our AI will analyze your case.</p>
      
      <iframe 
         src="https://ard-chatbot-831148457361.us-central1.run.app" 
         width="100%" 
         height="500px" 
         style="border: none; border-radius: 12px; border: 1px solid #E8DDD0; max-height: 65vh;"
         title="ARD Rights Scan Tool">
      </iframe>
   </div>"""

# The cleaned-up script that keeps your mobile menu working but removes the Google Sheet logic
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
});
</script>"""

def update_html_files():
    updated_count = 0
    
    # Walk through every folder and subfolder
    for root, dirs, files in os.walk(DIRECTORY_PATH):
        for file in files:
            # Only target the specific guide files
            if file == "ard-process-guide.html":
                filepath = os.path.join(root, file)
                district_name = os.path.basename(root)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    original_content = content
                    
                    # 1. REMOVE OLD CSS: Strip out the old Sidebar Form CSS so pages load faster
                    css_pattern = re.compile(r'/\*\s*── SIDEBAR FORM STYLES.*?(?=</style>)', re.DOTALL)
                    content = css_pattern.sub('', content)
                    
                    # 2. INJECT NEW IFRAME: Replace everything inside the <aside> tags
                    aside_pattern = re.compile(r'(<aside class="sidebar-column">)(.*?)(</aside>)', re.DOTALL)
                    content = aside_pattern.sub(r'\1\n' + NEW_SIDEBAR_CONTENT + r'\n</aside>', content)
                    
                    # 3. REMOVE GOOGLE SHEET SCRIPT: Replace the old lead capture script block
                    # Looks for the comment block and script tag
                    script_block_pattern = re.compile(
                        r'<!-- =+ -->\s*<!-- THE LEAD CAPTURE SCRIPT.*?-->\s*<!-- =+ -->\s*<script>.*?</script>', 
                        re.DOTALL
                    )
                    
                    if script_block_pattern.search(content):
                        content = script_block_pattern.sub(CLEAN_SCRIPT, content)
                    else:
                        # Fallback just in case the comments were deleted: look for the script containing the Google URL
                        fallback_pattern = re.compile(r'<script>[^<]*GOOGLE_SCRIPT_URL.*?</script>', re.DOTALL)
                        content = fallback_pattern.sub(CLEAN_SCRIPT, content)
                        
                    # Only save the file if we actually changed something
                    if content != original_content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"✅ Updated: {district_name}")
                        updated_count += 1
                    else:
                        print(f"⏩ Skipped (no changes needed): {district_name}")
                        
                except Exception as e:
                    print(f"❌ Error processing {district_name}: {e}")
                    
    print(f"\n🎉 Done! Successfully updated {updated_count} district pages.")

if __name__ == "__main__":
    print(f"Scanning directory: {DIRECTORY_PATH}\n")
    update_html_files()