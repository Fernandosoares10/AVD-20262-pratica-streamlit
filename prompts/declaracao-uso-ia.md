# Declaração de Uso de IA

**Nome:** Fernando Soares da Silva
**Data:** 29/10/2026 (Aula 21)

## Ferramenta

Claude Code (extensão do VS Code), modelo Claude Opus 5.5, da Anthropic.

## Prompt usado

Pedidos feitos ao longo da Aula 21, em linguagem natural:

1. "Separe exatamente o que tenho que fazer e o que tenho que commitar" (a partir dos slides das Aulas 21/22 e do repositório da disciplina).
2. Ajuda no setup: clonar o fork, instalar o Python e resolver erros de autenticação do Git e de PATH.
3. Colocar o meu notebook da Aula 11 (`EDA_Spotify_Tracks_Fernando_Soares_da_Silva.ipynb`) no lugar de `notebooks/eda.ipynb`.
4. Adaptar o `eda-com-downloads.ipynb` ao Spotify Tracks e gerar o `data/clean/dataset.csv`.
5. Fazer o rascunho do layout do Dashboard 1 no formato do rascunho da professora.
6. Gerar o esqueleto do `app.py` a partir do rascunho. O prompt completo está em [layout-skeleton-prompt.md](layout-skeleton-prompt.md).
7. Implementar o seletor de variáveis, o toggle Popular x Nicho e os sliders de intervalo.

## O que foi aceito, modificado ou rejeitado e por quê

- **Aceito:**
  - O `eda-com-downloads.ipynb` montado a partir do meu EDA original, com a seção de download no fim, igual à do notebook de exemplo. A análise e o tratamento são os da minha EDA da Aula 11, que não foi alterada.
  - O rascunho `entregas/rascunho-dashboard1.png`, gerado em código pela IA seguindo a estrutura do rascunho da professora (Sidebar | Correlação | Distribuição), com as variáveis do meu dataset.
  - O esqueleto do `app.py` e os widgets da sidebar: multiselect, toggle e um slider por variável escolhida.
- **Modificado:**
  - As variáveis e a classe vieram da minha EDA, não do exemplo da professora: as 11 quantitativas de `VARS_QUANT` e `faixa_pop` (Popular se popularity ≥ 50, Nicho caso contrário) no lugar de `doenca_cardiaca`.
  - Os sliders das variáveis contínuas usam um passo de 1/100 da faixa da variável, porque um passo fixo de 0,1 não serve para variáveis em escalas muito diferentes, como `duration_ms` (em milissegundos) e `danceability` (de 0 a 1).
- **Rejeitado:**
  - A IA tentou criar o ambiente virtual e instalar as dependências sozinha. Recusei e rodei esses comandos eu mesmo, para acompanhar o setup.
