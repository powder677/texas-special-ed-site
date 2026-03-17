import os

# Start searching from the main folder
FOLDER_PATH = "." 

def fix_spanish_html(directory):
    files_fixed = 0
    
    old_text_broken = """            const signupData = {
                email: email,
                source: 'newsletter_popup',"""
                
    old_text_english = """            const signupData = {
                email: email,
                site: 'texas_special_ed',
                language: 'en',
                source: 'newsletter_popup',"""
    
    new_text_spanish = """            const signupData = {
                email: email,
                site: 'texas_special_ed',
                language: 'es',
                source: 'newsletter_popup',"""

    print("🔍 Scanning entire site for Spanish HTML files...")
    
    # Walk through EVERY folder and subfolder
    for root, dirs, files in os.walk(directory):
        
        # Check if the folder we are currently looking at is named "es"
        if os.path.basename(root) == "es":
            
            for file in files:
                if file.endswith(".html"):
                    filepath = os.path.join(root, file)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Replace the code if found
                        if old_text_broken in content or old_text_english in content:
                            if old_text_broken in content:
                                new_content = content.replace(old_text_broken, new_text_spanish)
                            else:
                                new_content = content.replace(old_text_english, new_text_spanish)
                                
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            
                            files_fixed += 1
                            print(f"✅ Fixed (Spanish): {filepath}")
                    except Exception as e:
                        print(f"⚠️ Could not read {filepath}: {e}")

    print(f"\n🎉 Done! Successfully updated {files_fixed} Spanish files.")

if __name__ == "__main__":
    fix_spanish_html(FOLDER_PATH)