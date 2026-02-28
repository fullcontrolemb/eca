import streamlit as st
from google_auth_oauthlib.flow import Flow
from processor import extract_invoice_details, save_to_user_sheets
import requests


st.write("Current URL:", st.query_params)
st.write("Redirect URI config:", st.secrets["REDIRECT_URI"])

# --- Configuração ---
st.set_page_config(page_title="AI Invoice Scanner", page_icon="📑")

CLIENT_CONFIG = {
    "web": {
        "client_id": st.secrets["GOOGLE_CLIENT_ID"],
        "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = "https://2b3irbf73cytwnmyerrpwc.streamlit.app"

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/spreadsheets",
]

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

# =============================
# CALLBACK
# =============================
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
        st.session_state["user_creds"] = token_json
        st.query_params.clear()
        st.rerun()
    else:
        st.error(token_json)
        st.stop()

# =============================
# LOGIN
# =============================
if "user_creds" not in st.session_state:

    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }

    auth_request = requests.Request("GET", AUTH_URL, params=params).prepare()
    st.link_button("🚀 Fazer Login com Google", auth_request.url)
    st.stop()


# ============================================================
# ✅ USUÁRIO LOGADO
# ============================================================

st.sidebar.success("Conectado com Google")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

st.title("📸 Scanner de Notas Fiscais")

uploaded_file = st.file_uploader("Envie a nota (JPG, PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, use_container_width=True)

    if st.button("🪄 Processar Nota"):
        with st.spinner("Processando..."):
            result = extract_invoice_details(uploaded_file)

            if result:
                st.json(result)
                save_to_user_sheets(result, st.session_state["user_creds"])

st.divider()
st.caption("Powered by Google Gemini AI & Streamlit")