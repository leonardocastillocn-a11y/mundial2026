import streamlit as st
import pandas as pd
import sqlite3
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Quiniela 2026", layout="centered", page_icon="⚽")

# --- BASE DE DATOS ---
def get_db_connection():
    return sqlite3.connect('resultados_quiniela.db')

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    archivo = 'FIFA2026_schedule_Fixtures.csv'
    if not os.path.exists(archivo): return pd.DataFrame()
    df = pd.read_csv(archivo)
    if 'teams' in df.columns:
        df[['Local', 'Visitante']] = df['teams'].str.split(' v ', n=1, expand=True)
    return df

# --- INTERFAZ ---
st.title("🏆 Quiniela de Incentivos")
st.markdown("### Premio: $3,000 MXN")

df = load_data()

# Obtener resultados
conn = get_db_connection()
res_df = pd.read_sql('SELECT * FROM resultados', conn)
conn.close()

# --- VISTA SEPARADA (TARJETAS) ---
st.subheader("⚽ Juegos")

for _, row in df.iterrows():
    # Buscar si ya tiene resultado
    res = res_df[res_df['match_id'] == row['match_number']]
    
    # Crear un bloque visual para cada juego
    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**{row['match_number']}**: {row['Local']} vs {row['Visitante']}")
            if not res.empty:
                st.success(f"Marcador: {int(res.iloc[0]['goles_local'])} - {int(res.iloc[0]['goles_visitante'])}")
            else:
                st.warning("Pendiente de resultado")
        
        with col2:
            if st.button("Registrar", key=f"btn_{row['match_number']}"):
                st.session_state['edit_match'] = row['match_number']

# --- MODAL DE REGISTRO ---
if 'edit_match' in st.session_state:
    st.divider()
    st.subheader(f"Registrar {st.session_state['edit_match']}")
    g_l = st.number_input("Goles Local", 0)
    g_v = st.number_input("Goles Visitante", 0)
    
    if st.button("Guardar Marcador"):
        conn = get_db_connection()
        conn.execute('REPLACE INTO resultados VALUES (?, ?, ?)', (st.session_state['edit_match'], g_l, g_v))
        conn.commit()
        conn.close()
        del st.session_state['edit_match']
        st.rerun()026")
