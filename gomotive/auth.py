import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_gomotive_access_token(auth_code: str):
    client_id = os.getenv("GOMOTIVE_CLIENT_ID")
    client_secret = os.getenv("GOMOTIVE_CLIENT_SECRET")
    token_url = os.getenv("GOMOTIVE_TOKEN_URL")
    redirect_uri = os.getenv("GOMOTIVE_REDIRECT_URI")

    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
    }

    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get token: {response.text}")
