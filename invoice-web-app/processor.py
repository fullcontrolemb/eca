import google.generativeai as genai
import os
import json

def extract_invoice_details(image_path):
    # Pega a chave das configurações (Secrets) do site
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    # Prompt focado em extrair dados estruturados
    prompt = """
    Analyze this invoice and return ONLY a JSON object with:
    {
      "vendor_name": "string",
      "date": "YYYY-MM-DD",
      "total_amount": float,
      "currency": "string"
    }
    """
    
    # Carrega a imagem
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    contents = [
        prompt,
        {"mime_type": "image/jpeg", "data": image_data}
    ]
    
    response = model.generate_content(contents)
    
    # Limpa a resposta para garantir que seja um JSON válido
    json_text = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(json_text)