import streamlit as st
import os
from processor import extract_invoice_details
# Comente as linhas do uploader se ainda não configurou as credenciais do Google
# from uploader import authenticate_drive, upload_invoice, append_to_sheet

st.set_page_config(page_title="AI Invoice Scanner", page_icon="📑")

st.title("📑 AI Invoice Scanner")
st.info("Upload your receipt and let Gemini AI organize your finances.")

uploaded_file = st.file_uploader("Choose an invoice image", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    st.image(uploaded_file, caption='Invoice Preview', use_container_width=True)
    
    if st.button("Process Invoice"):
        with st.spinner('AI is analyzing the document...'):
            # Salva temporariamente
            with open("temp_file.jpg", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # Chama a função do processor.py
                data = extract_invoice_details("temp_file.jpg")
                
                st.subheader("Results:")
                col1, col2 = st.columns(2)
                col1.metric("Vendor", data['vendor_name'])
                col2.metric("Total", f"{data['currency']} {data['total_amount']}")
                st.write(f"**Date:** {data['date']}")
                
                st.success("Analysis complete!")
                
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                if os.path.exists("temp_file.jpg"):
                    os.remove("temp_file.jpg")