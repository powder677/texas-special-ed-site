import os
import shutil
import time
from bs4 import BeautifulSoup

class FIESpecificCROPatcher:
    def __init__(self, target_dir: str, backup_dir: str):
        self.target_dir = target_dir
        self.backup_dir = backup_dir
        self.stats = {
            "files_scanned": 0,
            "naked_files_rebuilt": 0,
            "files_patched": 0,
            "sidebars_stripped": 0,
            "mobile_injected": 0
        }

    def create_backup(self):
        # Create a unique timestamped folder to bypass OneDrive/Windows file lock errors
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        safe_backup_dir = f"{self.backup_dir}_{timestamp}"
        
        print(f"Creating backup of {self.target_dir} to {safe_backup_dir}...")
        shutil.copytree(self.target_dir, safe_backup_dir)
        print("Backup complete.\n")

    def ensure_full_template(self, html_content: str) -> BeautifulSoup:
        """Detects if a file is 'naked' (missing <body>) and wraps it in the full site template."""
        soup = BeautifulSoup(html_content, "html.parser")
        
        # If the file already has a body, it's a full page. Return as-is.
        if soup.find("body"):
            return soup
            
        # Extract the title from the H1 for the <head>
        h1 = soup.find("h1")
        page_title = h1.get_text() if h1 else "FIE Guide - Texas Special Ed"
        
        # Build the wrapper template
        template = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8"/>
            <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
            <title>{page_title}</title>
            <link href="https://fonts.googleapis.com" rel="preconnect"/>
            <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&family=Lora:wght@400;600;700&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet"/>
            <link href="/style.css" rel="stylesheet"/>
        </head>
        <body>
            <header class="site-header">
                <nav aria-label="Main navigation" class="navbar" role="navigation">
                    <div class="nav-container" style="display:flex; justify-content:space-between; align-items:center;">
                        <div class="nav-logo">
                            <a aria-label="Texas Special Ed Home" class="text-logo" href="/" style="text-decoration:none; font-size:1.5rem; color:#1a1a2e; font-weight:bold; font-family:'Lora', serif;">
                                Texas <em style="color:#1a56db; font-style:italic;">Special Ed</em>
                            </a>
                        </div>
                        <ul class="nav-menu" style="display:flex; list-style:none; gap:20px; align-items:center;">
                            <li><a href="/" style="text-decoration:none; color:#333; font-weight:600;">Home</a></li>
                            <li><a href="/districts/index.html" style="text-decoration:none; color:#333; font-weight:600;">Districts</a></li>
                            <li><a href="/tools/fie-letter-bot/index.html" style="background:#d4af37; color:#0f172a; padding:10px 18px; border-radius:4px; font-weight:700; text-decoration:none;">Get Your Letter — $25</a></li>
                        </ul>
                    </div>
                </nav>
            </header>
            
            <main class="container" style="max-width: 1100px; margin: 0 auto; padding: 20px;">
                <div class="layout-grid">
                    <article class="content-column">
                        {html_content}
                    </article>
                    <aside class="sidebar-column">
                        <!-- Sidebar injected later -->
                    </aside>
                </div>
            </main>
        </body>
        </html>
        """
        self.stats["naked_files_rebuilt"] += 1
        return BeautifulSoup(template, "html.parser")

    def patch_css(self, soup: BeautifulSoup) -> bool:
        """Injects the missing FIE layout CSS + Mobile CRO fixes."""
        if soup.find("style", id="fie-core-formatting"):
            return False

        patch_style = soup.new_tag("style", id="fie-core-formatting")
        patch_style.string = """
        /* ── AUTOMATED CRO PATCH: FIE Layout & Mobile Fixes ── */
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background: #f8fafc; }
        h1 { font-size: 2.2rem; margin-top: 10px; font-family: 'Lora', serif; color: #0a2342; }
        
        /* 1. Core Layout */
        .layout-grid { display: grid; grid-template-columns: 1fr; gap: 50px; margin-top: 30px; align-items: start; }
        @media (min-width: 951px) { .layout-grid { grid-template-columns: 1fr 380px; } }
        .sidebar-column { position: sticky; top: 100px; z-index: 10; }
        .content-column { min-width: 0; font-family: 'Source Sans 3', sans-serif; font-size: 17px; line-height: 1.75; color: #1a1a2e; background: #fff; padding: 40px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0; }
        .content-column h2 { font-family: 'Lora', serif; font-size: 1.6rem; font-weight: 700; color: #0a2342; margin: 2.5rem 0 1rem; padding-top: 1.5rem; border-top: 2px solid #e8f0fe; }
        .content-column p { margin: 0 0 1.25rem; }
        .content-column ul { padding-left: 20px; margin-bottom: 1.5rem; }
        .content-column li { margin-bottom: 8px; }

        /* 3. Mobile Display & Padding Fixes */
        @media (max-width: 950px) {
            .hide-on-mobile { display: none !important; }
            .mobile-only { display: block !important; }
            .content-column { padding: 10px !important; border: none !important; box-shadow: none !important; background: transparent !important; }
            .nav-menu { display: none !important; }
        }
        @media (min-width: 951px) {
            .mobile-only { display: none !important; }
            .hide-on-mobile { display: block !important; }
        }
        
        /* 4. Protect Bot Banners from global style.css hijacking */
        .banner-btn { text-decoration: none !important; display: block; border-radius: 6px; font-weight: 800; font-family: 'DM Sans', sans-serif; font-size: 16px; transition: background 0.2s; padding: 15px; }
        .banner-btn:hover { color: #0f172a !important; }
        .banner-btn-gold { background: #d4af37; color: #0f172a !important; }
        .banner-btn-blue { background: #1a56db; color: #fff !important; }
        .banner-btn-blue:hover { background: #1e3a8a; color: #fff !important; }
        """
        
        head = soup.find("head")
        if head:
            old_patch = soup.find("style", id="cro-mobile-patch")
            if old_patch:
                old_patch.decompose()
            head.append(patch_style)
            return True
        return False

    def strip_and_rebuild_sidebar(self, soup: BeautifulSoup) -> bool:
        """Empties the cluttered sidebar, hides it on mobile, and adds the 2 Bot Banners."""
        sidebar = soup.find("aside", class_="sidebar-column")
        if not sidebar:
            sidebar = soup.find("aside", class_="sidebar-col")
            
        if not sidebar:
            return False

        classes = sidebar.get("class", [])
        if "hide-on-mobile" not in classes:
            sidebar["class"] = classes + ["hide-on-mobile"]

        sidebar.clear()

        desktop_banners_html = """
        <!-- FUNNEL 1: FIE Letter Writer Bot (High Intent/Top of Funnel) -->
        <div style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);padding:28px;border-radius:12px;text-align:center;color:#fff;margin-bottom:24px;box-shadow:0 10px 25px -5px rgba(0,0,0,0.15);border:1px solid #1e40af;">
            <span style="background:#d4af37;color:#0f172a;padding:4px 12px;border-radius:50px;font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;display:inline-block;margin-bottom:12px;">Premium AI Tool</span>
            <h3 style="font-family:'Lora',serif;font-size:1.5rem;margin:0 0 10px;color:#fff;">Draft Your FIE Request</h3>
            <p style="font-family:'Source Sans 3',sans-serif;font-size:14px;color:#cbd5e1;margin:0 0 18px;line-height:1.5;">A casual email won't work. Your request is a legal trigger. Use our AI to write a compliant letter that forces a 15-day timeline.</p>
            <a href="/tools/fie-letter-bot/index.html" class="banner-btn banner-btn-gold">Draft My Letter — $25 →</a>
        </div>

        <!-- FUNNEL 2: ARD Diagnostic Audit Bot (Escalation/Problem Solving) -->
        <div style="background:#fff;border:1px solid #e2e8f0;padding:28px;border-radius:12px;text-align:center;box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);">
            <span style="background:#ef4444;color:#fff;padding:4px 12px;border-radius:50px;font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;display:inline-block;margin-bottom:12px;">Diagnostic Bot</span>
            <h3 style="font-family:'Lora',serif;font-size:1.3rem;margin:0 0 10px;color:#0a2342;">Are Your Rights Being Violated?</h3>
            <p style="font-family:'Source Sans 3',sans-serif;font-size:14px;color:#475569;margin:0 0 18px;line-height:1.5;">Take our 9-question ARD assessment to instantly find out your next legal step—whether it's our DIY templates, an advocate, or a lawyer.</p>
            <a href="/tools/ard-rights-scan/index.html" class="banner-btn banner-btn-blue">Run Free ARD Audit →</a>
        </div>
        """
        sidebar.append(BeautifulSoup(desktop_banners_html, "html.parser"))
        self.stats["sidebars_stripped"] += 1
        return True

    def inject_mobile_in_content_banners(self, soup: BeautifulSoup) -> bool:
        """Injects the mobile banners directly into the article flow."""
        content_col = soup.find(class_="content-column")
        if not content_col:
            content_col = soup.find(class_="main-content-col")
            
        if not content_col or soup.find(id="mobile-bot-1"):
            return False

        h2_tags = content_col.find_all("h2")
        first_h2 = h2_tags[0] if len(h2_tags) > 0 else None
        anchor_two = h2_tags[1] if len(h2_tags) > 1 else None

        injected = False

        if first_h2:
            banner_1 = """
            <div id="mobile-bot-1" class="mobile-only" style="margin: 2.5rem 0;">
                <div style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);padding:28px;border-radius:12px;text-align:center;color:#fff;box-shadow:0 10px 25px -5px rgba(0,0,0,0.15);border:1px solid #1e40af;">
                    <span style="background:#d4af37;color:#0f172a;padding:4px 12px;border-radius:50px;font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;display:inline-block;margin-bottom:12px;">Premium AI Tool</span>
                    <h3 style="font-family:'Lora',serif;font-size:1.6rem;margin:0 0 10px;color:#fff;">Draft Your FIE Request</h3>
                    <p style="font-family:'Source Sans 3',sans-serif;font-size:15px;color:#cbd5e1;margin:0 0 18px;line-height:1.5;">Sending a casual email is a mistake. Use our AI to write a legally binding letter that forces a response.</p>
                    <a href="/tools/fie-letter-bot/index.html" class="banner-btn banner-btn-gold">Draft My Letter — $25 →</a>
                </div>
            </div>
            """
            first_h2.insert_after(BeautifulSoup(banner_1, "html.parser"))
            injected = True

        if anchor_two:
            banner_2 = """
            <div id="mobile-bot-2" class="mobile-only" style="margin: 2.5rem 0;">
                <div style="background:#fff;border:1px solid #e2e8f0;padding:28px;border-radius:12px;text-align:center;box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);">
                    <span style="background:#ef4444;color:#fff;padding:4px 12px;border-radius:50px;font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;display:inline-block;margin-bottom:12px;">Diagnostic Bot</span>
                    <h3 style="font-family:'Lora',serif;font-size:1.3rem;margin:0 0 10px;color:#0a2342;">Are Your Rights Being Violated?</h3>
                    <p style="font-family:'Source Sans 3',sans-serif;font-size:14px;color:#475569;margin:0 0 18px;line-height:1.5;">Take our 9-question ARD assessment to find out your next legal step.</p>
                    <a href="/tools/ard-rights-scan/index.html" class="banner-btn banner-btn-blue">Run Free ARD Audit →</a>
                </div>
            </div>
            """
            anchor_two.insert_after(BeautifulSoup(banner_2, "html.parser"))
            injected = True

        if injected:
            self.stats["mobile_injected"] += 1
            
        return injected

    def process_file(self, filepath: str):
        self.stats["files_scanned"] += 1
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()

        # Phase 1: Ensure it's not a naked fragment
        soup = self.ensure_full_template(html)
        
        # Phase 2: Apply the layout styles, clean the sidebar, and inject mobile
        c1 = self.patch_css(soup)
        c2 = self.strip_and_rebuild_sidebar(soup)
        c3 = self.inject_mobile_in_content_banners(soup)

        # If it was rebuilt from naked OR had CRO changes, save it
        if any([c1, c2, c3]) or not BeautifulSoup(html, "html.parser").find("body"):
            self.stats["files_patched"] += 1
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(str(soup))

    def run(self):
        self.create_backup()
        print("Scanning for 'FIE' HTML files to apply template and funnel layout...")
        
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                if file.endswith(".html") and ("fie" in file.lower() or "evaluation" in file.lower()):
                    self.process_file(os.path.join(root, file))
        
        print("\n" + "="*45)
        print(" 🚀 FIE TEMPLATE REBUILD & CRO COMPLETE 🚀")
        print("="*45)
        print(f"Total FIE Files Scanned:   {self.stats['files_scanned']}")
        print(f"Naked HTML Files Rebuilt:  {self.stats['naked_files_rebuilt']}")
        print(f"Total FIE Files Patched:   {self.stats['files_patched']}")
        print(f"Cluttered Sidebars Nuked:  {self.stats['sidebars_stripped']}")
        print(f"Mobile Banners Injected:   {self.stats['mobile_injected']}")
        print("="*45)

if __name__ == "__main__":
    TARGET_WEBSITE_DIR = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"
    BACKUP_DIR = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts_backup"
    
    if not os.path.exists(TARGET_WEBSITE_DIR):
        print(f"Error: Directory {TARGET_WEBSITE_DIR} not found.")
    else:
        patcher = FIESpecificCROPatcher(TARGET_WEBSITE_DIR, BACKUP_DIR)
        patcher.run()