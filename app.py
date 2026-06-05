import streamlit as st
import sqlite3
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Quiniela Incentivos Mundial 2026", page_icon="🏆", layout="wide")
st.title("🏆 Quiniela Incentivos Mundial 2026")
st.write("Gestiona tus pronósticos y estadísticas oficiales del torneo (Horario de Culiacán, Sinaloa - PT).")

# 2. DICCIONARIO MAESTRO DE SELECCIONES
# Aquí puedes actualizar los nombres reales del sorteo. El calendario se actualizará solo.
selecciones = {
    # GRUPO A
    "A1": "México", "A2": "Nueva Zelanda", "A3": "Marruecos", "A4": "Estados Unidos",
    # GRUPO B
    "B1": "Canadá", "B2": "Argelia", "B3": "Argentina", "B4": "Ecuador",
    # GRUPO C
    "C1": "España", "C2": "Japón", "C3": "Uruguay", "C4": "Camerún",
    # GRUPO D
    "D1": "Brasil", "D2": "Corea del Sur", "D3": "Bélgica", "D4": "Gales"
    # Puedes seguir agregando E1, E2, etc., según el sorteo oficial.
}

def obtener_equipo(codigo):
    # Si el equipo está en el diccionario, pone el nombre. Si no, deja el código.
    return selecciones.get(codigo, f"Por definir ({codigo})")

