import os
import re

# Protect backups and git history
SKIP_DIRS = {'.git', '_canonical_backups', '_trailing_slash_backups', 'districts_updated'}

def remove_inline_styles():
    # Regex to match ANY <style> block and its contents
    style_pattern = re.compile(r'<style[^>]*>.*?</style>', re.DOTALL | re.IGNORECASE)
    updated_count = 0

    for root, dirs, files in os.walk('.'):
        # Modify dirs in-place to skip backup directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Strip the style block entirely
                    new_content = re.sub(style_pattern, '', content)

                    # Only write to disk if a style tag was actually found and removed
                    if new_content != content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        updated_count += 1
                        print(f"Cleaned styles from: {filepath}")
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

    print(f"\n✅ Success! Purged inline styles from {updated_count} files.")

if __name__ == "__main__":
    remove_inline_styles()