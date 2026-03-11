import json
import os

INPUT_FILE = "translated_results.jsonl"
EN_OUTPUT_DIR = "districts"
ES_OUTPUT_DIR = "es-districts"

# Mapping the original page identifiers to your exact SEO slugs
SEO_SLUGS_MAPPING = {
    # Spanish SEO Slugs
    "index": "index.html", 
    "evaluation-child-find": "evaluacion-educacion-especial-child-find.html",
    "ard-process-guide": "proceso-ard-guia-para-padres.html",
    "grievance-dispute-resolution": "quejas-y-disputas-educacion-especial.html",
    
    # English SEO Slug (Translated from the Spanish document)
    "como-solicitar-una-evaluacion-fie": "how-to-request-evaluation.html" 
}

def create_seo_files():
    count = 0

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
                
            record = json.loads(line)
            
            # Extract identifiers
            custom_id = record.get("custom_id", "")
            html_content = record.get("translated_html", "")
            
            if not custom_id or not html_content:
                continue

            # Parse district and page type
            clean_id = custom_id.replace("_translated", "")
            parts = clean_id.split("_", 1)
            
            if len(parts) != 2:
                print(f"Skipping unparseable ID: {custom_id}")
                continue
                
            district_name = parts[0]
            page_type = parts[1]

            # Look up the correct SEO file name
            file_name = SEO_SLUGS_MAPPING.get(page_type, f"{page_type}.html")

            # Route to the correct root folder based on language
            if page_type == "como-solicitar-una-evaluacion-fie":
                # English page goes to 'districts'
                district_dir = os.path.join(EN_OUTPUT_DIR, district_name)
            else:
                # Spanish pages go to 'es-districts' 
                # Keeping the 'es' subfolder so your SEO paths remain intact
                district_dir = os.path.join(ES_OUTPUT_DIR, district_name, "es")
            
            # Create the nested directories
            os.makedirs(district_dir, exist_ok=True)
            
            # Define the full file path and write the HTML
            file_path = os.path.join(district_dir, file_name)
            with open(file_path, 'w', encoding='utf-8') as html_file:
                html_file.write(html_content)
                
            count += 1

    print(f"✅ Success! Generated {count} HTML files separated into '{EN_OUTPUT_DIR}' and '{ES_OUTPUT_DIR}'.")

if __name__ == "__main__":
    create_seo_files()