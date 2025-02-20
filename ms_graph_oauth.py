import time
import requests
import webbrowser
import json
import os
from flask import Flask, request

# Microsoft OAuth2 Credentials
CLIENT_ID = "8128da9b-2e36-4d8f-b719-aafcad1362cf"
TENANT_ID = "2ad5f5a4-ecef-4ca2-97aa-e35dcf4c7658"
CLIENT_SECRET = "Dal8Q~s3EnYNAQMyLqJ4E-Lpgi4oHip7QdA9wbmc"
REDIRECT_URI = "http://localhost:5000/callback"
AUTH_URL = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
TOKEN_URL = f"https://login.microsoftonline.com/common/oauth2/v2.0/token"
SCOPES = "https://graph.microsoft.com/.default"
TOKEN_FILE = "token_data.json"
SCOPES = "offline_access https://graph.microsoft.com/.default"

app = Flask(__name__)

# Function to save token data
def save_token(token_data):
    token_data["expires_at"] = token_data.get("expires_in", 3600) + time.time()
    
    print("🔍 Saving new token data...")
    print(json.dumps(token_data, indent=4))  # Print the token before saving
    
    try:
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f, indent=4)
        print("✅ Token successfully saved!")
    except Exception as e:
        print(f"❌ Error saving token: {e}")

# Step 1: Redirect User to Microsoft Login
@app.route("/login")
def login():
    auth_params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "response_mode": "query",
        "scope": SCOPES,
    }
    auth_request_url = f"{AUTH_URL}?" + "&".join([f"{k}={v}" for k, v in auth_params.items()])
    webbrowser.open(auth_request_url)
    return "Please check your browser to authenticate."

# Step 2: Handle Microsoft OAuth Callback
@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
    }
    response = requests.post(TOKEN_URL, data=token_data)
    tokens = response.json()
    
    if "access_token" in tokens:
        save_token(tokens)
        return "✅ Authentication successful! Token saved. You may close this window."
    else:
        return f"❌ Authentication failed: {tokens}" 

if __name__ == "__main__":
    app.run(port=5000)
