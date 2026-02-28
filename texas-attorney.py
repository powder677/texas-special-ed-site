import vertexai
import json
import csv
import time
import os
from vertexai.generative_models import GenerativeModel, Tool, GenerationConfig
from google.api_core.exceptions import GoogleAPIError

# =========================
# CONFIGURE THIS
# =========================
PROJECT_ID = "texasspecialed"
LOCATION = "us-central1" # Change if your project is in a different region
OUTPUT_DIR = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site"

# Ensure we are saving exactly into your project folder
if not os.path.exists(OUTPUT_DIR):
    print(f"Directory {OUTPUT_DIR} not found. Saving in current directory.")
else:
    os.chdir(OUTPUT_DIR)

# =========================
# INIT VERTEX
# =========================
vertexai.init(project=PROJECT_ID, location=LOCATION)

model = GenerativeModel(
    model_name="gemini-2.0-flash",
    tools=[Tool.from_dict({"google_search": {}})]
)

generation_config = GenerationConfig(
    temperature=0.2, # Keep low for factual extraction
    max_output_tokens=2048
)

# =========================
# TEXAS DISTRICTS FROM HTML
# =========================
DISTRICTS = [
    "Houston ISD", "Dallas ISD", "Cypress-Fairbanks ISD", "Northside ISD", "Katy ISD", 
    "Fort Bend ISD", "IDEA Public Schools", "Conroe ISD", "Austin ISD", "Fort Worth ISD", 
    "Frisco ISD", "Aldine ISD", "North East ISD", "Arlington ISD", "Klein ISD", 
    "Garland ISD", "El Paso ISD", "Lewisville ISD", "Plano ISD", "Pasadena ISD", 
    "Humble ISD", "Socorro ISD", "Round Rock ISD", "San Antonio ISD", "Killeen ISD", 
    "Lamar CISD", "Leander ISD", "United ISD", "Clear Creek ISD", "Harmony Public Schools", 
    "Mesquite ISD", "Richardson ISD", "Alief ISD", "Mansfield ISD", "Ysleta ISD", 
    "Denton ISD", "Ector County ISD", "Spring ISD", "Spring Branch ISD", "Corpus Christi ISD", 
    "Keller ISD", "Irving ISD", "Prosper ISD", "Pharr-San Juan-Alamo ISD", "Alvin ISD", 
    "Amarillo ISD", "Northwest ISD", "Comal ISD", "Edinburg CISD", "Midland ISD", 
    "Judson ISD", "Pflugerville ISD", "Carrollton-Farmers Branch ISD", "Lubbock ISD", 
    "Hays CISD", "La Joya ISD", "Eagle Mountain-Saginaw ISD", "Goose Creek CISD", 
    "McKinney ISD", "Tomball ISD", "Birdville ISD", "Allen ISD", "Hurst-Euless-Bedford ISD", 
    "Laredo ISD", "McAllen ISD", "Wylie ISD", "New Caney ISD", "Rockwall ISD", 
    "Harlingen CISD", "Crowley ISD", "Forney ISD", "Weslaco ISD", "Bryan ISD", 
    "Schertz-Cibolo-Universal City ISD", "Magnolia ISD", "Belton ISD", "Abilene ISD", 
    "College Station ISD", "Mission CISD", "Donna ISD", "Coppell ISD", 
    "Grapevine-Colleyville ISD", "San Angelo ISD", "Bastrop ISD", "Wichita Falls ISD", 
    "Dickinson ISD", "Burleson ISD", "Lake Travis ISD", "East Central ISD", "Del Valle ISD", 
    "Clint ISD", "Sherman ISD", "Georgetown ISD", "Montgomery ISD", "Royse City ISD", 
    "Rio Grande City Grulla ISD", "San Benito CISD", "Waller ISD", "Little Elm ISD", 
    "Midway ISD", "Temple ISD", "San Marcos CISD", "Longview ISD", "Eanes ISD", 
    "Texas City ISD", "Seguin ISD", "Texarkana ISD", "Copperas Cove ISD", "Crosby ISD", 
    "Princeton ISD", "Melissa ISD", "Friendswood ISD", "Channelview ISD", "Victoria ISD", 
    "Waco ISD", "Beaumont ISD", "Tyler ISD", "Santa Fe ISD", "Grand Prairie ISD"
]

# =========================
# FUNCTION
# =========================
def search_sped_attorneys(district_name, csv_filename="tx_sped_attorneys.csv"):
    
    # Custom prompt explicitly instructing the tool to leverage the TEA database 
    prompt = f"""
    Find 3 to 5 special education attorneys or law firms representing parents/students in disputes against {district_name} in Texas.
    Please use the Google Search tool to search: `site:tea.texas.gov "{district_name}" "attorney for petitioner"` OR `site:tea.texas.gov "{district_name}" "representing student"`. 
    You may also search general Texas law firm websites if you cannot find enough from the TEA site.
    
    Respond ONLY with a valid JSON array of objects. Do not use markdown blocks (no ```json). 
    Do not include any other text. Each object must have these exact keys:
    "attorney_name", "law_firm", "website", "phone_number", "city".
    If no results are found, return an empty array [].
    """

    try:
        print(f"Searching for: {district_name}...")
        response = model.generate_content(prompt, generation_config=generation_config)

        if response.candidates:
            raw_text = response.candidates[0].content.parts[0].text
            clean_text = raw_text.replace('```json', '').replace('```', '').strip()
            
            try:
                data = json.loads(clean_text)
                
                if not data:
                    print(f"  ⚠ Model returned empty array for {district_name}")
                    return

                # Append to CSV
                with open(csv_filename, "a", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    for item in data:
                        writer.writerow([
                            district_name,
                            item.get("attorney_name", "N/A"),
                            item.get("law_firm", "N/A"),
                            item.get("website", "N/A"),
                            item.get("phone_number", "N/A"),
                            item.get("city", "N/A")
                        ])
                print(f"  ✅ Saved {len(data)} results for {district_name}")
                
            except json.JSONDecodeError:
                print(f"  ❌ Failed to parse JSON for {district_name}. Raw output snippet: {raw_text[:100]}")
                
        else:
            print(f"  ⚠ No candidates returned for {district_name}")

    except GoogleAPIError as e:
        print(f"  ❌ Vertex API Error for {district_name}: {e}")
    except Exception as e:
        print(f"  ❌ Unexpected error for {district_name}: {e}")

# =========================
# EXECUTION
# =========================
if __name__ == "__main__":
    output_csv = "tx_sped_attorneys.csv"
    
    # Initialize CSV with headers
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["District", "Attorney Name", "Law Firm", "Website", "Phone Number", "City"])
    
    print(f"Starting search for {len(DISTRICTS)} districts. Saving to: {os.path.abspath(output_csv)}\n")
    
    for district in DISTRICTS:
        search_sped_attorneys(district, csv_filename=output_csv)
        # 3-second delay to ensure we respect Google Search API rate limits for 116 consecutive queries
        time.sleep(3) 
        
    print(f"\n🎉 All done! Data is ready in {output_csv}")