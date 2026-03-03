import os
import re

# --- CONFIGURATION ---
OUTPUT_DIR = "districts"

# Define the pages in your silo, including a short description for the Index Cards
SILO_PAGES = [
    {
        "title": "What is an FIE?", 
        "file": "what-is-fie.html",
        "desc": "Understand the Full Individual Evaluation process and timeline."
    },
    {
        "title": "IEE Guide", 
        "file": "independent-educational-evaluation.html",
        "desc": "Learn how to request an Independent Educational Evaluation."
    },
    {
        "title": "Special Ed Rights", 
        "file": "special-education-rights.html",
        "desc": "Know your parental rights under IDEA and Texas law."
    },
    {
        "title": "Contact Consultant", 
        "file": "contact.html",
        "desc": "Get professional help navigating your child's education."
    }
]

# (Truncated for brevity, but include your full list of 50 here)
TARGET_DISTRICTS = [
    {"name": "Houston ISD", "slug": "houston-isd"},
    {"name": "Dallas ISD", "slug": "dallas-isd"},
    {"name": "Cypress-Fairbanks ISD", "slug": "cypress-fairbanks-isd"},
    {"name": "Northside ISD", "slug": "northside-isd"},
    {"name": "Katy ISD", "slug": "katy-isd"}
]

def generate_nav_bar(current_file, district_name):
    """Generates the updated horizontal top navigation bar."""
    nav_links = []
    for page in SILO_PAGES:
        if page['file'] == current_file:
            # Active page (bold, no link)
            nav_links.append(f'<span style="font-weight:bold; color:#0a2342; text-decoration:underline; margin-right:15px; font-family:\'DM Sans\', sans-serif;">{page["title"]}</span>')
        else:
            # Clickable link
            nav_links.append(f'<a href="./{page["file"]}" style="color:#1a56db; text-decoration:none; margin-right:15px; font-family:\'DM Sans\', sans-serif; font-weight:600;">{page["title"]}</a>')
    
    links_str = " | ".join(nav_links)
    
    return f"""
<nav class="district-silo-nav" style="background:#f8fafc; padding:15px 20px; border-bottom:2px solid #e2e8f0; margin-bottom:30px;">
    <div style="max-width:1100px; margin:0 auto; display:flex; flex-wrap:wrap; align-items:center; gap:10px;">
        <span style="margin-right:15px; font-weight:700; color:#0f172a; font-family:\'Lora\', serif; font-size:1.1rem;">{district_name} Resources:</span>
        <div>{links_str}</div>
    </div>
</nav>
"""

def generate_index_cards(district_name):
    """Generates a modern CSS grid of cards for the index page."""
    cards_html = ""
    for page in SILO_PAGES:
        cards_html += f"""
        <a href="./{page['file']}" style="background:#fff; border:1px solid #e2e8f0; border-radius:8px; padding:24px; text-decoration:none; transition:transform 0.2s, box-shadow 0.2s; display:block; box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);" onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 10px 15px -3px rgba(0,0,0,0.1)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px -1px rgba(0,0,0,0.05)';">
            <h3 style="font-family:'Lora', serif; color:#0a2342; font-size:1.3rem; margin:0 0 10px 0;">{page['title']} &rarr;</h3>
            <p style="font-family:'DM Sans', sans-serif; color:#475569; font-size:15px; margin:0; line-height:1.5;">{page['desc']}</p>
        </a>"""

    return f"""
<section class="silo-cards-section" style="max-width:1100px; margin:40px auto; padding:0 20px;">
    <h2 style="font-family:'Lora', serif; color:#0a2342; font-size:1.8rem; margin-bottom:20px; border-bottom:2px solid #e8f0fe; padding-bottom:10px;">Explore {district_name} Special Ed Resources</h2>
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(250px, 1fr)); gap:24px;">
        {cards_html}
    </div>
</section>
"""

def update_silos():
    print("🚀 Starting Silo Navigation & Card Update...")
    
    for district in TARGET_DISTRICTS:
        slug = district['slug']
        district_folder = os.path.join(OUTPUT_DIR, slug)
        
        if not os.path.exists(district_folder):
            continue

        # 1. Update the Linking Bar on ALL silo pages
        for silo_page in SILO_PAGES:
            file_path = os.path.join(district_folder, silo_page['file'])
            if not os.path.exists(file_path):
                continue
                
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Remove the old nav bar if it exists
            content = re.sub(r'.*?', '', content, flags=re.DOTALL)
            
            # Remove any raw <nav class="district-silo-nav"> that doesn't have the comments (from the previous attempt)
            content = re.sub(r'<nav class="district-silo-nav".*?</nav>', '', content, flags=re.DOTALL)

            # Generate and inject the new nav bar right after the opening <body> tag
            new_nav = generate_nav_bar(silo_page['file'], district['name'])
            
            if "<body" in content:
                body_end_idx = content.find(">", content.find("<body")) + 1
                content = content[:body_end_idx] + "\n" + new_nav + content[body_end_idx:]

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
        # 2. Inject the Linking Cards into index.html
        index_path = os.path.join(district_folder, "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                index_content = f.read()
                
            # Remove old cards if they exist so we don't duplicate
            index_content = re.sub(r'.*?', '', index_content, flags=re.DOTALL)
            
            new_cards = generate_index_cards(district['name'])
            
            # Inject cards into the main content area. Assuming there's a <main> tag or appending before <footer>
            if "</main>" in index_content:
                index_content = index_content.replace("</main>", new_cards + "\n</main>")
            elif "</body>" in index_content:
                index_content = index_content.replace("</body>", new_cards + "\n</body>")
                
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(index_content)
                print(f"✅ Updated nav & index cards for {slug}")

if __name__ == "__main__":
    update_silos()