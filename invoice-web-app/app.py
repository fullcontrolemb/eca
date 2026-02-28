import streamlit as st
import os
from processor import extract_invoice_details

st.set_page_config(page_title="AI Invoice Scanner", page_icon="📑")

st.title("📑 AI Invoice Scanner")
st.info("Upload your receipt and let Gemini AI organize your finances.")

uploaded_file = st.file_uploader("Choose an invoice image", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    # Mostra a imagem na tela
    
    st.image(uploaded_file, caption='Invoice Preview', use_container_width=True)
    if st.button("Process Invoice"):
        with st.spinner('AI is analyzing the document...'):
            # Salva o arquivo temporariamente
            with open("temp_file.jpg", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # Chama a função do processor.py
                data = extract_invoice_details("temp_file.jpg")
                
                if data:
                    st.subheader("Results:")
                    col1, col2 = st.columns(2)
                    col1.metric("Vendor", data.get('vendor_name', 'Unknown'))
                    col2.metric("Total", f"{data.get('currency', '$')} {data.get('total_amount', 0)}")
                    st.write(f"**Date:** {data.get('date', 'N/A')}")
                    st.success("Analysis complete!")
                else:
                    st.error("AI could not extract data. Please try a clearer image.")
                
            except Exception as e:
                st.error(f"Error during processing: {e}")
            finally:
                # Sempre remove o arquivo temporário, dando certo ou errado
                if os.path.exists("temp_file.jpg"):
                    os.remove("temp_file.jpg")