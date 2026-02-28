import streamlit as st
from google import genai
from google.genai import types
import os
import json
import gspread
from datetime import datetime

def extract_invoice_details(uploaded_file):
    """Extrai dados da nota fiscal usando a API do Gemini 2.0."""
    # Busca a chave nos Secrets do Streamlit (mais seguro que osenv puro)
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        st.error("API KEY (GEMINI_API_KEY) não encontrada nos Secrets!")
        return None

    # Inicializa o cliente Gemini
    client = genai.Client(api_key=api_key)
    
    try:
        # IMPORTANTE: Lemos os bytes diretamente do arquivo subido no Streamlit
        image_bytes = uploaded_file.getvalue()
        
        image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

        # Chama o modelo para processar a imagem
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=[
                "Extract ONLY JSON: vendor_name, date (YYYY-MM-DD), total_amount (float), currency.",
                image_part
            ]
        )
        
        if not response or not response.text:
            st.error("A IA não conseguiu ler os dados da imagem.")
            return None
            
        # Limpa a resposta para garantir que seja um JSON válido
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        
        # RETORNO: Apenas devolvemos os dados. 
        # NÃO chamamos o salvamento aqui dentro para evitar erros de credenciais.
        return data
        
    except Exception as e:
        st.error(f"Erro na extração dos dados: {str(e)}")
        return None

# --- FUNÇÕES DE ARMAZENAMENTO ---

def save_to_user_sheets(data, user_creds):
    """
    Salva os dados extraídos na planilha do Google Drive do usuário logado.
    """
    try:
        # Autoriza o gspread usando as credenciais dinâmicas do usuário (OAuth2)
        client = gspread.authorize(user_creds)
        
        # Nome do arquivo que será criado/buscado no Drive do usuário
        spreadsheet_name = "My_Invoice_Control_2026"
        
        try:
            # Tenta abrir a planilha existente
            sh = client.open(spreadsheet_name)
        except gspread.SpreadsheetNotFound:
            # Se não existir, cria uma nova automaticamente
            sh = client.create(spreadsheet_name)
            # Define o cabeçalho na primeira linha
            sh.sheet1.append_row(["Date", "Vendor", "Total Amount", "Currency", "Processed At"])
            st.info(f"Uma nova planilha '{spreadsheet_name}' foi criada no seu Google Drive.")
            
        sheet = sh.sheet1
        
        # Prepara a linha com os dados do JSON + carimbo de data/hora
        row = [
            data.get('date', 'N/A'),
            data.get('vendor_name', 'Unknown'),
            data.get('total_amount', 0),
            data.get('currency', '$'),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        
        # Insere a linha na planilha
        sheet.append_row(row)
        st.toast("✅ Dados salvos com sucesso no seu Google Sheets!", icon="📊")
        
    except Exception as e:
        st.error(f"Erro ao salvar na planilha: {e}")