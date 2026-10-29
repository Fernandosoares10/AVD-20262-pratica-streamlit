import pandas as pd
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

    variaveis = st.multiselect(
        "Variáveis quantitativas",
        options=VARS_QUANT,
        default=["danceability", "energy", "loudness", "valence"],
        help="Escolha as variáveis que entram na correlação e na distribuição.",
    )

    separar_por_classe = st.toggle(
        "Distinguir Popular x Nicho",
        value=False,
        help="Separa as faixas em Popular (popularity ≥ 50) e Nicho, como na EDA.",
    )

    # Um slider de intervalo para cada variável selecionada
    intervalos = {}
    for var in variaveis:
        if pd.api.types.is_integer_dtype(df[var]):
            minimo, maximo, passo = int(df[var].min()), int(df[var].max()), 1
        else:
            minimo, maximo = float(df[var].min()), float(df[var].max())
            passo = round((maximo - minimo) / 100, 3) or 0.001
        intervalos[var] = st.slider(
            f"Intervalo de {var}",
            min_value=minimo,
            max_value=maximo,
            value=(minimo, maximo),
            step=passo,
            key=f"intervalo_{var}",
        )

# Mantém só as faixas dentro de todos os intervalos escolhidos
df_filtrado = df
for var, (inicio, fim) in intervalos.items():
    df_filtrado = df_filtrado[df_filtrado[var].between(inicio, fim)]

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
