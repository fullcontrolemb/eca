from google import genai
from google.genai import types
import os
import json

def extract_invoice_details(image_path):
    # Configura o cliente
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    # Define o modelo
    model_id = "gemini-1.5-flash"
    
    # Prompt focado em extrair dados estruturados
    prompt = "Analyze this invoice and return ONLY a JSON object with: vendor_name, date (YYYY-MM-DD), total_amount (float), and currency."
    
    # Prepara a imagem da forma correta para o SDK novo
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    
    # Cria a estrutura de "Part" que a biblioteca exige
    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type="image/jpeg" # Funciona para JPG e PNG
    )
    
    try:
        # Chama a API com a estrutura correta
        response = client.models.generate_content(
            model=model_id,
            contents=[prompt, image_part]
        )
        
        # Limpa o texto para garantir que venha apenas o JSON
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        
        return json.loads(text.strip())
        
    except Exception as e:
        print(f"Erro detalhado: {e}")
        return None