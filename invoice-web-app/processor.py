import streamlit as st
from google import genai
from google.genai import types
import os
import json

def extract_invoice_details(image_path):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("API KEY não encontrada nos Secrets!")
        return None

    # Forçamos o cliente a usar a versão estável da API
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})
    
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

        # Mudamos o nome do modelo para o formato canônico
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=[
                "Extract: vendor_name, date (YYYY-MM-DD), total_amount (number), currency. Return ONLY JSON.",
                image_part
            ]
        )
        
        # Limpeza do JSON
        raw_text = response.text
        clean_text = raw_text.replace("```json", "").replace("```", "").strip()
        
        return json.loads(clean_text)
        
    except Exception as e:
        # Se o erro 404 persistir, vamos tentar o modelo 'gemini-1.5-pro' como alternativa
        st.error(f"AI Error: {str(e)}") 
        return None