import os
import shutil
from bs4 import BeautifulSoup

class ARDLayoutIntegrator:
    def __init__(self, target_dir: str):
        self.target_dir = target_dir
        self.stats = {
            "files_scanned": 0,
            "files_updated": 0,
            "sidebars_removed": 0,
            "ctas_injected": 0
        }

        self.css_content = """
        /* ── AUTOMATED CRO PATCH: Layout & Mobile Fixes ── */
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background: #f8fafc; }
        h1 { font-size: 2.2rem; margin-top: 10px; font-family: 'Lora', serif; color: #0a2342; }
        
        /* Core Layout - Single Column Optimized for Readability */
        .layout-grid { max-width: 850px; margin: 30px auto; display: block; }
        .content-column { font-family: 'Source Sans 3', sans-serif; font-size: 17px; line-height: 1.75; color: #1a1a2e; background: #fff; padding: 40px 60px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0; }
        .content-column h2 { font-family: 'Lora', serif; font-size: 1.6rem; font-weight: 700; color: #0a2342; margin: 2.5rem 0 1rem; padding-top: 1.5rem; border-top: 2px solid #e8f0fe; }
        .content-column h3 { font-family: 'Lora', serif; font-size: 1.3rem; font-weight: 700; color: #1e3a8a; margin: 2rem 0 1rem; }
        .content-column p { margin: 0 0 1.25rem; }
        .content-column ul { padding-left: 20px; margin-bottom: 1.5rem; }
        .content-column li { margin-bottom: 8px; }

        /* Mobile Display & Padding Fixes */
        @media (max-width: 950px) {
            .content-column { padding: 20px !important; border: none !important; box-shadow: none !important; background: transparent !important; }
            .nav-menu { display: none !important; }
        }
        
        /* Protect Bot Banners from global style.css hijacking */
        .banner-btn { text-decoration: none !important; display: inline-block; border-radius: 6px; font-weight: 800; font-family: 'DM Sans', sans-serif; font-size: 16px; transition: all 0.2s ease; padding: 14px 28px; margin-top: 10px;}
        .banner-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .banner-btn-gold { background: #d4af37; color: #0f172a !important; }
        .banner-btn-blue { background: #1a56db; color: #fff !important; }
        .banner-btn-blue:hover { background: #1e3a8a; color: #fff !important; }
        
        /* Integrated Inline CTA Styles */
        .integrated-cta { margin: 3rem 0; border-radius: 12px; padding: 36px 28px; text-align: center; }
        .integrated-cta.light { background: #fff; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); }
        .integrated-cta.dark { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: #fff; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15); border: 1px solid #1e40af; }
        """

        self.cta_1_html = """
        <div class="integrated-cta light" id="inline-bot-1">
        <span style="background:#ef4444;color:#fff;padding:4px 12px;border-radius:50px;font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;display:inline-block;margin-bottom:12px;">Diagnostic Bot</span>
        <h3 style="font-family:'Lora',serif;font-size:1.5rem;margin:0 0 10px;color:#0a2342;border:none;padding:0;">Are Your ARD Rights Being Violated?</h3>
        <p style="font-family:'Source Sans 3',sans-serif;font-size:16px;color:#475569;margin:0 auto 18px;line-height:1.6;max-width:600px;">Take our 9-question ARD assessment to find out your next legal step before your meeting.</p>
        <a class="banner-btn banner-btn-blue" href="/tools/ard-rights-scan/index.html">Run Free ARD Audit →</a>
        </div>
        """

        self.cta_2_html = """
        <div class="integrated-cta dark" id="inline-bot-2">
        <span style="background:#d4af37;color:#0f172a;padding:4px 12px;border-radius:50px;font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;display:inline-block;margin-bottom:12px;">Premium AI Tool</span>
        <h3 style="font-family:'Lora',serif;font-size:1.6rem;margin:0 0 10px;color:#fff;border:none;padding:0;">Draft Your FIE Request</h3>
        <p style="font-family:'Source Sans 3',sans-serif;font-size:16px;color:#cbd5e1;margin:0 auto 18px;line-height:1.6;max-width:600px;">Sending a casual email is a mistake. Use our AI to write a legally binding letter that forces a response.</p>
        <a class="banner-btn banner-btn-gold" href="/resources/iep-letter/index.html">Draft My Letter — $25 →</a>
        </div>
        """

    def clean_old_elements(self, soup: BeautifulSoup) -> bool:
        """Removes sidebars, old mobile bots, and stacked offers."""
        modified = False
        
        # 1. Remove Sidebar
        sidebar = soup.find('aside', class_=lambda c: c and 'sidebar-column' in c)
        if sidebar:
            sidebar.decompose()
            self.stats["sidebars_removed"] += 1
            modified = True

        # 2. Remove Old Offers Container (the stacked Stripe boxes)
        offers = soup.find('div', id='premium-offers')
        if offers:
            offers.decompose()
            modified = True

        offers_container = soup.find('div', class_=lambda c: c and 'offers-container' in c)
        if offers_container:
            offers_container.decompose()
            modified = True

        # 3. Remove Old Mobile-Only Bots
        for old_bot_id in ['mobile-bot-1', 'mobile-bot-2']:
            old_bot = soup.find('div', id=old_bot_id)
            if old_bot:
                old_bot.decompose()
                modified = True
                
        return modified

    def inject_css(self, soup: BeautifulSoup) -> bool:
        """Replaces or injects the new single-column CSS into the head."""
        head = soup.find('head')
        if not head:
            return False
            
        existing_style = soup.find('style', id='cro-core-formatting')
        if existing_style:
            existing_style.string = self.css_content
            return True
        else:
            style_tag = soup.new_tag('style', id='cro-core-formatting')
            style_tag.string = self.css_content
            head.append(style_tag)
            return True

    def inject_inline_ctas(self, soup: BeautifulSoup) -> bool:
        """Dynamically inserts CTAs after specific headings."""
        modified = False
        
        # Insert CTA 1 after "What Is an ARD Meeting"
        if not soup.find('div', id='inline-bot-1'):
            for h2 in soup.find_all('h2'):
                if 'What Is an ARD' in h2.get_text():
                    cta1_soup = BeautifulSoup(self.cta_1_html, 'html.parser')
                    h2.insert_after(cta1_soup.div)
                    self.stats["ctas_injected"] += 1
                    modified = True
                    break

        # Insert CTA 2 after "Your 5-Day Notice Right"
        if not soup.find('div', id='inline-bot-2'):
            for h2 in soup.find_all('h2'):
                if '5-Day Notice' in h2.get_text() or 'Notice Right' in h2.get_text():
                    cta2_soup = BeautifulSoup(self.cta_2_html, 'html.parser')
                    h2.insert_after(cta2_soup.div)
                    self.stats["ctas_injected"] += 1
                    modified = True
                    break

        return modified

    def process_file(self, filepath: str):
        """Processes a single ARD file."""
        self.stats["files_scanned"] += 1
        print(f"Scanning: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')

        # Execute DOM surgeries
        changes = any([
            self.clean_old_elements(soup),
            self.inject_css(soup),
            self.inject_inline_ctas(soup)
        ])

        if changes:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            self.stats["files_updated"] += 1
            print(f" -> Updated {os.path.basename(filepath)}")

    def run(self):
        """Walks the target directory to find and fix ARD process guides."""
        print(f"Starting auto-integration in: {self.target_dir}")
        print("-" * 50)
        
        # Traverse directory looking for the ARD guide HTML files
        for root, dirs, files in os.walk(self.target_dir):
            for file in files:
                # Target specifically the ARD pages to ensure safety
                if "ard-process-guide" in file and file.endswith('.html'):
                    filepath = os.path.join(root, file)
                    self.process_file(filepath)
                    
        print("-" * 50)
        print("Integration Complete! CRO Report:")
        print(f"  Files Scanned:    {self.stats['files_scanned']}")
        print(f"  Files Updated:    {self.stats['files_updated']}")
        print(f"  Sidebars Removed: {self.stats['sidebars_removed']}")
        print(f"  CTAs Injected:    {self.stats['ctas_injected']}")

if __name__ == "__main__":
    # Pointing strictly to your requested local Windows directory
    TARGET_DIRECTORY = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"
    
    if os.path.exists(TARGET_DIRECTORY):
        integrator = ARDLayoutIntegrator(TARGET_DIRECTORY)
        integrator.run()
    else:
        print(f"Error: Could not find the directory at {TARGET_DIRECTORY}")
        print("Please check the path and try again.")