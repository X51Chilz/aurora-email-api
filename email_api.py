from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ms_graph_oauth import get_auth_url
import requests
import json
import time
import os

app = FastAPI()

# Microsoft Graph API details
CLIENT_ID = "8128da9b-2e36-4d8f-b719-aafcad1362cf"
CLIENT_SECRET = "Dal8Q~s3EnYNAQMyLqJ4E-Lpgi4oHip7QdA9wbmc"
TENANT_ID = "common"
REDIRECT_URI = "http://localhost:5000/callback"
TOKEN_FILE = "token_data.json"

GRAPH_API_BASE_URL = "https://graph.microsoft.com/v1.0/me"

# Load token from file with error handling
def load_token():
    if not os.path.exists(TOKEN_FILE):
        return None

    try:
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)
            if "access_token" in data and "expires_at" in data:
                return data
            else:
                return None  # Invalid token data
    except (json.JSONDecodeError, FileNotFoundError):
        return None

# Save token to file
def save_token(token_data):
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=4)

# Refresh the access token when expired
def get_access_token():
    token_data = load_token()

    if not token_data or "expires_at" not in token_data:
        raise HTTPException(status_code=401, detail="No valid token found. Please authenticate first.")

    if "access_token" not in token_data or not token_data["access_token"] or time.time() > token_data["expires_at"]:
        print("🔄 Token expired or missing, attempting refresh...")

        if "refresh_token" not in token_data:
            raise HTTPException(status_code=401, detail="No refresh token available. Re-authentication required.")

        refresh_token = token_data["refresh_token"]
        token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
        payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "redirect_uri": REDIRECT_URI
        }

        response = requests.post(token_url, data=payload)

        if response.status_code == 200:
            new_token_data = response.json()
            new_token_data["expires_at"] = time.time() + new_token_data["expires_in"]
            save_token(new_token_data)
            print("✅ Token refreshed successfully!")
            return new_token_data["access_token"]
        else:
            raise HTTPException(status_code=401, detail=f"Authentication failed: {response.text}")

    return token_data["access_token"]


class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    confirm: bool = False

class MarkAsReadRequest(BaseModel):
    email_id: str
    confirm: bool = False

class ReplyRequest(BaseModel):
    email_id: str
    body: str
    confirm: bool = False

class ForwardRequest(BaseModel):
    email_id: str
    to: str
    confirm: bool = False


@app.get("/login")
def login():
    """Redirect user to Microsoft login page."""
    return {"login_url": get_auth_url()}

@app.post("/send")
def send_email(request: EmailRequest):
    """Send email only after confirmation."""
    if not request.confirm:
        return {
            "message": "Are you sure you want to send this email?",
            "details": {
                "to": request.to,
                "subject": request.subject,
                "body": request.body
            },
            "confirmation_required": True
        }

    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    url = f"{GRAPH_API_BASE_URL}/sendMail"
    email_data = {
        "message": {
            "subject": request.subject,
            "body": {"contentType": "Text", "content": request.body},
            "toRecipients": [{"emailAddress": {"address": request.to}}]
        },
        "saveToSentItems": True
    }
    response = requests.post(url, headers=headers, json=email_data)

    if response.status_code == 202:
        return {"message": "Email sent successfully"}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())

@app.post("/mark-as-read")
def mark_as_read(request: MarkAsReadRequest):
    """Mark an email as read."""
    if not request.confirm:
        return {"message": "Are you sure you want to mark this email as read?", "confirmation_required": True}

    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    url = f"{GRAPH_API_BASE_URL}/messages/{request.email_id}"
    data = {"isRead": True}
    response = requests.patch(url, headers=headers, json=data)

    if response.status_code == 200:
        return {"message": f"Email {request.email_id} marked as read."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())


@app.post("/reply")
def reply_to_email(request: ReplyRequest):
    """Reply to an email."""
    if not request.confirm:
        return {"message": "Are you sure you want to reply to this email?", "confirmation_required": True}

    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    url = f"{GRAPH_API_BASE_URL}/messages/{request.email_id}/reply"
    data = {"comment": request.body}
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 202:
        return {"message": "Reply sent successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())


@app.post("/forward")
def forward_email(request: ForwardRequest):
    """Forward an email."""
    if not request.confirm:
        return {"message": "Are you sure you want to forward this email?", "confirmation_required": True}

    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    url = f"{GRAPH_API_BASE_URL}/messages/{request.email_id}/forward"
    data = {"toRecipients": [{"emailAddress": {"address": request.to}}]}
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 202:
        return {"message": "Email forwarded successfully."}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())


@app.get("/email/{email_id}")
def fetch_specific_email(email_id: str):
    """Fetch a specific email by ID."""
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    url = f"{GRAPH_API_BASE_URL}/messages/{email_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())



@app.get("/fetch-all-emails")
def fetch_all_emails():
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    url = f"{GRAPH_API_BASE_URL}/mailFolders/inbox/messages"
    params = {
        "$top": 10,
        "$select": "id,sender,subject,bodyPreview",
        "$filter": "isDraft eq false"
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        emails = response.json().get("value", [])
        categorized_emails = [
            {
                "email_id": email["id"],
                "sender": email["sender"]["emailAddress"],
                "subject": email["subject"],
                "body_preview": email["bodyPreview"],
                "category": "lead" if "lead" in email["subject"].lower() or "opportunity" in email["subject"].lower() else "non-lead"
            }
            for email in emails
        ]
        return {"message": "Fetched and categorized emails successfully.", "emails": categorized_emails}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())

@app.get("/fetch-leads")
def fetch_leads():
    all_emails = fetch_all_emails()
    lead_emails = [email for email in all_emails["emails"] if email["category"] == "lead"]
    return {"message": "Fetched lead emails successfully.", "leads": lead_emails}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
