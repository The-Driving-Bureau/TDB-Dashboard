import requests
import os
from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv()

def get_gomotive_access_token(auth_code: str):
    """
    Exchange an authorization code for an access token from GoMotive API.
    """
    url = "https://api.gomotive.com/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": os.getenv("GOMOTIVE_REDIRECT_URI"),
        "client_id": os.getenv("GOMOTIVE_CLIENT_ID"),
        "client_secret": os.getenv("GOMOTIVE_CLIENT_SECRET"),
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to retrieve GoMotive API token: {response.status_code} - {response.text}")

def get_current_user_info(token: str):
    url = "https://api.gomotive.com/v1/users/me"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    print(f"Requesting user info from: {url}")
    print(f"Using headers: {headers}")

    response = requests.get(url, headers=headers)

    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to retrieve user info: {response.status_code} - {response.text}")

def get_user_info(token: str):
    """
    Fetches user information using GoMotive API (matches /v1/users structure).
    """
    url = "https://api.gomotive.com/v1/users"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    print(f"Requesting user info from: {url}")
    print(f"Using headers: {headers}")

    response = requests.get(url, headers=headers)

    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to retrieve user info: {response.status_code} - {response.text}")
