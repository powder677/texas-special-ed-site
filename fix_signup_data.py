import os

# The folder where your HTML files live ('.' means the current folder)
FOLDER_PATH = "." 

def fix_html_files(directory):
    files_fixed = 0
    
    # The exact block of code we are looking for
    old_text = """            const signupData = {
                email: email,
                source: 'newsletter_popup',"""
    
    # The new block of code with the missing fields added
    new_text = """            const signupData = {
                email: email,
                site: 'texas_special_ed',
                language: 'en',
                source: 'newsletter_popup',"""

    print("🔍 Scanning for HTML files to fix...")
    
    # Walk through every folder and subfolder
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                filepath = os.path.join(root, file)
                
                try:
                    # Read the file
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # If the file has the old code, replace it and save
                    if old_text in content:
                        new_content = content.replace(old_text, new_text)
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        files_fixed += 1
                        print(f"✅ Fixed: {filepath}")
                except Exception as e:
                    print(f"⚠️ Could not read {filepath}: {e}")

    print(f"\n🎉 Done! Successfully updated {files_fixed} files.")

if __name__ == "__main__":
    fix_html_files(FOLDER_PATH)