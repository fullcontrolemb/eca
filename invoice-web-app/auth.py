import streamlit as st
import requests
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPES

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"


def handle_callback():
    if "code" in st.query_params:

        token_data = {
            "code": st.query_params["code"],
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        response = requests.post(TOKEN_URL, data=token_data)
        token_json = response.json()

        if "access_token" in token_json:

            # 🔥 Preserva refresh_token se já existir
            if "user_creds" in st.session_state:
                existing_refresh = st.session_state["user_creds"].get("refresh_token")
                if existing_refresh and "refresh_token" not in token_json:
                    token_json["refresh_token"] = existing_refresh

            st.session_state["user_creds"] = token_json

            st.query_params.clear()
            st.rerun()

        else:
            st.error(token_json)
            st.stop()


def login_page():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }

    auth_request = requests.Request("GET", AUTH_URL, params=params).prepare()

    st.title("📊 Finance SaaS")
    st.markdown("Gerencie suas despesas com segurança.")
    st.link_button("🚀 Login com Google", auth_request.url)