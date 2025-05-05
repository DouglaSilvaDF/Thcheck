import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Análise de Propostas - CLT Águas Lindas", layout="wide")

st.title("🏡 Análise de Pastas - Corretores CLT Águas Lindas")

uploaded_file = st.file_uploader("📤 Envie a planilha CSV", type="csv")

if uploaded_file:
    # Lê o CSV com separador ; e encoding latin1 (padrão do Excel BR)
    df = pd.read_csv(uploaded_file, sep=';', encoding='latin1')

    # Define colunas de interesse
    coluna_corretor = df.columns[0]  # Ex: "Corretor"
    coluna_status = 'Situação'      # Altere se o nome da coluna for diferente
    coluna_data = df.columns[24]    # Coluna Y (índice 24)

    # Converte datas
    df[coluna_data] = pd.to_datetime(df[coluna_data], errors='coerce')

    # Filtra somente CLTs (assumindo que nome do corretor contém "- CLT")
    df_clt = df[df[coluna_corretor].str.contains('- CLT', case=False, na=False)]

    # Lista de status esperados
    status_list = ['Aprovado', 'Condicionado', 'Reprovado', 'Reserva', 'Pendente Comercial', 'Análise CCA']

    # ================= RESULTADO DO DIA =================
    st.subheader("📅 Resultado do Dia")
    data_hoje = pd.to_datetime("today").normalize()
    df_dia = df_clt[df_clt[coluna_data] == data_hoje]

    def gerar_resumo(df):
        base = df.groupby(coluna_corretor)[coluna_status].value_counts().unstack(fill_value=0)
        for status in status_list:
            if status not in base.columns:
                base[status] = 0
        base['Total de Pastas'] = base.sum(axis=1)
        base['Pastas c/ Resposta'] = base[['Aprovado', 'Condicionado', 'Reprovado', 'Reserva']].sum(axis=1)
        return base.reset_index()

    resumo_dia = gerar_resumo(df_dia)
    st.dataframe(resumo_dia, use_container_width=True)

    # Funil do dia
    total_dia = resumo_dia['Total de Pastas'].sum()
    respostas_dia = resumo_dia['Pastas c/ Resposta'].sum()
    funil_dia = {
        'Total de Pastas': total_dia,
        'Respostas': respostas_dia,
        'Aprovados': resumo_dia['Aprovado'].sum(),
        'Condicionados': resumo_dia['Condicionado'].sum(),
        'Reprovados': resumo_dia['Reprovado'].sum(),
        'Em Análise': resumo_dia['Análise CCA'].sum(),
        'Pendentes': resumo_dia['Pendente Comercial'].sum(),
    }

    col1, col2 = st.columns([1, 1])
    with col2:
        st.markdown("#### 📊 Funil de Vendas - Diário")
        funil_dia_df = pd.DataFrame.from_dict(funil_dia, orient='index', columns=['Qtd']).reset_index()
        fig_dia = px.bar(funil_dia_df, x='Qtd', y='index', orientation='h', text='Qtd',
                         color='index', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_dia.update_layout(yaxis_title="", xaxis_title="", showlegend=False, height=400)
        st.plotly_chart(fig_dia, use_container_width=True)

    # ================= RESULTADO DO MÊS =================
    st.subheader("📆 Resultado do Mês")

    col1, col2 = st.columns(2)
    with col1:
        data_ini = st.date_input("📅 De:", pd.to_datetime("today").replace(day=1))
    with col2:
        data_fim = st.date_input("📅 Até:", pd.to_datetime("today"))

    df_mes = df_clt[(df_clt[coluna_data] >= pd.to_datetime(data_ini)) & (df_clt[coluna_data] <= pd.to_datetime(data_fim))]
    resumo_mes = gerar_resumo(df_mes)

    st.dataframe(resumo_mes, use_container_width=True)

    # Funil do mês
    total_mes = resumo_mes['Total de Pastas'].sum()
    respostas_mes = resumo_mes['Pastas c/ Resposta'].sum()
    funil_mes = {
        'Total de Pastas': total_mes,
        'Respostas': respostas_mes,
