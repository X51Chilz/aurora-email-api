import os
import json
import time
import requests

TOKEN_FILE = "token_data.json"

# Load token from environment variables or fallback to file
def load_token():
    token_data = {
        "access_token": os.getenv("EwA4BMl6BAAUBKgm8k1UswUNwklmy2v7U/S+1fEAAf1PRjfXGc+PFA0JjMJH9Udz9d6sq5bj2SfTmSH8/Bd9YMBgPHpBiG9b9xaUZMlSELJSSLNoZEDVon3v1IblMjG4lwkLwEArNAIctM8XFlL9VhNc9miZW70i7dF7Z/2/NuDpVPxO0KD5H4+FtacSkU833VN4i6864sHiQGfl5eJvoTgwvTGz6NMI2BC5NGRfDCkEuOcqQqz74qimg1MF07E7V1N8b1XPRMN9OjP1tdpagsvCdvgqvJzjzkUSl5Sj0XtuWAzdNbEiDUQpSGwTycqv1IwQyIrfH3IqfVUx7RXBBk+Jbc99B5S9oNWnBe82H7u387TGRSlotPsrV1FFE2EQZgAAECFeZRkS0swcMFV4qGArT8oAAybhMuRkpffCBmcelJbOxME+iwA4Mfbx9tXLZT6+EzMctQt8lnvA9wa2lKZPQ4BPUPQpsjLTmnv8spbSDZDqUO5f+SpLjj8M5sRWn6lAxO+Ao/sfzzrt5E9SI4/9hLgPW+upPzdD3wkn/UQbnvCVf61s6j4X0ZLWVAdVBLv5ImFlfjA8V323W9GwOWPM2sI9VGj7WbCdilnypJ8o7IRVU0TiSgo5awaEDrSQdIyD5me/PAQig8KJ3jPOYwkcrpxMTtheFSx4cbZeRWs+0+i9cQzli3klbRJgeYT85i+YOp27PmKMKEmN+FTmZ+3M2uR/AImmcZYfP9K3XrUd1j+HzBKnvo5knx6hEvDjHK+w9GMWC9/o9lVXYr2pJM42FJoLPQGCQJHcL12ZuMJ3JQ8lrX3aR7L2wLHSHnFDlQmdO3VmqJl7cfHKdk2pDoINjVS/mAsM7XmhGFJGWRO9V34YJI7YhkJr7ErArsV13dmUg2mAEptgyYoYR3wJx+8oc1c1/RHu8cEqKHz9wm50qWHWYryzxoEsGzwYHEZzVixVFWo5srislJWGmH5SCWwGF2JhXK9d/XwLAzQ5ckdonOz5ZT2C61OmhynY2YSOkY65Pbfw+y5ALxT37alq4HwXRbuQI3Z2mcFCSKGG9JoSo/ST6hvmr7TM1vmO+H51/fu/FThGALOGLiatybVAWUZLLHHqPMm6uSEmGX/LDs7lInkvcwI43M20YNDDzk8j17q5oolIdPi1Kse6BpltlRxrEfgksQGdFQ1TsHJKKUa4dX9Lq9vrwFnueaOfNsZBdOoWnM6CV8kOYnEHmoAkHoBUMTan/3d4QFLfmr+2SL0kSOily0RsnVDtCaiePshlHSLv2au0WlKDn/SYMFMk3zXVBMEJFJKrcnS5aUT76p7XXYcERPn832s1jmdXxu6Kk/Xbbr8a80TEbvQ6uA83NrGFGbst2Ph8tIW4yL5GLCyQOwPBD9znQhzYXABSlZUdNR7+LIt8AggYAYcV044jDbIF5wsWOUI"),
        "refresh_token": os.getenv("M.C526_SN1.0.U.-CmqpcZY2g*qRrzi3tK72xfJGF60L79l8Dmqu1eAVXuxLQi4rB6xwbp*CyCkWxYtIwZyoh!yOcshEmjwgVNZDM6naLJarjZQx40RoXpI!3RbHKYzt2Vl7BTU0hUM*5HrabnbkK*3HxWnf7FQYXiGY!elbSk5eAmcVEmOmwPKIMx4!VxUjIVdh1KpWOafJyQW*wHyW8wD4drosJb6hu8sLAL6C6mEb8S!VxYdXOGSOEJunz0KXZ4DIIWggvhMrqqChI0Mhd3AK*4XC1tV7AAeQOls*trv982J12ma9upVQYH0h7loTNqS2JyKf!zZWfn5kf5303y!JhdezxdRL37JXry!V3AJrao5pvJzLcB3DcD7nnVxldEhyfolnevG6HVFqSA$$"),
        "expires_at": float(os.getenv("1740050615.0838075", "0"))
    }
    if token_data["access_token"] and token_data["refresh_token"]:
        return token_data

    # Fallback: If env vars are missing, load from file
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return None

