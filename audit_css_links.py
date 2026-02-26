import os
import re

SKIP_DIRS = {'.git', '_canonical_backups', '_trailing_slash_backups', 'districts_updated'}

def ensure_css_links():
    # 1. Look for the style.css link
    css_link_pattern = re.compile(r'<link[^>]*href=["\'][./]*style\.css["\'][^>]*>', re.IGNORECASE)
    # 2. Look for the closing head tag to inject right before it
    head_close_pattern = re.compile(r'</head>', re.IGNORECASE)
    
    updated_count = 0
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # If the file DOES NOT have the style.css link
                    if not css_link_pattern.search(content):
                        # Inject the absolute root-relative link right before </head>
                        new_content = head_close_pattern.sub('    <link href="/style.css" rel="stylesheet"/>\n</head>', content)
                        
                        if new_content != content:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            updated_count += 1
                            print(f"Fixed missing CSS link in: {filepath}")
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

    print(f"\n✅ Audit Complete! Injected missing CSS link into {updated_count} files.")

if __name__ == "__main__":
    ensure_css_links()