import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Gestión de Quiniela 2026", layout="wide")

# 1. Conexión a BD para resultados
def registrar_resultado(match_id, goles_local, goles_visitante):
    conn = sqlite3.connect('resultados_quiniela.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS resultados 
                      (match_id TEXT PRIMARY KEY, goles_local INTEGER, goles_visitante INTEGER)''')
    cursor.execute('REPLACE INTO resultados VALUES (?, ?, ?)', (match_id, goles_local, goles_visitante))
    conn.commit()
    conn.close()

st.title("⚽ Panel de Administración: Quiniela")

# Carga el calendario que subiste
df = pd.read_csv('FIFA2026_schedule.csv')
df[['Local', 'Visitante']] = df['teams'].str.split(' v ', n=1, expand=True)

# 2. Formulario para registrar marcadores
st.subheader("Registrar Marcador")
match_number = st.selectbox("Selecciona el número de partido:", df['match_number'].unique())
col1, col2 = st.columns(2)
with col1:
    goles_l = st.number_input("Goles Local", min_value=0, step=1)
with col2:
    goles_v = st.number_input("Goles Visitante", min_value=0, step=1)

if st.button("Guardar Resultado"):
    registrar_resultado(match_number, goles_l, goles_v)
    st.success(f"Resultado registrado para {match_number}: {goles_l}-{goles_v}")

# 3. Mostrar Tabla con Resultados
st.subheader("Calendario y Marcadores")
st.dataframe(df[['match_number', 'Local', 'Visitante', 'stadium']], use_container_width=True)
