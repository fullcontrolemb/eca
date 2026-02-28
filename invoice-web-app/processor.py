from google import genai
from google.genai import types
import os
import json

def extract_invoice_details(image_path):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("DEBUG: GEMINI_API_KEY não encontrada nos Secrets!")
        return None

    client = genai.Client(api_key=api_key)
    
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

        # Configuração: JSON forçado + Filtros de segurança desativados
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
            safety_settings=[
                types.SafetySetting(category="HATE_SPEECH", threshold="BLOCK_NONE"),
                types.SafetySetting(category="HARASSMENT", threshold="BLOCK_NONE"),
                types.SafetySetting(category="SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
                types.SafetySetting(category="DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
            ]
        )

        prompt = "Extract from this invoice and return JSON: vendor_name (string), date (YYYY-MM-DD), total_amount (float), currency (string)."

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[prompt, image_part],
            config=config
        )
        
        # Log para vermos no console o que a IA mandou
        print(f"DEBUG - Resposta da IA: {response.text}")
        
        return json.loads(response.text)
        
    except Exception as e:
        print(f"DEBUG - Erro Crítico no Processor: {str(e)}")
        return None