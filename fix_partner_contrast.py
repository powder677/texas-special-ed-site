import os

def fix_blue_on_blue():
    root_dir = './districts'
    modified_count = 0
    
    # The exact text we are rescuing from the background
    h_text = "Why Partner With Us?"
    p_text = "We are the only independent, data-driven resource hub for Texas special education parents. Our pages capture high-intent traffic from families actively seeking evaluations and legal support."
    
    # Ensure directory exists
    if not os.path.exists(root_dir):
        print(f"❌ Could not find {root_dir} folder.")
        return

    for subdir, _, files in os.walk(root_dir):
        if 'partners.html' in files:
            filepath = os.path.join(subdir, 'partners.html')
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Only fix if it hasn't been fixed yet
            if h_text in content and "UX FIX: Contrast" not in content:
                
                # Generate the high-contrast "Inner Card" overrides
                # Top half (Header): White background, bold dark blue text
                new_h = f"<span style='display: block; background-color: #ffffff; color: #004085; font-size: 22px; font-weight: bold; padding: 15px 20px 5px 20px; border-radius: 8px 8px 0 0; box-shadow: 0 -2px 10px rgba(0,0,0,0.05);'>{h_text}</span>"
                
                # Bottom half (Text): White background, accessible dark gray text
                new_p = f"<span style='display: block; background-color: #ffffff; color: #333333; font-size: 16px; line-height: 1.6; padding: 5px 20px 20px 20px; border-radius: 0 0 8px 8px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);'>{p_text}</span>"
                
                # Swap the text
                content = content.replace(h_text, new_h)
                content = content.replace(p_text, new_p)
                
                # Add a safety flag
                content = content.replace('</body>', '\n</body>')
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                modified_count += 1

    print(f"✅ UX Fix Complete! Rescued the partner text with high-contrast cards in {modified_count} files.")

if __name__ == '__main__':
    fix_blue_on_blue()