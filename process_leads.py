import csv
import json
import time
import requests
from bs4 import BeautifulSoup
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

# 1. Initialize Vertex AI (Replace with your actual Project ID)
vertexai.init(project="texasspecialed", location="us-central1")
model = GenerativeModel("gemini-2.0-flash")

def scrape_website_text(url):
    """Fetches a URL and extracts clean, readable text."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'} 
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
            
        text = " ".join(soup.stripped_strings)
        return text[:5000] # Send first ~5,000 characters to save money and tokens
    except Exception as e:
        print(f"  [!] Scraping failed for {url}: {e}") 
        return None

def analyze_and_draft(business_name, district, website_text):
    """Asks Vertex AI to categorize the business AND draft the email in one go."""
    
    prompt = f"""
    You are doing sales outreach for texasspecialed.com. 
    First, analyze the following website text to categorize the business into one of four buckets:
    1. Attorney: Special ed law firms representing parents in disputes/hearings.
    2. Advocate: Independent advocates attending ARD meetings and reviewing IEPs.
    3. Tutor: Tutors, reading specialists, or therapy practices (OT, speech).
    4. Irrelevant: Does not fit the above or is a generic/unrelated business.
    
    If the business is Irrelevant, leave the drafted email blank.
    If the business is relevant, write a 4-5 sentence cold email to {business_name} in the {district} area.
    Always lead with a monthly pricing offer and never mention annual pricing. 
    Keep the tone professional, helpful, and brief.
    
    Email drafting rules based on category:
    - If Attorney: Pitch a Tier 2 ad placement at $249/mo on the 'Grievance & Discipline' or 'ARD' page. Mention that parents on these pages are in crisis (e.g., facing suspension) and actively looking for an attorney. Note that one retained client pays for 12 months.
    - If Advocate: Pitch a Tier 1 ($59/mo) or Tier 2 ($129/mo) placement on the 'ARD Meeting Guide' page. Mention parents reading this are terrified of an upcoming meeting and need an advocate to sit next to them. Point out that $59/mo is less than $2 a day.
    - If Tutor: Pitch a Tier 1 ($39/mo) or Tier 2 ($89/mo) placement on the 'Dyslexia Services' page. Mention parents reading this are in the early "something is wrong" phase researching support. Point out one new student covers the cost for 6 months.

    Website Text:
    {website_text}
    """
    
    # Force Gemini to output strictly structured JSON data
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "actual_category": {
                "type": "STRING", 
                "enum": ["Attorney", "Advocate", "Tutor", "Irrelevant"]
            },
            "drafted_email": {
                "type": "STRING",
                "description": "The drafted cold email, or blank if irrelevant."
            }
        },
        "required": ["actual_category", "drafted_email"]
    }
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=GenerationConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.2 
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"  [!] AI Processing failed: {e}")
        return {"actual_category": "Error", "drafted_email": ""}

# --- Main Execution Block ---
if __name__ == "__main__":
    input_csv = "texas_special_ed_leads_top20.csv"
    output_csv = "texas_leads_ready_to_send.csv"
    
    with open(input_csv, mode='r', encoding='utf-8') as infile, \
         open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:
         
        reader = csv.DictReader(infile)
        # We add two new columns: The AI's verified category, and the drafted email
        fieldnames = reader.fieldnames + ['AI_Verified_Category', 'Drafted_Email']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        print(f"Starting AI analysis and drafting for 368 leads...")
        
        for i, row in enumerate(reader, 1):
            print(f"\n[{i}/368] Processing: {row['Business Name']}...")
            
            # Step 1: Scrape
            website_text = scrape_website_text(row['Website'])
            
            if not website_text:
                row['AI_Verified_Category'] = "Scrape Failed"
                row['Drafted_Email'] = ""
                writer.writerow(row)
                continue
                
            # Step 2: Analyze and Draft via Vertex AI
            ai_result = analyze_and_draft(
                business_name=row['Business Name'],
                district=row['District'],
                website_text=website_text
            )
            
            # Save the results
            row['AI_Verified_Category'] = ai_result['actual_category']
            row['Drafted_Email'] = ai_result['drafted_email']
            writer.writerow(row)
            
            print(f"  -> Verified as: {ai_result['actual_category']}")
            
            # Small pause to respect Vertex AI rate limits
            time.sleep(1.5)
            
    print(f"\nSuccess! All leads processed and saved to {output_csv}")