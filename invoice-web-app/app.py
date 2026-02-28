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

def create_oauth_flow():
    """Cria o objeto de fluxo de autenticação do Google."""
    return Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=[
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/spreadsheets',
            'openid'
        ],
        redirect_uri=st.secrets["REDIRECT_URI"]
    )

# --- Configuração da Página ---
st.set_page_config(page_title="AI Invoice Scanner", page_icon="📑")

# --- Lógica de Captura do Retorno do Google (Callback) ---
# Se o Google redirecionar de volta com um código (?code=...)
if "code" in st.query_params and "user_creds" not in st.session_state:
    try:
        flow = create_oauth_flow()
        flow.fetch_token(code=st.query_params["code"])
        # Guardamos as credenciais completas na sessão
        st.session_state["user_creds"] = flow.credentials
        # Limpa os parâmetros da URL para o app ficar limpo
        st.query_params.clear()
        st.rerun()
    except Exception as e:
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
    
    # Gera a URL de login
    flow = create_oauth_flow()
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    
    st.link_button("🚀 Fazer Login com Google", auth_url)

# CASO 2: Usuário ESTÁ logado
else:
    # Sidebar com informações e Logout
    st.sidebar.success("Conectado com Google")
    if st.sidebar.button("Sair / Logout"):
        del st.session_state["user_creds"]
        st.rerun()

    st.title("📸 Scanner de Notas Fiscais")
    st.write("Suba a imagem da sua nota e a IA fará o resto.")

    uploaded_file = st.file_uploader("Escolha um arquivo (JPG, PNG)", type=['jpg', 'png', 'jpeg'])

    if uploaded_file:
        # Mostra a imagem para o usuário
        st.image(uploaded_file, caption="Nota enviada", use_container_width=True)
        
        # Botão para processar
        if st.button("🪄 Processar Nota Fiscal"):
            with st.spinner("A IA está analisando os dados..."):
                try:
                    # 1. Chama a função de extração (que usa sua Gemini API Key)
                    result = extract_invoice_details(uploaded_file)
                    
                    if result:
                        st.subheader("Dados Extraídos")
                        st.json(result)
                        
                        # 2. Salva na planilha DO USUÁRIO usando as credenciais dele
                        save_to_user_sheets(result, st.session_state["user_creds"])
                        
                except Exception as e:
                    st.error(f"Ocorreu um erro no processamento: {e}")

# Rodapé ou avisos
st.divider()
st.caption("Powered by Google Gemini AI & Streamlit")