import os
import re

def title_case_district(slug):
    """Converts a URL slug like 'fort-bend-isd' to 'Fort Bend ISD'"""
    words = slug.split('-')
    # Capitalize normal words, uppercase ISD/CISD
    words = [w.capitalize() if w.lower() not in ['isd', 'cisd'] else w.upper() for w in words]
    return ' '.join(words)

def fix_index_buttons():
    filepath = 'index.html'
    
    if not os.path.exists(filepath):
        print(f"❌ Could not find {filepath} in the current directory.")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex breakdown:
    # Group 1: The start of the tag up to the district folder (e.g., <a href="districts/ )
    # Group 2: The district slug (e.g., austin-isd )
    # Group 3: The rest of the opening tag (e.g., /index.html" class="button"> )
    # Group 4: The inner text/HTML of the button (e.g., <i class="icon"></i> Parent Resources )
    # Group 5: The closing tag (e.g., </a> )
    pattern = re.compile(r'(<a[^>]+href=["\']?(?:/?districts/))([^/"\'>]+)([^>]*>)(.*?)(</a>)', flags=re.IGNORECASE | re.DOTALL)
    
    modified_count = 0

    def replacer(match):
        nonlocal modified_count
        full_tag_start = match.group(1)
        slug = match.group(2)
        full_tag_mid = match.group(3)
        link_text = match.group(4)
        full_tag_end = match.group(5)
        
        district_name = title_case_district(slug)
        
        # We look for "Resource" or "Resources" in the button.
        # We safely inject the district name right before it, preserving any icons/spans.
        if "resource" in link_text.lower() and district_name.lower() not in link_text.lower():
            # Replace "Parent Resources" with "Austin ISD Parent Resources"
            new_text = re.sub(r'(parent resources?)', f'{district_name} \\1', link_text, flags=re.IGNORECASE)
            
            # Fallback if "Parent" isn't explicitly in the button but "Resources" is
            if new_text == link_text:
                 new_text = re.sub(r'(resources?)', f'{district_name} \\1', link_text, flags=re.IGNORECASE)

            modified_count += 1
            return f"{full_tag_start}{slug}{full_tag_mid}{new_text}{full_tag_end}"
        
        return match.group(0) # Return unchanged if it doesn't match our criteria

    new_content = pattern.sub(replacer, content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ UX Fix Complete. Updated {modified_count} buttons on index.html!")
        print("Example change: 'Parent Resources' -> 'Austin ISD Parent Resources'")
    else:
        print("⚠️ No changes made. The buttons might already include the district names or use different text.")

if __name__ == '__main__':
    fix_index_buttons()