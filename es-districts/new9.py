import os
from bs4 import BeautifulSoup
from pathlib import Path

def main():
    # 1. Locate ONLY your master template
    template_path = Path(r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-districts\template.html")

    if not template_path.exists():
        print(f"❌ Error: Could not find template.html at {template_path}")
        return

    print("Cleaning up the master template.html...\n")
    
    with open(template_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # 2. LOCATE THE MAIN CONTAINER
    main_tag = soup.find("main")
    
    if main_tag:
        # Remove the hardcoded Abilene H1
        for h1 in main_tag.find_all("h1", recursive=False):
            h1.decompose()
            print("✅ Removed hardcoded <h1>")
            
        # Remove the Breadcrumb nav
        for nav in main_tag.find_all("nav", recursive=False):
            nav.decompose()
            print("✅ Removed breadcrumbs")
            
        # Remove the Silo Nav (Abilene Resources)
        for silo in main_tag.find_all("div", class_="silo-nav"):
            silo.decompose()
            print("✅ Removed old Abilene silo nav")
            
        # Remove the "Respuesta Rapida" quick answer box
        for div in main_tag.find_all("div", recursive=False):
            if div.text and "⚡ Respuesta Rápida" in div.text:
                div.decompose()
                print("✅ Removed Respuesta Rápida box")

    # 3. ENFORCE THE MAX WIDTH (800px) & CENTER IT
    # Apply inline CSS directly to the containers so it NEVER stretches too wide
    layout_grid = soup.find("div", class_="layout-grid")
    if layout_grid:
        layout_grid["style"] = "max-width: 800px !important; margin: 0 auto !important; width: 100%; display: block;"

    content_col = soup.find("article", class_="content-column") or soup.find("div", class_="content-column")
    if content_col:
        content_col["style"] = "max-width: 800px !important; margin: 0 auto !important; width: 100%; display: block; box-sizing: border-box;"
        print("✅ Locked content width to 800px (Centered)")

    # 4. SAVE THE CLEAN TEMPLATE
    with open(template_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
        
    print("\n🎉 Success! Your master template.html is now completely clean and properly sized.")

if __name__ == "__main__":
    main()