import json
import time
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import HarmCategory, HarmBlockThreshold

# ==========================================
# CONFIGURATION
# ==========================================
PROJECT_ID = "texasspecialed"  # Replace with your GCP Project ID
LOCATION = "us-central1"        # e.g., us-central1
INPUT_FILE = "msgbatch_01MGmmvhTMRMVyLZDNVYkqGe_results.jsonl"
OUTPUT_FILE = "translated_results.jsonl"

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Using Gemini 2.5 Flash: Cheapest and highly efficient for translation
model = GenerativeModel("gemini-2.5-flash")

# Define safety settings to prevent the model from blocking educational content
safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# ==========================================
# PROMPT DEFINITION
# ==========================================
def get_translation_prompt(html_content):
    return f"""
    You are an expert bilingual SEO specialist and web content translator. 
    Analyze the following HTML document and determine its language.

    SCENARIO A: If the document is in SPANISH, translate it entirely to ENGLISH.
    SCENARIO B: If the document is in ENGLISH, translate it entirely to SPANISH. 
    
    IF TRANSLATING TO SPANISH, you MUST apply these strict SEO rules:
    1. NEVER translate the name of the school district (e.g., keep "Brownsville ISD", "Robinson ISD").
    2. Always append "Texas" to the district name when mentioning it in key headers or meta content. 
       Example format: "Educación Especial en [District Name] Texas".
    3. Update the H1 tags based on the topic of the page using these guidelines:
       - Index/General Page H1: "Guía de Educación Especial para Padres en [District Name] Texas"
       - Evaluation/Child Find H1: "Cómo Solicitar una Evaluación de Educación Especial en [District Name] Texas"
       - ARD Process H1: "Qué es una Reunión ARD y Cómo Prepararse en [District Name] Texas" (Keep "ARD" as "ARD")
       - Grievance/Dispute H1: "Cómo Presentar una Queja de Educación Especial en [District Name] Texas"

    CRITICAL INSTRUCTIONS FOR ALL TRANSLATIONS:
    - Preserve all HTML tags, structure, and formatting perfectly. 
    - Do not add any markdown formatting (like ```html) to your response. Return ONLY raw HTML.
    
    HTML CONTENT TO TRANSLATE:
    {html_content}
    """

# ==========================================
# PROCESSING LOOP
# ==========================================
def process_batch():
    with open(INPUT_FILE, 'r', encoding='utf-8') as infile, \
         open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        
        for line in infile:
            if not line.strip():
                continue
                
            try:
                # Parse the Anthropic batch JSON structure
                record = json.loads(line)
                custom_id = record.get("custom_id", "unknown_id")
                
                # Extract the HTML content from the Anthropic response
                message_content = record["result"]["message"]["content"][0]["text"]
                
                # Clean out markdown formatting if it exists in the original
                if message_content.startswith("```html"):
                    message_content = message_content.replace("```html\n", "").replace("```", "")
                
                print(f"Translating record: {custom_id}...")
                
                # Call Vertex AI
                response = model.generate_content(
                    get_translation_prompt(message_content),
                    safety_settings=safety_settings
                )
                
                translated_html = response.text.strip()
                if translated_html.startswith("```html"):
                     translated_html = translated_html.replace("```html\n", "").replace("```", "")
                
                # Re-package the translated HTML into a new JSON line
                output_record = {
                    "custom_id": f"{custom_id}_translated",
                    "original_id": custom_id,
                    "translated_html": translated_html
                }
                
                outfile.write(json.dumps(output_record) + "\n")
                
                # Sleep briefly to avoid hitting standard quota limits
                time.sleep(2) 
                
            except Exception as e:
                print(f"Error processing record {custom_id}: {str(e)}")

if __name__ == "__main__":
    process_batch()
    print("Translation complete! Saved to", OUTPUT_FILE)