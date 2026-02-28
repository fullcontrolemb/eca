import streamlit as st
from google import genai
from google.genai import types
import os
import json
import gspread
from google.oauth2.service_account import Credentials

def extract_invoice_details(image_path):
    """Extrai dados da imagem usando o modelo 1.5-flash-8b para evitar erros de cota."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("API KEY not found in Secrets!")
        return None

    client = genai.Client(api_key=api_key)
    
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

        # Usando o modelo 1.5-flash-8b (mais leve e com cota mais flexível)
        response = client.models.generate_content(
            model="gemini-1.5-flash-8b", 
            contents=[
                "Extract ONLY JSON: vendor_name, date (YYYY-MM-DD), total_amount (float), currency.",
                image_part
            ]
        )
        
        # Limpeza e conversão do texto para dicionário Python
        raw_text = response.text
        clean_text = raw_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        
        # Tenta salvar no Google Sheets automaticamente após extrair
        save_to_google_sheets(data)
        
        return data
        
    except Exception as e:
        st.error(f"AI Error: {str(e)}") 
        return None

# --- FUNÇÕES AUXILIARES ---

def save_to_google_sheets(data):
    """Salva os dados extraídos na sua planilha do Google."""
    try:
        # Define os escopos necessários
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        
        # Carrega as credenciais do segredo do Streamlit
        # Certifique-se de que 'GOOGLE_SHEETS_CREDENTIALS' está nos seus Secrets
        creds_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        
        client = gspread.authorize(creds)
        
        # Abre a planilha pelo nome (mude 'my_invoice_control' para o nome da sua)
        sheet = client.open("my_invoice_control").sheet1
        
        # Prepara a linha para inserir
        row = [
            data.get('date', 'N/A'),
            data.get('vendor_name', 'Unknown'),
            data.get('total_amount', 0),
            data.get('currency', '$')
        ]
        
        sheet.append_row(row)
        st.toast("✅ Data saved to Google Sheets!", icon="📊")
        
    except Exception as e:
        st.warning(f"Could not save to Sheets: {e}")