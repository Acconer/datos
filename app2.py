import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configurar la página
st.set_page_config(
    page_title="Dashboard Nayarit", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="data/nayarit.png"
)

# CSS personalizado para mejorar el diseño
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79, #2e8b57);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #1f4e79;
    }
    .sidebar-info {
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>Dashboard de Nayarit</h1>
    <p>Análisis demográfico y socioeconómico de municipios y localidades</p>
</div>
""", unsafe_allow_html=True)

# Cargar datos con manejo de errores
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel("data/nayarit2_limpio.xlsx")
        columnas_numericas = [
            "Población total", "Población femenina", "Población masculina",
            "Población de 3 años y más que habla alguna lengua indígena",
            "Población con discapacidad", "Grado promedio de escolaridad",
            "Población de 12 años y más económicamente activa",
            "Población sin afiliación a servicios de salud",
            "Población afiliada a servicios de salud",
            "Total de viviendas", "Total de viviendas habitadas", "Total de viviendas particulares"
        ]
        for col in columnas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    except FileNotFoundError:
        st.error("⚠️ No se pudo encontrar el archivo de datos. Asegúrate de que 'data/nayarit2_limpio.xlsx' existe.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ Error al cargar los datos: {str(e)}")
        return pd.DataFrame()

df = cargar_datos()

if df.empty:
    st.stop()

# Sidebar mejorado
with st.sidebar:
    st.markdown("### 🎛️ Panel de Control")
    
    # Información del dataset
    st.markdown("""
    <div class="sidebar-info">
        <strong>📊 Información del Dataset</strong><br>
        • Municipios: {}<br>
        • Localidades: {}<br>
        • Población total: {:,}
    </div>
    """.format(
        df["Nombre del municipio o demarcación territorial"].nunique(),
        len(df),  # 👈 CAMBIO: Ahora cuenta todas las filas (2850)
        df["Población total"].sum()
    ), unsafe_allow_html=True)
    
    # Filtros
    st.markdown("#### 🔍 Filtros")
    municipios = sorted(df["Nombre del municipio o demarcación territorial"].dropna().unique())
    municipio = st.selectbox("🏙️ Municipio", municipios, key="municipio_select")
    
    localidades = df[df["Nombre del municipio o demarcación territorial"] == municipio]["Nombre de la localidad"].dropna().unique()
    localidad = st.selectbox("📍 Localidad", ["Todas"] + list(sorted(localidades)), key="localidad_select")
    
    # Opciones de visualización
    st.markdown("#### ⚙️ Opciones de Visualización")
    top_n = st.slider("📈 Top N localidades a mostrar", 5, 20, 10)

# Filtrar datos
df_mpio = df[df["Nombre del municipio o demarcación territorial"] == municipio]
df_local = df_mpio if localidad == "Todas" else df_mpio[df_mpio["Nombre de la localidad"] == localidad]

# Métricas principales mejoradas
st.markdown("## 📊 Panel de Métricas")
col1, col2, col3, col4 = st.columns(4)

with col1:
    poblacion_total = df_local['Población total'].sum()
    st.metric(
        "👥 Población Total", 
        f"{poblacion_total:,.0f}",
        delta=f"{(poblacion_total/df['Población total'].sum()*100):.1f}% del estado"
    )

with col2:
    viviendas = df_local['Total de viviendas habitadas'].sum()
    promedio_hab_vivienda = poblacion_total / viviendas if viviendas > 0 else 0
    st.metric(
        "🏘️ Viviendas Habitadas", 
        f"{viviendas:,.0f}",
        delta=f"{promedio_hab_vivienda:.1f} hab/vivienda"
    )

with col3:
    prom_escolaridad = df_local["Grado promedio de escolaridad"].mean()
    st.metric(
        "🎓 Escolaridad Promedio", 
        f"{prom_escolaridad:.1f}" if pd.notna(prom_escolaridad) else "N/D",
        delta="años de estudio"
    )

with col4:
    pob_indigena = df_local["Población de 3 años y más que habla alguna lengua indígena"].sum()
    pct_indigena = (pob_indigena / poblacion_total * 100) if poblacion_total > 0 else 0
    st.metric(
        "🗣️ Población Indígena", 
        f"{pob_indigena:,.0f}",
        delta=f"{pct_indigena:.1f}%"
    )

# Funciones de visualización mejoradas
def crear_grafico_barras(df, x, y, titulo, color_col=None, horizontal=False):
    """Crear gráfico de barras mejorado"""
    df_sorted = df.sort_values(by=y, ascending=True if horizontal else False)
    
    if horizontal:
        fig = px.bar(df_sorted.tail(top_n), y=x, x=y, title=titulo, 
                     color=color_col, orientation='h', height=500)
    else:
        fig = px.bar(df_sorted.head(top_n), x=x, y=y, title=titulo, 
                     color=color_col, height=500)
    
    fig.update_layout(
        font=dict(size=12),
        title_font_size=16,
        showlegend=True if color_col else False
    )
    return fig

def crear_grafico_dona(valores, etiquetas, titulo):
    """Crear gráfico de dona"""
    fig = go.Figure(data=[go.Pie(
        labels=etiquetas, 
        values=valores, 
        hole=.3,
        textinfo='label+percent',
        textposition='outside'
    )])
    fig.update_layout(
        title=titulo,
        font=dict(size=12),
        showlegend=True,
        height=400
    )
    return fig

# Visualizaciones principales
st.markdown("## 📈 Análisis Visual")

if localidad == "Todas":
    # Tabs para organizar mejor el contenido
    tab1, tab2, tab3, tab4 = st.tabs(["🏘️ Población", "👥 Demografía", "📚 Educación", "🏥 Salud"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Población por localidad
            df_pop = df_local.groupby("Nombre de la localidad")["Población total"].sum().reset_index()
            fig_pop = crear_grafico_barras(df_pop, "Nombre de la localidad", "Población total", 
                                         f"🏘️ Top {top_n} Localidades por Población", horizontal=True)
            st.plotly_chart(fig_pop, use_container_width=True)
        
        with col2:
            # Distribución de viviendas
            viviendas_data = [
                df_local["Total de viviendas habitadas"].sum(),
                df_local["Total de viviendas"].sum() - df_local["Total de viviendas habitadas"].sum()
            ]
            fig_viviendas = crear_grafico_dona(viviendas_data, 
                                             ["Habitadas", "Deshabitadas"], 
                                             "🏠 Distribución de Viviendas")
            st.plotly_chart(fig_viviendas, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución por género
            genero_data = [
                df_local["Población femenina"].sum(),
                df_local["Población masculina"].sum()
            ]
            fig_genero = crear_grafico_dona(genero_data, 
                                          ["Femenina", "Masculina"], 
                                          "👥 Distribución por Género")
            st.plotly_chart(fig_genero, use_container_width=True)
        
        with col2:
            # Población con discapacidad
            discapacidad_data = [
                df_local["Población con discapacidad"].sum(),
                df_local["Población total"].sum() - df_local["Población con discapacidad"].sum()
            ]
            fig_discapacidad = crear_grafico_dona(discapacidad_data, 
                                                ["Con discapacidad", "Sin discapacidad"], 
                                                "♿ Población con Discapacidad")
            st.plotly_chart(fig_discapacidad, use_container_width=True)
    
    with tab3:
        # Escolaridad por localidad
        df_edu = df_local.groupby("Nombre de la localidad")["Grado promedio de escolaridad"].mean().reset_index()
        df_edu = df_edu.dropna()
        fig_edu = crear_grafico_barras(df_edu, "Nombre de la localidad", "Grado promedio de escolaridad", 
                                     f"🎓 Escolaridad Promedio por Localidad", horizontal=True)
        st.plotly_chart(fig_edu, use_container_width=True)
    
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            # Afiliación a servicios de salud
            salud_data = [
                df_local["Población afiliada a servicios de salud"].sum(),
                df_local["Población sin afiliación a servicios de salud"].sum()
            ]
            fig_salud = crear_grafico_dona(salud_data, 
                                         ["Con afiliación", "Sin afiliación"], 
                                         "🏥 Afiliación a Servicios de Salud")
            st.plotly_chart(fig_salud, use_container_width=True)
        
        with col2:
            # Población económicamente activa
            pea = df_local["Población de 12 años y más económicamente activa"].sum()
            pob_12_mas = df_local["Población total"].sum() * 0.75  # Estimación
            pea_data = [pea, pob_12_mas - pea]
            fig_pea = crear_grafico_dona(pea_data, 
                                       ["Económicamente activa", "No activa"], 
                                       "💼 Población Económicamente Activa")
            st.plotly_chart(fig_pea, use_container_width=True)

else:
    # Vista detallada de localidad específica
    st.markdown(f"### 📊 Análisis Detallado: {localidad}")
    
    # Información específica de la localidad
    if not df_local.empty:
        datos_localidad = df_local.iloc[0]
        
        # Métricas adicionales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 👥 Demografía")
            st.write(f"**Población femenina:** {datos_localidad['Población femenina']:,.0f}")
            st.write(f"**Población masculina:** {datos_localidad['Población masculina']:,.0f}")
            st.write(f"**Población indígena:** {datos_localidad['Población de 3 años y más que habla alguna lengua indígena']:,.0f}")
        
        with col2:
            st.markdown("#### 🏠 Vivienda")
            st.write(f"**Total de viviendas:** {datos_localidad['Total de viviendas']:,.0f}")
            st.write(f"**Viviendas habitadas:** {datos_localidad['Total de viviendas habitadas']:,.0f}")
            ocupacion = (datos_localidad['Total de viviendas habitadas'] / datos_localidad['Total de viviendas'] * 100) if datos_localidad['Total de viviendas'] > 0 else 0
            st.write(f"**Tasa de ocupación:** {ocupacion:.1f}%")
        
        with col3:
            st.markdown("#### 🎯 Indicadores Sociales")
            st.write(f"**Escolaridad promedio:** {datos_localidad['Grado promedio de escolaridad']:.1f} años")
            st.write(f"**Con discapacidad:** {datos_localidad['Población con discapacidad']:,.0f}")
            st.write(f"**PEA:** {datos_localidad['Población de 12 años y más económicamente activa']:,.0f}")

# Tabla de datos mejorada
st.markdown("## 📋 Datos Detallados")
if not df_local.empty:
    # Opciones de la tabla
    col1, col2 = st.columns([3, 1])
    with col2:
        mostrar_todas_columnas = st.checkbox("Mostrar todas las columnas", value=False)
    
    if mostrar_todas_columnas:
        st.dataframe(df_local, use_container_width=True, height=400)
    else:
        columnas_principales = [
            "Nombre de la localidad", "Población total", "Población femenina", 
            "Población masculina", "Grado promedio de escolaridad", 
            "Total de viviendas habitadas"
        ]
        columnas_disponibles = [col for col in columnas_principales if col in df_local.columns]
        st.dataframe(df_local[columnas_disponibles], use_container_width=True, height=400)
else:
    st.warning("No hay datos disponibles para la selección actual.")

# Descarga de datos mejorada
st.markdown("## 📥 Exportar Datos")
col1, col2, col3 = st.columns(3)

@st.cache_data
def convertir_csv(df):
    return df.to_csv(index=False).encode('utf-8')

@st.cache_data
def generar_resumen():
    resumen = f"""
RESUMEN ESTADÍSTICO - {municipio}
{'='*50}

POBLACIÓN:
- Total: {df_local['Población total'].sum():,.0f}
- Femenina: {df_local['Población femenina'].sum():,.0f}
- Masculina: {df_local['Población masculina'].sum():,.0f}
- Indígena: {df_local['Población de 3 años y más que habla alguna lengua indígena'].sum():,.0f}

VIVIENDA:
- Total de viviendas: {df_local['Total de viviendas'].sum():,.0f}
- Viviendas habitadas: {df_local['Total de viviendas habitadas'].sum():,.0f}

EDUCACIÓN:
- Escolaridad promedio: {df_local['Grado promedio de escolaridad'].mean():.2f} años

SALUD:
- Con afiliación: {df_local['Población afiliada a servicios de salud'].sum():,.0f}
- Sin afiliación: {df_local['Población sin afiliación a servicios de salud'].sum():,.0f}
"""
    return resumen.encode('utf-8')

with col1:
    csv = convertir_csv(df_local)
    st.download_button(
        "📊 Descargar CSV",
        csv,
        f"datos_{municipio.replace(' ', '_')}.csv",
        "text/csv",
        help="Descargar datos en formato CSV"
    )

with col2:
    resumen = generar_resumen()
    st.download_button(
        "📋 Descargar Resumen",
        resumen,
        f"resumen_{municipio.replace(' ', '_')}.txt",
        "text/plain",
        help="Descargar resumen estadístico"
    )

with col3:
    st.markdown("📧 **Compartir Dashboard**")
    st.code(f"Municipio: {municipio}\nLocalidad: {localidad}", language=None)

