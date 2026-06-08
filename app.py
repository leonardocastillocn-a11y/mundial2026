import streamlit as st
import pandas as pd
import sqlite3
from st_aggrid import AgGrid, GridOptionsBuilder

# Configuración con diseño ancho
st.set_page_config(page_title="Quiniela Pro 2026", layout="wide")

# CSS Personalizado para un look corporativo (Estilo oscuro/moderno)
st.markdown("""
    <style>
    .main { background-color: #0f172a; }
    .stApp { color: #f8fafc; }
    h1 { color: #38bdf8; font-weight: 800; text-align: center; margin-bottom: 2rem; }
    .css-1r6slb0 { border: 1px solid #334155; border-radius: 10px; padding: 20px; }
    </style>
""", unsafe_allow_html=True)

# Lógica de Datos
@st.cache_data
def get_data():
    df = pd.read_csv('FIFA2026_schedule_Fixtures.csv')
    if 'teams' in df.columns:
        df[['Local', 'Visitante']] = df['teams'].str.split(' v ', n=1, expand=True)
    return df

st.title("🏆 TAHONA EMPERADORES | QUINIELA 2026")

df = get_data()

# Layout en dos columnas de alto nivel
col1, col2 = st.columns([1, 3], gap="large")

with col1:
    st.markdown("### 📝 Registrar Marcador")
    m_id = st.selectbox("Selecciona Partido:", df['match_number'].unique())
    col_a, col_b = st.columns(2)
    g_l = col_a.number_input("Local", 0)
    g_v = col_b.number_input("Visitante", 0)
    
    if st.button("Actualizar Marcador", use_container_width=True):
        conn = sqlite3.connect('resultados_quiniela.db')
        conn.execute('REPLACE INTO resultados VALUES (?, ?, ?)', (m_id, g_l, g_v))
        conn.commit()
        conn.close()
        st.rerun()

with col2:
    st.markdown("### 📊 Calendario y Resultados")
    conn = sqlite3.connect('resultados_quiniela.db')
    res = pd.read_sql('SELECT * FROM resultados', conn)
    conn.close()
    
    df_final = df.merge(res, left_on='match_number', right_on='match_id', how='left').fillna("-")
    
    # Configuración de Tabla Profesional (AgGrid)
    gb = GridOptionsBuilder.from_dataframe(df_final)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_default_column(sortable=True, filter=True)
    grid_options = gb.build()
    
    AgGrid(df_final, gridOptions=grid_options, theme='streamlit', fit_columns_on_grid_load=True)
