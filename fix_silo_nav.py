import os
import re

def title_case_district(slug):
    """Converts a URL slug like 'frisco-isd' to 'Frisco ISD'"""
    words = slug.split('-')
    words = [w.capitalize() if w.lower() not in ['isd', 'cisd'] else w.upper() for w in words]
    return ' '.join(words)

def inject_silo_nav():
    root_dir = '.'
    modified_count = 0

    for subdir, dirs, files in os.walk(root_dir):
        # Normalize the path for Windows
        normalized_dir = subdir.replace('\\', '/')
        
        # Target specifically district sub-folders, ignore backups
        if 'districts/' in normalized_dir and not 'backup' in normalized_dir.lower() and not '.git' in normalized_dir:
            
            # Extract the exact district folder name (e.g., 'frisco-isd')
            folder_name = normalized_dir.split('/')[-1]
            if not folder_name or folder_name == 'districts':
                continue
                
            district_name = title_case_district(folder_name)
            
            # The sleek, inline HTML navigation bar to inject
            silo_nav_html = f"""
<div class="silo-nav" style="background-color: #e9ecef; padding: 12px 16px; border-radius: 6px; margin: 20px 0; font-size: 14px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; flex-wrap: wrap; gap: 12px; align-items: center; border-left: 4px solid #6c757d;">
    <strong style="color: #495057;">{district_name} Resources:</strong>
    <a href="index.html" style="text-decoration: none; color: #0056b3; font-weight: 500;">District Home</a> &bull;
    <a href="ard-process-guide.html" style="text-decoration: none; color: #0056b3; font-weight: 500;">ARD Guide</a> &bull;
    <a href="evaluation-child-find.html" style="text-decoration: none; color: #0056b3; font-weight: 500;">Evaluations (FIE)</a> &bull;
    <a href="dyslexia-services.html" style="text-decoration: none; color: #0056b3; font-weight: 500;">Dyslexia/504</a> &bull;
    <a href="grievance-dispute-resolution.html" style="text-decoration: none; color: #0056b3; font-weight: 500;">Dispute Resolution</a>
</div>
"""
            
            for file in files:
                # Target sub-pages only, ignore the main index.html of the district
                if file.endswith('.html') and file != 'index.html':
                    filepath = os.path.join(subdir, file)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Only inject if it hasn't been added yet
                    if "UX FIX: In-Silo Navigation" not in content:
                        # Find the first </h1> tag and insert the navigation directly below it
                        new_content = re.sub(r'(</h1>)', r'\1\n' + silo_nav_html, content, count=1, flags=re.IGNORECASE)
                        
                        if new_content != content:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            modified_count += 1
                            
    print(f"✅ UX Fix Complete. Injected Silo Navigation into {modified_count} sub-pages.")

if __name__ == '__main__':
    inject_silo_nav()