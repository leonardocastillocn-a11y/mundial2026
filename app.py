import streamlit as st
import pandas as pd
import sqlite3
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Quiniela Mundial 2026", layout="wide", page_icon="⚽")

# --- CONEXIÓN A BASE DE DATOS ---
def get_db_connection():
    conn = sqlite3.connect('resultados_quiniela.db')
    return conn

# Inicializar tabla si no existe
conn = get_db_connection()
conn.execute('''CREATE TABLE IF NOT EXISTS resultados 
                (match_id TEXT PRIMARY KEY, goles_local INTEGER, goles_visitante INTEGER)''')
conn.commit()
conn.close()

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    archivo = 'FIFA2026_schedule_Fixtures.csv'
    if not os.path.exists(archivo):
        return pd.DataFrame()
    
    df = pd.read_csv(archivo)
    # Extraer nombres si existe la columna 'teams'
    if 'teams' in df.columns:
        df[['Local', 'Visitante']] = df['teams'].str.split(' v ', n=1, expand=True)
    return df

# --- INTERFAZ ---
st.markdown("""
    <div style="background-color: #1e293b; padding: 20px; border-radius: 10px; color: white; text-align: center;">
        <h1>🏆 Quiniela de Incentivos 2026</h1>
        <p style="font-size: 1.2em;">Gran Premio: <b>$3,000 MXN</b> | ¡Sé el Campeón!</p>
    </div>
""", unsafe_allow_html=True)

df = load_data()

if df.empty:
    st.error("Error: No se encontró el archivo 'FIFA2026_schedule_Fixtures.csv'.")
else:
    col_input, col_viz = st.columns([1, 2])

    with col_input:
        st.subheader("📝 Registrar Marcador")
        match_id = st.selectbox("Seleccionar Partido:", df['match_number'].unique())
        
        c1, c2 = st.columns(2)
        g_l = c1.number_input("Goles Local", min_value=0, step=1)
        g_v = c2.number_input("Goles Visitante", min_value=0, step=1)
        
        if st.button("Guardar Marcador", type="primary", use_container_width=True):
            conn = get_db_connection()
            conn.execute('REPLACE INTO resultados VALUES (?, ?, ?)', (match_id, g_l, g_v))
            conn.commit()
            conn.close()
            st.toast("Marcador guardado con éxito", icon="✅")
            st.rerun()

    with col_viz:
        st.subheader("⚽ Marcadores y Resultados")
        
        # Unir datos
        conn = get_db_connection()
        res_df = pd.read_sql('SELECT * FROM resultados', conn)
        conn.close()
        
        df_final = df.merge(res_df, left_on='match_number', right_on='match_id', how='left')
        
        # Lógica de ganador limpia
        def obtener_campeon(row):
            if pd.isna(row['goles_local']): return "Pendiente"
            if row['goles_local'] > row['goles_visitante']: return str(row['Local'])
            if row['goles_local'] < row['goles_visitante']: return str(row['Visitante'])
            return "Empate"
        
        df_final['Campeon'] = df_final.apply(obtener_campeon, axis=1)
        
        # Mostrar tabla profesional
        st.dataframe(
            df_final[['match_number', 'Local', 'goles_local', 'goles_visitante', 'Visitante', 'Campeon']],
            use_container_width=True,
            hide_index=True
        )

# Pie de página
st.markdown("---")
st.caption("Sistema de Quiniela de Incentivos - Mundial 2026")