# Save token to environment variables and file
def save_token(token_data):
    os.environ["EwA4BMl6BAAUBKgm8k1UswUNwklmy2v7U/S+1fEAAf1PRjfXGc+PFA0JjMJH9Udz9d6sq5bj2SfTmSH8/Bd9YMBgPHpBiG9b9xaUZMlSELJSSLNoZEDVon3v1IblMjG4lwkLwEArNAIctM8XFlL9VhNc9miZW70i7dF7Z/2/NuDpVPxO0KD5H4+FtacSkU833VN4i6864sHiQGfl5eJvoTgwvTGz6NMI2BC5NGRfDCkEuOcqQqz74qimg1MF07E7V1N8b1XPRMN9OjP1tdpagsvCdvgqvJzjzkUSl5Sj0XtuWAzdNbEiDUQpSGwTycqv1IwQyIrfH3IqfVUx7RXBBk+Jbc99B5S9oNWnBe82H7u387TGRSlotPsrV1FFE2EQZgAAECFeZRkS0swcMFV4qGArT8oAAybhMuRkpffCBmcelJbOxME+iwA4Mfbx9tXLZT6+EzMctQt8lnvA9wa2lKZPQ4BPUPQpsjLTmnv8spbSDZDqUO5f+SpLjj8M5sRWn6lAxO+Ao/sfzzrt5E9SI4/9hLgPW+upPzdD3wkn/UQbnvCVf61s6j4X0ZLWVAdVBLv5ImFlfjA8V323W9GwOWPM2sI9VGj7WbCdilnypJ8o7IRVU0TiSgo5awaEDrSQdIyD5me/PAQig8KJ3jPOYwkcrpxMTtheFSx4cbZeRWs+0+i9cQzli3klbRJgeYT85i+YOp27PmKMKEmN+FTmZ+3M2uR/AImmcZYfP9K3XrUd1j+HzBKnvo5knx6hEvDjHK+w9GMWC9/o9lVXYr2pJM42FJoLPQGCQJHcL12ZuMJ3JQ8lrX3aR7L2wLHSHnFDlQmdO3VmqJl7cfHKdk2pDoINjVS/mAsM7XmhGFJGWRO9V34YJI7YhkJr7ErArsV13dmUg2mAEptgyYoYR3wJx+8oc1c1/RHu8cEqKHz9wm50qWHWYryzxoEsGzwYHEZzVixVFWo5srislJWGmH5SCWwGF2JhXK9d/XwLAzQ5ckdonOz5ZT2C61OmhynY2YSOkY65Pbfw+y5ALxT37alq4HwXRbuQI3Z2mcFCSKGG9JoSo/ST6hvmr7TM1vmO+H51/fu/FThGALOGLiatybVAWUZLLHHqPMm6uSEmGX/LDs7lInkvcwI43M20YNDDzk8j17q5oolIdPi1Kse6BpltlRxrEfgksQGdFQ1TsHJKKUa4dX9Lq9vrwFnueaOfNsZBdOoWnM6CV8kOYnEHmoAkHoBUMTan/3d4QFLfmr+2SL0kSOily0RsnVDtCaiePshlHSLv2au0WlKDn/SYMFMk3zXVBMEJFJKrcnS5aUT76p7XXYcERPn832s1jmdXxu6Kk/Xbbr8a80TEbvQ6uA83NrGFGbst2Ph8tIW4yL5GLCyQOwPBD9znQhzYXABSlZUdNR7+LIt8AggYAYcV044jDbIF5wsWOUI"] = token_data["access_token"]
    os.environ["M.C526_SN1.0.U.-CmqpcZY2g*qRrzi3tK72xfJGF60L79l8Dmqu1eAVXuxLQi4rB6xwbp*CyCkWxYtIwZyoh!yOcshEmjwgVNZDM6naLJarjZQx40RoXpI!3RbHKYzt2Vl7BTU0hUM*5HrabnbkK*3HxWnf7FQYXiGY!elbSk5eAmcVEmOmwPKIMx4!VxUjIVdh1KpWOafJyQW*wHyW8wD4drosJb6hu8sLAL6C6mEb8S!VxYdXOGSOEJunz0KXZ4DIIWggvhMrqqChI0Mhd3AK*4XC1tV7AAeQOls*trv982J12ma9upVQYH0h7loTNqS2JyKf!zZWfn5kf5303y!JhdezxdRL37JXry!V3AJrao5pvJzLcB3DcD7nnVxldEhyfolnevG6HVFqSA$$"] = token_data["refresh_token"]
    os.environ["1740050615.0838075"] = str(token_data["expires_at"])

    # Save to file as backup
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=4)

def get_auth_url():
    """Generate the Microsoft OAuth login URL."""
    return f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={8128da9b-2e36-4d8f-b719-aafcad1362cf}&response_type=code&redirect_uri={https://aurora-email-api.onrender.com/callback}&scope=openid profile email https://graph.microsoft.com/.default"

# Refresh the access token
def get_access_token():
    token_data = load_token()

    if not token_data or time.time() > token_data["expires_at"]:
        print("🔄 Token expired or missing, attempting refresh...")
        
        if "refresh_token" not in token_data:
            raise Exception("No refresh token available. Re-authentication required.")

        refresh_token = token_data["refresh_token"]
        token_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/token"
        payload = {
            "client_id": "8128da9b-2e36-4d8f-b719-aafcad1362cf",
            "client_secret": "Dal8Q~s3EnYNAQMyLqJ4E-Lpgi4oHip7QdA9wbmc",
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "redirect_uri": "https://aurora-email-api.onrender.com/callback"
        }
        response = requests.post(token_url, data=payload)

        if response.status_code == 200:
            new_token_data = response.json()
            new_token_data["expires_at"] = time.time() + new_token_data["expires_in"]
            save_token(new_token_data)
            print("✅ Token refreshed successfully!")
            return new_token_data["access_token"]
        else:
            raise Exception(f"Authentication failed: {response.text}")

    return token_data["access_token"]