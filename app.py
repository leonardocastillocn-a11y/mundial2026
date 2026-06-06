import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Quiniela Mundial 2026", layout="wide")

# Conexión a Base de Datos
def get_db_connection():
    return sqlite3.connect('resultados_quiniela.db')

# Inicializar tabla de resultados
conn = get_db_connection()
conn.execute('''CREATE TABLE IF NOT EXISTS resultados 
                (match_id TEXT PRIMARY KEY, goles_local INTEGER, goles_visitante INTEGER)''')
conn.commit()
conn.close()

st.title("⚽ Gestión Oficial: Quiniela Mundial 2026")

# Intentar cargar datos desde los dos archivos que tienes
try:
    # Intentamos leer el segundo archivo que subiste, que suele ser el que tiene los nombres
    if os.path.exists('FIFA2026_schedule_Fixtures.csv'):
        df = pd.read_csv('FIFA2026_schedule_Fixtures.csv')
    else:
        df = pd.read_csv('FIFA2026_schedule.csv')

    # Ajuste automático: buscamos la columna de equipos
    # Si la columna se llama 'teams' o similar, la normalizamos
    if 'teams' in df.columns:
        df[['Local', 'Visitante']] = df['teams'].str.split(' v ', n=1, expand=True)
    elif 'Local' not in df.columns:
        # Si no hay columna de equipos, creamos columnas vacías para no romper el código
        df['Local'] = "Equipo A"
        df['Visitante'] = "Equipo B"

    # Formulario
    st.sidebar.header("Administración")
    match_number = st.sidebar.selectbox("Selecciona Partido:", df['match_number'].unique())
    goles_l = st.sidebar.number_input("Goles Local", min_value=0, step=1)
    goles_v = st.sidebar.number_input("Goles Visitante", min_value=0, step=1)

    if st.sidebar.button("Guardar Resultado"):
        conn = get_db_connection()
        conn.execute('REPLACE INTO resultados VALUES (?, ?, ?)', (match_number, goles_l, goles_v))
        conn.commit()
        conn.close()
        st.sidebar.success("Guardado!")

    # Merge de resultados
    res_df = pd.read_sql('SELECT * FROM resultados', get_db_connection())
    df_final = df.merge(res_df, left_on='match_number', right_on='match_id', how='left')

    # Lógica de ganador
    def calc_ganador(row):
        if pd.isna(row['goles_local']): return "Pendiente"
        if row['goles_local'] > row['goles_visitante']: return str(row['Local'])
        if row['goles_local'] < row['goles_visitante']: return str(row['Visitante'])
        return "Empate"

    df_final['Ganador'] = df_final.apply(calc_ganador, axis=1)

    st.subheader("Calendario Actualizado")
    st.dataframe(df_final[['match_number', 'group', 'Local', 'goles_local', 'goles_visitante', 'Visitante', 'Ganador', 'stadium']], use_container_width=True)

except Exception as e:
    st.error("Error al cargar los datos. Revisa que los archivos CSV existan en GitHub.")
    st.write(f"Detalle técnico: {e}")
