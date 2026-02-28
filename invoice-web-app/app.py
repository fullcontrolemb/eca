import streamlit as st
from google_auth_oauthlib.flow import Flow
from processor import extract_invoice_details, save_to_user_sheets

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

from google_auth_oauthlib.flow import Flow
import streamlit as st

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/spreadsheets",
]

def create_flow(state=None):
    return Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=st.secrets["REDIRECT_URI"],
        state=state
    )

# ===============================
# CALLBACK
# ===============================

if "code" in st.query_params:

    flow = create_flow(state=st.session_state.get("oauth_state"))

    flow.fetch_token(code=st.query_params["code"])

    st.session_state["user_creds"] = flow.credentials

    st.query_params.clear()
    st.rerun()


# ===============================
# LOGIN
# ===============================

if "user_creds" not in st.session_state:

    flow = create_flow()

    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )

    # 🔥 SALVA O STATE CORRETO
    st.session_state["oauth_state"] = state

    st.link_button("🚀 Fazer Login com Google", auth_url)
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