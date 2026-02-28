from google import genai
from google.genai import types
import os
import json

def extract_invoice_details(image_path):
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
    
    try:
        # Configuração para forçar a saída como JSON
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1 # Menos "criatividade", mais precisão
        )

        prompt = "Extract: vendor_name (string), date (YYYY-MM-DD), total_amount (float), currency (string)."

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[prompt, image_part],
            config=config
        )
        
        # O Gemini agora entrega o JSON direto, sem markdown
        return json.loads(response.text)
        
    except Exception as e:
        # Isso vai aparecer nos logs do Streamlit para você investigar
        print(f"DEBUG - Erro na IA: {e}")
        return None