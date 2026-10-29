import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from src.data_loader import load_data

st.set_page_config(
    page_title="Spotify Tracks Dashboard",
    layout="wide",
)

st.title("Spotify Tracks: o que as faixas e os gêneros revelam")

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

# Cores da EDA: rosa-claro para Nicho (referência), roxo para Popular (destaque).
# O roxo ficou um pouco mais claro que o da EDA (#2d223a) para aparecer também no tema escuro.
COR_NICHO = "#e9d4d0"
COR_POPULAR = "#6a4c93"
CORES_CLASSE = alt.Scale(domain=["Nicho", "Popular"], range=[COR_NICHO, COR_POPULAR])
# Destaque do gênero clicado na dispersão: laranja contrasta com o roxo nos temas claro e escuro
COR_CLICADO = "#f28e2b"


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


def sem_zeros(dados, ignorar_zeros):
    """Tira as faixas com popularity = 0 (suspeita de falha de coleta, ver EDA) se pedido."""
    return dados[~dados["pop_suspeita"]] if ignorar_zeros else dados


@st.cache_data
def calcular_kpis(dados, ignorar_zeros):
    """KPIs do Dashboard 2. Duração, explícitas e suspeitas usam todas as faixas."""
    pop = sem_zeros(dados, ignorar_zeros)
    return {
        "pop_mediana": pop["popularity"].median(),
        "pct_popular": (pop[CLASSE] == "Popular").mean() * 100,
        "dur_mediana": dados["duration_ms"].median() / 60000,
        "pct_explicit": dados["explicit"].mean() * 100,
        "pct_suspeita": dados["pop_suspeita"].mean() * 100,
    }


@st.cache_data
def calcular_por_genero(dados, ignorar_zeros):
    """Popularidade mediana, % de populares e nº de faixas por gênero (uma linha por gênero)."""
    return (
        sem_zeros(dados, ignorar_zeros)
        .groupby("track_genre")
        .agg(
            mediana=("popularity", "median"),
            pct_popular=(CLASSE, lambda s: (s == "Popular").mean() * 100),
            faixas=("popularity", "size"),
        )
        .reset_index()
    )


@st.cache_data
def calcular_dispersao(dados, ignorar_zeros):
    """Por gênero: % de popularidade suspeita (todas as faixas) x popularidade mediana.

    O merge à esquerda mantém gêneros em que todas as faixas têm popularidade 0
    (eles somem do cálculo da mediana quando os zeros são ignorados).
    """
    suspeita = (
        dados.groupby("track_genre")
        .agg(pct_suspeita=("pop_suspeita", lambda s: s.mean() * 100), faixas=("popularity", "size"))
        .reset_index()
    )
    mediana = sem_zeros(dados, ignorar_zeros).groupby("track_genre")["popularity"].median().rename("mediana")
    return suspeita.merge(mediana.reset_index(), on="track_genre", how="left")


