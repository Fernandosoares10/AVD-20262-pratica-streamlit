# Template: rascunho de layout → esqueleto do app

Preencha cada bloco e envie à ferramenta de IA.

## Contexto

Sou aluno de Análise e Visualização de Dados (CESAR School). Estou criando um app Streamlit com dois dashboards sobre o dataset da minha EDA da Aula 11: **Spotify Tracks** (Kaggle, maharshipandya), já tratado e salvo em `data/clean/dataset.csv` (113.386 faixas). O Dashboard 1 deve mostrar a **correlação** e a **distribuição** das variáveis quantitativas, com a possibilidade de comparar faixas **Popular** (popularity ≥ 50) e **Nicho**.

## Entrada

Rascunho em anexo: `entregas/rascunho-dashboard1.png`.

Layout (caso a imagem não seja interpretada): sidebar à esquerda com o título "Filtros", um seletor de variáveis quantitativas, um toggle "Distinguir Popular x Nicho" e um slider de intervalo por variável escolhida; na área principal, duas colunas: à esquerda "Correlação" (heatmap de Spearman) e à direita, mais larga, "Distribuição" (um histograma por variável).

Colunas do dataset:
- Quantitativas: `popularity`, `duration_ms`, `danceability`, `energy`, `loudness`, `speechiness`, `acousticness`, `instrumentalness`, `liveness`, `valence`, `tempo`
- Qualitativas: `explicit`, `key`, `mode`, `time_signature`, `track_genre`, `faixa_pop` (Popular/Nicho)
- Identificação: `track_id`, `artists`, `album_name`, `track_name`
- Derivadas na EDA: `pop_suspeita`, `duration_log`

Perguntas que o dashboard deve responder:
1. Quais audio features andam juntas (ex.: energy x loudness)?
2. Como cada variável se distribui, e essa distribuição muda entre faixas populares e de nicho?

## Restrições

- Streamlit, editando só o `app.py`.
- Carregar os dados com `load_data()` de `src/data_loader.py` (não ler o CSV direto no `app.py`).
- Layout `wide`, sidebar com os filtros, `st.columns` para correlação e distribuição.
- Não implementar os gráficos nem os widgets ainda: só a estrutura.
- Não criar o Dashboard 2 (fica para a Aula 22).

## Formato de saída

Código completo do `app.py` só com o **esqueleto**: título, carregamento dos dados, lista das variáveis quantitativas, sidebar e as duas colunas com `st.subheader`, marcando com comentários `# TODO` onde entram os widgets e os gráficos. Explicação breve de cada seção.
