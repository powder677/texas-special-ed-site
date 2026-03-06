import os
from bs4 import BeautifulSoup

# These specific phrases identify the old floating ad text
ORPHAN_PHRASES = [
    "ARD Meeting in 7 Days?",
    "Stop going into ARD meetings unprepared",
    "advocates charge $200/hr",
    "4.9/5 stars (327 Texas parents)",
    "327 Texas parents",
    "Response scripts for district pushback",
    "10-Day Recess Playbook",
    "IEP Red Flag Analyzer",
    "Meeting prep checklist",
    "Used the eval request template",
    "- Maria, Round Rock ISD",
    "Get the ARD Toolkit",
    "Instant Access — $47",
    "30-Day Money-Back Guarantee"
]

def is_safely_in_new_box(element):
    """Checks if the text is inside the new formatted ad box so we don't delete the good one."""
    current = element
    while current and current.name != 'body':
        if current.name == 'div':
            style = current.get('style', '')
            classes = current.get('class', [])
            
            # Identifies the specific background and border of the new boxes we injected
            if 'background-color: #f8f9fa' in style.lower() and 'border' in style.lower():
                return True
            # Failsafe for Bootstrap class styling if you used that version
            if 'card' in classes and any(c in classes for c in ['border-danger', 'border-primary']):
                return True
                
        current = current.parent
    return False

def cleanup_duplicates():
    updated_count = 0
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Fast check: does it contain ARD ad text?
                    if "ARD Meeting" not in content and "advocates charge" not in content:
                        continue

                    soup = BeautifulSoup(content, 'html.parser')
                    modified = False
                    
                    # Find tags that usually wrap paragraphs and list items
                    tags_to_check = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'ul', 'li', 'div', 'span', 'strong', 'em', 'center'])
                    
                    for tag in tags_to_check:
                        # Skip if this element was already deleted
                        if tag.parent is None:
                            continue
                            
                        text = tag.get_text(strip=True).replace('\n', ' ')
                        
                        # Target specific text blocks (avoiding giant structural page sections)
                        if 0 < len(text) < 800:
                            is_orphan = False
                            for phrase in ORPHAN_PHRASES:
                                if phrase in text:
                                    is_orphan = True
                                    break
                            
                            # If it contains old ad text BUT is not safely inside our new box, delete it
                            if is_orphan and not is_safely_in_new_box(tag):
                                tag.decompose()
                                modified = True
                    
                    # Extra cleanup: clear out empty elements left behind by the deleted text
                    for tag in soup.find_all(['p', 'span', 'ul', 'center']):
                        if tag.parent is not None and not tag.get_text(strip=True) and not tag.find_all(['img', 'a', 'iframe']):
                            tag.decompose()
                            modified = True

                    if modified:
                        # Save the cleaned file perfectly
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(str(soup))
                        updated_count += 1
                        print(f"🧹 Cleaned up duplicates in: {file_path}")
                            
                except Exception as e:
                    print(f"⚠️ Error cleaning {file_path}: {e}")

    print(f"\n✨ Finished! Successfully removed floating duplicates in {updated_count} files.")

if __name__ == "__main__":
    cleanup_duplicates()