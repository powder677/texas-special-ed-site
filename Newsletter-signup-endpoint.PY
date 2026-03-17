"""
NEWSLETTER SIGNUP ENDPOINT - Add to your app.py

This endpoint captures newsletter signups from the universal popup
and saves them to Firestore in the tx_newsletter_signups collection.
"""

from flask import Flask, request, jsonify
from google.cloud import firestore
from datetime import datetime

# Your existing Flask app and Firestore client
app = Flask(__name__)
db = firestore.Client(project="ard-intake-bot")


@app.route("/api/newsletter-signup", methods=["POST"])
def newsletter_signup():
    """
    Handle newsletter popup signups
    
    POST body:
    {
        "email": "sarah@example.com",
        "source": "newsletter_popup",
        "page_url": "/districts/dallas-isd",
        "page_title": "How to Request an FIE in Dallas ISD",
        "district": "dallas-isd",
        "timestamp": "2026-03-17T10:30:00Z"
    }
    """
    
    try:
        data = request.json
        
        # Validate email
        email = data.get("email", "").strip().lower()
        if not email or "@" not in email:
            return jsonify({"error": "Invalid email"}), 400
        
        # Create document ID from email (safe for Firestore)
        doc_id = email.replace("@", "_at_").replace(".", "_")
        
        # Build signup record
        signup_data = {
            "email": email,
            "source": data.get("source", "newsletter_popup"),
            "page_url": data.get("page_url", ""),
            "page_title": data.get("page_title", ""),
            "district": data.get("district"),  # null if not on district page
            "timestamp": datetime.now(),
            "subscribed": True,
            "subscriber_tier": "free",
            "tags": [data.get("source", "newsletter_popup")],
            
            # Tracking fields
            "emails_sent": 0,
            "emails_opened": 0,
            "unsubscribed": False,
            
            # Add district tag if present
            "district_tag": data.get("district") if data.get("district") else None
        }
        
        # If district present, add to tags
        if data.get("district"):
            signup_data["tags"].append(data.get("district"))
        
        # Save to Firestore (merge=True won't overwrite if already exists)
        db.collection("tx_newsletter_signups").document(doc_id).set(
            signup_data, 
            merge=True
        )
        
        # ALSO save to master email list (for unified tracking)
        db.collection("tx_emails").document(doc_id).set({
            "email": email,
            "source": data.get("source", "newsletter_popup"),
            "district": data.get("district"),
            "captured_at": datetime.now(),
            "subscribed": True,
            "subscriber_tier": "free",
            "tags": signup_data["tags"],
            "page_url": data.get("page_url"),
        }, merge=True)
        
        print(f"✓ Newsletter signup: {email} from {data.get('page_url', 'unknown page')}")
        
        return jsonify({
            "success": True,
            "message": "Newsletter signup successful",
            "email": email
        }), 200
        
    except Exception as e:
        print(f"Newsletter signup error: {e}")
        return jsonify({"error": "Signup failed"}), 500


# Optional: Unsubscribe endpoint
@app.route("/api/newsletter-unsubscribe", methods=["POST"])
def newsletter_unsubscribe():
    """
    Handle unsubscribe requests
    
    POST body:
    {
        "email": "sarah@example.com"
    }
    """
    
    try:
        email = request.json.get("email", "").strip().lower()
        doc_id = email.replace("@", "_at_").replace(".", "_")
        
        # Update both collections
        db.collection("tx_newsletter_signups").document(doc_id).update({
            "subscribed": False,
            "unsubscribed_at": datetime.now()
        })
        
        db.collection("tx_emails").document(doc_id).update({
            "subscribed": False,
            "unsubscribed_at": datetime.now()
        })
        
        return jsonify({"success": True}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)