import streamlit as st
import pandas as pd
import sqlite3
import os

# --- CONFIGURACIÓN UX ---
st.set_page_config(page_title="Quiniela de Incentivos 2026", layout="wide", page_icon="⚽")

# --- BASE DE DATOS ---
def get_db_connection():
    return sqlite3.connect('resultados_quiniela.db')

# --- LÓGICA DE DATOS ---
@st.cache_data
def load_data():
    archivo = 'FIFA2026_schedule_Fixtures.csv'
    if not os.path.exists(archivo):
        return pd.DataFrame(), "Archivo no encontrado"
    
    df = pd.read_csv(archivo)
    # Ajuste: Si existe la columna 'teams', la separamos
    if 'teams' in df.columns:
        df[['Local', 'Visitante']] = df['teams'].str.split(' v ', n=1, expand=True)
    else:
        df['Local'] = "Equipo A"
        df['Visitante'] = "Equipo B"
    return df, None

# --- INTERFAZ ---
st.markdown('<div style="background:#1e293b; padding:20px; border-radius:10px; color:white;"><h1>🏆 Quiniela de Incentivos</h1><p>Premio: <b>$3,000 MXN</b> | ¡El ganador es el Campeón!</p></div>', unsafe_allow_html=True)

df, error = load_data()

if error:
    st.error(error)
else:
    col_input, col_viz = st.columns([1, 2])
    
    with col_input:
        st.subheader("📝 Registrar Resultado")
        match_id = st.selectbox("Partido:", df['match_number'].unique())
        g_l = st.number_input("Goles Local", min_value=0, step=1)
        g_v = st.number_input("Goles Visitante", min_value=0, step=1)
        
        if st.button("Guardar Marcador", type="primary"):
            conn = get_db_connection()
            conn.execute('REPLACE INTO resultados VALUES (?, ?, ?)', (match_id, g_l, g_v))
            conn.commit()
            conn.close()
            st.rerun()

    with col_viz:
        st.subheader("⚽ Tabla Oficial")
        conn = get_db_connection()
        res_df = pd.read_sql('SELECT * FROM resultados', conn)
        conn.close()
        
        df_final = df.merge(res_df, left_on='match_number', right_on='match_id', how='left')
        st.dataframe(
            df_final[['match_number', 'Local', 'goles_local', 'goles_visitante', 'Visitante']], 
            use_container_width=True, 
            hide_index=True
        )
