import streamlit as st
from auth import handle_callback, login_page
from sheets import save_entry, get_data
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

# ========================
# TELA PRINCIPAL
# ========================

st.title("💰 Controle Financeiro")

col1, col2 = st.columns(2)

if col1.button("➕ Adicionar"):
    st.session_state["page"] = "add"

if col2.button("📊 Visualizar"):
    st.session_state["page"] = "view"

if "page" not in st.session_state:
    st.session_state["page"] = "add"

# ========================
# PÁGINA ADICIONAR
# ========================

if st.session_state["page"] == "add":

    tab1, tab2 = st.tabs(["Despesa", "Receita"])

    with tab1:
        with st.form("expense_form"):
            date = st.date_input("Data")
            desc = st.text_input("Descrição")
            amount = st.number_input("Valor", min_value=0.0)
            currency = st.selectbox("Moeda", ["BRL", "USD", "EUR"])
            submit = st.form_submit_button("Salvar Despesa")

            if submit:
                save_entry({
                    "date": str(date),
                    "type": "Despesa",
                    "description": desc,
                    "amount": amount,
                    "currency": currency
                }, st.session_state["user_creds"])
                st.success("Despesa registrada!")

    with tab2:
        with st.form("income_form"):
            date = st.date_input("Data Receita")
            desc = st.text_input("Descrição Receita")
            amount = st.number_input("Valor Receita", min_value=0.0)
            currency = st.selectbox("Moeda Receita", ["BRL", "USD", "EUR"])
            submit = st.form_submit_button("Salvar Receita")

            if submit:
                save_entry({
                    "date": str(date),
                    "type": "Receita",
                    "description": desc,
                    "amount": amount,
                    "currency": currency
                }, st.session_state["user_creds"])
                st.success("Receita registrada!")

# ========================
# PÁGINA VISUALIZAR
# ========================

if st.session_state["page"] == "view":

    data = get_data(st.session_state["user_creds"])

    if data:
        df, receitas, despesas, saldo = data
        render_dashboard(df, receitas, despesas, saldo)
    else:
        st.info("Sem dados para o mês atual.")