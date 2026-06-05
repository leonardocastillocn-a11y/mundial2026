import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Gestión de Quiniela 2026", layout="wide")

# 1. Función para registrar
def registrar_resultado(match_id, goles_local, goles_visitante):
    conn = sqlite3.connect('resultados_quiniela.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS resultados 
                      (match_id TEXT PRIMARY KEY, goles_local INTEGER, goles_visitante INTEGER)''')
    cursor.execute('REPLACE INTO resultados VALUES (?, ?, ?)', (match_id, goles_local, goles_visitante))
    conn.commit()
    conn.close()

# 2. Función para obtener resultados actuales
def obtener_resultados():
    try:
        conn = sqlite3.connect('resultados_quiniela.db')
        res_df = pd.read_sql('SELECT * FROM resultados', conn)
        conn.close()
        return res_df
    except:
        return pd.DataFrame(columns=['match_id', 'goles_local', 'goles_visitante'])

st.title("⚽ Panel de Administración: Quiniela")

# Carga y procesa calendario
df = pd.read_csv('FIFA2026_schedule.csv')
df[['Local', 'Visitante']] = df['teams'].str.split(' v ', n=1, expand=True)

# Formulario
match_number = st.selectbox("Selecciona partido:", df['match_number'].unique())
col1, col2 = st.columns(2)
goles_l = col1.number_input("Goles Local", min_value=0, step=1)
goles_v = col2.number_input("Goles Visitante", min_value=0, step=1)

if st.button("Guardar Resultado"):
    registrar_resultado(match_number, goles_l, goles_v)
    st.success("¡Marcador guardado!")

# 3. Fusión de datos para mostrar el tablero actualizado
res_df = obtener_resultados()
# Unimos el calendario con los resultados registrados
df_final = df.merge(res_df, left_on='match_number', right_on='match_id', how='left')

# Calcular ganador automáticamente
def determinar_ganador(row):
    if pd.isna(row['goles_local']): return "Pendiente"
    if row['goles_local'] > row['goles_visitante']: return row['Local']
    if row['goles_local'] < row['goles_visitante']: return row['Visitante']
    return "Empate"

df_final['Ganador'] = df_final.apply(determinar_ganador, axis=1)

st.subheader("Calendario y Marcadores en Tiempo Real")
st.dataframe(df_final[['match_number', 'Local', 'goles_local', 'goles_visitante', 'Visitante', 'Ganador']], use_container_width=True)
