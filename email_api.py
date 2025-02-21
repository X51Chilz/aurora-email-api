from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from ms_graph_oauth import get_auth_url
import requests
import json
import time
import os

app = FastAPI()

# Microsoft Graph API details
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = "common"
REDIRECT_URI = os.getenv("REDIRECT_URI")
TOKEN_ENV_VAR = "ACCESS_TOKEN"
REFRESH_TOKEN_ENV_VAR = "REFRESH_TOKEN"

GRAPH_API_BASE_URL = "https://graph.microsoft.com/v1.0/me"

# Load token from environment variables
def load_token():
    access_token = os.getenv(TOKEN_ENV_VAR)
    refresh_token = os.getenv(REFRESH_TOKEN_ENV_VAR)
    expires_at = os.getenv("TOKEN_EXPIRES_AT")
    if not access_token or not expires_at or time.time() > float(expires_at):
        return None
    return {"access_token": access_token, "refresh_token": refresh_token, "expires_at": float(expires_at)}

# Save token to environment variables
def save_token(token_data):
    os.environ[TOKEN_ENV_VAR] = token_data["access_token"]
    os.environ[REFRESH_TOKEN_ENV_VAR] = token_data["refresh_token"]
    os.environ["TOKEN_EXPIRES_AT"] = str(time.time() + token_data["expires_in"])

def get_access_token():
    token_data = load_token()
    if not token_data:
        raise HTTPException(status_code=401, detail="No valid token found. Please authenticate first.")
    if time.time() > token_data["expires_at"]:
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
    auth_url = (f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?"
                f"client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&"
                f"scope=openid profile email https://graph.microsoft.com/.default")
    return {"login_url": auth_url}

@app.get("/callback")
def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found.")
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    response = requests.post(token_url, data=payload)
    if response.status_code == 200:
        token_data = response.json()
        token_data["expires_at"] = time.time() + token_data["expires_in"]
        save_token(token_data)
        return {"message": "Authentication successful! Token saved."}
    else:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {response.text}")

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
    uvicorn.run(app, host="0.0.0.0", port=8000)