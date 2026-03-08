import os
import re
from markdown import Markdown

MD_DIR = os.path.join("blog", "es")
TEMPLATE_PATH = "carta-evaluacion-educacion-especial-texas.html"

def create_html_from_md(md_filename):
    filepath = os.path.join(MD_DIR, md_filename)
    slug = md_filename.replace(".md", "")
    output_filepath = os.path.join(MD_DIR, f"{slug}.html")

    # 1. Read Markdown
    with open(filepath, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Extract title (first line)
    title_line = md_content.split('\n')[0].replace('#', '').strip()
    
    # Convert markdown body to HTML using the Class method (bypasses the module callable bug)
    md_converter = Markdown(extensions=['tables'])
    article_html = md_converter.convert(md_content)

    # 2. Read Base HTML Template
    if not os.path.exists(TEMPLATE_PATH):
        print(f"❌ Error: Cannot find template {TEMPLATE_PATH}")
        return

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # 3. Surgical Replacements using Regex (Preserves your original formatting)
    
    # Update <title>
    html = re.sub(r'<title>.*?</title>', f'<title>{title_line} | Texas Special Ed</title>', html, flags=re.DOTALL)

    # Update Meta Description (Grab first 150 chars of article)
    text_only = re.sub(r'<[^>]+>', '', article_html)
    meta_desc = text_only[:150].replace('\n', ' ') + "..."
    html = re.sub(r'<meta content="[^"]*" name="description" />', f'<meta content="{meta_desc}" name="description" />', html)

    # Update Canonical & Hreflang links
    new_url = f"https://www.texasspecialed.com/es/{slug}"
    html = re.sub(r'<link href="[^"]*" rel="canonical" />', f'<link href="{new_url}" rel="canonical" />', html)
    html = re.sub(r'<link rel="alternate" hreflang="es" href="[^"]*" />', f'<link rel="alternate" hreflang="es" href="{new_url}" />', html)

    # Update Hero H1
    html = re.sub(
        r'<h1>.*?</h1>', 
        f'<h1>{title_line}</h1>', 
        html, 
        count=1, 
        flags=re.DOTALL
    )
    
    # Update Hero <p>
    html = re.sub(
        r'(<section class="es-hero">.*?<h1>.*?</h1>\s*<p>)(.*?)(</p>)',
        r'\1Información esencial para padres en Texas sobre sus derechos de educación especial y cómo solicitar evaluaciones bajo la ley IDEA.\3',
        html,
        count=1,
        flags=re.DOTALL
    )

    # 4. Inject Content into the Content Card
    content_card_pattern = r'(<div class="content-card">)(.*?)(</div>)'
    
    def replace_content(match):
        original_inner_html = match.group(2)
        
        # Extract and preserve the quick-answer box if it exists
        quick_answer = ""
        qa_match = re.search(r'<div class="quick-answer">.*?</div>', original_inner_html, flags=re.DOTALL)
        if qa_match:
            quick_answer = qa_match.group(0)
            
        # Rebuild the content card
        return f'{match.group(1)}\n               {quick_answer}\n               {article_html}\n            {match.group(3)}'

    html = re.sub(content_card_pattern, replace_content, html, flags=re.DOTALL)

    # 5. Save the perfectly formatted HTML
    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"✅ Generated properly formatted HTML for: {slug}.html")

if __name__ == "__main__":
    if not os.path.exists(MD_DIR):
        print(f"Directory {MD_DIR} does not exist.")
    else:
        for file in os.listdir(MD_DIR):
            if file.endswith(".md"):
                create_html_from_md(file)
        print("\n🎉 All Spanish articles wrapped in HTML!")