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
    """Cria o objeto de fluxo de autenticação do Google corrigindo o erro de Verifier."""
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
    # RESOLVE O ERRO: "Missing code verifier"
    flow.code_verifier = None 
    return flow

# --- Configuração da Página ---
st.set_page_config(page_title="AI Invoice Scanner", page_icon="📑")

# --- Lógica de Captura do Retorno do Google (Callback) ---
if "code" in st.query_params and "user_creds" not in st.session_state:
    try:
        flow = create_oauth_flow()
        flow.fetch_token(code=st.query_params["code"])
        st.session_state["user_creds"] = flow.credentials
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.query_params.clear()
        st.error(f"Erro ao processar login: {e}")

# --- Interface do Usuário ---

# CASO 1: Usuário NÃO está logado
if "user_creds" not in st.session_state:
    st.title("📑 AI Invoice Scanner")
    st.markdown("""
    Bem-vindo! Este app utiliza IA para extrair dados de suas notas fiscais 
    e salvá-los diretamente na sua conta do Google Sheets.
    """)
    
    st.info("Por favor, faça login com sua conta Google para começar.")
    
    flow = create_oauth_flow()
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    
    # Usamos o link_button original para evitar o erro 403 do Google
    st.link_button("🚀 Fazer Login com Google", auth_url)

# CASO 2: Usuário ESTÁ logado
else:
    st.sidebar.success("Conectado com Google")
    if st.sidebar.button("Sair / Logout"):
        del st.session_state["user_creds"]
        st.rerun()

    st.title("📸 Scanner de Notas Fiscais")
    st.write("Suba a imagem da sua nota e a IA fará o resto.")

    uploaded_file = st.file_uploader("Escolha um arquivo (JPG, PNG)", type=['jpg', 'png', 'jpeg'])

    if uploaded_file:
        st.image(uploaded_file, caption="Nota enviada", use_container_width=True)
        
        if st.button("🪄 Processar Nota Fiscal"):
            with st.spinner("A IA está analisando os dados..."):
                try:
                    # 1. Extração via Gemini
                    result = extract_invoice_details(uploaded_file)
                    
                    if result:
                        st.subheader("Dados Extraídos")
                        st.json(result)
                        
                        # 2. Salva na planilha do usuário logado
                        save_to_user_sheets(result, st.session_state["user_creds"])
                        
                except Exception as e:
                    st.error(f"Ocorreu um erro no processamento: {e}")

st.divider()
st.caption("Powered by Google Gemini AI & Streamlit")