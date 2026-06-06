import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Quiniela Pro 2026", layout="wide")

# Diccionario de dueños (mantenemos los nombres estándar)
participantes = {
    "Andres": ["Congo", "Irak", "Egypt", "Panama", "Austria", "Iran", "Germany", "England"],
    "Roberto": ["Haiti", "Curacao", "Tunisia", "Uzbekistan", "Morocco", "South Korea", "Netherlands", "Portugal"],
    "Ruben": ["Cabo Verde", "Turkey", "Saudi Arabia", "South Africa", "Croatia", "Ecuador", "Belgium", "France"],
    "Leo": ["New Zealand", "Ghana", "Paraguay", "Greece", "Uruguay", "Senegal", "Mexico", "Argentina"],
    "Yahir": ["Czech Republic", "Bosnia", "Algeria", "Côte d'Ivoire", "Colombia", "Switzerland", "USA", "Spain"],
    "Heri": ["Jordan", "Sweden", "Norway", "Qatar", "Japan", "Austria", "Canada", "Brazil"]
}

def obtener_dueno(equipo):
    equipo = str(equipo).strip().lower()
    for persona, lista in participantes.items():
        for item in lista:
            if equipo == item.lower():
                return persona
    return "Sin dueño"

@st.cache_data
def load_data():
    archivo = 'FIFA2026_schedule_Fixtures.csv'
    df = pd.read_csv(archivo)
    if 'teams' in df.columns:
        df[['Local', 'Visitante']] = df['teams'].str.split(' v ', n=1, expand=True)
    return df

# --- INTERFAZ ---
st.markdown("<h1>🏆 Quiniela de Incentivos: $3,000 MXN</h1>", unsafe_allow_html=True)
df = load_data()

# Procesar resultados
conn = sqlite3.connect('resultados_quiniela.db')
res_df = pd.read_sql('SELECT * FROM resultados', conn)
conn.close()

df_final = df.merge(res_df, left_on='match_number', right_on='match_id', how='left')

# lógica mejorada
def logica_ganador(row):
    if pd.isna(row['goles_local']): return "Pendiente", "N/A"
    if row['goles_local'] > row['goles_visitante']: 
        return row['Local'], obtener_dueno(row['Local'])
    if row['goles_local'] < row['goles_visitante']: 
        return row['Visitante'], obtener_dueno(row['Visitante'])
    return "Empate", "N/A"

df_final[['Campeon', 'Propietario']] = df_final.apply(lambda r: pd.Series(logica_ganador(r)), axis=1)

# Mostrar
st.dataframe(df_final[['match_number', 'Local', 'goles_local', 'goles_visitante', 'Visitante', 'Campeon', 'Propietario']], 
             use_container_width=True, hide_index=True)

# Registro
with st.sidebar:
    st.subheader("Registrar")
    m = st.selectbox("Partido", df['match_number'].unique())
    gl = st.number_input("Goles Local", 0)
    gv = st.number_input("Goles Visita", 0)
    if st.button("Guardar"):
        conn = sqlite3.connect('resultados_quiniela.db')
        conn.execute('REPLACE INTO resultados VALUES (?, ?, ?)', (m, gl, gv))
        conn.commit()
        conn.close()
        st.rerun()
