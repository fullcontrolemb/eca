import streamlit as st


def render_dashboard(summary):
    if not summary:
        st.info("Nenhum dado neste mês ainda.")
        return

    st.metric("💰 Total do Mês", f"{summary['total']:.2f}")

    st.subheader("Gastos por Categoria")
    st.bar_chart(summary["by_category"])