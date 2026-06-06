import streamlit as st
import pandas as pd
import sqlite3
import os

# --- CONFIGURACIÓN UX ---
st.set_page_config(page_title="Quiniela de Incentivos 2026", layout="wide", page_icon="🏆")

# Estilos Pro
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .header-box { background-color: #1e293b; padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
def get_db_connection():
    return sqlite3.connect('resultados_quiniela.db')

# --- LÓGICA DE DATOS ---
@st.cache_data
def load_data():
    archivo = 'FIFA2026_schedule_Fixtures.csv'
    if os.path.exists(archivo):
        df = pd.read_csv(archivo)
        if 'teams' in df.columns:
            df[['Local', 'Visitante']] = df['teams'].str.split(' v ', n=1, expand=True)
        return df
    return pd.DataFrame()

# --- INTERFAZ ---
st.markdown('<div class="header-box"><h1>🏆 Quiniela de Incentivos</h1><p>Premio al ganador: <b>$3,000 MXN</b> | ¡Sé el Campeón!</p></div>', unsafe_allow_html=True)

df = load_data()
if df.empty:
    st.error("Archivo no encontrado.")
else:
    col_input, col_viz = st.columns([1, 2])

    with col_input:
        st.subheader("📝 Registrar Resultado")
        match_id = st.selectbox("Seleccionar Partido:", df['match_number'].unique())
        
        c1, c2 = st.columns(2)
        g_l = c1.number_input("Goles Local", min_value=0, step=1)
        g_v = c2.number_input("Goles Visitante", min_value=0, step=1)
        
        if st.button("Guardar Marcador", type="primary", use_container_width=True):
            conn = get_db_connection()
            conn.execute('REPLACE INTO resultados VALUES (?, ?, ?)', (match_id, g_l, g_v))
            conn.commit()
            conn.close()
            st.toast("Resultado registrado", icon="✅")
            st.rerun()

    with col_viz:
        st.subheader("⚽ Tabla de Posiciones y Resultados")
        res_df = pd.read_sql('SELECT * FROM resultados', get_db_connection())
        df_final = df.merge(res_df, left_on='match_number', right_on='match_id', how='left')
        
        def determinar_estado(row):
            if pd.isna(row['goles_local']): return "Pendiente"
            if row['goles_local'] > row['goles_visitante']: return f"🏆 Campeón: {row['Local']}"
            if row['goles_local'] < row['goles_visitante']: return f"🏆 Campeón: {row['Visitante']}"
            return "Empate"
        
        df_final['Resultado_Final'] = df_final.apply(determinar_estado, axis=1)
        
        st.dataframe(
            df_final[['match_number', 'Local', 'goles_local', 'goles_visitante', 'Visitante', 'Resultado_Final']],
            use_container_width=True, hide_index=True
        )

st.markdown("---")
st.caption("Quiniela de Incentivos 2026 - ¡El ganador se lleva el gran premio!")
