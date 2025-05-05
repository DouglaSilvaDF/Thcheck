import streamlit as st
import pandas as pd

st.set_page_config(page_title="Análise de Pastas por Corretor", layout="wide")

st.title("📊 Análise de Pastas por Corretor")

uploaded_file = st.file_uploader("Faça o upload da planilha (.csv)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Ajustar os nomes das colunas se necessário
    df.columns = [col.strip().lower() for col in df.columns]

    # Exemplo de mapeamento de colunas (ajuste para combinar com sua planilha)
    corretor_col = 'corretor'
    status_col = 'status'
    data_col = 'data'  # Essa coluna deve conter as datas de cadastro

    df[data_col] = pd.to_datetime(df[data_col], errors='coerce')

    # Filtro por dia do mês
    df['dia'] = df[data_col].dt.day
    dias_unicos = sorted(df['dia'].dropna().unique())
    dia_selecionado = st.selectbox("Selecione o dia do mês para análise:", dias_unicos)

    df_filtrado = df[df['dia'] == dia_selecionado]

    # Agrupamento geral por corretor
    resumo = df_filtrado.groupby(corretor_col)[status_col].value_counts().unstack(fill_value=0)
    resumo['Total'] = resumo.sum(axis=1)
    status_list = ['aprovado', 'reprovado', 'condicionado', 'reserva']

    for status in status_list:
        if status not in resumo.columns:
            resumo[status] = 0

    resumo['Com Resposta'] = resumo[status_list].sum(axis=1)
    resumo = resumo.reset_index()

    st.subheader("📋 Tabela Resumo por Corretor")
    st.dataframe(resumo, use_container_width=True)

    st.subheader("📈 Desempenho Individual dos Corretores")
    for _, linha in resumo.iterrows():
        st.markdown(f"### 👤 Corretor: {linha[corretor_col]}")
        st.write(f"- Total de Pastas: {linha['Total']}")
        st.write(f"- Aprovadas: {linha['aprovado']}")
        st.write(f"- Reprovadas: {linha['reprovado']}")
        st.write(f"- Condicionadas: {linha['condicionado']}")
        st.write(f"- Em Reserva: {linha['reserva']}")
        st.write(f"- Total com Resposta: {linha['Com Resposta']}")
        st.markdown("---")

else:
    st.info("⏳ Aguarde... Faça o upload da planilha para começar.")

