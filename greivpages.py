import os
import re
from bs4 import BeautifulSoup

class GrievanceLayoutIntegrator:
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

        self.css_content = """
        /* ── DISCIPLINE & GRIEVANCE PATCH: Optimized for Mobile & CRO ── */
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background: #f8fafc; }
        
        h1 { font-size: clamp(1.8rem, 5vw, 2.2rem); margin-top: 10px; font-family: 'Lora', serif; color: #0a2342; text-align: center; padding: 0 15px; }
        
        .layout-grid { max-width: 850px; margin: 20px auto; display: block; width: 100%; }
        
        .content-column { 
            font-family: 'Source Sans 3', sans-serif; 
            font-size: 17px; 
            line-height: 1.75; 
            color: #1a1a2e; 
            background: #fff; 
            padding: 40px 60px; 
            border-radius: 12px; 
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); 
            border: 1px solid #e2e8f0; 
            margin: 0 15px;
        }

        .content-column h2 { font-family: 'Lora', serif; font-size: clamp(1.4rem, 4vw, 1.6rem); font-weight: 700; color: #0a2342; margin: 2.5rem 0 1rem; padding-top: 1.5rem; border-top: 2px solid #e8f0fe; }
        
        /* Mobile Overrides */
        @media (max-width: 768px) {
            .content-column { 
                padding: 30px 20px !important; 
                margin: 0 !important; 
                border-radius: 0 !important; 
                border-left: none !important; 
                border-right: none !important; 
                box-shadow: none !important;
            }
            .ai-tool-banner { padding: 30px 20px !important; border-radius: 0 !important; margin: 2rem -20px !important; }
            .integrated-cta { padding: 30px 20px !important; border-radius: 0 !important; margin: 2rem -20px !important; }
        }

        /* AI Tool Styling */
        .ai-tool-banner { 
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); 
            color: white; 
            border-radius: 16px; 
            padding: 40px; 
            margin: 3rem 0; 
            text-align: center; 
            border: 1px solid #2a4382; 
        }
        .ai-tool-banner h3 { font-family: 'Lora', serif; font-size: clamp(1.5rem, 5vw, 1.8rem); color: #fff; margin: 0 0 10px; border:none; }
        
        .btn-gold { 
            background: #d4af37; 
            color: #0f172a !important; 
            padding: 16px 32px; 
            border-radius: 8px; 
            font-weight: 800; 
            text-decoration: none; 
            display: inline-block; 
            transition: 0.2s; 
            border: none; 
            cursor: pointer; 
            width: auto;
            max-width: 100%;
        }
        .btn-gold:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }

        .integrated-cta { margin: 3rem 0; border-radius: 12px; padding: 36px 28px; text-align: center; }
        .integrated-cta.dark { background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%); color: #fff; border: 1px solid #991b1b; }
        
        /* Modal & Mobile Accessibility */
        #ai-modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.8); z-index: 10000; backdrop-filter: blur(4px); overflow-y: auto; }
        .modal-content { 
            background: white; 
            max-width: 600px; 
            width: 95%; 
            margin: 20px auto; 
            border-radius: 16px; 
            overflow: hidden; 
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); 
            font-family: sans-serif; 
            position: relative;
        }
        @media (max-height: 600px) {
            .modal-content { margin: 10px auto; }
        }
        """

        self.ai_tool_cta = """
        <div class="ai-tool-banner">
            <span style="background:#d4af37;color:#0f172a;padding:4px 12px;border-radius:50px;font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;display:inline-block;margin-bottom:12px;">Live AI Tool</span>
            <h3>Free ARD Rights Scan</h3>
            <p style="font-size:1.1rem;color:#cbd5e1;margin-bottom:24px;max-width:600px;margin-left:auto;margin-right:auto;">Wondering if the school violated your child's rights? Answer a few questions for an instant analysis based on Texas law.</p>
            <button class="btn-gold" onclick="openRightsScan()">Run My Free ARD Scan →</button>
        </div>
        """

        self.defense_kit_cta = """
        <div class="integrated-cta dark">
            <span style="background:#fca5a5;color:#450a0a;padding:4px 12px;border-radius:50px;font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;display:inline-block;margin-bottom:12px;">Urgent Defense</span>
            <h3 style="font-family:'Lora',serif;font-size:1.6rem;margin:0 0 10px;color:#fff;border:none;">The Behavior & Discipline Defense Kit</h3>
            <p style="font-size:16px;color:#fecaca;margin:0 auto 20px;max-width:550px;">Protect your child from DAEP and informal suspensions. Includes the Shadow Discipline Tracker and exact scripts to win your MDR hearing.</p>
            <a class="btn-gold" href="https://buy.stripe.com/bJe14mcgt6M0d0j8qFbbG0I" target="_blank" style="background:#fca5a5;">Get Defense Kit — $47</a>
        </div>
        """

        self.iep_letter_cta = """
        <div class="ai-tool-banner">
            <span style="background:#cbd5e1;color:#0f172a;padding:4px 12px;border-radius:50px;font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;display:inline-block;margin-bottom:12px;">Official Request</span>
            <h3>Show the ISD You Mean Business</h3>
            <p style="font-size:1.1rem;color:#cbd5e1;margin-bottom:24px;max-width:600px;margin-left:auto;margin-right:auto;">A verbal request has no legal weight. A formal Level 1 Grievance letter starts the official district clock.</p>
            <a class="btn-gold" href="/resources/Iep-letter.html">Get Your Letter — $25 →</a>
        </div>
        """

        self.ai_modal_and_script = """
<div id="ai-modal-overlay">
    <div class="modal-content">
        <div style="padding:20px; background:#0f172a; color:white; display:flex; justify-content:space-between; align-items:center;">
            <h3 style="margin:0; font-family:'Lora',serif;">ARD Rights Analysis</h3>
            <button onclick="closeRightsScan()" style="background:none; border:none; color:white; font-size:24px; cursor:pointer;">&times;</button>
        </div>
        <div style="padding:25px;" id="modal-body">
            <div id="scan-form">
                <p style="color:#475569; margin-bottom:20px; font-size:15px;">Describe the situation (e.g., suspension days, manifestation hearing outcome).</p>
                <textarea id="situation-text" style="width:100%; padding:12px; border:1px solid #cbd5e1; border-radius:8px; height:120px; font-size:16px;" placeholder="Explain what happened..."></textarea>
                <button onclick="runAnalysis()" id="run-scan-btn" style="width:100%; background:#1a56db; color:white; padding:16px; border-radius:8px; font-weight:700; border:none; cursor:pointer; margin-top:15px; font-size:16px;">Start Rights Scan</button>
            </div>
            <div id="scan-results" style="display:none;">
                <div id="analysis-content" style="color:#1e293b; line-height:1.6; font-size:15px;"></div>
                <button onclick="closeRightsScan()" style="width:100%; margin-top:20px; background:#f1f5f9; border:none; padding:12px; border-radius:8px; cursor:pointer; font-weight:700;">Close</button>
            </div>
        </div>
    </div>
</div>
<script>
    const apiKey = ""; 
    function openRightsScan() { 
        document.getElementById('ai-modal-overlay').style.display='block';
        document.body.style.overflow = 'hidden'; // Prevent background scroll
    }
    function closeRightsScan() { 
        document.getElementById('ai-modal-overlay').style.display='none';
        document.body.style.overflow = 'auto';
    }
    async function runAnalysis() {
        const sit = document.getElementById('situation-text').value;
        const btn = document.getElementById('run-scan-btn');
        if(!sit) return alert("Please describe the situation.");
        btn.innerText = "Analyzing...";
        btn.disabled = true;
        try {
            const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
                method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({ 
                    contents: [{ parts: [{ text: "Analyze the following special education discipline situation under Texas IDEA regulations and provide clear guidance: " + sit }] }],
                    systemInstruction: { parts: [{ text: "You are a Texas Special Education Law Expert. Format responses with bold headers and clear bullet points. Keep it professional and supportive." }] }
                })
            });
            const d = await r.json();
            const txt = d.candidates[0].content.parts[0].text;
            document.getElementById('analysis-content').innerHTML = txt.replace(/\\n/g, '<br>').replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
            document.getElementById('scan-form').style.display='none';
            document.getElementById('scan-results').style.display='block';
        } catch(e) { 
            document.getElementById('analysis-content').innerHTML = "<strong>Error:</strong> Could not connect to the AI analysis service. Please try again later.";
        }
        finally { 
            btn.innerText = "Start Rights Scan"; 
            btn.disabled = false;
        }
    }
</script>
"""

    def standardize_page_structure(self, soup: BeautifulSoup) -> bool:
        modified = False
        body = soup.find('body')
        if not body: return False

        if not soup.find('header') and not soup.find(class_='site-header'):
            header_soup = BeautifulSoup(self.header_html, 'html.parser')
            body.insert(0, header_soup.header)
            modified = True

        if not soup.find(class_='layout-grid'):
            layout_grid = soup.new_tag('div', attrs={'class': 'layout-grid'})
            content_col = soup.new_tag('article', attrs={'class': 'content-column'})
            layout_grid.append(content_col)
            container = soup.find('main') or soup.find('div', class_='container') or body
            children = list(container.children)
            for child in children:
                if child.name not in ['header', 'nav', 'footer', 'script', 'style'] and hasattr(child, 'extract'):
                    content_col.append(child.extract())
            if soup.find('main'): soup.find('main').append(layout_grid)
            elif soup.find('div', class_='container'): soup.find('div', class_='container').append(layout_grid)
            else: body.append(layout_grid)
            modified = True
            self.stats["structures_standardized"] += 1

        if not soup.find('footer') and not soup.find(class_='site-footer'):
            footer_soup = BeautifulSoup(self.footer_html, 'html.parser')
            body.append(footer_soup.footer)
            body.append(footer_soup.script)
            modified = True
        return modified

    def clean_slate(self, soup: BeautifulSoup) -> bool:
        modified = False
        for s in soup.find_all(['aside', 'div'], class_=lambda c: c and ('sidebar' in c or 'offers-container' in c or 'quick-answer' in c)):
            s.decompose()
            modified = True
            self.stats["sidebars_removed"] += 1
        for old in soup.find_all('div', class_=lambda c: c and ('inline-cta' in c or 'integrated-cta' in c or 'sales-card' in c or 'ai-tool-banner' in c or 'bg-gradient-to-br' in c)):
            old.decompose()
            self.stats["old_ctas_cleared"] += 1
            modified = True
        return modified

    def inject_assets(self, soup: BeautifulSoup) -> bool:
        head = soup.find('head')
        if not head: return False
        existing_style = soup.find('style', id='grievance-formatting')
        if existing_style: existing_style.string = self.css_content
        else:
            style = soup.new_tag('style', id='grievance-formatting')
            style.string = self.css_content
            head.append(style)
        body = soup.find('body')
        if body and not soup.find(id='ai-modal-overlay'):
            footer_assets = BeautifulSoup(self.ai_modal_and_script, 'html.parser')
            body.append(footer_assets)
        return True

    def inject_ctas(self, soup: BeautifulSoup) -> bool:
        col = soup.find(class_='content-column')
        if not col: return False
        
        paras = col.find_all('p')
        if len(paras) >= 2:
            paras[1].insert_after(BeautifulSoup(self.ai_tool_cta, 'html.parser'))
        elif len(paras) > 0:
            paras[0].insert_after(BeautifulSoup(self.ai_tool_cta, 'html.parser'))

        placed_kit = False
        for h2 in col.find_all('h2'):
            txt = h2.get_text().lower()
            if any(kw in txt for kw in ["mdr", "manifestation", "suspension", "discipline"]):
                h2.insert_after(BeautifulSoup(self.defense_kit_cta, 'html.parser'))
                placed_kit = True
                break
        
        placed_letter = False
        for h2 in col.find_all('h2'):
            txt = h2.get_text().lower()
            if any(kw in txt for kw in ["due process", "tea complaint", "legal representation"]):
                h2.insert_after(BeautifulSoup(self.iep_letter_cta, 'html.parser'))
                placed_letter = True
                break
        
        if not placed_letter:
            col.append(BeautifulSoup(self.iep_letter_cta, 'html.parser'))

        self.stats["new_ctas_injected"] += 3
        return True

    def process_file(self, filepath: str):
        self.stats["files_scanned"] += 1
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        self.clean_slate(soup)
        self.standardize_page_structure(soup)
        self.inject_assets(soup)
        self.inject_ctas(soup)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        self.stats["files_updated"] += 1

    def run(self):
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                if "grievance-dispute-resolution" in file and file.endswith('.html'):
                    self.process_file(os.path.join(root, file))
        print(f"Scanned: {self.stats['files_scanned']} | Updated: {self.stats['files_updated']}")

if __name__ == "__main__":
    TARGET = "./districts" 
    if os.path.exists(TARGET):
        GrievanceLayoutIntegrator(TARGET).run()