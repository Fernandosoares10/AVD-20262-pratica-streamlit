import streamlit as st

from src.data_loader import load_data

st.set_page_config(
    page_title="Spotify Tracks: correlação e distribuição",
    layout="wide",
)

st.title("Spotify Tracks: correlação e distribuição das variáveis quantitativas")

df = load_data()

# Variáveis quantitativas do estudo (mesma lista VARS_QUANT do notebook de EDA)
VARS_QUANT = [
    "popularity",
    "duration_ms",
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
]

# Variável de classe criada na EDA: Popular (popularity >= 50) x Nicho
CLASSE = "faixa_pop"

# Sidebar: filtros (variáveis + intervalo)
with st.sidebar:
    st.header("Filtros")
    # TODO: seletor das variáveis quantitativas (st.multiselect)
    # TODO: toggle "Distinguir Popular x Nicho" (st.toggle)
    # TODO: um slider de intervalo para cada variável selecionada (st.slider)

# TODO: filtrar o df pelos intervalos escolhidos
df_filtrado = df

st.caption(f"{len(df_filtrado):,} de {len(df):,} faixas.".replace(",", "."))

# Dashboard 1: correlação à esquerda, distribuição (mais larga) à direita
col_correlacao, col_distribuicao = st.columns([1, 1.5])

with col_correlacao:
    st.subheader("Correlação (Spearman)")
    # TODO: heatmap de Spearman entre as variáveis selecionadas (aviso se < 2)

with col_distribuicao:
    st.subheader("Distribuição")
    # TODO: um histograma por variável selecionada, colorido por Popular x Nicho (aviso se 0)

# TODO: Dashboard 2 — KPIs (Aula 22)
