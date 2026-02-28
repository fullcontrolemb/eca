import streamlit as st
from google_auth_oauthlib.flow import Flow
from processor import extract_invoice_details

# Configurações do OAuth (Pegue nos Secrets do Streamlit)
CLIENT_CONFIG = {
    "web": {
        "client_id": st.secrets["GOOGLE_CLIENT_ID"],
        "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

def login_with_google():
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=[
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/spreadsheets',
            'openid'
        ],
        redirect_uri=st.secrets["REDIRECT_URI"]
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url

# --- Lógica de Interface ---
if "user_token" not in st.session_state:
    st.title("📑 AI Invoice Scanner")
    st.info("Log in with your Google account to save invoices directly to your Sheets.")
    url = login_with_google()
    st.link_button("🚀 Login with Google", url)
else:
    st.sidebar.success(f"Connected!")
    if st.sidebar.button("Logout"):
        del st.session_state["user_token"]
        st.rerun()
        
    # Aqui entra o seu código antigo do scanner...
    uploaded_file = st.file_uploader("Upload Invoice", type=['jpg', 'png'])
    if uploaded_file:
        # Processamento...
        pass