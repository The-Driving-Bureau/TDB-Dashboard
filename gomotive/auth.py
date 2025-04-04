import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_gomotive_access_token():
    auth_url = os.getenv("GOMOTIVE_AUTH_URL")
    client_id = os.getenv("GOMOTIVE_CLIENT_ID")
    client_secret = os.getenv("GOMOTIVE_CLIENT_SECRET")

    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "all"
    }

    response = requests.post(auth_url, data=payload)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to get token: {response.text}")