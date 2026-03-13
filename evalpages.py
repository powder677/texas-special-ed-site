import os
from bs4 import BeautifulSoup

class EvaluationLayoutIntegrator:
    def __init__(self, target_dir: str):
        self.target_dir = target_dir
        self.stats = {
            "files_scanned": 0,
            "files_updated": 0,
            "sidebars_removed": 0,
            "old_ctas_cleared": 0,
            "new_ctas_injected": 0,
            "structures_standardized": 0
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

        /* Protect Bot Banners */
        .banner-btn { text-decoration: none !important; display: inline-block; border-radius: 6px; font-weight: 800; font-family: 'DM Sans', sans-serif; font-size: 16px; transition: all 0.2s ease; padding: 14px 28px; margin-top: 10px;}
        .banner-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .banner-btn-gold { background: #d4af37; color: #0f172a !important; }
        .banner-btn-blue { background: #1a56db; color: #fff !important; }
        .banner-btn-slate { background: #cbd5e1; color: #0f172a !important; }
        
        .integrated-cta { margin: 3rem 0; border-radius: 12px; padding: 36px 28px; text-align: center; }
        .integrated-cta.light { background: #fff; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); }
        .integrated-cta.dark { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: #fff; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15); border: 1px solid #1e40af; }
        .integrated-cta.slate { background: linear-gradient(135deg, #334155 0%, #0f172a 100%); color: #fff; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15); border: 1px solid #1e293b; }

        details { border-bottom: 1px solid #e2e8f0; padding: 16px 0; cursor: pointer; }
        summary { font-weight: 600; list-style: none; display: flex; justify-content: space-between; align-items: center; font-family: 'Source Sans 3', sans-serif; font-size: 1.1rem; color: #0f172a; }
        summary::-webkit-details-marker { display: none; }
        details p { margin: 12px 0 0; color: #475569; line-height: 1.7; }
        """

        self.header_html = """
<header class="site-header">
<nav aria-label="Main navigation" class="navbar" role="navigation">
<div class="nav-container">
<div class="nav-logo">
<a aria-label="Texas Special Ed Home" class="text-logo" href="/">Texas <em>Special Ed</em></a>
</div>
<button aria-expanded="false" aria-label="Toggle menu" class="mobile-menu-toggle">
<span class="hamburger"></span><span class="hamburger"></span><span class="hamburger"></span>
</button>
<ul class="nav-menu">
<li class="nav-item"><a class="nav-link" href="/">Home</a></li>
<li class="nav-item"><a class="nav-link" href="/districts/index.html">Districts</a></li>
<li class="nav-item"><a class="nav-link" href="/resources/index.html">Resources</a></li>
<li class="nav-item nav-cta">
<a href="/resources/Iep-letter" style="background:#d4af37;color:#0f172a;padding:10px 18px;border-radius:4px;font-weight:700;font-size:14px;text-decoration:none;">Get Your Letter — $25</a>
</li>
</ul>
</div>
</nav>
</header>
"""

        self.footer_html = """
<footer class="site-footer">
<div class="footer-container">
<div class="footer-about">
<img alt="Texas Special Ed Logo" height="auto" src="/images/texasspecialed-logo.png" width="160"/>
<p>© 2026 Texas Special Education Resources. Not affiliated with the TEA.</p>
</div>
</div>
</footer>
<script>
document.addEventListener('DOMContentLoaded', function() {
    var toggle = document.querySelector('.mobile-menu-toggle');
    var menu   = document.querySelector('.nav-menu');
    if (toggle && menu) {
        toggle.addEventListener('click', function() { menu.classList.toggle('active'); });
    }
});
</script>
"""

        self.cta_1_html = """
        <div class="integrated-cta dark" id="inline-bot-1">
        <span style="background:#d4af37;color:#0f172a;padding:4px 12px;border-radius:50px;font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;display:inline-block;margin-bottom:12px;">Premium AI Tool</span>
        <h3 style="font-family:'Lora',serif;font-size:1.6rem;margin:0 0 10px;color:#fff;border:none;padding:0;">Draft Your FIE Request</h3>
        <p style="font-family:'Source Sans 3',sans-serif;font-size:16px;color:#cbd5e1;margin:0 auto 18px;line-height:1.6;max-width:600px;">Sending a casual email is a mistake. Use our AI to write a legally binding evaluation letter that forces the 15-day district response clock.</p>
        <a class="banner-btn banner-btn-gold" href="/resources/iep-letter/index.html">Draft My Letter — $25 →</a>
        </div>
        """

        self.cta_2_html = """
        <div class="integrated-cta light" id="inline-bot-2">
        <span style="background:#ef4444;color:#fff;padding:4px 12px;border-radius:50px;font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;display:inline-block;margin-bottom:12px;">Diagnostic Bot</span>
        <h3 style="font-family:'Lora',serif;font-size:1.5rem;margin:0 0 10px;color:#0a2342;border:none;padding:0;">Is the school ignoring your request?</h3>
        <p style="font-family:'Source Sans 3',sans-serif;font-size:16px;color:#475569;margin:0 auto 18px;line-height:1.6;max-width:600px;">If the district has refused to evaluate your child, or they are forcing you to try "RTI interventions" before testing, they may be violating Child Find laws.</p>
        <a class="banner-btn banner-btn-blue" href="/tools/ard-rights-scan/index.html">Run Free Rights Audit →</a>
        </div>
        """

        self.cta_3_html = """
        <div class="integrated-cta slate" id="inline-bot-3">
        <span style="background:#cbd5e1;color:#0f172a;padding:4px 12px;border-radius:50px;font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;display:inline-block;margin-bottom:12px;">IEP & 504 Planning</span>
        <h3 style="font-family:'Lora',serif;font-size:1.6rem;margin:0 0 10px;color:#fff;border:none;padding:0;">The Accommodations Encyclopedia</h3>
        <p style="font-family:'Source Sans 3',sans-serif;font-size:16px;color:#cbd5e1;margin:0 auto 18px;line-height:1.6;max-width:600px;">Once the evaluation is done, stop guessing what supports to ask for. Use our evidence-based "If/Then" decision matrix to match your child's specific diagnosis to research-backed interventions.</p>
        <a class="banner-btn banner-btn-slate" href="https://buy.stripe.com/3cIcN43JX9Yc7FZ6ixbbG0F" target="_blank">Get the Encyclopedia — $27</a>
        </div>
        """

    def standardize_page_structure(self, soup: BeautifulSoup) -> bool:
        """Injects Nav/Footer and wraps content in the layout grid if missing."""
        modified = False
        body = soup.find('body')
        if not body: return False

        # 1. Inject Header/Nav if missing
        if not soup.find('header') and not soup.find(class_='site-header'):
            header_soup = BeautifulSoup(self.header_html, 'html.parser')
            body.insert(0, header_soup.header)
            modified = True

        # 2. Wrap main content in layout grid
        if not soup.find(class_='layout-grid'):
            # Group all content that isn't header/footer/nav
            layout_grid = soup.new_tag('div', attrs={'class': 'layout-grid'})
            content_col = soup.new_tag('article', attrs={'class': 'content-column'})
            layout_grid.append(content_col)
            
            # Find the primary content container (usually .container)
            container = soup.find('main') or soup.find('div', class_='container')
            if container:
                # Move children into content column
                children = list(container.children)
                for child in children:
                    if child.name not in ['h1', 'header', 'nav', 'footer']:
                        content_col.append(child.extract())
                container.append(layout_grid)
                modified = True
                self.stats["structures_standardized"] += 1

        # 3. Inject Footer if missing
        if not soup.find('footer') and not soup.find(class_='site-footer'):
            footer_soup = BeautifulSoup(self.footer_html, 'html.parser')
            body.append(footer_soup.footer)
            body.append(footer_soup.script)
            modified = True

        return modified

    def clean_slate(self, soup: BeautifulSoup) -> bool:
        """Removes sidebars and old CTA formats."""
        modified = False
        for s in soup.find_all(['aside', 'div'], class_=lambda c: c and ('sidebar' in c or 'offers-container' in c)):
            s.decompose()
            modified = True
            self.stats["sidebars_removed"] += 1
        for old_cta in soup.find_all('div', class_=lambda c: c and ('inline-cta' in c or 'integrated-cta' in c)):
            old_cta.decompose()
            self.stats["old_ctas_cleared"] += 1
            modified = True
        return modified

    def inject_css(self, soup: BeautifulSoup) -> bool:
        head = soup.find('head')
        if not head: return False
        existing = soup.find('style', id='cro-core-formatting')
        if existing: existing.string = self.css_content
        else:
            style = soup.new_tag('style', id='cro-core-formatting')
            style.string = self.css_content
            head.append(style)
        return True

    def inject_ctas(self, soup: BeautifulSoup) -> bool:
        modified = False
        def insert_after_kw(keywords, html):
            for h2 in soup.find_all('h2'):
                if any(kw in h2.get_text().lower() for kw in keywords):
                    cta = BeautifulSoup(html, 'html.parser')
                    h2.insert_after(cta.div)
                    return True
            return False

        if insert_after_kw(["requesting", "understanding the full"], self.cta_1_html):
            self.stats["new_ctas_injected"] += 1
            modified = True
        if insert_after_kw(["submit", "how to request"], self.cta_2_html):
            self.stats["new_ctas_injected"] += 1
            modified = True
        if insert_after_kw(["refuses", "eligibility meeting"], self.cta_3_html):
            self.stats["new_ctas_injected"] += 1
            modified = True
        return modified

    def process_file(self, filepath: str):
        self.stats["files_scanned"] += 1
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        changes = any([
            self.standardize_page_structure(soup),
            self.clean_slate(soup),
            self.inject_css(soup),
            self.inject_ctas(soup)
        ])

        if changes:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            self.stats["files_updated"] += 1

    def run(self):
        print(f"Scanning: {self.target_dir}")
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                if "evaluation-child-find" in file and file.endswith('.html'):
                    self.process_file(os.path.join(root, file))
        
        print("-" * 30)
        print(f"Scanned: {self.stats['files_scanned']}")
        print(f"Updated: {self.stats['files_updated']}")
        print(f"Nav/Layout Patch: {self.stats['structures_standardized']}")
        print(f"CTAs Injected: {self.stats['new_ctas_injected']}")

if __name__ == "__main__":
    TARGET = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"
    if os.path.exists(TARGET):
        EvaluationLayoutIntegrator(TARGET).run()