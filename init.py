import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📊 Análise de Produção de Corretores CLT - Águas Lindas")

uploaded_file = st.file_uploader("Faça o upload da planilha (.csv)", type=["csv"])

if uploaded_file:
    try:
        # Tentativa de leitura com separador automático
        df = pd.read_csv(uploaded_file, encoding="utf-8", sep=None, engine='python')
    except Exception as e:
        st.error("Erro ao ler o arquivo. Verifique se ele está no formato .csv válido.")
        st.stop()

    # Força as colunas importantes a serem string
    coluna_corretor = df.columns[0]  # Primeira coluna deve ser os corretores
    df[coluna_corretor] = df[coluna_corretor].astype(str)

    # Filtra apenas os corretores CLT de Águas Lindas
    df_clt = df[df[coluna_corretor].str.contains('- CLT', case=False, na=False)]
    df_clt = df_clt[df_clt[coluna_corretor].str.contains('ÁGUAS LINDAS', case=False, na=False)]

    # Converte coluna de data (coluna Y = index 24)
    df_clt.iloc[:, 24] = pd.to_datetime(df_clt.iloc[:, 24], errors='coerce')

    # Coluna de status
    coluna_status = df_clt.columns[df_clt.columns.str.contains("status", case=False)][0]

    # Data selecionada para filtro
    data_selecionada = st.date_input("Filtrar por dia:", datetime.today())
    df_dia = df_clt[df_clt.iloc[:, 24].dt.date == data_selecionada]

    def gerar_resumo(df_base, titulo):
        resumo = df_base.groupby(coluna_corretor).agg(
            total_pastas=('Número da Proposta', 'count'),
            aprovadas=(coluna_status, lambda x: (x.str.lower() == 'aprovado').sum()),
            reprovadas=(coluna_status, lambda x: (x.str.lower() == 'reprovado').sum()),
            condicionadas=(coluna_status, lambda x: (x.str.lower() == 'condicionado').sum()),
            reserva=(coluna_status, lambda x: (x.str.lower() == 'reserva').sum()),
        )
        resumo['com_resposta'] = resumo[['aprovadas', 'reprovadas', 'condicionadas', 'reserva']].sum(axis=1)
        resumo = resumo.reset_index()
        st.subheader(titulo)
        st.dataframe(resumo, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        gerar_resumo(df_dia, f"📅 Resultado do Dia ({data_selecionada.strftime('%d/%m/%Y')})")
    with col2:
        gerar_resumo(df_clt, "🗓️ Resultado do Mês (Todos os Dados)")

    st.markdown("---")
    st.subheader("📌 Desempenho Detalhado por Corretor (Dia Selecionado)")
    for corretor in df_dia[coluna_corretor].unique():
        st.markdown(f"**🔹 {corretor}**")
        st.dataframe(df_dia[df_dia[coluna_corretor] == corretor], use_container_width=True)

else:
    st.info("Faça o upload de uma planilha CSV para iniciar.")
