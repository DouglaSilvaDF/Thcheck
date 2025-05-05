import streamlit as st
import pandas as pd

st.set_page_config(page_title="Análise de Pastas por Corretor", layout="wide")

st.title("📊 Análise de Pastas por Corretor")

uploaded_file = st.file_uploader("📂 Faça o upload da planilha (.csv)", type="csv")

if uploaded_file:
    try:
        # Leitura corrigida com separador ; e encoding latin1
        df = pd.read_csv(uploaded_file, sep=';', encoding='latin1')
    except Exception as e:
        st.error(f"❌ Erro ao ler o arquivo: {e}")
        st.stop()

    # Normaliza os nomes das colunas para facilitar o uso
    df.columns = [col.strip().lower() for col in df.columns]

    # Detecta colunas principais
    colunas = df.columns.tolist()
    st.write("📌 Colunas detectadas:", colunas)

    # Substitua conforme o nome exato na sua planilha
    corretor_col = st.selectbox("🔍 Escolha a coluna de CORRETOR:", colunas)
    status_col = st.selectbox("📄 Escolha a coluna de STATUS:", colunas)
    data_col = st.selectbox("📅 Escolha a coluna de DATA:", colunas)

    df[data_col] = pd.to_datetime(df[data_col], errors='coerce')

    # Filtro por dia
    df['dia'] = df[data_col].dt.day
    dias_unicos = sorted(df['dia'].dropna().unique())
    dia_selecionado = st.selectbox("📆 Selecione o DIA para análise:", dias_unicos)

    df_filtrado = df[df['dia'] == dia_selecionado]

    # Agrupamento por corretor e status
    resumo = df_filtrado.groupby(corretor_col)[status_col].value_counts().unstack(fill_value=0)

    # Garante que todas as colunas existam
    status_list = ['aprovado', 'reprovado', 'condicionado', 'reserva']
    for status in status_list:
        if status not in resumo.columns:
            resumo[status] = 0

    resumo['Total'] = resumo.sum(axis=1)
    resumo['Com Resposta'] = resumo[status_list].sum(axis=1)

    resumo = resumo.reset_index()

    st.subheader("📋 Tabela Resumo por Corretor")
    st.dataframe(resumo, use_container_width=True)

    st.subheader("📈 Desempenho Detalhado dos Corretores")
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
    st.info("📁 Envie sua planilha .csv para começar a análise.")

