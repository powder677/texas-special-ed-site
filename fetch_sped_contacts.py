import csv
import time
import json
import os
from google import genai
from google.genai import types

# --- Configuration ---
PROJECT_ID = "ny-build-487810"  
LOCATION = "us-central1"                     
INPUT_CSV = "texas_districts_websites.csv"
OUTPUT_CSV = "texas_districts_sped_contacts.csv"
MODEL_NAME = "gemini-2.0-flash"          

def init_client():
    """Initializes the new Google GenAI client for Vertex AI."""
    return genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

def get_district_sped_info(client, district_name, website):
    """Asks Gemini to search the district website and return a JSON object."""
    prompt = f"""
    You are an expert data researcher. Search for the Special Education (SPED) department 
    information for {district_name} in Texas. 
    Focus your search heavily on their official website: {website}.
    
    Find the following specific information:
    1. Executive Director Email (Special Education)
    2. Main Phone (Special Education Office)
    3. Office Address (Special Education Office)
    4. Dyslexia Coordinator Name
    5. Autism Specialist Name
    6. Evaluation Coordinator Name
    7. Records Clerk Name
    8. Any free resources offered for special ed (summarize in 1-2 sentences)
    
    Return ONLY a valid, raw JSON object with the exact keys below. Do not include markdown formatting like ```json.
    If a specific piece of information cannot be found, set its value to "NOT FOUND".
    
    {{
        "Executive Director Email": "",
        "Main Phone": "",
        "Office Address": "",
        "Dyslexia Coordinator": "",
        "Autism Specialist": "",
        "Evaluation Coordinator": "",
        "Records Clerk": "",
        "Free Resources": ""
    }}
    """
    
    config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.2, 
    )
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config
        )
        text_output = response.text.strip()
        
        if text_output.startswith("```json"):
            text_output = text_output[7:]
        if text_output.endswith("```"):
            text_output = text_output[:-3]
            
        return json.loads(text_output.strip())
        
    except json.JSONDecodeError:
        print(f"[ERROR] Model did not return valid JSON for {district_name}.")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to fetch {district_name}: {e}")
        return None

def main():
    print("Initializing the GenAI Client...")
    client = init_client()
    
    # 1. Figure out what we have already processed
    processed_districts = set()
    file_exists = os.path.exists(OUTPUT_CSV)
    
    if file_exists:
        try:
            with open(OUTPUT_CSV, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    processed_districts.add(row['District Name'])
            print(f"Found {len(processed_districts)} already processed districts. Resuming where we left off...")
        except Exception as e:
            print(f"[WARNING] Could not read existing output file: {e}")

    # 2. Read the input file
    all_districts = []
    print(f"Reading data from {INPUT_CSV}...")
    try:
        with open(INPUT_CSV, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                if row.get('Official Website') and row['Official Website'] not in ['NOT FOUND', 'ERROR']:
                    all_districts.append(row)
    except FileNotFoundError:
        print(f"[ERROR] Could not find {INPUT_CSV}.")
        return

    # 3. Filter out the districts we already finished
    districts_to_process = [d for d in all_districts if d['District Name'] not in processed_districts]
    
    if not districts_to_process:
        print("All districts have already been processed!")
        return
        
    print(f"Processing {len(districts_to_process)} remaining districts. This will take time as the AI performs live searches...")
    
    # 4. Open the file in APPEND mode ('a') so we don't overwrite existing data
    with open(OUTPUT_CSV, mode='a', encoding='utf-8', newline='') as outfile:
        fieldnames = [
            'District Name', 'Official Website', 'Executive Director Email', 
            'Main Phone', 'Office Address', 'Dyslexia Coordinator', 
            'Autism Specialist', 'Evaluation Coordinator', 'Records Clerk', 
            'Free Resources'
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        
        # Only write the header row if the file is brand new
        if not file_exists or os.path.getsize(OUTPUT_CSV) == 0:
            writer.writeheader()
        
        for i, row in enumerate(districts_to_process, 1):
            district = row['District Name']
            website = row['Official Website']
            
            print(f"[{i}/{len(districts_to_process)}] Searching Special Ed data for: {district}...")
            
            sped_data = get_district_sped_info(client, district, website)
            
            out_row = {
                'District Name': district,
                'Official Website': website
            }
            
            if sped_data:
                out_row.update(sped_data)
            else:
                for key in fieldnames[2:]:
                    out_row[key] = "ERROR"
            
            writer.writerow(out_row)
            
            # Flush the file buffer to ensure data is written to the disk immediately
            outfile.flush()
            
            time.sleep(3)
            
    print(f"\nDone! Contacts and resources successfully saved to '{OUTPUT_CSV}'.")

if __name__ == "__main__":
    main()