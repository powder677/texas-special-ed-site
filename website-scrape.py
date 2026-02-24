import requests
import csv
import time

# 1. Setup Your API Key (Get this from Google Cloud Console)
API_KEY = "AIzaSyCAUxJRM8Iqr02FEB0ZTgWP-Cc_v325XIM"
# Using the Places API (New) Text Search for high accuracy
SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

# 2. Define the 20 Texas Districts 
# Formatted to give the API the best geographic context
districts = [
    "Houston ISD, Houston, Texas",
    "Dallas ISD, Dallas, Texas",
    "Cypress-Fairbanks ISD, Houston, Texas",
    "Northside ISD, San Antonio, Texas",
    "Katy ISD, Houston, Texas",
    "Fort Bend ISD, Houston, Texas",
    "IDEA Public Schools, Texas", 
    "Conroe ISD, Houston, Texas",
    "Austin ISD, Austin, Texas",
    "Fort Worth ISD, Fort Worth, Texas",
    "Frisco ISD, DFW, Texas",
    "Aldine ISD, Houston, Texas",
    "North East ISD, San Antonio, Texas",
    "Arlington ISD, DFW, Texas",
    "Klein ISD, Houston, Texas",
    "Garland ISD, DFW, Texas",
    "El Paso ISD, El Paso, Texas",
    "Lewisville ISD, DFW, Texas",
    "Plano ISD, DFW, Texas",
    "Pasadena ISD, Houston, Texas"
]

# 3. Define the 3 Buyer Categories and Search Terms
search_categories = {
    "Attorney": "Special education attorney",
    "Advocate": "Special education advocate",
    "Tutor": "Dyslexia tutor or learning center"
}

def search_businesses(district, category_name, search_term):
    """Calls Google Places API to find businesses matching the term in the district."""
    query = f"{search_term} near {district}"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        # Restricting field mask to save data costs and speed up the response
        "X-Goog-FieldMask": "places.displayName,places.websiteUri,places.nationalPhoneNumber"
    }
    
    payload = {
        "textQuery": query,
        "pageSize": 10 # Adjust up to 20 if you want to pull more leads per district
    }
    
    results = []
    try:
        response = requests.post(SEARCH_URL, json=payload, headers=headers)
        response.raise_for_status()
        
        places_data = response.json().get('places', [])
        
        for place in places_data:
            # We ONLY keep leads with websites so our Vertex AI script can evaluate them later
            if 'websiteUri' in place:
                results.append({
                    "District": district.split(",")[0], # Cleans up the name for the spreadsheet
                    "Category": category_name,
                    "Business Name": place.get('displayName', {}).get('text', 'N/A'),
                    "Website": place.get('websiteUri', 'N/A'),
                    "Phone": place.get('nationalPhoneNumber', 'N/A')
                })
        return results
    except Exception as e:
        print(f"Error searching for {query}: {e}")
        return []

# --- Main Execution block ---
if __name__ == "__main__":
    all_leads = []
    
    print(f"Starting lead generation for {len(districts)} districts...")
    
    for district in districts:
        print(f"\nSearching in {district}...")
        for cat_name, search_term in search_categories.items():
            print(f"  -> Finding {cat_name}s...")
            leads = search_businesses(district, cat_name, search_term)
            all_leads.extend(leads)
            
            # 2-second pause to strictly avoid Google Maps API rate limits
            time.sleep(2) 

    # 4. Save the results to a CSV file
    csv_filename = "texas_special_ed_leads_top20.csv"
    if all_leads:
        keys = all_leads[0].keys()
        with open(csv_filename, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(all_leads)
        print(f"\nSuccess! Saved {len(all_leads)} highly targeted leads to {csv_filename}")
    else:
        print("\nNo leads found with websites. Check your API key and connection.")