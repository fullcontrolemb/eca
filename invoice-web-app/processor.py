import streamlit as st
from google import genai
from google.genai import types
import os
import json
import gspread
from google.oauth2.service_account import Credentials

def extract_invoice_details(image_path):
    """Extrai dados da imagem forçando a API v1 para evitar o erro 404."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("API KEY not found in Secrets!")
        return None

    # FORÇA O USO DA API V1 (ESTÁVEL) - Isso resolve o erro 404 da v1beta
    client = genai.Client(
        api_key=api_key,
        http_options={'api_version': 'v1'}
    )
    
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

        # Usamos o nome do modelo sem prefixos extras, agora na rota estável
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=[
                "Extract ONLY JSON: vendor_name, date (YYYY-MM-DD), total_amount (float), currency.",
                image_part
            ]
        )
        
        if not response.text:
            st.error("AI returned an empty response. Try a clearer image.")
            return None
            
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        
        save_to_google_sheets(data)
        return data
        
    except Exception as e:
        # Se o erro 404 persistir, tentaremos o modelo gemini-2.0-flash na próxima
        st.error(f"AI Error: {str(e)}") 
        return None

# --- FUNÇÕES AUXILIARES ---

def save_to_google_sheets(data):
    """Salva os dados extraídos na sua planilha do Google."""
    try:
        # Define os escopos necessários para Sheets e Drive
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        
        # Carrega as credenciais do segredo do Streamlit
        if "GOOGLE_SHEETS_CREDENTIALS" not in st.secrets:
            st.warning("Google Sheets credentials not found in Secrets!")
            return

        creds_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        
        client = gspread.authorize(creds)
        
        # Abre a planilha pelo nome configurado
        # Certifique-se de que a planilha 'my_invoice_control' existe e foi compartilhada com o e-mail do JSON
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