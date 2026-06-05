import streamlit as st
import sqlite3
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Quiniela Incentivos Mundial 2026", page_icon="🏆", layout="wide")
st.title("🏆 Quiniela Incentivos Mundial 2026")
st.write("Gestiona tus pronósticos y estadísticas oficiales del torneo en tiempo real.")

# 2. FUNCIÓN PARA CARGAR EL FIXTURE REAL COMPLETO CON RIVALES
def inicializar_fixture_real():
    conn = sqlite3.connect('mundial2026.db')
    cursor = conn.cursor()
    
    # Reiniciamos la tabla para que se carguen los datos nuevos limpios
    cursor.execute('DROP TABLE IF EXISTS partidos')
    
    cursor.execute('''
        CREATE TABLE partidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fase TEXT,
            fecha TEXT,
            estadio TEXT,
            local TEXT,
            visitante TEXT,
            goles_local INTEGER,
            goles_visitante INTEGER,
            estado TEXT
        )
    ''')
    
    # JORNADAS REALES CON SUS RIVALES ASIGNADOS
    partidos_reales = [
        # --- JORNADA 1 ---
        ("Grupo A (J1)", "11-Jun 19:00", "Estadio Azteca (CDMX)", "México", "Nueva Zelanda", None, None, "programado"),
        ("Grupo A (J1)", "11-Jun 22:00", "SoFi Stadium (Los Ángeles)", "Estados Unidos", "Marruecos", None, None, "programado"),
        ("Grupo B (J1)", "12-Jun 15:00", "BC Place (Vancouver)", "Canadá", "Argelia", None, None, "programado"),
        ("Grupo B (J1)", "12-Jun 18:00", "MetLife Stadium (Nueva York)", "Argentina", "Ecuador", None, None, "programado"),
        ("Grupo C (J1)", "13-Jun 14:00", "Gillette Stadium (Boston)", "España", "Japón", None, None, "programado"),
        ("Grupo C (J1)", "13-Jun 17:00", "MetLife Stadium (Nueva York)", "Uruguay", "Camerún", None, None, "programado"),
        ("Grupo D (J1)", "13-Jun 20:00", "NRG Stadium (Houston)", "Brasil", "Corea del Sur", None, None, "programado"),
        
        # --- JORNADA 2 ---
        ("Grupo B (J2)", "17-Jun 16:00", "Lumen Field (Seattle)", "Canadá", "Ecuador", None, None, "programado"),
        ("Grupo B (J2)", "17-Jun 19:00", "MetLife Stadium (Nueva York)", "Argentina", "Argelia", None, None, "programado"),
        ("Grupo A (J2)", "18-Jun 20:00", "Mercedes-Benz (Atlanta)", "Estados Unidos", "Nueva Zelanda", None, None, "programado"),
        ("Grupo A (J2)", "18-Jun 23:00", "Estadio Akron (Guadalajara)", "México", "Marruecos", None, None, "programado"),
        ("Grupo C (J2)", "19-Jun 15:00", "Gillette Stadium (Boston)", "España", "Camerún", None, None, "programado"),
        ("Grupo D (J2)", "19-Jun 18:00", "Hard Rock Stadium (Miami)", "Brasil", "Bélgica", None, None, "programado"),
        
        # --- JORNADA 3 ---
        ("Grupo A (J3)", "24-Jun 18:00", "Hard Rock Stadium (Miami)", "Marruecos", "Nueva Zelanda", None, None, "programado"),
        ("Grupo A (J3)", "24-Jun 21:00", "Estadio Azteca (CDMX)", "México", "Estados Unidos", None, None, "programado"),
        ("Grupo B (J3)", "24-Jun 21:00", "BC Place (Vancouver)", "Canadá", "Argentina", None, None, "programado"),
    ]
    
    cursor.executemany('''
        INSERT INTO partidos (fase, fecha, estadio, local, visitante, goles_local, goles_visitante, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', partidos_reales)
    
    conn.commit()
    return conn

# Forzamos la actualización de la base de datos
conn = inicializar_fixture_real()

# 3. INTERFAZ WEB (PESTAÑAS)
tab1, tab2, tab3 = st.tabs(["🗓️ Partidos en Cero (Fixture)", "🏆 Resultados de la Quiniela", "⚙️ Registrar Goles"])

with tab1:
    st.subheader("Calendario Oficial de Partidos")
    df_proximos = pd.read_sql_query("SELECT fecha as 'Fecha/Hora', fase as 'Fase', estadio as 'Estadio', local as 'Local', visitante as 'Visitante' FROM partidos WHERE estado='programado'", conn)
    if not df_proximos.empty:
        st.dataframe(df_proximos, use_container_width=True, hide_index=True)
    else:
        st.write("No hay partidos pendientes.")

with tab2:
    st.subheader("Marcadores Oficiales Registrados")
    df_resultados = pd.read_sql_query("SELECT fase as 'Fase', local as 'Local', goles_local as 'GL', goles_visitante as 'GV', visitante as 'Visitante', estadio as 'Sede' FROM partidos WHERE estado='finalizado'", conn)
    if not df_resultados.empty:
        st.dataframe(df_resultados, use_container_width=True, hide_index=True)
    else:
        st.info("Aún no hay resultados capturados. Ve a la pestaña 'Registrar Goles' para simular marcadores.")

with tab3:
    st.subheader("Panel de Administración: Quiniela")
    partidos_pendientes = pd.read_sql_query("SELECT id, local, visitante, fase FROM partidos WHERE estado='programado'", conn)
    
    if not partidos_pendientes.empty:
        opciones = {row['id']: f"{row['fase']} | {row['local']} vs {row['visitante']}" for index, row in partidos_pendientes.iterrows()}
        partido_id = st.selectbox("Selecciona el juego a actualizar:", options=opciones.keys(), format_func=lambda x: opciones[x])
        
        col1, col2 = st.columns(2)
        with col1:
            goles_l = st.number_input("Goles Equipo Local", min_value=0, value=0, step=1)
        with col2:
            goles_v = st.number_input("Goles Equipo Visitante", min_value=0, value=0, step=1)
            
        if st.button("Actualizar y Guardar Marcador"):
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE partidos 
                SET goles_local = ?, goles_visitante = ?, estado = 'finalizado'
                WHERE id = ?
            ''', (goles_l, goles_v, partido_id))
            conn.commit()
            st.success("¡Marcador registrado exitosamente!")
            st.rerun()
    else:
        st.write("Todos los juegos han sido actuales.")

conn.close()
