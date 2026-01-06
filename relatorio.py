import streamlit as st
import duckdb
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Painel Pluma Analytics", layout="wide", initial_sidebar_state="collapsed")

# --- CSS (Visual Pluma/Oracle) ---
st.markdown("""
    <style>
    .header-pluma {
        background-color: #004d40; padding: 20px; border-radius: 8px;
        color: white; text-align: center; margin-bottom: 20px;
    }
    div[data-testid="metric-container"] {
        background-color: #ffffff; border-left: 5px solid #004d40;
        padding: 10px; border-radius: 5px; box-shadow: 1px 1px 5px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown('<div class="header-pluma"><h2>🚀 Painel de Contabilidade - High Performance</h2></div>', unsafe_allow_html=True)

# --- CONEXÃO COM DADOS (DUCKDB) ---
try:
    con = duckdb.connect()
    # Verifica se existem arquivos DENTRO da pasta 'dados_part_'
    # O asterisco *.parquet lê tudo que estiver lá dentro
    con.execute("SELECT count(*) FROM 'dados_part_/*.parquet'").fetchone()
except Exception as e:
    st.error(f"Erro crítico: Não foi possível ler os arquivos na pasta 'dados_part_'. Detalhe: {e}")
    st.stop()

# --- FILTROS LATERAIS (SQL Otimizado) ---
with st.sidebar:
    st.header("🔧 Filtros Globais")
    
    # CORREÇÃO AQUI: Antes estava 'data_part_', agora está 'dados_part_/*.parquet'
    colunas = [x[0] for x in con.execute("DESCRIBE SELECT * FROM 'dados_part_/*.parquet'").fetchall()]
    
    coluna_filtro = st.selectbox("Escolha a Coluna Principal", colunas)
    
    # CORREÇÃO AQUI TAMBÉM
    valores_unicos = [x[0] for x in con.execute(f"""
        SELECT DISTINCT "{coluna_filtro}" 
        FROM 'dados_part_/*.parquet' 
        WHERE "{coluna_filtro}" IS NOT NULL 
        LIMIT 500
    """).fetchall()]
    
    valor_selecionado = st.selectbox("Valor do Filtro", ["(Todos)"] + [str(v) for v in valores_unicos])

# --- ÁREA DE BUSCA TEXTUAL ---
st.markdown("### 🔎 Consulta Rápida")
col1, col2 = st.columns([3, 1])
with col1:
    busca_livre = st.text_input("Buscar texto (ID, Nome, Valor...)", placeholder="Digite e aperte Enter...")
with col2:
    limite_linhas = st.selectbox("Linhas p/ exibir", [100, 1000, 5000, "Todas"])

# --- CONSTRUÇÃO DA QUERY ---
# CORREÇÃO AQUI TAMBÉM: Uniformizado para dados_part_/*.parquet
query_base = "SELECT * FROM 'dados_part_/*.parquet' WHERE 1=1"
params = []

if valor_selecionado != "(Todos)":
    query_base += f" AND CAST(\"{coluna_filtro}\" AS VARCHAR) = ?"
    params.append(valor_selecionado)

if busca_livre:
    filtros_texto = []
    for col in colunas[:5]: 
        filtros_texto.append(f"CAST(\"{col}\" AS VARCHAR) ILIKE ?")
        params.append(f"%{busca_livre}%")
    query_base += " AND (" + " OR ".join(filtros_texto) + ")"

# --- EXECUÇÃO ---
try:
    total_filtrado = con.execute(f"SELECT COUNT(*) FROM ({query_base})", params).fetchone()[0]
except:
    total_filtrado = 0

# KPIs
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Registros Encontrados", f"{total_filtrado:,.0f}".replace(",", "."))
kpi2.metric("Fonte de Dados", "Arquivo Otimizado")
kpi3.metric("Status", "Online 🟢")

st.divider()

if total_filtrado > 0:
    limit_clause = "" if limite_linhas == "Todas" else f" LIMIT {limite_linhas}"
    df_final = con.execute(query_base + limit_clause, params).df()
    st.dataframe(df_final, use_container_width=True, hide_index=True)
else:
    st.warning("Nenhum resultado encontrado.")