@st.cache_data
def calcular_hist_popularidade(dados, ignorar_zeros, largura=5):
    """Contagem de faixas por faixa de popularidade (0-4, 5-9, ..., 95-100), já com a classe.

    As faixas de largura 5 começam em 0, então o corte de 50 (Popular x Nicho) cai
    exatamente na borda de uma barra.
    """
    pop = sem_zeros(dados, ignorar_zeros)["popularity"]
    inicio = (np.minimum(pop // largura, 100 // largura - 1) * largura).astype(int)
    contagem = inicio.value_counts().rename_axis("inicio").rename("faixas").reset_index()
    contagem["fim"] = contagem["inicio"] + largura
    contagem[CLASSE] = np.where(contagem["inicio"] >= 50, "Popular", "Nicho")
    return contagem.sort_values("inicio")


def formatar_numero(valor, formato, sufixo=""):
    """Formata um KPI; mostra "–" quando não há faixas para calcular (NaN)."""
    return "–" if pd.isna(valor) else f"{valor:{formato}}{sufixo}"


def formatar_minutos(minutos):
    if pd.isna(minutos):
        return "–"
    m, seg = divmod(round(minutos * 60), 60)
    return f"{m}:{seg:02d} min"

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

aba_d1, aba_d2 = st.tabs(
    ["Dashboard 1: correlação e distribuição", "Dashboard 2: popularidade por gênero (KPIs)"]
)

# Dashboard 1: correlação à esquerda, distribuição (mais larga) à direita
with aba_d1:
    col_correlacao, col_distribuicao = st.columns([1, 1.5])

    with col_correlacao:
        st.subheader("Correlação (Spearman)")

        if len(variaveis) == 0:
            st.warning("Selecione pelo menos 2 variáveis na barra lateral para calcular a correlação.")
        elif len(variaveis) == 1:
            st.info(
                f"Só **{variaveis[0]}** está selecionada. A correlação compara pares de variáveis: "
                "selecione mais uma para ver o heatmap."
            )
        elif df_filtrado.empty:
            st.warning("Nenhuma faixa dentro dos intervalos escolhidos. Amplie os intervalos na barra lateral.")
        elif len(df_filtrado) < 30:
            st.warning(
                f"Só {len(df_filtrado)} faixas dentro dos intervalos escolhidos: poucas para uma "
                "correlação confiável. Amplie os intervalos na barra lateral."
            )
        else:
            corr = calcular_correlacao(df_filtrado, variaveis)

            # Variável constante dentro do filtro (ex.: intervalo de um único valor) não tem correlação
            sem_valor = corr[corr["correlacao"].isna()]
            if not sem_valor.empty:
                constantes = sorted(set(sem_valor["var_x"]) | set(sem_valor["var_y"]))
                st.caption(
                    "Células vazias: não há correlação quando a variável não varia dentro do filtro "
                    f"(verifique: {', '.join(constantes)})."
                )

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

        if len(variaveis) == 0:
            st.warning("Selecione pelo menos 1 variável na barra lateral para ver a distribuição.")
        elif df_filtrado.empty:
            st.warning("Nenhuma faixa dentro dos intervalos escolhidos. Amplie os intervalos na barra lateral.")

        # Um histograma por variável selecionada, em grade de 2 colunas (cada um com a sua escala)
        for inicio in range(0, len(variaveis) if not df_filtrado.empty else 0, 2):
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

# Dashboard 2: KPIs de popularidade, com filtro de gêneros e gráfico de barras clicável
with aba_d2:
    st.caption(
        "Para quem monta playlists ou planeja lançamentos: como os gêneros se comparam em popularidade. "
        "Parte das mesmas faixas filtradas na barra lateral."
    )

    # Widgets do Dashboard 2 (definidos antes do rascunho, como pede o roteiro)
    col_generos, col_zeros, col_qtd, col_ordem = st.columns([2.2, 1.3, 1.2, 1.1])
    with col_generos:
        generos = st.multiselect(
            "Gêneros",
            options=sorted(df["track_genre"].unique()),
            placeholder="Todos os 114 gêneros",
            help="Deixe vazio para considerar todos os gêneros.",
        )
    with col_zeros:
        ignorar_zeros = st.toggle(
            "Ignorar popularidade = 0",
            value=True,
            help="Na EDA, os zeros se concentram em gêneros inteiros (ex.: jazz, iranian): "
            "são falha de coleta, não falta de audiência. Por isso ficam fora por padrão.",
        )
    with col_qtd:
        n_generos = st.slider("Gêneros no gráfico", min_value=5, max_value=30, value=15, step=1)
    with col_ordem:
        ordem = st.radio("Mostrar", ["Mais populares", "Menos populares"], horizontal=False)

    base = df_filtrado[df_filtrado["track_genre"].isin(generos)] if generos else df_filtrado

    if base.empty:
        st.warning("Nenhuma faixa para os filtros escolhidos. Amplie os intervalos ou troque os gêneros.")
    else:
        # Os KPIs ficam acima do gráfico, mas dependem do clique nele: reservamos o espaço agora
        area_kpis = st.container()

        st.subheader("Popularidade mediana por gênero")
        st.caption(
            "Clique numa barra para ver os KPIs e os dois gráficos abaixo só daquele gênero "
            "(shift + clique para vários; clique fora das barras para limpar)."
        )

        por_genero = calcular_por_genero(base, ignorar_zeros)
        por_genero = (
            por_genero.nlargest(n_generos, "mediana")
            if ordem == "Mais populares"
            else por_genero.nsmallest(n_generos, "mediana")
        )

        clique = alt.selection_point(name="clique", fields=["track_genre"])
        barras = (
            alt.Chart(por_genero)
            .mark_bar(color=COR_POPULAR)
            .encode(
                x=alt.X("mediana:Q", title="Popularidade mediana (0 a 100)",
                          scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(tickCount=10)),
                y=alt.Y(
                    "track_genre:N",
                    title=None,
                    sort=alt.EncodingSortField("mediana", order="descending" if ordem == "Mais populares" else "ascending"),
                    axis=alt.Axis(labelOverlap=False, labelLimit=160),
                ),
                opacity=alt.condition(clique, alt.value(1), alt.value(0.3)),
                tooltip=[
                    alt.Tooltip("track_genre:N", title="Gênero"),
                    alt.Tooltip("mediana:Q", title="Popularidade mediana", format=".0f"),
                    alt.Tooltip("pct_popular:Q", title="% populares", format=".1f"),
                    alt.Tooltip("faixas:Q", title="Faixas", format=","),
                ],
            )
            .add_params(clique)
        )
        # Altura explícita: ~26 px por gênero, para nenhum nome ficar escondido
        evento = st.altair_chart(
            barras, key="barras_genero", on_select="rerun", width="stretch",
            height=max(260, 26 * len(por_genero) + 60),
        )

        clicados = [item["track_genre"] for item in evento.selection.get("clique", [])]
        selecionado = base[base["track_genre"].isin(clicados)] if clicados else base

        with area_kpis:
            if clicados:
                st.markdown(f"**KPIs de:** {', '.join(clicados)}, comparados com o total filtrado")
            elif generos:
                st.markdown("**KPIs dos gêneros escolhidos**, comparados com a base inteira filtrada")
            else:
                st.markdown("**KPIs da base inteira filtrada**")

            referencia = base if clicados else df_filtrado
            atual = calcular_kpis(selecionado, ignorar_zeros)
            ref = calcular_kpis(referencia, ignorar_zeros)
            comparar = bool(clicados or generos)

            def delta(chave, sufixo=""):
                if not comparar or pd.isna(atual[chave]) or pd.isna(ref[chave]):
                    return None
                return f"{atual[chave] - ref[chave]:+.1f}{sufixo}"

            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("Popularidade mediana", formatar_numero(atual["pop_mediana"], ".0f"), delta("pop_mediana"),
                      border=True, help="Mediana de popularity (0 a 100). Robusta à assimetria vista na EDA.")
            k2.metric("Faixas populares", formatar_numero(atual["pct_popular"], ".1f", "%"),
                      delta("pct_popular", " p.p."), border=True,
                      help="% de faixas com popularity ≥ 50 (classe Popular da EDA).")
            delta_dur = None if delta("dur_mediana") is None else f"{(atual['dur_mediana'] - ref['dur_mediana']) * 60:+.0f} s"
            k3.metric("Duração mediana", formatar_minutos(atual["dur_mediana"]), delta_dur,
                      delta_color="off", border=True,
                      help="Mediana da duração. A média seria puxada por DJ sets de mais de 1 hora.")
            k4.metric("Faixas explícitas", f"{atual['pct_explicit']:.1f}%", delta("pct_explicit", " p.p."),
                      delta_color="off", border=True, help="% de faixas marcadas como explicit.")
            k5.metric("Popularidade suspeita", f"{atual['pct_suspeita']:.1f}%", delta("pct_suspeita", " p.p."),
                      delta_color="inverse", border=True,
                      help="% de faixas com popularity = 0 (falha de coleta). Quanto maior, menos confiáveis "
                      "os outros KPIs de popularidade.")
            st.caption(f"{len(selecionado):,} faixas nos KPIs.".replace(",", "."))

        # Visuais 2 e 3: lado a lado, abaixo das barras. Os dois reagem ao clique nas barras.
        col_disp, col_hist = st.columns(2)

        with col_disp:
            st.subheader("Popularidade x dados suspeitos, por gênero")
            st.caption(
                "Cada ponto é um gênero. Mais à direita = mais faixas com popularidade 0 (falha de coleta, "
                "achado da EDA). Gênero baixo e à direita pode parecer impopular só porque o dado está incompleto. "
                "O gênero clicado nas barras aparece em laranja."
            )
            dispersao_genero = calcular_dispersao(base, ignorar_zeros)
            dispersao_genero["destaque"] = (
                dispersao_genero["track_genre"].isin(clicados) if clicados else False
            )
            pontos = (
                alt.Chart(dispersao_genero)
                .mark_circle(size=70)
                .encode(
                    x=alt.X("pct_suspeita:Q", title="% de faixas com popularidade 0"),
                    y=alt.Y("mediana:Q", title="Popularidade mediana", scale=alt.Scale(domain=[0, 100])),
                    color=alt.condition("datum.destaque", alt.value(COR_CLICADO), alt.value("#b9a7cf")),
                    size=alt.condition("datum.destaque", alt.value(160), alt.value(70)),
                    tooltip=[
                        alt.Tooltip("track_genre:N", title="Gênero"),
                        alt.Tooltip("pct_suspeita:Q", title="% popularidade 0", format=".1f"),
                        alt.Tooltip("mediana:Q", title="Popularidade mediana", format=".0f"),
                        alt.Tooltip("faixas:Q", title="Faixas", format=","),
                    ],
                )
                .properties(height=320)
            )
            st.altair_chart(pontos, width="stretch")

        with col_hist:
            st.subheader("Distribuição da popularidade")
            st.caption(
                "Faixas nos KPIs (gênero clicado ou todos), agrupadas de 5 em 5 pontos. "
                "Roxo = Popular (≥ 50), rosa = Nicho."
            )
            hist_pop = calcular_hist_popularidade(selecionado, ignorar_zeros)
            if hist_pop.empty:
                st.info("Todas as faixas selecionadas têm popularidade 0. Desligue \"Ignorar popularidade = 0\" para vê-las.")
            else:
                barras_pop = (
                    alt.Chart(hist_pop)
                    .mark_bar()
                    .encode(
                        x=alt.X("inicio:Q", bin="binned", title="Popularidade (0 a 100)",
                                scale=alt.Scale(domain=[0, 100])),
                        x2="fim:Q",
                        y=alt.Y("faixas:Q", title="Faixas"),
                        color=alt.Color(f"{CLASSE}:N", title="Classe", scale=CORES_CLASSE,
                                        legend=alt.Legend(orient="top")),
                        tooltip=[
                            alt.Tooltip("inicio:Q", title="de"),
                            alt.Tooltip("fim:Q", title="até"),
                            alt.Tooltip("faixas:Q", title="Faixas", format=","),
                        ],
                    )
                    .properties(height=320)
                )
                st.altair_chart(barras_pop, width="stretch")
