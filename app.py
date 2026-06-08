import streamlit as st
import pandas as pd
import sqlite3

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Quiniela de Incentivos", layout="wide", page_icon="🏆")

# CSS para un look profesional y limpio
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    h1 { color: #1e293b !important; font-weight: 800 !important; margin-bottom: 30px !important; }
    .css-1r6slb0 { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    df = pd.read_csv('FIFA2026_schedule_Fixtures.csv')
    return df

df = load_data()

# --- HEADER ---
st.markdown("<h1>🏆 Quiniela de Incentivos</h1>", unsafe_allow_html=True)

# --- LAYOUT PRINCIPAL ---
col_sidebar, col_main = st.columns([1, 3], gap="large")

with col_sidebar:
    st.markdown("### 📝 Registro")
    m_id = st.selectbox("Seleccionar Partido:", df['match_number'].unique())
    g_l = st.number_input("Goles Local", 0, step=1)
    g_v = st.number_input("Goles Visitante", 0, step=1)
    
    if st.button("Guardar Marcador", type="primary"):
        conn = sqlite3.connect('resultados_quiniela.db')
        conn.execute('REPLACE INTO resultados VALUES (?, ?, ?)', (m_id, g_l, g_v))
        conn.commit()
        conn.close()
        st.rerun()

with col_main:
    st.markdown("### ⚽ Calendario Oficial")
    conn = sqlite3.connect('resultados_quiniela.db')
    res = pd.read_sql('SELECT * FROM resultados', conn)
    conn.close()
    
    # Fusionar resultados
    df_final = df.merge(res, left_on='match_number', right_on='match_id', how='left')
    df_final[['goles_local', 'goles_visitante']] = df_final[['goles_local', 'goles_visitante']].fillna(0).astype(int)
    
    # Tabla profesional
    st.dataframe(
        df_final[['date', 'match_number', 'teams', 'group', 'stadium', 'goles_local', 'goles_visitante']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "date": "Fecha",
            "match_number": "Partido",
            "teams": "Enfrentamiento",
            "group": "Grupo",
            "stadium": "Estadio"
        }
    )
