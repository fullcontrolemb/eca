import streamlit as st
import matplotlib.pyplot as plt


def render_dashboard(df, receitas, despesas, saldo):

    if df is None:
        st.info("Sem dados no mês atual.")
        return

    st.subheader("📋 Movimentações")
    st.dataframe(df)

    st.subheader("📊 Resumo Financeiro")

    col1, col2, col3 = st.columns(3)

    col1.metric("Receitas", f"{receitas:.2f}")
    col2.metric("Despesas", f"{despesas:.2f}")

    if saldo >= 0:
        col3.markdown(f"<h3 style='color:blue;'>Saldo: {saldo:.2f}</h3>", unsafe_allow_html=True)
    else:
        col3.markdown(f"<h3 style='color:red;'>Saldo: {saldo:.2f}</h3>", unsafe_allow_html=True)

    # Gráfico Pizza
    st.subheader("📈 Distribuição")

    labels = ["Receitas", "Despesas"]
    values = [receitas, despesas]

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%")
    ax.axis("equal")

    st.pyplot(fig)