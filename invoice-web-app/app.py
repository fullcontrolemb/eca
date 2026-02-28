import streamlit as st
from auth import handle_callback, login_page
from sheets import save_invoice, get_summary
from drive import upload_file
from dashboard import render_dashboard

st.set_page_config(page_title="Finance SaaS", page_icon="📊")

handle_callback()

if "user_creds" not in st.session_state:
    login_page()
    st.stop()

st.sidebar.success("Conectado")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

st.title("📄 Nova Despesa")

with st.form("invoice_form"):
    date = st.date_input("Data")
    vendor = st.text_input("Fornecedor")
    amount = st.number_input("Valor", min_value=0.0)
    currency = st.selectbox("Moeda", ["BRL", "USD", "EUR"])
    category = st.selectbox("Categoria", ["Alimentação", "Transporte", "Moradia", "Outros"])
    file = st.file_uploader("Anexar comprovante", type=["pdf", "jpg", "png"])

    submit = st.form_submit_button("Salvar")

    if submit and vendor and amount > 0:
        file_link = None
        if file:
            file_link = upload_file(file, st.session_state["user_creds"])

        save_invoice({
            "date": str(date),
            "vendor": vendor,
            "amount": amount,
            "currency": currency,
            "category": category,
            "file": file_link
        }, st.session_state["user_creds"])

        st.success("Salvo com sucesso!")

st.divider()
render_dashboard(get_summary(st.session_state["user_creds"]))