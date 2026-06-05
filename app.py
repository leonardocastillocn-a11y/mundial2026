import streamlit as st
import pandas as pd

st.set_page_config(page_title="Quiniela Mundial 2026", layout="wide")
st.title("⚽ Calendario Oficial Mundial 2026")

# Intentamos cargar el archivo principal
try:
    # Leemos el archivo CSV desde la raíz del repositorio
    df = pd.read_csv('FIFA2026_schedule.csv')
    
    # Procesamos la columna 'teams' para separar Local y Visitante
    if 'teams' in df.columns:
        df[['Local', 'Visitante']] = df['teams'].str.split(' v ', n=1, expand=True)
        # Mostramos las columnas clave
        columnas_a_mostrar = ['date', 'match_number', 'group', 'Local', 'Visitante', 'stadium']
        df_final = df[columnas_a_mostrar]
    else:
        df_final = df

    st.subheader("Fixture Completo")
    st.dataframe(df_final, use_container_width=True)
    
    st.info(f"Total de partidos cargados: {len(df)}")

except Exception as e:
    st.error("Error al cargar el archivo. Verifica el nombre del archivo en el repositorio.")
    st.write(e)
