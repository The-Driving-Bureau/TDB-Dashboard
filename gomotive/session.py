import streamlit as st
import time

def save_token_to_session(token_data):
    """
    Stores access token and expiration details in Streamlit session state.
    """
    st.session_state["access_token"] = token_data.get("access_token")
    st.session_state["token_created_at"] = time.time()
    st.session_state["token_expires_in"] = token_data.get("expires_in")

def get_token_from_session():
    """
    Retrieves the access token from Streamlit session state.
    """
    return st.session_state.get("access_token")

def is_token_expired():
    """
    Checks if the current access token has expired.
    """
    created = st.session_state.get("token_created_at", 0)
    expires_in = st.session_state.get("token_expires_in", 0)
    return (time.time() - created) > expires_in
