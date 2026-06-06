import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Quiniela Pro 2026", layout="wide")

# --- LISTA DE EQUIPOS NORMALIZADA ---
# He simplificado los nombres para que coincidan con la mayoría de archivos CSV estándar
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
    # Quita acentos, pone en minúsculas y quita espacios
    return nombre.lower().strip().replace("é", "e").replace("á", "a").replace("í", "i").replace("ó", "o").replace("ú", "u")

def obtener_dueno(equipo):
    nombre_busqueda = normalizar(equipo)
    for persona, lista in participantes.items():
        if nombre_busqueda in lista:
            return persona
    return "No asignado"

@st.cache_data
def load_data():
    archivo = 'FIFA2026_schedule_Fixtures.csv'
    df = pd.read_csv(archivo)
    if 'teams' in df.columns:
        df[['Local', 'Visitante']] = df['teams'].str.split(' v ', n=1, expand=True)
    return df

# --- INTERFAZ ---
st.title("🏆 Quiniela de Incentivos")
df = load_data()

# Procesar resultados
conn = sqlite3.connect('resultados_quiniela.db')
res_df = pd.read_sql('SELECT * FROM resultados', conn)
conn.close()

df_final = df.merge(res_df, left_on='match_number', right_on='match_id', how='left')

# Lógica robusta
def determinar(row):
    if pd.isna(row['goles_local']): return "Pendiente", "N/A"
    if row['goles_local'] > row['goles_visitante']: 
        return row['Local'], obtener_dueno(row['Local'])
    if row['goles_local'] < row['goles_visitante']: 
        return row['Visitante'], obtener_dueno(row['Visitante'])
    return "Empate", "N/A"

df_final[['Campeon', 'Propietario']] = df_final.apply(lambda r: pd.Series(determinar(r)), axis=1)

# Mostrar Tabla
st.dataframe(df_final[['Local', 'goles_local', 'goles_visitante', 'Visitante', 'Campeon', 'Propietario']], 
             use_container_width=True, hide_index=True)

# Registro
with st.sidebar:
    m = st.selectbox("Partido", df['match_number'].unique())
    gl = st.number_input("Goles Local", 0)
    gv = st.number_input("Goles Visita", 0)
    if st.button("Guardar"):
        conn = sqlite3.connect('resultados_quiniela.db')
        conn.execute('REPLACE INTO resultados VALUES (?, ?, ?)', (m, gl, gv))
        conn.commit()
        conn.close()
        st.rerun()
