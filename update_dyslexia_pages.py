import os
import re
import traceback

# --- 1. The Premium HTML & CSS to Inject ---
PREMIUM_DYSLEXIA_BOX = """
<style>
  /* --- Premium Vertical Offers Box CSS --- */
  .premium-offers-container {
    background: linear-gradient(145deg, #ffffff, #f8fafc);
    border: 2px solid #e2e8f0;
    border-radius: 16px;
    padding: 35px 25px;
    margin: 40px 0;
    box-shadow: 0 20px 40px -10px rgba(0,0,0,0.08);
    position: relative;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }

  /* Floating Header Badge */
  .offers-header-badge {
    position: absolute;
    top: -16px;
    left: 50%;
    transform: translateX(-50%);
    background: #0f172a;
    color: #ffffff;
    padding: 6px 20px;
    font-size: 0.85rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    border-radius: 30px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    white-space: nowrap;
  }

  .premium-offers-header {
    text-align: center;
    margin-bottom: 30px;
  }

  .premium-offers-header h2 {
    color: #0f172a;
    font-size: 1.75rem;
    margin: 0 0 8px 0;
    font-weight: 800;
  }

  .premium-offers-header p {
    color: #64748b;
    font-size: 1.05rem;
    margin: 0;
  }

  /* Individual Stacked Cards */
  .stacked-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-bottom: 20px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
  }

  /* Hover Effect */
  .stacked-card:hover {
    transform: translateY(-6px) scale(1.01);
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
    border-color: #cbd5e1;
  }

  /* Accent Borders */
  .border-red { border-left: 6px solid #ef4444; }

  /* Card Layout: Split content and checkout */
  .card-inner {
    display: flex;
    flex-direction: column;
  }

  .card-main-content {
    padding: 24px;
    flex: 1;
  }

  .card-checkout-zone {
    background: #f8fafc;
    padding: 24px;
    border-top: 1px solid #e2e8f0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
  }

  /* Typography & Tags */
  .topic-tag {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 12px;
  }
  .tag-red { background: #fef2f2; color: #b91c1c; }

  .card-title {
    font-size: 1.35rem;
    color: #0f172a;
    margin: 0 0 6px 0;
    font-weight: 800;
  }

  .card-tagline {
    font-size: 0.95rem;
    font-weight: 600;
    color: #475569;
    margin: 0 0 12px 0;
    font-style: italic;
  }

  .card-desc {
    font-size: 0.95rem;
    color: #334155;
    line-height: 1.5;
    margin: 0 0 16px 0;
  }

  .card-bullets {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .card-bullets li {
    font-size: 0.9rem;
    color: #475569;
    margin-bottom: 8px;
    display: flex;
    align-items: flex-start;
  }

  .card-bullets li::before {
    content: '✓';
    color: #10b981;
    font-weight: bold;
    margin-right: 8px;
  }

  /* Pricing & Buttons */
  .price-block {
    margin-bottom: 16px;
  }
  .price-label {
    display: block;
    font-size: 0.8rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
  }
  .price-amount {
    font-size: 1.8rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1;
  }

  .btn-premium {
    background: #16a34a;
    color: white;
    text-decoration: none;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 1rem;
    display: inline-block;
    width: 100%;
    transition: background 0.2s;
    box-shadow: 0 4px 6px -1px rgba(22, 163, 74, 0.2);
  }
  .btn-premium:hover {
    background: #15803d;
  }

  /* Desktop View */
  @media (min-width: 768px) {
    .card-inner { flex-direction: row; }
    .card-checkout-zone { border-top: none; border-left: 1px solid #e2e8f0; width: 220px; padding: 30px 20px; }
    .card-main-content { padding: 30px; }
  }
</style>

<div class="premium-offers-container">
  <div class="offers-header-badge">Targeted Reading Support</div>
  
  <div class="premium-offers-header">
    <h2>Don't Let the School "Wait and See"</h2>
    <p>Get the definitive Texas roadmap for HB 3928 and the dyslexia evaluation process.</p>
  </div>

  <div class="stacked-card border-red">
    <div class="card-inner">
      <div class="card-main-content">
        <span class="topic-tag tag-red">Dyslexia / Reading</span>
        <h3 class="card-title">Dyslexia Parent Support Toolkit</h3>
        <p class="card-tagline">Don't Let the School "Wait and See."</p>
        <p class="card-desc">The definitive Texas roadmap for HB 3928 and the dyslexia evaluation process. Includes legally cited request templates, the 15-45-30 timeline breakdown, and structured literacy progress logs.</p>
        <ul class="card-bullets">
          <li>Pre-written FIIE request letters</li>
          <li>HB 3928 timeline decoder</li>
          <li>504 → IEP transition guide</li>
          <li>Structured literacy progress tracker</li>
        </ul>
      </div>
      <div class="card-checkout-zone">
        <div class="price-block">
          <span class="price-label">Complete Kit</span>
          <span class="price-amount">$37.00</span>
        </div>
        <a href="https://buy.stripe.com/14A00i5S5eesd0jgXbbbG0J" class="btn-premium">Buy Now →</a>
      </div>
    </div>
  </div>
</div>
"""

