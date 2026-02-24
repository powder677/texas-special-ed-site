import json
import requests
from bs4 import BeautifulSoup
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

# 1. Initialize Vertex AI (Replace with your actual Project ID)
vertexai.init(project="texasspecialed", location="us-central1")

def scrape_website_text(url):
    """Fetches a URL and extracts clean, readable text."""
    try:
        # Adding a common user-agent helps prevent simple bot-blocks
        headers = {'User-Agent': 'Mozilla/5.0'} 
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove javascript and stylesheet code
        for script in soup(["script", "style"]):
            script.extract()
            
        # Extract text and limit to ~5,000 characters to save tokens
        text = " ".join(soup.stripped_strings)
        return text[:5000] 
    except Exception as e:
        return None

def qualify_and_categorize_lead(website_text):
    """Sends the text to Gemini and forces it to categorize the business."""
    model = GenerativeModel("gemini-1.5-flash-002")
    
    # We feed the AI your exact buyer profiles from the marketing offer
    prompt = f"""
    You are a lead qualification and routing engine. Analyze the following website text. 
    Categorize this business into one of the following four buckets based on these definitions:
    
    1. Attorney: Special education law firms or solo practitioners who represent parents in disputes or hearings.
    2. Advocate: Independent educational advocates (non-attorneys) who attend ARD meetings and review IEPs.
    3. Tutor: Private tutors, reading specialists, therapy practices (OT, speech), or learning centers.
    4. Irrelevant: The business does not fit any of the above categories.
    
    Website Text:
    {website_text}
    """
    
    # We update the schema to force the output into one of the 4 specific text strings
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "category": {
                "type": "STRING", 
                "enum": ["Attorney", "Advocate", "Tutor", "Irrelevant"]
            },
            "reason": {
                "type": "STRING",
                "description": "A single sentence explaining why it was placed in this category."
            }
        },
        "required": ["category", "reason"]
    }
    
    response = model.generate_content(
        prompt,
        generation_config=GenerationConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=0.1 
        )
    )
    
    return json.loads(response.text)
# --- Test the Pipeline ---
test_url = "https://www.example-pediatric-therapy.com" 
website_data = scrape_website_text(test_url)

if website_data:
    result = qualify_lead(website_data)
    print(f"Qualified: {result['is_relevant']}")
    print(f"Reason: {result['reason']}")
else:
    print("Could not scrape website.")