import os
from bs4 import BeautifulSoup

# The CORRECT unique ID for the bundle Stripe link
STRIPE_ID = "3cIcN4a8l7Q4d0j7mB"

# The new premium-styled HTML box for the bundle
NEW_COPY_HTML = """
<div style="background-color: #f8f9fa; border: 2px solid #0d6efd; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
    <div style="text-align: center; margin-bottom: 15px;">
        <span style="background-color: #ffc107; color: #000; padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">🏆 MOST POPULAR • BEST VALUE</span>
    </div>
    
    <h3 style="color: #0d6efd; font-weight: bold; margin-top: 10px; text-align: center; margin-bottom: 5px;">Complete Texas Special Ed Bundle</h3>
    <h4 style="color: #495057; font-weight: 600; text-align: center; margin-top: 0; margin-bottom: 15px;">All 6 Toolkits • Save $185</h4>
    
    <p style="text-align: center; border-bottom: 1px solid #dee2e6; padding-bottom: 15px; font-size: 1.05em;">Instead of buying toolkits one-by-one for $282, get everything for <strong>$97</strong>.</p>
    
    <div style="text-align: center; margin-bottom: 20px; background-color: #fff; padding: 10px; border-radius: 5px; border: 1px dashed #dee2e6;">
        <span style="text-decoration: line-through; color: #6c757d; font-size: 0.95em;">Regular Price: $282</span><br>
        <strong style="font-size: 1.3em; color: #212529;">Bundle Price: $97</strong><br>
        <span style="color: #28a745; font-weight: bold; font-size: 1.1em;">✅ YOU SAVE: $185</span>
    </div>
    
    <ul style="list-style-type: none; padding-left: 0; line-height: 1.8; margin-bottom: 20px; font-size: 1.05em;">
        <li>✅ <strong>Lifetime access + updates</strong></li>
        <li>✅ <strong>Works for multiple children</strong></li>
        <li>✅ <strong>All Texas districts</strong></li>
    </ul>

    <p style="font-style: italic; font-size: 0.95em; border-left: 4px solid #ffc107; padding-left: 15px; color: #495057; background-color: #fff; padding-top: 10px; padding-bottom: 10px; padding-right: 10px; border-radius: 0 5px 5px 0;">
        "Worth it for the Behavior toolkit alone. Saved my son from suspension." <br> 
        <strong style="color: #212529;">- Marcus, Houston ISD</strong>
    </p>
    
    <div style="text-align: center; margin-top: 20px;">
        <a href="https://buy.stripe.com/3cIcN4a8l7Q4d0j7mBbbG0G" target="_blank" style="display: block; background-color: #0d6efd; color: white; padding: 16px 20px; text-decoration: none; font-weight: bold; border-radius: 6px; font-size: 1.2em; box-shadow: 0 4px 6px rgba(13, 110, 253, 0.3); transition: background-color 0.2s;">Get All 6 Toolkits — $97</a>
    </div>
</div>
"""

def update_bundle_copy():
    updated_count = 0
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Only process if the Bundle Stripe link ID is in the file
                    if STRIPE_ID in content:
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Find all anchors that contain the bundle ID
                        anchors = soup.find_all('a', href=lambda href: href and STRIPE_ID in href)
                        modified = False
                        
                        for a in anchors:
                            # 1. Find the immediate wrapper of the link
                            target_to_replace = a
                            parent = a.parent
                            
                            if parent and parent.name in ['p', 'strong', 'em', 'li', 'center', 'h3', 'h4', 'div']:
                                if parent.name != 'div' or (parent.get('class') and any(c in ' '.join(parent.get('class')) for c in ['card', 'widget', 'product', 'box'])):
                                    target_to_replace = parent
                            
                            # 2. Cleanup old ad text floating directly above it
                            prev_sibling = target_to_replace.find_previous_sibling()
                            while prev_sibling and prev_sibling.name in ['p', 'h2', 'h3', 'h4', 'ul', 'div', 'span', 'center', 'strong']:
                                text_content = prev_sibling.get_text().lower()
                                cleanup_keywords = ['bundle', 'toolkits', 'popular', 'value', '282', '185', '97', 'marcus', 'lifetime access']
                                
                                if any(phrase in text_content for phrase in cleanup_keywords):
                                    sibling_to_remove = prev_sibling
                                    prev_sibling = prev_sibling.find_previous_sibling()
                                    sibling_to_remove.decompose() # Silently delete old text
                                else:
                                    break
                                    
                            # 3. Replace the exact spot with the new beautiful HTML box
                            new_soup = BeautifulSoup(NEW_COPY_HTML, 'html.parser')
                            target_to_replace.replace_with(new_soup)
                            modified = True
                        
                        if modified:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(str(soup))
                            updated_count += 1
                            print(f"🌟 Updated: {file_path}")
                            
                except Exception as e:
                    print(f"⚠️ Error updating {file_path}: {e}")

    print(f"\n🎉 Finished! Successfully updated the Complete Bundle ad in {updated_count} files.")

if __name__ == "__main__":
    update_bundle_copy()