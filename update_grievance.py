import os
import re
import traceback

URGENT_DEFENSE_BOX = """
<div style="background-color: #450a0a; border: 2px solid #ef4444; padding: 28px; margin: 30px 0; border-radius: 8px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2); color: white; position: relative;">
    <div style="position: absolute; top: -14px; left: 28px; background: #ef4444; color: white; padding: 6px 16px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">Urgent Defense</div>

    <h3 style="margin-top: 12px; color: #ffffff; font-family: 'Georgia', serif; font-size: 1.5rem; letter-spacing: 0.02em;">🛑 Is your child facing suspension?</h3>
    
    <p style="color: #fecaca; margin-bottom: 20px; font-family: sans-serif; line-height: 1.6; font-size: 1.05rem;">New Texas laws (HB 6) have changed the rules. Protect your child from informal removals with the <strong>Behavior Defense Kit</strong>.</p>
    
    <div style="display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 24px;">
        <span style="background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #fee2e2; padding: 6px 12px; font-size: 0.85rem; border-radius: 4px;">📝 Shadow Discipline Tracker</span>
        <span style="background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #fee2e2; padding: 6px 12px; font-size: 0.85rem; border-radius: 4px;">⚖️ MDR Defense Scripts</span>
    </div>
    
    <a href="https://buy.stripe.com/bJe14mcgt6M0d0j8qFbbG0I" style="background-color: #ef4444; color: white; padding: 14px 28px; text-decoration: none; border-radius: 4px; font-weight: 700; font-family: sans-serif; display: block; text-align: center; text-transform: uppercase; letter-spacing: 0.05em;">Get the Defense Kit - $47</a>
</div>
"""

def update_grievance_pages():
    root_dir = "districts"
    
    if not os.path.exists(root_dir):
        print(f"[ERROR] Cannot find '{root_dir}' directory.")
        return

    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for district_slug in os.listdir(root_dir):
        try:
            district_path = os.path.join(root_dir, district_slug)
            
            # Skip if it's not a folder
            if not os.path.isdir(district_path):
                continue
                
            file_path = os.path.join(district_path, "grievance-dispute-resolution.html")
            
            # Skip if the grievance page hasn't been generated for this district yet
            if not os.path.exists(file_path):
                continue

            # Read safely (errors="ignore" bulldozes through any bad formatting characters)
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                html_content = f.read()

            # 1. Remove old sales box (The "BEST VALUE" bundle)
            html_content = re.sub(
                r'<div[^>]*background:linear-gradient[^>]*>.*?BEST VALUE.*?</div>', 
                '', 
                html_content, 
                flags=re.DOTALL | re.IGNORECASE
            )

            # 2. Find the phrase "What is MDR" (allowing for minor variations like "What is an MDR" or spelling out Manifestation Determination)
            parts = re.split(r'(What is\s+(?:an?\s+)?(?:MDR|Manifestation Determination))', html_content, maxsplit=1, flags=re.IGNORECASE)
            
            if len(parts) > 1:
                before_text = parts[0]
                match_text = parts[1]
                after_text = parts[2]
                
                # Scan backwards in the text *before* the match to find the nearest starting block tag
                last_block_tag_index = -1
                for match in re.finditer(r'<(p|h[1-6]|div|section)[^>]*>', before_text, flags=re.IGNORECASE):
                    last_block_tag_index = match.start()
                
                if last_block_tag_index != -1:
                    # Insert the Urgent Defense box exactly right before that block tag
                    new_html = (
                        before_text[:last_block_tag_index] + 
                        URGENT_DEFENSE_BOX + "\n" + 
                        before_text[last_block_tag_index:] + 
                        match_text + 
                        after_text
                    )
                else:
                    # Fallback if no block tag is found right before it
                    new_html = before_text + URGENT_DEFENSE_BOX + "\n" + match_text + after_text
                    
                # Write the changes
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_html)
                    
                print(f"  [+] Updated grievance page for {district_slug}")
                updated_count += 1
            else:
                print(f"  [SKIPPED] Could not find 'What is MDR' in {district_slug}")
                skipped_count += 1
                
        except Exception as e:
            # If a major crash happens, print the exact reason and continue to the next folder!
            print(f"  [ERROR] Crash while processing {district_slug}!")
            traceback.print_exc()
            error_count += 1

    print(f"\nDone! Updated: {updated_count} | Skipped: {skipped_count} | Errors: {error_count}")

if __name__ == "__main__":
    update_grievance_pages()