import streamlit as st
from google import genai
from google.genai import types
import os
import json
import gspread
from datetime import datetime

def extract_invoice_details(uploaded_file):
    """Extrai dados usando a API do Gemini."""
    # O Streamlit Secrets ou Environment Variable deve ter a chave
    api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    
    if not api_key:
        st.error("GEMINI_API_KEY não encontrada!")
        return None

    client = genai.Client(api_key=api_key)
    
    try:
        # Lemos os bytes diretamente do objeto uploaded_file do Streamlit
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
            st.error("A IA retornou uma resposta vazia.")
            return None
            
        # Limpeza básica do Markdown JSON
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        
        return data # Retornamos apenas os dados. O salvamento será feito no app.py
        
    except Exception as e:
        st.error(f"Erro na extração Gemini: {str(e)}")
        return None

def save_to_user_sheets(data, user_creds):
    """Salva os dados na planilha do usuário logado via OAuth2."""
    try:
        # Autoriza o gspread com as credenciais do usuário vindas do login
        client = gspread.authorize(user_creds)
        
        spreadsheet_name = "My_Invoice_Control_2026"
        
        try:
            sh = client.open(spreadsheet_name)
        except gspread.SpreadsheetNotFound:
            # Cria se não existir
            sh = client.create(spreadsheet_name)
            sh.sheet1.append_row(["Date", "Vendor", "Total Amount", "Currency", "Processed At"])
            st.info(f"Nova planilha '{spreadsheet_name}' criada no seu Google Drive!")
            
        sheet = sh.sheet1
        
        row = [
            data.get('date', 'N/A'),
            data.get('vendor_name', 'Unknown'),
            data.get('total_amount', 0),
            data.get('currency', '$'),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        
        sheet.append_row(row)
        st.toast("✅ Salvo no Google Sheets!", icon="📊")
        
    except Exception as e:
        st.error(f"Erro ao salvar no Sheets: {e}")