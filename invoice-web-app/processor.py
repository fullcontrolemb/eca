import streamlit as st
from google import genai
from google.genai import types
import os
import json
import gspread
from google.oauth2.credentials import Credentials

def extract_invoice_details(image_path):
    """Extrai dados usando o nome técnico completo para evitar erro 404."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("API KEY not found!")
        return None

    # Deixamos o cliente no modo automático (SDK Default 2026)
    client = genai.Client(api_key=api_key)
    
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

        # Tentamos o modelo 2.0 que é o mais compatível em 2026
        # Se preferir manter o 1.5, use "models/gemini-1.5-flash-latest"
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
        
        save_to_google_sheets(data)
        return data
        
    except Exception as e:
        # LOG DE DEPURAÇÃO: Se der erro, vamos tentar o nome alternativo dentro do except
        st.error(f"Primary Model failed: {str(e)}")
        return None

# --- FUNÇÕES AUXILIARES ---

def save_to_user_sheets(data, user_creds):
    """
    Salva os dados extraídos na planilha do PRÓPRIO usuário logado.
    """
    try:
        # 1. Autoriza o gspread usando as credenciais do usuário (OAuth)
        # O objeto 'user_creds' já vem com os escopos autorizados no login
        client = gspread.authorize(user_creds)
        
        # 2. Define o nome da planilha que será usada no Drive do usuário
        spreadsheet_name = "My_Invoice_Control_2026"
        
        try:
            # Tenta abrir a planilha pelo nome
            sh = client.open(spreadsheet_name)
        except gspread.SpreadsheetNotFound:
            # Se a planilha não existir no Drive do usuário, o app CRIA uma para ele
            sh = client.create(spreadsheet_name)
            # Adiciona um cabeçalho bonitinho na primeira linha
            sh.sheet1.append_row(["Date", "Vendor", "Total Amount", "Currency", "Processed At"])
            st.info(f"Criamos uma nova planilha '{spreadsheet_name}' no seu Google Drive!")
            
        sheet = sh.sheet1
        
        # 3. Prepara a linha para inserir (mesma lógica que você já tinha)
        from datetime import datetime
        row = [
            data.get('date', 'N/A'),
            data.get('vendor_name', 'Unknown'),
            data.get('total_amount', 0),
            data.get('currency', '$'),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Coluna extra de controle
        ]
        
        # 4. Insere a linha
        sheet.append_row(row)
        st.toast("✅ Dados salvos na SUA planilha do Google!", icon="📊")
        
    except Exception as e:
        st.error(f"Erro ao salvar no Google Sheets: {e}")