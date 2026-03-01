import streamlit as st
import pandas as pd

def render_dashboard(df, entradas, saidas, saldo):

    if df is None:
        st.info("Sem dados no mês atual.")
        return

    st.subheader("📋 Movimentações do Mês")
    st.dataframe(df)

    st.subheader("📊 Resumo Financeiro")

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Entradas", f"{entradas:.2f}")
    col2.metric("💸 Saídas", f"{saidas:.2f}")

    if saldo >= 0:
        col3.markdown(
            f"<h3 style='color:blue;'>📊 Saldo disponível: {saldo:.2f}</h3>",
            unsafe_allow_html=True
        )
    else:
        col3.markdown(
            f"<h3 style='color:red;'>📉 Falta: {abs(saldo):.2f}</h3>",
            unsafe_allow_html=True
        )

    st.subheader("📈 Distribuição")

    # 🔹 Agora incluindo o SALDO no gráfico
    chart_data = pd.DataFrame({
        "Categoria": ["Entradas", "Saídas", "Saldo"],
        "Valor": [entradas, saidas, abs(saldo)]
    }).set_index("Categoria")

    st.pyplot(chart_data.plot.pie(y="Valor", autopct="%1.1f%%").figure)