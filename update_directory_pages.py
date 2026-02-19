import os
import re
import traceback

# --- 1. The Promotional HTML to Inject ---
ALL_ACCESS_PASS_BOX = """
<div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 32px; margin: 40px 0; border-radius: 8px; text-align: center; color: white; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); border: 1px solid #1e3a8a;">
    <span style="background: #d4af37; color: #0f172a; padding: 6px 16px; border-radius: 50px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em;">Most Popular</span>
    
    <h3 style="margin: 20px 0 12px 0; color: #ffffff; font-family: 'Georgia', serif; font-size: 1.8rem;">The "Parent Protection" All-Access Pass</h3>
    
    <p style="color: #e2e8f0; max-width: 600px; margin: 0 auto 24px auto; font-family: sans-serif; font-size: 1.05rem; line-height: 1.6;">Includes our complete library: ARD Prep, Behavior Defense, Dyslexia, ADHD, and the Accommodations Encyclopedia.</p>
    
    <a href="https://buy.stripe.com/3cIcN4a8l7Q4d0j7mBbbG0G" style="background-color: #d4af37; color: #0f172a; padding: 16px 32px; text-decoration: none; border-radius: 4px; font-weight: 700; font-size: 1.1rem; display: inline-block; font-family: sans-serif; transition: transform 0.2s;">GET ALL 6 KITS FOR $97</a>
    
    <p style="margin-top: 16px; font-size: 0.85rem; color: #cbd5e1; font-family: sans-serif;">Instant Digital Access • Secure Stripe Checkout</p>
</div>
"""

# --- 2. Configuration ---
ROOT_DIR = "districts"
TARGET_FILE = "leadership-directory.html"

def update_directory_pages():
    if not os.path.exists(ROOT_DIR):
        print(f"[ERROR] Cannot find '{ROOT_DIR}' directory. Ensure you are running this from the project root.")
        return

    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for district_slug in os.listdir(ROOT_DIR):
        try:
            district_path = os.path.join(ROOT_DIR, district_slug)
            
            # Skip if it's a file instead of a folder
            if not os.path.isdir(district_path):
                continue
                
            file_path = os.path.join(district_path, TARGET_FILE)
            
            # Skip if the directory page doesn't exist
            if not os.path.exists(file_path):
                continue

            # Read safely, ignoring weird characters
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                html_content = f.read()

            # Prevent double-inserting if run multiple times
            if "GET ALL 6 KITS FOR $97" in html_content:
                print(f"  [SKIPPED] All-Access box already exists in {district_slug}")
                skipped_count += 1
                continue

            # Inject the new box right after the closing </table> tag
            # We use re.sub with a limit of 1 to ensure it only happens once per page
            pattern = r'(</table>)'
            
            if re.search(pattern, html_content, flags=re.IGNORECASE):
                # Replace the </table> tag with </table> followed by our new box
                html_content = re.sub(
                    pattern, 
                    r'\1\n\n\n' + ALL_ACCESS_PASS_BOX + '\n', 
                    html_content, 
                    count=1, 
                    flags=re.IGNORECASE
                )
                
                # Write changes back to file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                    
                print(f"  [+] Injected All-Access box into {district_slug}")
                updated_count += 1
            else:
                print(f"  [SKIPPED] Could not find </table> insertion point in {district_slug}")
                skipped_count += 1
                
        except Exception as e:
            print(f"  [ERROR] Crash while processing {district_slug}!")
            traceback.print_exc()
            error_count += 1

    print(f"\nDeployment Complete! Updated: {updated_count} | Skipped: {skipped_count} | Errors: {error_count}")

if __name__ == "__main__":
    update_directory_pages()