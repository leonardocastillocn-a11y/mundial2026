import streamlit as st
import pandas as pd
import sqlite3
import os

# --- CONFIGURACIÓN PRO ---
st.set_page_config(page_title="Quiniela Pro 2026", layout="wide", page_icon="🏆")

# Estilo para que se vea elegante
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    h1 { color: #38bdf8; text-align: center; }
    .stDataFrame { border: 1px solid #334155; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# Base de datos
def get_db():
    return sqlite3.connect('resultados_quiniela.db')

# Cargar Datos desde tu archivo CSV
@st.cache_data
def load_data():
    # Asegúrate de que el archivo se llame exactamente así
    df = pd.read_csv('FIFA2026_schedule_Fixtures.csv')
    return df

st.title("🏆 TAHONA EMPERADORES | QUINIELA 2026")

df = load_data()

# Layout
col1, col2 = st.columns([1, 2.5], gap="large")

with col1:
    st.subheader("📝 Registrar Resultado")
    m_id = st.selectbox("Selecciona Partido (Match #):", df['match_number'].unique())
    c_a, c_b = st.columns(2)
    g_l = c_a.number_input("Goles Local", 0, step=1)
    g_v = c_b.number_input("Goles Visitante", 0, step=1)
    
    if st.button("Guardar Marcador", type="primary", use_container_width=True):
        conn = get_db()
        conn.execute('REPLACE INTO resultados VALUES (?, ?, ?)', (m_id, g_l, g_v))
        conn.commit()
        conn.close()
        st.success("¡Guardado!")
        st.rerun()

with col2:
    st.subheader("📊 Calendario Completo")
    conn = get_db()
    res = pd.read_sql('SELECT * FROM resultados', conn)
    conn.close()
    
    # Unir resultados con el CSV original usando match_number
    df_final = df.merge(res, left_on='match_number', right_on='match_id', how='left')
    
    # Rellenar campos vacíos para que no se vea "None"
    df_final[['goles_local', 'goles_visitante']] = df_final[['goles_local', 'goles_visitante']].fillna(0).astype(int)
    
    # Mostrar la tabla limpia con tus columnas reales
    st.dataframe(
        df_final[['date', 'match_number', 'teams', 'group', 'stadium', 'goles_local', 'goles_visitante']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "match_number": "Partido",
            "teams": "Enfrentamiento",
            "group": "Grupo",
            "stadium": "Estadio",
            "goles_local": "Goles Local",
            "goles_visitante": "Goles Visita"
        }
    )
