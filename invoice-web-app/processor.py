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
        # Removi as configurações de segurança complexas para evitar erros de validação
        prompt = "Return ONLY a JSON object with vendor_name, date (YYYY-MM-DD), total_amount (number), and currency."

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[prompt, image_part]
        )
        
        # Limpeza agressiva do texto para pegar o JSON
        raw_text = response.text
        clean_text = raw_text.replace("```json", "").replace("```", "").strip()
        
        return json.loads(clean_text)
        
    except Exception as e:
        # Isso aparecerá no "Manage App" -> "Logs" do Streamlit
        st.error(f"Internal AI Error: {str(e)}") 
        return None