# --- 2. Configuration ---
ROOT_DIR = "districts"

# IMPORTANT: Change this if your dyslexia file is named something else!
TARGET_FILE = "dyslexia-services.html" 

# This regex finds the entire Quick Answer box 
QUICK_ANSWER_PATTERN = r'(<div class="quick-answer"[^>]*>.*?</div>)'

# This regex finds the specific sales card at the bottom of the page to remove
OLD_SALES_CARD_PATTERN = r'<div class="sales-card"[^>]*>.*?</div>'

def update_dyslexia_pages():
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
            
            # Skip if the Dyslexia page doesn't exist in this folder yet
            if not os.path.exists(file_path):
                continue

            # Read safely
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                html_content = f.read()

            # Prevent double-inserting if run multiple times
            if "premium-offers-container" in html_content and "Dyslexia Parent Support Toolkit" in html_content:
                print(f"  [SKIPPED] Offers box already exists in {district_slug}")
                skipped_count += 1
                continue

            # 1. Remove the old sales card at the bottom
            html_content = re.sub(OLD_SALES_CARD_PATTERN, '', html_content, flags=re.DOTALL | re.IGNORECASE)

            # 2. Inject the new premium offer under the Quick Answer box
            match = re.search(QUICK_ANSWER_PATTERN, html_content, flags=re.IGNORECASE | re.DOTALL)
            
            if match:
                # Insert the new box right after the end of the Quick Answer block
                html_content = (
                    html_content[:match.end()] + 
                    "\n\n\n" + 
                    PREMIUM_DYSLEXIA_BOX + 
                    "\n\n" + 
                    html_content[match.end():]
                )
                
                # Write changes back to file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                    
                print(f"  [+] Injected vertical offer and removed bottom box in {district_slug}")
                updated_count += 1
            else:
                # Fallback: if no Quick Answer is found, put it at the top of the <main> block
                fallback_match = re.search(r'(<main[^>]*>.*?</h1>)', html_content, flags=re.IGNORECASE | re.DOTALL)
                if fallback_match:
                    html_content = (
                        html_content[:fallback_match.end()] + 
                        "\n\n\n" + 
                        PREMIUM_DYSLEXIA_BOX + 
                        "\n\n" + 
                        html_content[fallback_match.end():]
                    )
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(html_content)
                    print(f"  [+] Injected via fallback placement into {district_slug}")
                    updated_count += 1
                else:
                    print(f"  [SKIPPED] Could not find insertion point in {district_slug}")
                    skipped_count += 1
                
        except Exception as e:
            print(f"  [ERROR] Crash while processing {district_slug}!")
            traceback.print_exc()
            error_count += 1

    print(f"\nDeployment Complete! Updated: {updated_count} | Skipped: {skipped_count} | Errors: {error_count}")

if __name__ == "__main__":
    update_dyslexia_pages()