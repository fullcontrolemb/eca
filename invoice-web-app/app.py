import streamlit as st
from google_auth_oauthlib.flow import Flow
import os

# Importamos as funções do seu outro arquivo (processor.py)
# Certifique-se de que o arquivo processor.py está na mesma pasta
from processor import extract_invoice_details, save_to_user_sheets

# --- Configurações do OAuth ---
# Estas informações devem estar nos Secrets do Streamlit
CLIENT_CONFIG = {
    "web": {
        "client_id": st.secrets["GOOGLE_CLIENT_ID"],
        "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

import streamlit as st
from google_auth_oauthlib.flow import Flow
from processor import extract_invoice_details, save_to_user_sheets

# --- Configurações do OAuth ---
CLIENT_CONFIG = {
    "web": {
        "client_id": st.secrets["GOOGLE_CLIENT_ID"],
        "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

def create_oauth_flow():
    """Cria o objeto de fluxo de autenticação do Google."""
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
    # AJUSTE 1: Desativa o PKCE para evitar o erro "Missing code verifier"
    flow.code_verifier = None
    return flow

# --- Configuração da Página ---
st.set_page_config(page_title="AI Invoice Scanner", page_icon="📑")

# --- Lógica de Captura do Retorno do Google (Callback) ---
if "code" in st.query_params and "user_creds" not in st.session_state:
    try:
        flow = create_oauth_flow()
        # O fetch_token agora funcionará sem o verifier
        flow.fetch_token(code=st.query_params["code"])
        st.session_state["user_creds"] = flow.credentials
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao processar login: {e}")
        st.query_params.clear() # Limpa para permitir nova tentativa

# --- Interface do Usuário ---

if "user_creds" not in st.session_state:
    st.title("📑 AI Invoice Scanner")
    st.markdown("Bem-vindo! Faça login para salvar notas no seu Google Sheets.")
    st.info("Por favor, faça login com sua conta Google para começar.")
    
    flow = create_oauth_flow()
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    
    # AJUSTE 2: Usar um link HTML para abrir na MESMA aba (_self)
    # Isso evita que fiquem duas páginas abertas e o erro de sincronia
    st.markdown(f"""
        <a href="{auth_url}" target="_self">
            <button style="
                background-color: #ff4b4b; 
                color: white; 
                padding: 0.5rem 1rem; 
                border: none; 
                border-radius: 0.5rem; 
                cursor: pointer;
                font-weight: bold;">
                🚀 Fazer Login com Google
            </button>
        </a>
    """, unsafe_allow_html=True)

# CASO 2: Usuário ESTÁ logado
else:
    st.sidebar.success("Conectado com Google")
    if st.sidebar.button("Sair / Logout"):
        del st.session_state["user_creds"]
        st.rerun()

    st.title("📸 Scanner de Notas Fiscais")
    uploaded_file = st.file_uploader("Escolha um arquivo (JPG, PNG)", type=['jpg', 'png', 'jpeg'])

    if uploaded_file:
        st.image(uploaded_file, caption="Nota enviada", use_container_width=True)
        
        if st.button("🪄 Processar Nota Fiscal"):
            with st.spinner("A IA está analisando os dados..."):
                try:
                    result = extract_invoice_details(uploaded_file)
                    if result:
                        st.subheader("Dados Extraídos")
                        st.json(result)
                        save_to_user_sheets(result, st.session_state["user_creds"])
                except Exception as e:
                    st.error(f"Ocorreu um erro no processamento: {e}")

# Rodapé ou avisos
st.divider()
st.caption("Powered by Google Gemini AI & Streamlit")