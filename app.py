import streamlit as st
import pandas as pd
import sqlite3
import os

# --- CONFIGURACIÓN UX ---
st.set_page_config(page_title="Quiniela Mundial 2026", layout="wide", page_icon="⚽")

# Estilos CSS Pro
st.markdown("""
    <style>
    .metric-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border-left: 5px solid #22c55e; }
    .stApp { background-color: #f1f5f9; }
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
st.title("🏆 Mundial 2026: Quiniela Pro")

# --- SECCIÓN DE INCENTIVO (NUEVO) ---
with st.container():
    col_metric1, col_metric2 = st.columns(2)
    with col_metric1:
        st.metric(label="Pozo Acumulado Actual", value="$15,500 MXN", delta="¡Sigue creciendo!")
    with col_metric2:
        st.info("💡 **Incentivo:** ¡El usuario con más aciertos se llevará el 70% del pozo acumulado al finalizar la fase de grupos!")

st.markdown("---")

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
            st.toast("Marcador guardado", icon="✅")
            st.rerun()

    with col_viz:
        st.subheader("⚽ Marcadores y Ganadores")
        res_df = pd.read_sql('SELECT * FROM resultados', get_db_connection())
        df_final = df.merge(res_df, left_on='match_number', right_on='match_id', how='left')
        
        def get_winner(row):
            if pd.isna(row['goles_local']): return "Pendiente"
            if row['goles_local'] > row['goles_visitante']: return str(row['Local'])
            if row['goles_local'] < row['goles_visitante']: return str(row['Visitante'])
            return "Empate"
        
        df_final['Ganador'] = df_final.apply(get_winner, axis=1)
        
        st.dataframe(
            df_final[['match_number', 'Local', 'goles_local', 'goles_visitante', 'Visitante', 'Ganador']],
            use_container_width=True, hide_index=True
        )
