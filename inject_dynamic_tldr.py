import os
import re

def title_case_district(slug):
    """Converts 'austin-isd' to 'Austin ISD'"""
    if not slug: return "Your District"
    words = slug.split('-')
    words = [w.capitalize() if w.lower() not in ['isd', 'cisd'] else w.upper() for w in words]
    return ' '.join(words)

def get_dynamic_bullets(filename, district_name):
    if 'ard-process' in filename:
        return [
            f"ARD meetings determine your child's specific Special Education eligibility within {district_name}.",
            "You are a mandatory, equal member of the committee—do not let school staff dictate the terms.",
            f"Never sign an {district_name} IEP if you disagree; you have the legal right to request a 10-day recess."
        ]
    elif 'dyslexia' in filename:
        return [
            f"Under Texas HB 3928, {district_name} dyslexia evaluations must follow the full Special Education (FIE) process.",
            "Your child may qualify for a robust IEP, rather than just a basic 504 plan.",
            f"Ensure {district_name} provides evidence-based dyslexia instruction, not just general reading help."
        ]
    elif 'evaluation' in filename:
        return [
            f"{district_name} has a strict legal 'Child Find' mandate to evaluate any child suspected of a disability.",
            "Always submit your evaluation requests to the principal or sped director in writing to start the legal timeline.",
            f"{district_name} has exactly 15 school days from your written request to provide consent forms or a written refusal."
        ]
    elif 'grievance' in filename:
        return [
            f"Always request 'Prior Written Notice' (PWN) if {district_name} denies a service or evaluation request.",
            "Try resolving issues locally first, but know you can request state mediation at any time.",
            "Filing a TEA complaint or requesting a Due Process hearing are your formal legal escalations against the district."
        ]
    elif 'index' in filename:
        return [
            f"This is your local hub for {district_name} special education resources and administrative contacts.",
            "Familiarize yourself with your parental rights before engaging with school administration.",
            "Use the specific guides below to navigate ARDs, evaluations, and discipline in this district."
        ]
    else:
        return [
            "Understand your legal rights under federal IDEA and Texas state law.",
            "Always document your school communications and requests in writing.",
            "Never hesitate to politely disagree or ask for more time to review documents before signing."
        ]

def inject_dynamic_tldr():
    root_dir = '.'
    modified_count = 0

    for subdir, dirs, files in os.walk(root_dir):
        normalized_dir = subdir.replace('\\', '/')
        
        if 'backup' in normalized_dir.lower() or '.git' in normalized_dir:
            continue
            
        district_slug = None
        if 'districts/' in normalized_dir:
            parts = normalized_dir.split('/')
            if len(parts) >= 3 and parts[-1] != 'districts':
                district_slug = parts[-1]
                
        district_name = title_case_district(district_slug) if district_slug else "Texas"

        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(subdir, file)
                normalized_path = filepath.replace('\\', '/')
                
                if 'districts/' in normalized_path or 'blog/' in normalized_path or 'generated_pages/' in normalized_path:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    bullets = get_dynamic_bullets(file, district_name)
                    
                    tldr_html = f"""
<div class="tldr-box" style="background-color: #fffde7; border-left: 5px solid #ffc107; padding: 20px; margin: 25px 0; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
    <h3 style="margin-top: 0; color: #856404; font-size: 18px; font-weight: bold; display: flex; align-items: center; gap: 8px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="min-width: 20px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
        TL;DR / Quick Summary
    </h3>
    <ul style="margin-bottom: 0; color: #333; font-size: 15px; line-height: 1.6; padding-left: 25px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <li style="margin-bottom: 8px;">{bullets[0]}</li>
        <li style="margin-bottom: 8px;">{bullets[1]}</li>
        <li style="margin-bottom: 0;">{bullets[2]}</li>
    </ul>
</div>
"""
                    
                    new_content = content
                    
                    # Memory-Safe String Replacement (No Regex used here)
                    start_tag = ""
                    end_tag = ""
                    
                    if start_tag in content:
                        # Find precise locations without loading Regex into memory
                        start_idx = content.find(start_tag)
                        end_idx = content.find(end_tag, start_idx)
                        
                        if start_idx != -1 and end_idx != -1:
                            # Slice out the old box and drop the new one in
                            new_content = content[:start_idx] + tldr_html.strip() + "\n" + content[end_idx + len(end_tag):]
                    else:
                        # Inject after H1 if it doesn't exist yet
                        new_content = re.sub(r'(</h1>)', r'\1\n' + tldr_html, content, count=1, flags=re.IGNORECASE)
                    
                    if new_content != content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        modified_count += 1

    print(f"✅ Memory-Safe UX Fix Complete. Updated Dynamic Local TL;DR Boxes in {modified_count} files.")

if __name__ == '__main__':
    inject_dynamic_tldr()