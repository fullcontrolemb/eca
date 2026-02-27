from google import genai
import os
import json

def extract_invoice_details(image_path):
    # Pega a chave do ambiente
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    # Prompt otimizado
    prompt = "Extract from this invoice: vendor_name, date (YYYY-MM-DD), total_amount (float), and currency. Return ONLY JSON."
    
    # Carrega a imagem
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # Chama a API
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[prompt, image_bytes]
    )
    
    # Limpeza de texto para garantir JSON puro
    try:
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Erro no parse do JSON: {e}")
        return None