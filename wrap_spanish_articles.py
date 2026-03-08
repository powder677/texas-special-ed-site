import os
import markdown
from bs4 import BeautifulSoup

# Paths
MD_DIR = os.path.join("blog", "es")
TEMPLATE_PATH = "carta-evaluacion-educacion-especial-texas.html" # Using your uploaded file as the base template

def create_html_from_md(md_filename):
    filepath = os.path.join(MD_DIR, md_filename)
    slug = md_filename.replace(".md", "")
    output_filepath = os.path.join(MD_DIR, f"{slug}.html")

    # 1. Read the Markdown content
    with open(filepath, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Extract the title (assuming H1 or first line is the title)
    title_line = md_content.split('\n')[0].replace('#', '').strip()

    # Convert Markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

    # 2. Read the base HTML template
    if not os.path.exists(TEMPLATE_PATH):
        print(f"❌ Error: Cannot find template {TEMPLATE_PATH}")
        return

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # 3. Update the SEO Metadata
    # Update Title
    if soup.title:
        soup.title.string = f"{title_line} | Texas Special Ed"
    
    # Update Meta Description (grab the first paragraph of the markdown for the description)
    first_p = BeautifulSoup(html_content, "html.parser").find("p")
    meta_desc = first_p.text[:150] + "..." if first_p else title_line
    meta_tag = soup.find("meta", {"name": "description"})
    if meta_tag:
        meta_tag["content"] = meta_desc

    # Update Canonical Link
    canonical_link = soup.find("link", {"rel": "canonical"})
    if canonical_link:
        canonical_link["href"] = f"https://www.texasspecialed.com/es/{slug}"

    # Update Alternate Hreflang
    alt_link = soup.find("link", {"hreflang": "es"})
    if alt_link:
        alt_link["href"] = f"https://www.texasspecialed.com/es/{slug}"

    # 4. Inject the Content
    # Find the main content column (where the quick-answer and main text go)
    main_col = soup.find("div", class_="main-col")
    
    if main_col:
        # Clear out the old content card (keeping the bot-wrap and lang-toggle if desired)
        content_card = main_col.find("div", class_="content-card")
        if content_card:
            # Clear existing content but keep the div
            content_card.clear()
            # Parse our new markdown HTML and append it
            new_content_soup = BeautifulSoup(html_content, "html.parser")
            content_card.append(new_content_soup)

            # Optional: Add the quick-answer box back in programmatically if needed
            # For now, it just injects the raw article.

    # 5. Update the Hero Section
    hero_h1 = soup.find("div", class_="es-hero").find("h1")
    if hero_h1:
        hero_h1.string = title_line
        
    hero_p = soup.find("div", class_="es-hero").find("p")
    if hero_p:
        hero_p.string = "Información esencial para padres en Texas sobre sus derechos de educación especial."

    # 6. Save the new HTML file
    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(str(soup))
        
    print(f"✅ Generated HTML for: {slug}.html")

if __name__ == "__main__":
    if not os.path.exists(MD_DIR):
        print(f"Directory {MD_DIR} does not exist.")
    else:
        for file in os.listdir(MD_DIR):
            if file.endswith(".md"):
                create_html_from_md(file)
        print("\n🎉 All Spanish articles wrapped in HTML!")