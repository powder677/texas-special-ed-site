import csv
import time
import re
import vertexai
from vertexai.generative_models import GenerativeModel

# --- Configuration ---
# Replace with your actual Google Cloud Project ID
PROJECT_ID = "ny-build-487810"  
LOCATION = "us-central1"                     
INPUT_CSV = "texas_districts_data.csv"
OUTPUT_CSV = "texas_districts_websites.csv"

MODEL_NAME = "gemini-2.0-flash"          

def init_vertex():
    """Initializes Vertex AI and returns the generative model."""
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    return GenerativeModel(MODEL_NAME)

def get_official_website(model, district_name, region):
    """Calls Vertex AI to find the official website for a given district."""
    prompt = (
        f"What is the official website URL for {district_name} located in the {region} region of Texas? "
        "Return ONLY the raw URL (e.g., https://www.example.org) and absolutely nothing else. "
        "If you cannot find it, return 'NOT FOUND'."
    )
    
    try:
        response = model.generate_content(prompt)
        url = response.text.strip()
        return url
    except Exception as e:
        print(f"[ERROR] Failed to fetch {district_name}: {e}")
        return "ERROR"

def load_and_clean_data(filepath):
    """Robustly parses the CSV, ignoring source tags and whole-line quotes."""
    districts = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            # 1. Remove tags
            clean_line = re.sub(r'\\s*', '', line)
            # 2. Strip whitespace and remove quotes wrapping the entire line
            clean_line = clean_line.strip().strip('"')
            
            # Skip empty lines or the header row
            if not clean_line or 'District Name' in clean_line:
                continue
                
            # 3. Split by comma
            parts = clean_line.split(',')
            if len(parts) >= 3:
                districts.append({
                    'District Name': parts[0].strip(),
                    'Enrollment': parts[1].strip(),
                    'Region': parts[2].strip()
                })
        return districts
    except FileNotFoundError:
        print(f"[ERROR] Could not find {filepath}.")
        return None

def main():
    print("Loading and cleaning district data...")
    districts = load_and_clean_data(INPUT_CSV)
    
    if not districts:
        print("No districts found. Please check your CSV file.")
        return
        
    print(f"Successfully loaded {len(districts)} districts.")
    
    print("Initializing Vertex AI...")
    model = init_vertex()
    
    print(f"Processing websites. This will take a moment...")
    
    with open(OUTPUT_CSV, mode='w', encoding='utf-8', newline='') as outfile:
        # Define headers for the output file
        fieldnames = ['District Name', 'Enrollment', 'Region', 'Official Website']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, row in enumerate(districts, 1):
            district = row['District Name']
            region = row['Region']
            
            print(f"[{i}/{len(districts)}] Looking up: {district}...")
            website = get_official_website(model, district, region)
            
            # Write row to file immediately
            writer.writerow({
                'District Name': district,
                'Enrollment': row['Enrollment'],
                'Region': region,
                'Official Website': website
            })
            
            # Brief pause to respect API rate limits
            time.sleep(1)
            
    print(f"\nDone! Websites successfully saved to '{OUTPUT_CSV}'.")

if __name__ == "__main__":
    main()