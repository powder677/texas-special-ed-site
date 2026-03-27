from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # <-- Cleanly added here!
from pydantic import BaseModel
from typing import Dict, Any, Optional
import vertexai
from vertexai.generative_models import GenerativeModel, Tool
from vertexai.preview.generative_models import grounding
from google.cloud import firestore
import uuid
import stripe

# --- Configuration & Initialization ---
PROJECT_ID = "texasspecialed"
LOCATION = "us-central1"

# Stripe Configuration (Use your TEST keys for now)
stripe.api_key = "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"
STRIPE_WEBHOOK_SECRET = "whsec_02a8c1e32bab35eae548a48451242fdec5dca16fa0687e3195c9422609d3a7c2"
DOMAIN_URL = "http://localhost:8000" # Change to texasspecialed.com in production

# Your specific Data Store details
DATA_STORE_ID = "texas-sped-knowledge-base_1774276993820"
# Note: Vertex AI Search data stores usually live in the "global" location
DATA_STORE_PATH = f"projects/{PROJECT_ID}/locations/global/collections/default_collection/dataStores/{DATA_STORE_ID}"

# Initialize Vertex AI & Firestore
vertexai.init(project=PROJECT_ID, location=LOCATION)
db = firestore.Client(project=PROJECT_ID)

# 1. Initialize the app cleanly
app = FastAPI(title="Texas Special Ed Advocate API")

# 2. Add the CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, lock this down to texasspecialed.com
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AI Model Setup ---
datastore_tool = Tool.from_retrieval(
    retrieval=grounding.Retrieval(
        source=grounding.VertexAISearch(datastore=DATA_STORE_PATH),
    )
)

system_instruction = """
You are a strict, retrieval-grounded legal analysis assistant specializing ONLY in Texas special education law. 

CRITICAL RULES:
1. ZERO HALLUCINATION: You MUST ONLY use the provided retrieved documents.
2. TEXAS SUPREMACY: If there is a conflict between Federal IDEA timelines and Texas Education Code (TEC) timelines, you MUST use the strict Texas timelines (e.g., the 45-school-day FIE rule). 
3. MANDATORY CITATION: Every claim or timeline must be backed by a specific citation from the retrieved context (e.g., TEC §29.004 or TAC §89.1011).
4. THE SAFETY VALVE: If the documents do not specifically mention Texas law for the user's issue, state: "The provided documents do not contain enough specific Texas information to verify this issue."
5. TONE: Objective, authoritative, clear. Do not claim to be a lawyer.
"""

model = GenerativeModel(
    model_name="gemini-2.5-flash",
    tools=[datastore_tool],
    system_instruction=system_instruction,
)

# --- Request/Response Models ---
class AnalyzeRequest(BaseModel):
    district: Optional[str] = ""
    grade: Optional[str] = ""
    urgency: str
    category: str
    additional_details: Optional[str] = ""
    follow_up: Dict[str, Any]  # Catches the dynamic nested dictionary from the frontend

class AnalyzeResponse(BaseModel):
    session_id: str
    teaser_summary: str
    issues_found_count: int

class CheckoutSessionRequest(BaseModel):
    session_id: str

