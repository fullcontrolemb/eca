import streamlit as st
from auth import handle_callback, login_page
from sheets import save_entry, get_month_data
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

# ——————————————
# Tela Principal
# ——————————————

if st.session_state["page"] == "main":

    st.title("📊 Controle Financeiro")

    col1,col2,col3 = st.columns(3)

    data = get_month_data(st.session_state["user_creds"]) or (None,0,0,0)
    entradas, saidas, saldo = data[1], data[2], data[3]

    col1.metric("Entradas", f"{entradas:.2f}")
    col2.metric("Saídas", f"{saidas:.2f}")

    color = "blue" if saldo >= 0 else "red"
    col3.markdown(f"<h3 style='color:{color};'>{saldo:.2f}</h3>", unsafe_allow_html=True)

    if st.button("➕ Adicionar"):
        st.session_state["page"] = "add"
        st.experimental_rerun()

    if st.button("📊 Visualizar"):
        st.session_state["page"] = "view"
        st.experimental_rerun()
# ========================
# PÁGINA ADICIONAR
# ========================

if st.session_state["page"] == "add":

    with st.form("finance_form"):

        date = st.date_input("Data")
        tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
        value = st.number_input("Valor", min_value=0.0, format="%.2f")
        description = st.text_input("Descrição")
        obs = st.text_area("Observação (opcional)")

        submit = st.form_submit_button("Salvar")

        if submit:
            save_entry({
                "date": str(date),
                "type": tipo,
                "value": value,
                "description": description,
                "obs": obs
            }, st.session_state["user_creds"])

            st.success("📝 Lançamento salvo!")
            st.session_state["page"] = "main"
            st.experimental_rerun()

# ========================
# PÁGINA VISUALIZAR
# ========================

if st.session_state["page"] == "view":

    data = get_month_data(st.session_state["user_creds"])

    if data:
        df, entradas, saidas, saldo = data
        render_dashboard(df, entradas, saidas, saldo)
    else:
        st.info("Não há dados no mês atual.")

    if st.button("🔙 Voltar"):
        st.session_state["page"] = "main"
        st.experimental_rerun()