import streamlit as st
import pandas as pd
import sqlite3
import os

# --- CONFIGURACIÓN UX ---
st.set_page_config(page_title="Quiniela Mundial 2026", layout="wide", page_icon="⚽")

# Estilos Pro
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
def get_db_connection():
    return sqlite3.connect('resultados_quiniela.db')

# Crear tabla si no existe
conn = get_db_connection()
conn.execute('''CREATE TABLE IF NOT EXISTS resultados 
                (match_id TEXT PRIMARY KEY, goles_local INTEGER, goles_visitante INTEGER)''')
conn.commit()
conn.close()

# --- LÓGICA DE DATOS ---
@st.cache_data
def load_data():
    # USAMOS EL ARCHIVO QUE CONTIENE LOS FIXTURES (EQUIPOS)
    archivo = 'FIFA2026_schedule_Fixtures.csv'
    
    if os.path.exists(archivo):
        df = pd.read_csv(archivo)
        # Verificamos si la columna existe y separamos los equipos
        if 'teams' in df.columns:
            df[['Local', 'Visitante']] = df['teams'].str.split(' v ', n=1, expand=True)
        return df
    else:
        return pd.DataFrame()

# --- INTERFAZ ---
st.title("🏆 Mundial 2026: Panel Pro")
df = load_data()

if df.empty:
    st.error("Error: Asegúrate de que el archivo 'FIFA2026_schedule_Fixtures.csv' esté en tu repositorio.")
else:
    col_input, col_viz = st.columns([1, 2])

    with col_input:
        st.markdown("### 📝 Registrar Marcador")
        # Aseguramos que el selectbox use el match_number correcto
        match_id = st.selectbox("Seleccionar Partido:", df['match_number'].unique())
        
        c1, c2 = st.columns(2)
        g_l = c1.number_input("Goles Local", min_value=0, step=1)
        g_v = c2.number_input("Goles Visitante", min_value=0, step=1)
        
        if st.button("Guardar Marcador", type="primary", use_container_width=True):
            conn = get_db_connection()
            conn.execute('REPLACE INTO resultados VALUES (?, ?, ?)', (match_id, g_l, g_v))
            conn.commit()
            conn.close()
            st.toast("¡Resultado guardado!", icon="✅")
            st.rerun()

    with col_viz:
        st.markdown("### ⚽ Calendario Oficial")
        # Unir resultados de la base de datos con el calendario
        res_df = pd.read_sql('SELECT * FROM resultados', get_db_connection())
        df_final = df.merge(res_df, left_on='match_number', right_on='match_id', how='left')
        
        # Lógica del ganador
        def get_winner(row):
            if pd.isna(row['goles_local']): return "Pendiente"
            if row['goles_local'] > row['goles_visitante']: return str(row['Local'])
            if row['goles_local'] < row['goles_visitante']: return str(row['Visitante'])
            return "Empate"
        
        df_final['Ganador'] = df_final.apply(get_winner, axis=1)
        
        # Mostrar tabla profesional
        st.dataframe(
            df_final[['match_number', 'Local', 'goles_local', 'goles_visitante', 'Visitante', 'Ganador', 'stadium']],
            use_container_width=True,
            hide_index=True
        )
