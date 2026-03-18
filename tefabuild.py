import os
import re
import markdown

# ======================================================================
# CONFIGURATION & PATHS
# ======================================================================
# Define your specific directories
MD_DIR = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\tefa_markdown_pages"
TEMPLATE_PATH = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\tefa\tefa-template.html"

# Output directories for English and Spanish
OUT_DIR_EN = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\tefa\en"
OUT_DIR_ES = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\tefa\es"

def build_pages():
    # 1. Ensure output directories exist
    os.makedirs(OUT_DIR_EN, exist_ok=True)
    os.makedirs(OUT_DIR_ES, exist_ok=True)

    # 2. Load the HTML template
    try:
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as tf:
            html_template = tf.read()
    except FileNotFoundError:
        print(f"❌ Error: Could not find template at {TEMPLATE_PATH}")
        return

    # Check if the placeholder exists in the template
    if "{{CONTENT}}" not in html_template:
        print("⚠️ Warning: Could not find '{{CONTENT}}' placeholder in your template.")
        print("The script will run, but the content might not be injected properly.")

    # 3. Process each Markdown file
    md_files = [f for f in os.listdir(MD_DIR) if f.endswith(".md")]
    
    if not md_files:
        print(f"No Markdown files found in {MD_DIR}.")
        return

    print(f"Found {len(md_files)} Markdown files. Starting conversion...\n")

    for filename in md_files:
        md_filepath = os.path.join(MD_DIR, filename)
        
        with open(md_filepath, "r", encoding="utf-8") as f:
            raw_content = f.read()

        # Optional: Remove the YAML frontmatter (---...---) we added in the generation script
        # so it doesn't show up as text on the final webpage
        content_to_convert = re.sub(r'^---.*?---\n', '', raw_content, flags=re.DOTALL)

        # Convert Markdown to HTML
        # The 'extra' extension adds support for tables, nested lists, etc.
        html_content = markdown.markdown(content_to_convert, extensions=['extra'])

        # Inject the content into the template
        final_html = html_template.replace("{{CONTENT}}", html_content)

        # Determine where to save it based on the filename (EN vs ES)
        base_name = filename.replace(".md", ".html")
        if filename.startswith("ES"):
            out_filepath = os.path.join(OUT_DIR_ES, base_name)
        else:
            out_filepath = os.path.join(OUT_DIR_EN, base_name)

        # Save the final HTML file
        with open(out_filepath, "w", encoding="utf-8") as out_f:
            out_f.write(final_html)
            
        print(f"✅ Created: {out_filepath}")

    print("\n🎉 All pages successfully built!")

if __name__ == "__main__":
    build_pages()