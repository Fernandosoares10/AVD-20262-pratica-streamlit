# Justificativa das métricas — Dashboard 2

**Dataset:** Spotify Tracks (113.386 faixas de 114 gêneros, já tratado na EDA da Aula 11).
**Público-alvo do dashboard:** curadores de playlist e equipes de lançamento de selos/artistas independentes, que precisam comparar gêneros sem ler histogramas ou testes estatísticos.
**Widgets que controlam as métricas:** filtro de gêneros, toggle "Ignorar popularidade = 0", número de gêneros no gráfico e ordem (mais/menos populares). Clicar numa barra do gráfico de gêneros recalcula todas as métricas só para o gênero clicado. Cada métrica mostra, abaixo do valor, a diferença em relação ao total.

Valores de referência citados abaixo: base inteira, sem filtros, ignorando popularidade = 0.

## Métrica 1: Popularidade mediana
- **Variável:** `popularity` (índice de 0 a 100 calculado pelo Spotify a partir das reproduções recentes).
- **O que mede:** o valor de popularidade que divide as faixas ao meio: metade está acima, metade abaixo. Na base inteira, **39**.
- **Por que foi escolhida:** a EDA mostrou que nenhuma variável segue distribuição normal e que `popularity` tem um pico artificial em zero. A mediana é robusta a isso; a média seria puxada para baixo pelos zeros e por poucas faixas muito populares.
- **Público-alvo:** curadores de playlist e equipes de lançamento.
- **Qual decisão pode ser apoiada por essa métrica?** Em quais gêneros apostar para uma playlist ou um lançamento com maior chance de audiência (ex.: `dance`, `pop` e `electro` têm mediana acima de 65; `latin` e `iranian`, abaixo de 10, e são justamente gêneros com muitos zeros suspeitos, ver métrica 5).
- **O que comunica ao público-alvo:** "uma faixa típica deste gênero tem popularidade X", e se isso está acima ou abaixo do típico da base.

## Métrica 2: Faixas populares (%)
- **Variável:** `faixa_pop` (criada na EDA a partir de `popularity`: Popular se ≥ 50, que é o 3º quartil; Nicho caso contrário).
- **O que mede:** a proporção de faixas na classe Popular. Na base inteira, **30,1%**.
- **Por que foi escolhida:** complementa a mediana. Dois gêneros podem ter a mesma mediana, mas um ter muito mais faixas no topo. É a mesma classe (Popular x Nicho) usada no Dashboard 1 e em toda a EDA.
- **Público-alvo:** curadores de playlist.
- **Qual decisão pode ser apoiada por essa métrica?** Onde procurar faixas com alcance comprovado ao montar uma playlist de sucessos.
- **O que comunica ao público-alvo:** "de cada 10 faixas deste gênero, X são populares". A diferença em pontos percentuais (p.p.) mostra se o gênero tem mais ou menos sucessos que o total.

## Métrica 3: Duração mediana
- **Variável:** `duration_ms` (duração da faixa em milissegundos, mostrada em minutos:segundos).
- **O que mede:** a duração típica das faixas. Na base inteira, **3:33 min**.
- **Por que foi escolhida:** a EDA encontrou faixas de até 87 minutos (DJ sets e mixes contínuos) e skewness de 11,2. A mediana mostra a duração real de uma faixa comum, sem ser distorcida por esses casos.
- **Público-alvo:** equipes de lançamento (produção e edição das faixas).
- **Qual decisão pode ser apoiada por essa métrica?** Que duração mirar ao editar uma faixa para um gênero, e se o gênero escolhido tende a faixas mais longas ou mais curtas que o padrão.
- **O que comunica ao público-alvo:** "uma faixa típica deste gênero dura cerca de X minutos", com a diferença em segundos em relação ao total.

## Métrica 4: Faixas explícitas (%)
- **Variável:** `explicit` (verdadeiro se a faixa tem letra explícita).
- **O que mede:** a proporção de faixas marcadas como explícitas. Na base inteira, **8,6%**.
- **Por que foi escolhida:** é uma variável qualitativa que afeta diretamente onde a faixa pode tocar (playlists infantis, rádio, ambientes comerciais), algo que o Dashboard 1, só com variáveis quantitativas, não mostra.
- **Público-alvo:** curadores de playlist.
- **Qual decisão pode ser apoiada por essa métrica?** Se um gênero é adequado para playlists com restrição de conteúdo, ou quanto trabalho de filtragem será preciso.
- **O que comunica ao público-alvo:** "X% das faixas deste gênero têm conteúdo explícito".

## Métrica 5: Popularidade suspeita (%)
- **Variável:** `pop_suspeita` (criada na EDA: verdadeiro quando `popularity` = 0).
- **O que mede:** a proporção de faixas com popularidade zero. Na base inteira, **14,0%**.
- **Por que foi escolhida:** é o principal achado da EDA. Os zeros se concentram em gêneros inteiros (mais de 58% em jazz, iranian, romance, soul, latin e country, quase 0% em forró), o que indica falha de coleta da API, não falta de audiência. Sem essa métrica, o público leria "latin é impopular" quando o dado é que está incompleto. Por isso também o toggle "Ignorar popularidade = 0" vem ligado por padrão.
- **Público-alvo:** os mesmos usuários das métricas 1 e 2, como alerta de qualidade do dado.
- **Qual decisão pode ser apoiada por essa métrica?** Quanto confiar nas métricas de popularidade de um gênero antes de decidir com base nelas. Se a porcentagem for alta, a recomendação é buscar outra fonte antes de descartar o gênero.
- **O que comunica ao público-alvo:** "X% das faixas deste gênero vieram sem popularidade; quanto maior esse número, menos confiáveis são as métricas 1 e 2". A diferença aparece em vermelho quando sobe, porque subir é ruim.