# 3. BASE DE DATOS CON FIXTURE DINÁMICO (HORA DE CULIACÁN)
def inicializar_fixture_completo():
    conn = sqlite3.connect('mundial2026.db')
    cursor = conn.cursor()
    
    # Reiniciamos la tabla para cargar la estructura nueva
    cursor.execute('DROP TABLE IF EXISTS partidos')
    
    cursor.execute('''
        CREATE TABLE partidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fase TEXT,
            fecha_culiacan TEXT,
            estadio TEXT,
            local TEXT,
            visitante TEXT,
            goles_local INTEGER,
            goles_visitante INTEGER,
            estado TEXT
        )
    ''')
    
    # FIXTURE ESTRUCTURADO: FASE DE GRUPOS (Generación automática de cruces)
    partidos_base = [
        # --- JORNADA 1 ---
        ("Grupo A", "11-Jun 14:30", "Estadio Azteca (CDMX)", "A1", "A2"),
        ("Grupo A", "11-Jun 18:00", "SoFi Stadium (Los Ángeles)", "A3", "A4"),
        ("Grupo B", "12-Jun 12:00", "BC Place (Vancouver)", "B1", "B2"),
        ("Grupo B", "12-Jun 16:00", "MetLife Stadium (Nueva York)", "B3", "B4"),
        ("Grupo C", "13-Jun 12:00", "Estadio Akron (Guadalajara)", "C1", "C2"),
        ("Grupo C", "13-Jun 15:00", "Gillette Stadium (Boston)", "C3", "C4"),
        ("Grupo D", "13-Jun 18:00", "NRG Stadium (Houston)", "D1", "D2"),
        ("Grupo D", "14-Jun 12:00", "Hard Rock Stadium (Miami)", "D3", "D4"),
        
        # --- JORNADA 2 ---
        ("Grupo B", "17-Jun 12:00", "Lumen Field (Seattle)", "B1", "B3"),
        ("Grupo B", "17-Jun 15:00", "MetLife Stadium (Nueva York)", "B4", "B2"),
        ("Grupo A", "18-Jun 16:00", "Mercedes-Benz (Atlanta)", "A4", "A2"),
        ("Grupo A", "18-Jun 17:30", "Estadio Akron (Guadalajara)", "A1", "A3"),
        ("Grupo C", "19-Jun 12:00", "Gillette Stadium (Boston)", "C1", "C3"),
        ("Grupo C", "19-Jun 15:00", "NRG Stadium (Houston)", "C4", "C2"),
        ("Grupo D", "19-Jun 18:00", "Levi's Stadium (San Francisco)", "D4", "D2"),
        ("Grupo D", "20-Jun 12:00", "Hard Rock Stadium (Miami)", "D1", "D3"),
        
        # --- JORNADA 3 ---
        ("Grupo A", "24-Jun 13:00", "Hard Rock Stadium (Miami)", "A2", "A3"),
        ("Grupo A", "24-Jun 13:00", "Estadio Azteca (CDMX)", "A1", "A4"),
        ("Grupo B", "24-Jun 13:00", "BC Place (Vancouver)", "B1", "B4"),
        ("Grupo B", "24-Jun 13:00", "Lumen Field (Seattle)", "B2", "B3"),
        ("Grupo C", "25-Jun 13:00", "Estadio Akron (Guadalajara)", "C1", "C4"),
        ("Grupo C", "25-Jun 13:00", "Gillette Stadium (Boston)", "C2", "C3"),
        ("Grupo D", "25-Jun 16:00", "NRG Stadium (Houston)", "D1", "D4"),
        ("Grupo D", "25-Jun 16:00", "Levi's Stadium (San Francisco)", "D2", "D3"),
    ]
    
    # Procesamos la lista para inyectar los nombres del Diccionario Maestro y preparar para SQL
    registros_db = []
    for p in partidos_base:
        fase = p[0]
        fecha = p[1]
        estadio = p[2]
        equipo_local = obtener_equipo(p[3])
        equipo_visita = obtener_equipo(p[4])
        registros_db.append((fase, fecha, estadio, equipo_local, equipo_visita, None, None, "programado"))
    
    cursor.executemany('''
        INSERT INTO partidos (fase, fecha_culiacan, estadio, local, visitante, goles_local, goles_visitante, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', registros_db)
    
    conn.commit()
    return conn

conn = inicializar_fixture_completo()

# 4. INTERFAZ EN PESTAÑAS
tab1, tab2, tab3 = st.tabs(["🗓️ Partidos en Cero (Fixture)", "🏆 Resultados de la Quiniela", "⚙️ Registrar Goles"])

with tab1:
    st.subheader("Calendario Oficial de la FIFA (Hora de Culiacán)")
    df_proximos = pd.read_sql_query("SELECT fecha_culiacan as 'Fecha/Hora (Sinaloa)', fase as 'Fase', estadio as 'Estadio', local as 'Local', visitante as 'Visitante' FROM partidos WHERE estado='programado'", conn)
    if not df_proximos.empty:
        st.dataframe(df_proximos, use_container_width=True, hide_index=True)
    else:
        st.write("No hay partidos pendientes.")

with tab2:
    st.subheader("Marcadores de la Quiniela")
    df_resultados = pd.read_sql_query("SELECT fase as 'Fase', local as 'Local', goles_local as 'GL', goles_visitante as 'GV', visitante as 'Visitante', estadio as 'Sede' FROM partidos WHERE estado='finalizado'", conn)
    if not df_resultados.empty:
        st.dataframe(df_resultados, use_container_width=True, hide_index=True)
    else:
        st.info("Aún no hay resultados. Captura marcadores en la pestaña 'Registrar Goles'.")

with tab3:
    st.subheader("Panel de Administración")
    partidos_pendientes = pd.read_sql_query("SELECT id, local, visitante, fase FROM partidos WHERE estado='programado'", conn)
    
    if not partidos_pendientes.empty:
        opciones = {row['id']: f"{row['fase']} | {row['local']} vs {row['visitante']}" for index, row in partidos_pendientes.iterrows()}
        partido_id = st.selectbox("Selecciona el juego:", options=opciones.keys(), format_func=lambda x: opciones[x])
        
        col1, col2 = st.columns(2)
        with col1:
            goles_l = st.number_input("Goles Local", min_value=0, value=0, step=1)
        with col2:
            goles_v = st.number_input("Goles Visitante", min_value=0, value=0, step=1)
            
        if st.button("Guardar Marcador"):
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
        st.write("Todos los juegos han sido actualizados.")

conn.close()
