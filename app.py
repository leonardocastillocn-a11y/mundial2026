import streamlit as st
import pandas as pd
import sqlite3
import os

# --- CONFIGURACIÓN UX ---
st.set_page_config(page_title="Quiniela de Incentivos 2026", layout="wide", page_icon="⚽")

# Diccionario de banderas limpio
banderas = {
    "Mexico": "🇲🇽", "South Africa": "🇿🇦", "USA": "🇺🇸", "Canada": "🇨🇦",
    "Brazil": "🇧🇷", "Argentina": "🇦🇷", "Germany": "🇩🇪", "France": "🇫🇷",
    "Spain": "🇪🇸", "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Italy": "🇮🇹", "Portugal": "🇵🇹"
}

def obtener_bandera(pais):
    if not isinstance(pais, str): return "🏳️"
    return banderas.get(pais.strip(), "🏳️")

# --- LÓGICA DE DATOS ---
@st.cache_data
def load_data():
    archivo = 'FIFA2026_schedule_Fixtures.csv'
    if not os.path.exists(archivo):
        return None, f"Archivo {archivo} no encontrado."
    
    df = pd.read_csv(archivo)
    
    # Verificamos si tenemos la columna necesaria para sacar los equipos
    if 'teams' in df.columns:
        df[['Local', 'Visitante']] = df['teams'].str.split(' v ', n=1, expand=True)
    else:
        # Creamos columnas por defecto si no existen
        df['Local'] = "TBD"
        df['Visitante'] = "TBD"
        
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
        match_id = st.selectbox("Seleccionar Partido:", df['match_number'].unique())
        
        c1, c2 = st.columns(2)
        g_l = c1.number_input("Goles Local", min_value=0, step=1)
        g_v = c2.number_input("Goles Visitante", min_value=0, step=1)
        
        if st.button("Guardar Marcador", type="primary"):
            conn = sqlite3.connect('resultados_quiniela.db')
            conn.execute('REPLACE INTO resultados VALUES (?, ?, ?)', (match_id, g_l, g_v))
            conn.commit()
            conn.close()
            st.rerun()

    with col_viz:
        st.subheader("⚽ Tabla Oficial")
        conn = sqlite3.connect('resultados_quiniela.db')
        res_df = pd.read_sql('SELECT * FROM resultados', conn)
        conn.close()
        
        df_final = df.merge(res_df, left_on='match_number', right_on='match_id', how='left')
        
        # Mostrar datos de forma segura
        df_final['Local_Display'] = df_final['Local'].apply(lambda x: f"{obtener_bandera(x)} {x}")
        df_final['Visitante_Display'] = df_final['Visitante'].apply(lambda x: f"{obtener_bandera(x)} {x}")
        
        st.dataframe(
            df_final[['match_number', 'Local_Display', 'goles_local', 'goles_visitante', 'Visitante_Display']],
            use_container_width=True, hide_index=True
        )
