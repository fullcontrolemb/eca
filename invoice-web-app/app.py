import streamlit as st
from processor import extract_invoice_details
from uploader import authenticate_drive, upload_invoice, append_to_sheet

st.title("📑 AI Invoice Scanner")
st.subheader("Upload your receipt and let the AI do the work")

# Upload do arquivo na página
uploaded_file = st.file_uploader("Choose an invoice image", type=['png', 'jpg', 'jpeg', 'pdf'])

if uploaded_file is not None:
    st.image(uploaded_file, caption='Invoice Preview', width=300)
    
    if st.button("Process & Save to Drive"):
        with st.spinner('AI is reading the invoice...'):
            # Salva temporariamente para processar
            with open("temp_file.jpg", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 1. Extração com IA
            data = extract_invoice_details("temp_file.jpg")
            st.success(f"Extracted: {data['vendor_name']} - {data['total_amount']} {data['currency']}")
            
            # 2. Upload e Planilha
            drive = authenticate_drive()
            new_name = f"{data['date']}_{data['vendor_name']}.jpg"
            upload_invoice(drive, "temp_file.jpg", "SEU_FOLDER_ID", new_name)
            append_to_sheet(data, "SEU_SHEET_ID")
            
            st.balloons()
            st.info("File saved and Sheet updated!")