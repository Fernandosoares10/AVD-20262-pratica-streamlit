import altair as alt
import numpy as np
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

# Mesmas cores da EDA: rosa-claro para Nicho (referência), roxo-escuro para Popular (destaque)
COR_NICHO = "#e9d4d0"
COR_POPULAR = "#2d223a"
CORES_CLASSE = alt.Scale(domain=["Nicho", "Popular"], range=[COR_NICHO, COR_POPULAR])


@st.cache_data
def calcular_correlacao(dados, variaveis):
    """Correlação de Spearman em formato longo, só o triângulo inferior (sem a diagonal)."""
    corr = (
        dados[variaveis]
        .corr(method="spearman")
        .rename_axis(index="var_y", columns="var_x")
        .stack()
        .rename("correlacao")
        .reset_index()
    )
    ordem = {var: i for i, var in enumerate(variaveis)}
    return corr[corr["var_y"].map(ordem) > corr["var_x"].map(ordem)]


@st.cache_data
def calcular_histograma(dados, var, separar_por_classe, n_bins=30):
    """Conta as faixas por intervalo (bin) já no pandas.

    Com 113 mil faixas, mandar as linhas cruas para o Altair deixaria o app lento
    (e passa do limite padrão de 5.000 linhas); assim o gráfico recebe só ~30 barras.
    """
    bordas = np.histogram_bin_edges(dados[var], bins=n_bins)
    grupos = [pd.cut(dados[var], bordas, include_lowest=True)]
    if separar_por_classe:
        grupos.append(dados[CLASSE])
    contagem = dados.groupby(grupos, observed=False).size().rename("faixas").reset_index()
    contagem["inicio"] = contagem[var].map(lambda b: b.left).astype(float)
    contagem["fim"] = contagem[var].map(lambda b: b.right).astype(float)
    return contagem.drop(columns=var)

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

    if len(variaveis) >= 2:
        corr = calcular_correlacao(df_filtrado, variaveis)

        base = alt.Chart(corr).encode(
            x=alt.X("var_x:N", title=None, sort=variaveis[:-1], axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("var_y:N", title=None, sort=variaveis[1:]),
        )
        heatmap = base.mark_rect().encode(
            color=alt.Color(
                "correlacao:Q",
                title="Spearman",
                scale=alt.Scale(scheme="redblue", domain=[-1, 1], reverse=True),
            ),
            tooltip=["var_x", "var_y", alt.Tooltip("correlacao:Q", format=".2f")],
        )
        valores = base.mark_text(fontSize=13).encode(
            text=alt.Text("correlacao:Q", format=".2f"),
            color=alt.condition("abs(datum.correlacao) > 0.5", alt.value("white"), alt.value("black")),
        )
        st.altair_chart(
            (heatmap + valores).properties(height=380),
            width="stretch",
        )

with col_distribuicao:
    st.subheader("Distribuição")

    # Um histograma por variável selecionada, em grade de 2 colunas (cada um com a sua escala)
    for inicio in range(0, len(variaveis), 2):
        colunas = st.columns(2)
        for coluna, var in zip(colunas, variaveis[inicio : inicio + 2]):
            contagem = calcular_histograma(df_filtrado, var, separar_por_classe)
            histograma = (
                alt.Chart(contagem)
                .mark_bar(color=COR_POPULAR)
                .encode(
                    x=alt.X("inicio:Q", title=var, bin="binned"),
                    x2="fim:Q",
                    y=alt.Y("faixas:Q", title="Faixas", stack=True),
                    tooltip=[
                        alt.Tooltip("inicio:Q", title="de", format=",.3~f"),
                        alt.Tooltip("fim:Q", title="até", format=",.3~f"),
                        alt.Tooltip("faixas:Q", title="Faixas", format=","),
                    ],
                )
                .properties(height=220)
            )
            if separar_por_classe:
                histograma = histograma.encode(
                    color=alt.Color(f"{CLASSE}:N", title="Classe", scale=CORES_CLASSE,
                                    legend=alt.Legend(orient="top")),
                    tooltip=[
                        alt.Tooltip(f"{CLASSE}:N", title="Classe"),
                        alt.Tooltip("inicio:Q", title="de", format=",.3~f"),
                        alt.Tooltip("fim:Q", title="até", format=",.3~f"),
                        alt.Tooltip("faixas:Q", title="Faixas", format=","),
                    ],
                )
            with coluna:
                st.altair_chart(histograma, width="stretch")

# TODO: Dashboard 2 — KPIs (Aula 22)
