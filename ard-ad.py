import os
from bs4 import BeautifulSoup
import re

STRIPE_LINK = "https://buy.stripe.com/6oU8wO2FTgmA5xReP3bbG0L"

# The new high-converting copy, styled perfectly as a standalone box
NEW_COPY_HTML = """
<div style="background-color: #f8f9fa; border: 2px solid #dc3545; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <h3 style="color: #dc3545; font-weight: bold; margin-top: 0;">🚨 ARD Meeting in 7 Days? You Need This</h3>
    <p style="border-bottom: 1px solid #dee2e6; padding-bottom: 10px;">Stop going into ARD meetings unprepared. Get the exact scripts Texas advocates charge $200/hr to provide.</p>
    
    <div style="font-weight: bold; margin-bottom: 15px;">
        <span style="color: #ffc107;">⭐⭐⭐⭐⭐</span> <span style="font-weight: normal; font-size: 0.9em; color: #6c757d;">4.9/5 stars (327 Texas parents)</span>
    </div>
    
    <ul style="list-style-type: none; padding-left: 0; line-height: 1.8; margin-bottom: 20px;">
        <li>✅ Email templates (copy &amp; paste)</li>
        <li>✅ Response scripts for district pushback</li>
        <li>✅ 10-Day Recess Playbook</li>
        <li>✅ IEP Red Flag Analyzer</li>
        <li>✅ Meeting prep checklist</li>
    </ul>

    <p style="font-style: italic; font-size: 0.9em; border-left: 3px solid #6c757d; padding-left: 10px; color: #6c757d;">
        "Used the eval request template—FIE scheduled in 48 hours!" <br> 
        <strong style="color: #212529;">- Maria, Round Rock ISD</strong>
    </p>
    
    <div style="text-align: center; margin-top: 20px;">
        <a href="https://buy.stripe.com/6oU8wO2FTgmA5xReP3bbG0L" target="_blank" style="display: block; background-color: #dc3545; color: white; padding: 15px 20px; text-decoration: none; font-weight: bold; border-radius: 5px; font-size: 1.1em;">Get Instant Access — $47</a>
        <small style="color: #6c757d; display: block; margin-top: 10px;">🔒 30-Day Money-Back Guarantee</small>
    </div>
</div>
"""

def update_ard_copy():
    updated_count = 0
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Only process if the Stripe link is in the file
                    if STRIPE_LINK in content:
                        soup = BeautifulSoup(content, 'html.parser')
                        anchors = soup.find_all('a', href=STRIPE_LINK)
                        modified = False
                        
                        for a in anchors:
                            # 1. Find the immediate wrapper of the link (usually a <p> or <div>)
                            target_to_replace = a
                            parent = a.parent
                            
                            # If the parent is just a paragraph, list item, or formatting tag, we'll replace the parent
                            if parent and parent.name in ['p', 'strong', 'em', 'li', 'center', 'h3', 'h4']:
                                target_to_replace = parent
                            
                            # 2. Cleanup old ad text that might be floating directly above it
                            # Looks at the previous 3 elements to see if they contain old ad keywords
                            prev_sibling = target_to_replace.find_previous_sibling()
                            while prev_sibling and prev_sibling.name in ['p', 'h2', 'h3', 'h4', 'ul', 'div']:
                                text_content = prev_sibling.get_text().lower()
                                if any(phrase in text_content for phrase in ['ard meeting', 'unprepared', 'advocates charge', '⭐⭐⭐⭐⭐']):
                                    sibling_to_remove = prev_sibling
                                    prev_sibling = prev_sibling.find_previous_sibling()
                                    sibling_to_remove.decompose() # Delete the old text block
                                else:
                                    break
                                    
                            # 3. Replace the link/wrapper with the new beautiful HTML box
                            new_soup = BeautifulSoup(NEW_COPY_HTML, 'html.parser')
                            target_to_replace.replace_with(new_soup)
                            modified = True
                        
                        # Save changes
                        if modified:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                # str(soup) prevents BeautifulSoup from re-formatting your entire file
                                f.write(str(soup))
                            updated_count += 1
                            print(f"✅ Updated: {file_path}")
                            
                except Exception as e:
                    print(f"⚠️ Error updating {file_path}: {e}")

    print(f"\n🎉 Finished! Successfully updated {updated_count} files.")

if __name__ == "__main__":
    update_ard_copy()