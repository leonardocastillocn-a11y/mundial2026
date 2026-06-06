import streamlit as st
import pandas as pd
import sqlite3
import os

# --- CONFIGURACIÓN UX ---
st.set_page_config(page_title="Quiniela de Incentivos 2026", layout="wide", page_icon="⚽")

# Diccionario de banderas (puedes añadir más si es necesario)
banderas = {
    "Mexico": "🇲🇽", "South Africa": "🇿🇦", "USA": "🇺🇸", "Canada": "🇨🇦",
    "Brazil": "🇧🇷", "Argentina": "🇦🇷", "Germany": "🇩🇪", "France": "🇫🇷",
    "Spain": "🇪🇸", "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Italy": "🇮🇹", "Portugal": "🇵🇹"
}

def obtener_bandera(pais):
    pais = pais.strip()
    return banderas.get(pais, "🏳️")

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

# --- INTERFAZ PRO ---
st.markdown("""
    <style>
    .header-box { background: linear-gradient(90deg, #1e293b, #334155); padding: 25px; border-radius: 15px; color: white; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-box"><h1>⚽ Quiniela de Incentivos 2026</h1><p>Gran Premio: <b>$3,000 MXN</b> | ¡Conviértete en el Campeón!</p></div>', unsafe_allow_html=True)

df = load_data()
col_input, col_viz = st.columns([1, 2])

with col_input:
    st.subheader("📝 Registrar Resultado")
    match_id = st.selectbox("Seleccionar Partido:", df['match_number'].unique())
    c1, c2 = st.columns(2)
    g_l = c1.number_input("Goles Local", min_value=0, step=1)
    g_v = c2.number_input("Goles Visitante", min_value=0, step=1)
    
    if st.button("Guardar Marcador", type="primary", use_container_width=True):
        conn = sqlite3.connect('resultados_quiniela.db')
        conn.execute('REPLACE INTO resultados VALUES (?, ?, ?)', (match_id, g_l, g_v))
        conn.commit()
        conn.close()
        st.rerun()

with col_viz:
    st.subheader("⚽ Resultados Actualizados")
    res_df = pd.read_sql('SELECT * FROM resultados', sqlite3.connect('resultados_quiniela.db'))
    df_final = df.merge(res_df, left_on='match_number', right_on='match_id', how='left')
    
    # Aplicar banderas a los nombres
    df_final['Local_Display'] = df_final['Local'].apply(lambda x: f"{obtener_bandera(x)} {x}")
    df_final['Visitante_Display'] = df_final['Visitante'].apply(lambda x: f"{obtener_bandera(x)} {x}")
    
    st.dataframe(
        df_final[['match_number', 'Local_Display', 'goles_local', 'goles_visitante', 'Visitante_Display']],
        use_container_width=True, hide_index=True
    )
