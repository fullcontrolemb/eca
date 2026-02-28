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

    # Cliente padrão (o SDK 2026 já escolhe a melhor rota)
    client = genai.Client(api_key=api_key)
    
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

        # Usando o modelo sucessor: gemini-2.0-flash
        # Ele é mais rápido e melhor para extrair JSON de imagens
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=[
                "Extract: vendor_name, date (YYYY-MM-DD), total_amount (number), currency. Return ONLY JSON.",
                image_part
            ]
        )
        
        # Limpeza do JSON para garantir que não haja markdown (```json ...)
        raw_text = response.text
        clean_text = raw_text.replace("```json", "").replace("```", "").strip()
        
        return json.loads(clean_text)
        
    except Exception as e:
        # Se der erro, mostra o erro detalhado na tela
        st.error(f"AI Error: {str(e)}") 
        return None