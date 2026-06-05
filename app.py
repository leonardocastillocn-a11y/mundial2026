import streamlit as st
import sqlite3
import pandas as pd

# 1. CONFIGURACIÓN Y ESTILO DE LA PÁGINA
st.set_page_config(page_title="Estadísticas Mundial 2026", page_icon="⚽", layout="wide")
st.title("⚽ Sistema de Estadísticas - Mundial 2026")

# 2. FUNCIÓN PARA CREAR Y CONECTAR LA BASE DE DATOS LOCAL
def inicializar_y_conectar_db():
    conn = sqlite3.connect('mundial2026.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fase TEXT,
            fecha TEXT,
            local TEXT,
            visitante TEXT,
            goles_local INTEGER,
            goles_visitante INTEGER,
            estado TEXT
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM partidos")
    if cursor.fetchone()[0] == 0:
        partidos_iniciales = [
            ("Grupo A", "11-Jun 19:00", "México", "Por definir", None, None, "programado"),
            ("Grupo A", "11-Jun 22:00", "Estados Unidos", "Por definir", None, None, "programado"),
            ("Grupo B", "12-Jun 15:00", "Canadá", "Por definir", None, None, "programado"),
            ("Grupo B", "12-Jun 18:00", "Argentina", "Por definir", None, None, "programado")
        ]
        cursor.executemany('''
            INSERT INTO partidos (fase, fecha, local, visitante, goles_local, goles_visitante, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', partidos_iniciales)
        conn.commit()
    return conn

conn = inicializar_y_conectar_db()

# 3. INTERFAZ WEB (PESTAÑAS)
tab1, tab2, tab3 = st.tabs(["🗓️ Próximos Partidos (En Cero)", "🏆 Resultados Finales", "⚙️ Panel de Control"])

with tab1:
    st.subheader("Juegos pendientes por disputarse")
    df_proximos = pd.read_sql_query("SELECT fecha as 'Fecha/Hora', fase as 'Fase', local as 'Equipo Local', visitante as 'Equipo Visitante' FROM partidos WHERE estado='programado'", conn)
    if not df_proximos.empty:
        st.dataframe(df_proximos, use_container_width=True, hide_index=True)
    else:
        st.write("¡Todos los partidos programados se han jugado!")

with tab2:
    st.subheader("Marcadores Oficiales")
    df_resultados = pd.read_sql_query("SELECT fase as 'Fase', local as 'Local', goles_local as 'GL', goles_visitante as 'GV', visitante as 'Visitante' FROM partidos WHERE estado='finalizado'", conn)
    if not df_resultados.empty:
        st.dataframe(df_resultados, use_container_width=True, hide_index=True)
    else:
        st.info("El torneo aún no reporta partidos finalizados. Actualiza los juegos en el Panel de Control.")

with tab3:
    st.subheader("Registrar marcador de partido")
    partidos_pendientes = pd.read_sql_query("SELECT id, local, visitante FROM partidos WHERE estado='programado'", conn)
    
    if not partidos_pendientes.empty:
        opciones = {row['id']: f"{row['local']} vs {row['visitante']}" for index, row in partidos_pendientes.iterrows()}
        partido_id = st.selectbox("Selecciona el partido:", options=opciones.keys(), format_func=lambda x: opciones[x])
        
        col1, col2 = st.columns(2)
        with col1:
            goles_l = st.number_input("Goles Local", min_value=0, value=0, step=1)
        with col2:
            goles_v = st.number_input("Goles Visitante", min_value=0, value=0, step=1)
            
        if st.button("Guardar Resultado"):
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE partidos 
                SET goles_local = ?, goles_visitante = ?, estado = 'finalizado'
                WHERE id = ?
            ''', (goles_l, goles_v, partido_id))
            conn.commit()
            st.success("¡Marcador registrado! Revisa la pestaña de Resultados.")
            st.rerun()
    else:
        st.write("No hay partidos pendientes por actualizar.")

conn.close()
