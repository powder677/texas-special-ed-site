import os
from bs4 import BeautifulSoup

class DyslexiaLayoutIntegrator:
    def __init__(self, target_dir: str):
        self.target_dir = target_dir
        self.stats = {
            "files_scanned": 0,
            "files_updated": 0,
            "sidebars_removed": 0,
            "old_ctas_cleared": 0,
            "new_ctas_injected": 0
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
        
        /* Scannable Blocks */
        .pull-quote { border-left: 4px solid #1a56db; margin: 2rem 0; padding: 20px 24px; background: #f8fbff; border-radius: 0 8px 8px 0; font-size: 1.15rem; font-style: italic; color: #1e3a8a; line-height: 1.6; }
        .action-steps { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 28px 32px; margin: 2.5rem 0; }
        .action-steps h2 { border-top: none; margin-top: 0; padding-top: 0; font-size: 1.4rem; color: #166534; }
        .action-steps ol { padding-left: 1.4rem; margin: 0; font-size: 17px; }
        .action-steps li { margin-bottom: 14px; line-height: 1.65; color: #166534;}
        .action-steps strong { color: #14532d; }

        .iep-list { list-style: none; padding: 0; margin: 1.5rem 0 2.5rem; }
        .iep-list li { display: flex; gap: 20px; padding: 20px 0; border-bottom: 1px solid #e8f0fe; font-size: 17px; }
        .iep-list li:last-child { border-bottom: none; }
        .iep-list li::before { content: "✓"; background: #1a56db; color: #fff; font-weight: 700; font-size: 14px; border-radius: 50%; min-width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px; }
        .iep-list strong { display: block; margin-bottom: 6px; color: #0f172a; font-size: 1.1rem; }
        .section-divider { text-align: center; color: #9ab0cc; font-size: 24px; margin: 3rem 0; letter-spacing: 0.4em; }

        /* Protect Bot Banners from global style.css hijacking */
        .banner-btn { text-decoration: none !important; display: inline-block; border-radius: 6px; font-weight: 800; font-family: 'DM Sans', sans-serif; font-size: 16px; transition: all 0.2s ease; padding: 14px 28px; margin-top: 10px;}
        .banner-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .banner-btn-gold { background: #d4af37; color: #0f172a !important; }
        .banner-btn-blue { background: #1a56db; color: #fff !important; }
        .banner-btn-blue:hover { background: #1e3a8a; color: #fff !important; }
        .banner-btn-red { background: #fca5a5; color: #450a0a !important; }
        .banner-btn-red:hover { background: #ef4444; color: #fff !important; }
        
        /* Integrated Inline CTA Styles */
        .integrated-cta { margin: 3rem 0; border-radius: 12px; padding: 36px 28px; text-align: center; }
        .integrated-cta.light { background: #fff; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); }
        .integrated-cta.dark { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: #fff; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15); border: 1px solid #1e40af; }
        .integrated-cta.red { background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%); color: #fff; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15); border: 1px solid #991b1b; }
        """

        self.cta_1_html = """
        <div class="integrated-cta light" id="inline-bot-1">
        <span style="background:#ef4444;color:#fff;padding:4px 12px;border-radius:50px;font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;display:inline-block;margin-bottom:12px;">Diagnostic Bot</span>
        <h3 style="font-family:'Lora',serif;font-size:1.5rem;margin:0 0 10px;color:#0a2342;border:none;padding:0;">Are Your ARD & 504 Rights Being Violated?</h3>
        <p style="font-family:'Source Sans 3',sans-serif;font-size:16px;color:#475569;margin:0 auto 18px;line-height:1.6;max-width:600px;">Take our free assessment to instantly find out your next legal step if the district is delaying testing.</p>
        <a class="banner-btn banner-btn-blue" href="/tools/ard-rights-scan/index.html">Run Free Rights Audit →</a>
        </div>
        """

        self.cta_2_html = """
        <div class="integrated-cta dark" id="inline-bot-2">
        <span style="background:#d4af37;color:#0f172a;padding:4px 12px;border-radius:50px;font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;display:inline-block;margin-bottom:12px;">Premium AI Tool</span>
        <h3 style="font-family:'Lora',serif;font-size:1.6rem;margin:0 0 10px;color:#fff;border:none;padding:0;">Draft Your FIE Dyslexia Request</h3>
        <p style="font-family:'Source Sans 3',sans-serif;font-size:16px;color:#cbd5e1;margin:0 auto 18px;line-height:1.6;max-width:600px;">Sending a casual email is a mistake. Use our AI to write a legally binding evaluation letter that forces the 15-day district response clock.</p>
        <a class="banner-btn banner-btn-gold" href="/tools/fie-letter-bot/index.html">Draft My Letter — $25 →</a>
        </div>
        """

        self.cta_3_html = """
        <div class="integrated-cta red" id="inline-bot-3">
        <span style="background:#fca5a5;color:#450a0a;padding:4px 12px;border-radius:50px;font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;display:inline-block;margin-bottom:12px;">Targeted Support</span>
        <h3 style="font-family:'Lora',serif;font-size:1.6rem;margin:0 0 10px;color:#fff;border:none;padding:0;">Tired of the "Wait and See" approach?</h3>
        <p style="font-family:'Source Sans 3',sans-serif;font-size:16px;color:#fca5a5;margin:0 auto 18px;line-height:1.6;max-width:600px;">Learn exactly how to force an evaluation, navigate the HB 3928 timelines, and transition your child from a basic 504 Plan to a fully protected IEP.</p>
        <a class="banner-btn banner-btn-red" href="https://buy.stripe.com/14A00i5S5eesd0jgXbbbG0J" target="_blank">Get the Dyslexia Toolkit — $37</a>
        </div>
        """

    def clean_slate(self, soup: BeautifulSoup) -> bool:
        """Removes sidebars, old premium offers, and wipes all existing inline CTAs."""
        modified = False
        
        # Remove Sidebars
        sidebar = soup.find('aside', class_=lambda c: c and 'sidebar-column' in c)
        if sidebar:
            sidebar.decompose()
            self.stats["sidebars_removed"] += 1
            modified = True

        # Remove Stacked Offers Containers
        offers = soup.find('div', id='premium-offers')
        if offers:
            offers.decompose()
            modified = True

        offers_container = soup.find('div', class_=lambda c: c and 'offers-container' in c)
        if offers_container:
            offers_container.decompose()
            modified = True

        # Wipe ALL old inline/integrated CTAs to ensure no duplicates
        for old_cta in soup.find_all('div', class_=lambda c: c and ('inline-cta' in c or 'integrated-cta' in c)):
            old_cta.decompose()
            self.stats["old_ctas_cleared"] += 1
            modified = True
            
        return modified

    def inject_css(self, soup: BeautifulSoup) -> bool:
        """Injects or updates the layout CSS block."""
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

    def inject_ctas(self, soup: BeautifulSoup) -> bool:
        """Precisely injects the 3 new narrative CTAs after specific headings."""
        modified = False
        
        # Helper to safely parse and insert HTML
        def insert_cta_after_h2(h2_text_match, cta_html):
            for h2 in soup.find_all('h2'):
                if h2_text_match.lower() in h2.get_text().lower():
                    cta_soup = BeautifulSoup(cta_html, 'html.parser')
                    h2.insert_after(cta_soup.div)
                    return True
            return False

        # 1. Light Bot after "The Texas Dyslexia Handbook"
        if insert_cta_after_h2("Handbook", self.cta_1_html):
            self.stats["new_ctas_injected"] += 1
            modified = True

        # 2. Dark Bot after "Structured Literacy Programs"
        if insert_cta_after_h2("Structured Literacy", self.cta_2_html):
            self.stats["new_ctas_injected"] += 1
            modified = True
            
        # 3. Red Dyslexia Toolkit after "504 Plan vs. IEP"
        if insert_cta_after_h2("504 Plan vs. IEP", self.cta_3_html):
            self.stats["new_ctas_injected"] += 1
            modified = True

        return modified

    def process_file(self, filepath: str):
        self.stats["files_scanned"] += 1
        print(f"Scanning: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')

        # Run the operations in order: Clean -> Style -> Inject
        changes = any([
            self.clean_slate(soup),
            self.inject_css(soup),
            self.inject_ctas(soup)
        ])

        if changes:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            self.stats["files_updated"] += 1
            print(f" -> Optimized {os.path.basename(filepath)}")

    def run(self):
        print(f"Starting Dyslexia auto-integration in: {self.target_dir}")
        print("-" * 50)
        
        # Traverse directory looking strictly for dyslexia files
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                if "dyslexia-services" in file and file.endswith('.html'):
                    filepath = os.path.join(root, file)
                    self.process_file(filepath)
                    
        print("-" * 50)
        print("Integration Complete! Dyslexia CRO Report:")
        print(f"  Files Scanned:       {self.stats['files_scanned']}")
        print(f"  Files Updated:       {self.stats['files_updated']}")
        print(f"  Sidebars Purged:     {self.stats['sidebars_removed']}")
        print(f"  Old CTAs Cleared:    {self.stats['old_ctas_cleared']}")
        print(f"  New CTAs Injected:   {self.stats['new_ctas_injected']}")

if __name__ == "__main__":
    # Pointing strictly to your requested local Windows directory
    TARGET_DIRECTORY = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"
    
    if os.path.exists(TARGET_DIRECTORY):
        integrator = DyslexiaLayoutIntegrator(TARGET_DIRECTORY)
        integrator.run()
    else:
        print(f"Error: Could not find the directory at {TARGET_DIRECTORY}")
        print("Please check the path and try again.")