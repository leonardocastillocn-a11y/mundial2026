import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Quiniela Debug", layout="wide")

# Lista de participantes
participantes = {
    "Andres": ["congo", "irak", "egypt", "panama", "austria", "iran", "germany", "england"],
    "Roberto": ["haiti", "curacao", "tunisia", "uzbekistan", "morocco", "south korea", "netherlands", "portugal"],
    "Ruben": ["cabo verde", "turkey", "saudi arabia", "south africa", "croatia", "ecuador", "belgium", "france"],
    "Leo": ["new zealand", "ghana", "paraguay", "greece", "uruguay", "senegal", "mexico", "argentina"],
    "Yahir": ["czech republic", "bosnia", "algeria", "cote d'ivoire", "colombia", "switzerland", "usa", "spain"],
    "Heri": ["jordan", "sweden", "norway", "qatar", "japan", "austria", "canada", "brazil"]
}

def normalizar(nombre):
    if not isinstance(nombre, str): return ""
    return nombre.lower().strip().replace("é", "e").replace("á", "a").replace("í", "i").replace("ó", "o").replace("ú", "u")

def obtener_dueno(equipo):
    nombre_busqueda = normalizar(equipo)
    # DEBUG: Mostramos qué está buscando
    st.sidebar.write(f"Buscando: '{nombre_busqueda}'")
    for persona, lista in participantes.items():
        if nombre_busqueda in lista:
            return persona
    return f"NO ENCONTRADO: {nombre_busqueda}"

# Carga de datos
@st.cache_data
def load_data():
    df = pd.read_csv('FIFA2026_schedule_Fixtures.csv')
    if 'teams' in df.columns:
        df[['Local', 'Visitante']] = df['teams'].str.split(' v ', n=1, expand=True)
    return df

df = load_data()
# Simulamos resultados para ver si funciona sin usar la BD por ahora
df['goles_local'] = 1 
df['goles_visitante'] = 0

df['Propietario'] = df['Local'].apply(obtener_dueno)

st.dataframe(df[['Local', 'Propietario']])
