import pandas as pd
import streamlit as st


@st.cache_data
def load_data(path="data/clean/dataset.csv"):
    """Lê o dataset já tratado (exportado ao final do notebook de EDA).

    O cache evita reler o CSV (113 mil faixas) a cada interação com os widgets.
    """
    return pd.read_csv(path)
