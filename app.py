import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Gestión de Quiniela 2026", layout="wide")

# 1. Función para registrar resultados
def registrar_resultado(match_id, goles_local, goles_visitante):
    conn = sqlite3.connect('resultados_quiniela.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS resultados 
                      (match_id TEXT PRIMARY KEY, goles_local INTEGER, goles_visitante INTEGER)''')
    cursor.execute('REPLACE INTO resultados VALUES (?, ?, ?)', (match_id, goles_local, goles_visitante))
    conn.commit()
    conn.close()

st.title("⚽ Panel de Administración: Quiniela")

# 2. Carga del archivo
try:
    df = pd.read_csv('FIFA2026_schedule.csv')
    
    # Si no existe la columna 'teams', la creamos vacía para que el código no falle
    if 'teams' not in df.columns:
        df['Local'] = "Por definir"
        df['Visitante'] = "Por definir"
    else:
        df[['Local', 'Visitante']] = df['teams'].str.split(' v ', n=1, expand=True)

    # 3. Formulario
    match_number = st.selectbox("Selecciona partido:", df['match_number'].unique())
    col1, col2 = st.columns(2)
    goles_l = col1.number_input("Goles Local", min_value=0, step=1)
    goles_v = col2.number_input("Goles Visitante", min_value=0, step=1)

    if st.button("Guardar Resultado"):
        registrar_resultado(match_number, goles_l, goles_v)
        st.success("¡Marcador guardado!")

    # 4. Mostrar tabla de forma segura
    res_df = pd.read_sql('SELECT * FROM resultados', sqlite3.connect('resultados_quiniela.db')) if True else pd.DataFrame()
    df_final = df.merge(res_df, left_on='match_number', right_on='match_id', how='left')

    st.subheader("Calendario y Marcadores")
    # Mostramos solo las columnas que sabemos que existen
    columnas_a_mostrar = [c for c in ['match_number', 'Local', 'goles_local', 'goles_visitante', 'Visitante', 'group'] if c in df_final.columns]
    st.dataframe(df_final[columnas_a_mostrar], use_container_width=True)

except Exception as e:
    st.error("Error al procesar el archivo. Revisa que el nombre sea exacto.")
    st.write(e)
