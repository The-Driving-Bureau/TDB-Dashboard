import requests
import os
from dotenv import load_dotenv
from urllib.parse import urlencode
import streamlit as st

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
    print("Token request payload:", payload)
    print("Token request headers:", headers)

    if response.status_code == 200:
        token_data = response.json()
        print("Token scopes granted:", token_data.get("scope"))
        return token_data
    else:
        raise Exception(f"Failed to retrieve GoMotive API token: {response.status_code} - {response.text}")

def get_from_gomotive(endpoint: str, token: str):
    """
    General-purpose GET request handler for GoMotive API using Bearer token.
    """
    if not token:
        raise ValueError("Missing access token.")

    url = f"https://api.gomotive.com/v1/{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    print(f"GET {url} → Headers: {headers}")

    response = requests.get(url, headers=headers)

    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.text}")

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed GET {endpoint}: {response.status_code} - {response.text}")

def get_current_user_info(token: str):
    return get_from_gomotive("users", token)

def get_user_info(token: str):
    return get_from_gomotive("users", token)

def get_driver_by_id(driver_id: int, token: str):
    return get_from_gomotive(f"users/{driver_id}", token)

def get_all_drivers(token: str):
    return get_from_gomotive("users", token)
