import streamlit as st
import pandas as pd
import sqlite3
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Quiniela de Incentivos 2026", layout="wide", page_icon="🏆")

# Mapeo de dueños basado en 571395.jpg
participantes = {
    "Andres": ["Congo", "Irak", "Egipto", "Panama", "Austria", "Iran", "Alemania", "Inglaterra"],
    "Roberto": ["Haiti", "Curazao", "Tunez", "Uzbekistan", "Marruecos", "Corea del Sur", "Paises Bajos", "Portugal"],
    "Ruben": ["Cabo Verde", "Turquia", "Arabia Saudita", "Sudafrica", "Croacia", "Ecuador", "Belgica", "Francia"],
    "Leo": ["Nueva Zelanda", "Ghana", "Paraguay", "Grecia", "Uruguay", "Senegal", "Mexico", "Argentina"],
    "Yahir": ["Republica Checa", "Bosnia", "Argelia", "Costa de Marfil", "Colombia", "Suiza", "USA", "Espana"],
    "Heri": ["Jordania", "Suecia", "Noruega", "Catar", "Japon", "Canada", "Brazil"]
}

def obtener_dueno(equipo):
    if not isinstance(equipo, str): return "-"
    for persona, equipos in participantes.items():
        if equipo.strip() in equipos:
            return persona
    return "Ninguno"

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
    if 'teams' in df.columns:
        df[['Local', 'Visitante']] = df['teams'].str.split(' v ', n=1, expand=True)
    else:
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
        st.subheader("⚽ Tabla Oficial de Ganadores")
        conn = get_db_connection()
        res_df = pd.read_sql('SELECT * FROM resultados', conn)
        conn.close()
        
        df_final = df.merge(res_df, left_on='match_number', right_on='match_id', how='left')
        
        # Identificar ganador y propietario
        def calcular_resultado(row):
            if pd.isna(row['goles_local']): return "Pendiente", "-"
            if row['goles_local'] > row['goles_visitante']: return row['Local'], obtener_dueno(row['Local'])
            if row['goles_local'] < row['goles_visitante']: return row['Visitante'], obtener_dueno(row['Visitante'])
            return "Empate", "-"

        df_final[['Campeon', 'Propietario']] = df_final.apply(lambda row: pd.Series(calcular_resultado(row)), axis=1)
        
        st.dataframe(
            df_final[['match_number', 'Local', 'goles_local', 'goles_visitante', 'Visitante', 'Campeon', 'Propietario']], 
            use_container_width=True, hide_index=True
        )
