import json
import os

INPUT_FILE = "translated_results.jsonl"
OUTPUT_DIR = "seo_pages_output"

# Mapping the original page identifiers to your exact Spanish SEO slugs
SEO_SLUGS_MAPPING = {
    "index": "index.html", # Will go inside /es/ folder -> /es/index.html
    "evaluation-child-find": "evaluacion-educacion-especial-child-find.html",
    "ard-process-guide": "proceso-ard-guia-para-padres.html",
    "grievance-dispute-resolution": "quejas-y-disputas-educacion-especial.html",
    
    # This was the 1 Spanish page that got translated to English
    "como-solicitar-una-evaluacion-fie": "how-to-request-evaluation.html" 
}

def create_seo_files():
    # Create the main output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    count = 0

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
                
            record = json.loads(line)
            
            # Extract identifiers
            # custom_id format looks like: "brownsville_index_translated"
            custom_id = record.get("custom_id", "")
            html_content = record.get("translated_html", "")
            
            if not custom_id or not html_content:
                continue

            # Remove the "_translated" suffix to parse district and page type
            clean_id = custom_id.replace("_translated", "")
            
            # Split into district and page type (e.g., "brownsville", "index")
            # We split on the FIRST underscore only, in case page types have underscores
            parts = clean_id.split("_", 1)
            if len(parts) != 2:
                print(f"Skipping unparseable ID: {custom_id}")
                continue
                
            district_name = parts[0]
            page_type = parts[1]

            # Look up the correct SEO file name
            file_name = SEO_SLUGS_MAPPING.get(page_type, f"{page_type}.html")

            # Determine the folder structure
            # If it's the English page, put it in the root district folder. 
            # If it's the Spanish pages, put them in the /es/ subfolder.
            if page_type == "como-solicitar-una-evaluacion-fie":
                district_dir = os.path.join(OUTPUT_DIR, district_name)
            else:
                district_dir = os.path.join(OUTPUT_DIR, district_name, "es")
            
            # Create the nested directories (e.g., seo_pages_output/brownsville/es/)
            os.makedirs(district_dir, exist_ok=True)
            
            # Define the full file path
            file_path = os.path.join(district_dir, file_name)
            
            # Write the HTML content to the file
            with open(file_path, 'w', encoding='utf-8') as html_file:
                html_file.write(html_content)
                
            count += 1

    print(f"✅ Success! Successfully generated {count} HTML files in the '{OUTPUT_DIR}' directory.")

if __name__ == "__main__":
    create_seo_files()