# --- API Endpoints ---

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_violation(request: AnalyzeRequest):
    try:
        # 1. Format the dynamic follow-up dictionary into a readable string for the AI
        follow_up_formatted = "\n".join([f"- {k.replace('_', ' ').title()}: {v}" for k, v in request.follow_up.items()])

        # 2. Combine all structured fields into a highly detailed prompt block
        combined_situation = f"""
        District: {request.district}
        Grade: {request.grade}
        Urgency Level: {request.urgency.upper()}
        Primary Category: {request.category.replace('_', ' ').title()}
        
        Specific Incident Details:
        {follow_up_formatted}
        
        Additional Parent Context:
        {request.additional_details}
        """

        # 3. Augment input for better Vertex Search retrieval
        augmented_input = f"{combined_situation}\n(Note: Consider Texas Education Code (TEC), Texas Administrative Code (TAC), timelines, and TEA guidelines for {request.district} district context)."

        # 4. Layer 2: Core Engine Prompt
        prompt = f"""
        Analyze the user's situation using ONLY the retrieved context.
        
        USER SITUATION:
        {augmented_input}
        
        Follow this exact structure for your response. Use the exact headers.
        
        [SUMMARY]
        Write a 2-3 sentence clear conclusion about their situation, explicitly citing a Texas timeline (like the 45-school-day rule) if applicable.
        
        [ISSUES_COUNT]
        (Output ONLY a single integer representing the number of potential violations or risks found. If none, output 0).
        
        [PAID_ANALYSIS]
        📘 What the Law Says:
        (Cite the specific Texas rule or timeline).
        
        ⚖️ What This Means for You:
        (Interpretation of their situation).
        
        ❗ Potential Problems:
        (Bullet points of risks).
        
        📎 Sources Referenced:
        (List the documents used).
        """

        # 5. Call the Model
        response = model.generate_content(
            prompt,
            tools=[datastore_tool], 
            generation_config={"temperature": 0.2} # Low temperature for strict factual output
        )
        
        raw_text = response.text
        
        # 6. Parse the structured output
        try:
            summary_part = raw_text.split("[SUMMARY]")[1].split("[ISSUES_COUNT]")[0].strip()
            count_str = raw_text.split("[ISSUES_COUNT]")[1].split("[PAID_ANALYSIS]")[0].strip()
            issues_count = int(count_str) if count_str.isdigit() else 1
            paid_analysis_part = raw_text.split("[PAID_ANALYSIS]")[1].strip()
        except IndexError:
            # Fallback if the AI messes up the formatting
            summary_part = "We have analyzed your situation against Texas special education timelines."
            issues_count = 1
            paid_analysis_part = raw_text

        # 7. Save EVERYTHING to Firestore securely
        session_id = str(uuid.uuid4())
        doc_ref = db.collection("violation_reports").document(session_id)
        
        # Saving the new structured data cleanly
        doc_ref.set({
            "district": request.district,
            "grade": request.grade,
            "urgency": request.urgency,
            "category": request.category,
            "follow_up_data": request.follow_up, # Saves the nested dict natively in Firestore
            "additional_details": request.additional_details,
            "prompt_used": combined_situation,
            "teaser_summary": summary_part,
            "issues_count": issues_count,
            "full_paid_analysis": paid_analysis_part,
            "payment_status": "unpaid",
            "created_at": firestore.SERVER_TIMESTAMP
        })

        # 8. Return ONLY the teaser to the frontend
        return AnalyzeResponse(
            session_id=session_id,
            teaser_summary=summary_part,
            issues_found_count=issues_count
        )

    except Exception as e:
        print(f"Error during analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during analysis.")


# --- Endpoint to fetch paid data AFTER Stripe/Payment ---
@app.get("/api/get-full-report/{session_id}")
async def get_full_report(session_id: str):
    doc_ref = db.collection("violation_reports").document(session_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Report not found")
        
    data = doc.to_dict()
    
    if data.get("payment_status") != "paid":
        raise HTTPException(status_code=403, detail="Payment required to view full analysis")
        
    return {"full_paid_analysis": data.get("full_paid_analysis")}


# --- Create the Stripe Checkout Page ---
@app.post("/api/create-checkout-session")
async def create_checkout_session(request: CheckoutSessionRequest):
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': 2900, # $29.00 in cents
                    'product_data': {
                        'name': 'Full IEP Violation & Strategy Report',
                        'description': 'Exact legal citations, missed deadlines, and next steps.',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            metadata={'session_id': request.session_id},
            success_url=f"http://localhost:8000/success.html?session_id={request.session_id}",
            cancel_url="http://localhost:8000/dashboard.html",
        )
        return {"checkout_url": checkout_session.url}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- The Webhook (Stripe talks to your API) ---
@app.post("/api/stripe-webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        document_id = session.get('metadata', {}).get('session_id')
        
        if document_id:
            # FLIP THE SWITCH IN FIRESTORE
            doc_ref = db.collection("violation_reports").document(document_id)
            doc_ref.update({"payment_status": "paid"})
            print(f"✅ Successfully unlocked report for {document_id}")

    return {"status": "success"}

# 👇 Notice how this is completely un-indented, flush left 👇
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")