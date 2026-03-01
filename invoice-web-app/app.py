import streamlit as st
from auth import handle_callback, login_page
from sheets import save_entry, get_month_data
from dashboard import render_dashboard
from database import get_token

st.set_page_config(page_title="Finance SaaS", page_icon="📊")

handle_callback()

if "user_creds" not in st.session_state:
    login_page()
    st.stop()

# 🔧 Inicializa página
if "page" not in st.session_state:
    st.session_state["page"] = "main"
    
    # 🔹 Inicializa atalhos
if "shortcuts" not in st.session_state:
    st.session_state["shortcuts"] = [
        {"label": "Mercado", "icon": "🛒"},
        {"label": "Farmácia", "icon": "💊"},
        {"label": "Gasolina", "icon": "⛽"},
        {"label": "Padaria", "icon": "🥖"},
        {"label": "Mercadinho", "icon": "🏪"},
        {"label": "Verdurão", "icon": "🥬"},
        {"label": "Shopping", "icon": "🛍"},
        {"label": "Compra Online", "icon": "💻"},
    ]

if "descricao_temp" not in st.session_state:
    st.session_state["descricao_temp"] = ""

st.sidebar.success("Conectado")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# ========================
# TELA PRINCIPAL
# ========================

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
        st.rerun()

    if st.button("📊 Visualizar"):
        st.session_state["page"] = "view"
        st.rerun()
# ========================
# PÁGINA ADICIONAR
# ========================

if st.session_state["page"] == "add":

    # 🔙 BOTÃO VOLTAR
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🔙 Voltar", key="voltar_add"):
            st.session_state["page"] = "main"
            st.rerun()

    st.title("➕ Novo Lançamento")

    # 🔹 Campo descrição temporária
    if "descricao_temp" not in st.session_state:
        st.session_state["descricao_temp"] = ""

    # 🔹 ATALHOS FORA DO FORM
    st.markdown("### ⚡ Atalhos rápidos")

    cols = st.columns(4)

    for i, item in enumerate(st.session_state["shortcuts"]):

        label = f"{item['icon']} {item['label']}" if item["icon"] else item["label"]

        if cols[i % 4].button(label, key=f"shortcut_{i}"):
            st.session_state["descricao_temp"] = item["label"]
            st.rerun()

    st.divider()

    # 🔹 Criar novo atalho
    colA, colB = st.columns(2)
    novo_nome = colA.text_input("Nome do botão")
    novo_icon = colB.text_input("Emoji (opcional)")

    if st.button("Adicionar Atalho", key="add_shortcut"):
        if novo_nome:
            st.session_state["shortcuts"].append({
                "label": novo_nome,
                "icon": novo_icon
            })
            st.success("Atalho criado!")
            st.rerun()

    st.divider()

    # 🔹 FORMULÁRIO PRINCIPAL
    with st.form("finance_form"):

        date = st.date_input("Data")
        tipo = st.selectbox("Tipo", ["Entrada", "Saída"], index=1)
        value = st.number_input("Valor", min_value=0.0, format="%.2f")

        description = st.text_input(
            "Descrição",
            value=st.session_state["descricao_temp"]
        )

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

            st.session_state["descricao_temp"] = ""
            st.success("📝 Lançamento salvo!")
            st.session_state["page"] = "main"
            st.rerun()

# ========================
# PÁGINA VISUALIZAR
# ========================
if st.session_state["page"] == "view":

    # 🔙 BOTÃO NO TOPO
    col1, col2 = st.columns([1, 5])

    with col1:
        if st.button("🔙 Voltar", key="voltar_view"):
            st.session_state["page"] = "main"
            st.rerun()

    st.title("📊 Visualização do Mês")

    data = get_month_data(st.session_state["user_creds"])

    if data:
        df, entradas, saidas, saldo = data
        render_dashboard(df, entradas, saidas, saldo)
    else:
        st.info("Não há dados no mês atual.")

    # 🔙 BOTÃO VOLTAR
    if st.button("🔙 Voltar", key="voltar_add"):
        st.session_state["page"] = "main"
        st.rerun()
        