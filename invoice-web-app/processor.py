import streamlit as st
from google import genai
from google.genai import types
import os
import json
import gspread
from google.oauth2.credentials import Credentials
from datetime import datetime

def extract_invoice_details(uploaded_file):
    """Extrai dados usando o Google Gemini 2.0."""
    # Busca a chave de ambiente ou secrets
    api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    
    if not api_key:
        st.error("GEMINI_API_KEY not found!")
        return None

    client = genai.Client(api_key=api_key)
    
    try:
        # CORREÇÃO: Lê os bytes do objeto UploadedFile diretamente
        image_bytes = uploaded_file.getvalue()
        
        image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=[
                "Extract ONLY JSON: vendor_name, date (YYYY-MM-DD), total_amount (float), currency.",
                image_part
            ]
        )
        
        if not response.text:
            st.error("AI returned an empty response.")
            return None
            
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        
        # Removida a chamada save_to_google_sheets(data) pois ela não existe.
        # O salvamento agora é feito pelo app.py chamando save_to_user_sheets
        return data
        
    except Exception as e:
        st.error(f"Gemini error: {str(e)}")
        return None

# --- FUNÇÕES AUXILIARES ---

def save_to_user_sheets(data, user_creds):
    """
    Salva os dados extraídos na planilha do PRÓPRIO usuário logado.
    """
    try:
        # 1. Autoriza o gspread usando as credenciais do usuário (OAuth)
        client = gspread.authorize(user_creds)
        
        # 2. Define o nome da planilha
        spreadsheet_name = "My_Invoice_Control_2026"
        
        try:
            sh = client.open(spreadsheet_name)
        except gspread.SpreadsheetNotFound:
            # Cria a planilha se não existir
            sh = client.create(spreadsheet_name)
            sh.sheet1.append_row(["Date", "Vendor", "Total Amount", "Currency", "Processed At"])
            st.info(f"Criamos uma nova planilha '{spreadsheet_name}' no seu Drive!")
            
        sheet = sh.sheet1
        
        # 3. Prepara a linha
        row = [
            data.get('date', 'N/A'),
            data.get('vendor_name', 'Unknown'),
            data.get('total_amount', 0),
            data.get('currency', '$'),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        
        # 4. Insere a linha
        sheet.append_row(row)
        st.toast("✅ Dados salvos na sua planilha!", icon="📊")
        
    except Exception as e:
        st.error(f"Erro ao salvar no Google Sheets: {e}")