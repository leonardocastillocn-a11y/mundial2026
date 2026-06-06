# 1. Carga el archivo
df = pd.read_csv('FIFA2026_schedule.csv')

# 2. DETECCIÓN AUTOMÁTICA: Buscamos qué columna tiene los equipos
# Si el archivo tiene 'teams', usamos esa. Si no, buscamos una que se le parezca.
if 'teams' in df.columns:
    columna_equipos = 'teams'
elif 'equipo' in df.columns: # Por si está en español
    columna_equipos = 'equipo'
else:
    # Si no encuentra ninguna, te avisamos cuál es el problema real
    st.error(f"No encuentro la columna de equipos. Las columnas actuales son: {list(df.columns)}")
    st.stop() # Detiene el código para que no explote

# 3. Procesamiento seguro
df[['Local', 'Visitante']] = df[columna_equipos].str.split(' v ', n=1, expand=True)
