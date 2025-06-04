import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Demográfico Nayarit",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stSelectbox > div > div {
        background-color: #f0f2f6;
    }
    h1 {
        color: #2E4057;
        text-align: center;
        font-weight: bold;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

class NayaritDashboard:
    def __init__(self):
        self.df = None
        self.column_mapping = {
            'Clave de entidad federativa': 'cve_entidad',
            'Nombre de la entidad': 'entidad',
            'Clave de municipio o demarcación territorial': 'cve_municipio',
            'Nombre del municipio o demarcación territorial': 'municipio',
            'Clave de localidad': 'cve_localidad',
            'Nombre de la localidad': 'localidad',
            'Población total': 'pob_total',
            'Población femenina': 'pob_femenina',
            'Población masculina': 'pob_masculina',
            'Población de 3 años y más que habla alguna lengua indígena': 'pob_indigena',
            'Población con discapacidad': 'pob_discapacidad',
            'Grado promedio de escolaridad': 'escolaridad_promedio',
            'Población de 12 años y más económicamente activa': 'pob_economicamente_activa',
            'Población sin afiliación a servicios de salud': 'pob_sin_salud',
            'Población afiliada a servicios de salud': 'pob_con_salud',
            'Total de viviendas': 'total_viviendas',
            'Total de viviendas habitadas': 'viviendas_habitadas',
            'Total de viviendas particulares': 'viviendas_particulares'
        }
    
    @st.cache_data
    def load_data(_self, uploaded_file):
        """Carga y procesa los datos del archivo Excel"""
        try:
            df = pd.read_excel(uploaded_file)
            
            # Renombrar columnas
            if all(col in df.columns for col in _self.column_mapping.keys()):
                df = df.rename(columns=_self.column_mapping)
            
            # Limpiar columnas de texto - convertir todo a string y limpiar
            text_columns = ['entidad', 'municipio', 'localidad']
            for col in text_columns:
                if col in df.columns:
                    df[col] = df[col].astype(str)
                    df[col] = df[col].str.strip()  # Eliminar espacios
                    df[col] = df[col].replace(['nan', 'None', ''], pd.NA)  # Convertir valores vacíos a NA
            
            # Eliminar filas donde municipio sea NA o vacía
            df = df.dropna(subset=['municipio'])
            df = df[df['municipio'] != '']
            
            # Convertir a numérico
            numeric_columns = [
                'pob_total', 'pob_femenina', 'pob_masculina', 'pob_indigena',
                'pob_discapacidad', 'escolaridad_promedio', 'pob_economicamente_activa',
                'pob_sin_salud', 'pob_con_salud', 'total_viviendas',
                'viviendas_habitadas', 'viviendas_particulares'
            ]
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Eliminar filas donde la población total sea 0 o NA
            df = df.dropna(subset=['pob_total'])
            df = df[df['pob_total'] > 0]
            
            # Calcular porcentajes y métricas adicionales (con manejo de división por cero)
            df['porcentaje_mujeres'] = np.where(df['pob_total'] > 0, 
                                               (df['pob_femenina'] / df['pob_total'] * 100).round(2), 0)
            df['porcentaje_hombres'] = np.where(df['pob_total'] > 0,
                                               (df['pob_masculina'] / df['pob_total'] * 100).round(2), 0)
            df['porcentaje_indigena'] = np.where(df['pob_total'] > 0,
                                                (df['pob_indigena'] / df['pob_total'] * 100).round(2), 0)
            df['porcentaje_discapacidad'] = np.where(df['pob_total'] > 0,
                                                    (df['pob_discapacidad'] / df['pob_total'] * 100).round(2), 0)
            df['porcentaje_sin_salud'] = np.where(df['pob_total'] > 0,
                                                 (df['pob_sin_salud'] / df['pob_total'] * 100).round(2), 0)
            df['porcentaje_con_salud'] = np.where(df['pob_total'] > 0,
                                                 (df['pob_con_salud'] / df['pob_total'] * 100).round(2), 0)
            df['porcentaje_ocupacion_viviendas'] = np.where(df['total_viviendas'] > 0,
                                                           (df['viviendas_habitadas'] / df['total_viviendas'] * 100).round(2), 0)
            df['personas_por_vivienda'] = np.where(df['viviendas_habitadas'] > 0,
                                                  (df['pob_total'] / df['viviendas_habitadas']).round(2), 0)
            
            return df
            
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
            return None
    
    def show_overview_metrics(self, df):
        """Muestra métricas generales en tarjetas"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_pop = df['pob_total'].sum()
            st.metric(
                label="🏘️ Población Total",
                value=f"{total_pop:,.0f}",
                delta="habitantes"
            )
        
        with col2:
            total_municipalities = df['municipio'].nunique()
            st.metric(
                label="🏛️ Total Municipios",
                value=f"{total_municipalities}",
                delta="municipios"
            )
        
        with col3:
            total_localities = df['localidad'].nunique()
            st.metric(
                label="🏘️ Total Localidades",
                value=f"{total_localities}",
                delta="localidades"
            )
        
        with col4:
            avg_education = df['escolaridad_promedio'].mean()
            st.metric(
                label="🎓 Escolaridad Promedio",
                value=f"{avg_education:.1f}",
                delta="años de estudio"
            )
    
    def create_municipality_ranking(self, df):
        """Crea un ranking de municipios por diferentes métricas"""
        municipality_stats = df.groupby('municipio').agg({
            'pob_total': 'sum',
            'escolaridad_promedio': 'mean',
            'pob_indigena': 'sum',
            'pob_sin_salud': 'sum',
            'total_viviendas': 'sum',
            'viviendas_habitadas': 'sum'
        }).reset_index()
        
        municipality_stats['porcentaje_indigena'] = (municipality_stats['pob_indigena'] / municipality_stats['pob_total'] * 100).round(2)
        municipality_stats['porcentaje_sin_salud'] = (municipality_stats['pob_sin_salud'] / municipality_stats['pob_total'] * 100).round(2)
        municipality_stats['ocupacion_viviendas'] = (municipality_stats['viviendas_habitadas'] / municipality_stats['total_viviendas'] * 100).round(2)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Población por Municipio', 'Escolaridad Promedio por Municipio', 
                          '% Población Indígena', '% Sin Servicios de Salud'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Ordenar por población para los gráficos
        municipality_stats_sorted = municipality_stats.sort_values('pob_total', ascending=True)
        
        # Gráfico 1: Población por municipio
        fig.add_trace(
            go.Bar(y=municipality_stats_sorted['municipio'], 
                   x=municipality_stats_sorted['pob_total'], 
                   name='Población', marker_color='#3498db', orientation='h'),
            row=1, col=1
        )
        
        # Gráfico 2: Escolaridad por municipio
        municipality_education = municipality_stats.sort_values('escolaridad_promedio', ascending=True)
        fig.add_trace(
            go.Bar(y=municipality_education['municipio'], 
                   x=municipality_education['escolaridad_promedio'], 
                   name='Escolaridad', marker_color='#2ecc71', orientation='h'),
            row=1, col=2
        )
        
        # Gráfico 3: % Población indígena
        municipality_indigenous = municipality_stats.sort_values('porcentaje_indigena', ascending=True)
        fig.add_trace(
            go.Bar(y=municipality_indigenous['municipio'], 
                   x=municipality_indigenous['porcentaje_indigena'], 
                   name='% Indígena', marker_color='#e74c3c', orientation='h'),
            row=2, col=1
        )
        
        # Gráfico 4: % Sin servicios de salud
        municipality_health = municipality_stats.sort_values('porcentaje_sin_salud', ascending=True)
        fig.add_trace(
            go.Bar(y=municipality_health['municipio'], 
                   x=municipality_health['porcentaje_sin_salud'], 
                   name='% Sin Salud', marker_color='#f39c12', orientation='h'),
            row=2, col=2
        )
        
        fig.update_layout(height=800, showlegend=False, template="plotly_white", 
                         title_text="Análisis Comparativo de Municipios en Nayarit")
        
        return fig
    
    def create_locality_analysis(self, df, selected_municipality=None):
        """Análisis de localidades dentro de un municipio"""
        if selected_municipality and selected_municipality != "Todos los municipios":
            df_filtered = df[df['municipio'] == selected_municipality]
            title_suffix = f" - {selected_municipality}"
        else:
            # Mostrar las localidades más grandes del estado
            df_filtered = df.nlargest(20, 'pob_total')
            title_suffix = " - Top 20 Localidades"
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=(f'Población por Localidad{title_suffix}', 
                          f'Escolaridad vs Acceso a Salud{title_suffix}')
        )
        
        # Gráfico 1: Población por localidad
        df_sorted = df_filtered.sort_values('pob_total', ascending=True).tail(15)  # Top 15
        
        fig.add_trace(
            go.Bar(y=df_sorted['localidad'], 
                   x=df_sorted['pob_total'],
                   name='Población',
                   marker_color='#9b59b6',
                   orientation='h'),
            row=1, col=1
        )
        
        # Gráfico 2: Scatter de escolaridad vs acceso a salud
        fig.add_trace(
            go.Scatter(x=df_filtered['escolaridad_promedio'],
                      y=df_filtered['porcentaje_con_salud'],
                      mode='markers',
                      marker=dict(size=df_filtered['pob_total']/1000,
                                 color=df_filtered['porcentaje_indigena'],
                                 colorscale='Viridis',
                                 showscale=True,
                                 colorbar=dict(title="% Población<br>Indígena")),
                      text=df_filtered['localidad'],
                      name='Localidades',
                      hovertemplate='Localidad: %{text}<br>' +
                                   'Escolaridad: %{x:.1f} años<br>' +
                                   'Con Salud: %{y:.1f}%<br>' +
                                   'Población: %{marker.size}k<extra></extra>'),
            row=1, col=2
        )
        
        fig.update_layout(height=600, template="plotly_white", showlegend=False)
        fig.update_xaxes(title_text="Población", row=1, col=1)
        fig.update_yaxes(title_text="Localidad", row=1, col=1)
        fig.update_xaxes(title_text="Escolaridad Promedio (años)", row=1, col=2)
        fig.update_yaxes(title_text="% Población con Servicios de Salud", row=1, col=2)
        
        return fig
    
    def create_demographic_pyramid(self, df, selected_municipality=None):
        """Crea una pirámide demográfica para Nayarit o un municipio específico"""
        if selected_municipality and selected_municipality != "Todos los municipios":
            df_filtered = df[df['municipio'] == selected_municipality]
            title = f"Pirámide Poblacional - {selected_municipality}"
        else:
            df_filtered = df
            title = "Pirámide Poblacional - Nayarit"
        
        total_women = df_filtered['pob_femenina'].sum()
        total_men = df_filtered['pob_masculina'].sum()
        
        # Crear grupos de edad aproximados basados en distribución típica de México
        age_groups = ['0-14', '15-29', '30-44', '45-59', '60-74', '75+']
        age_distribution = [0.27, 0.26, 0.20, 0.15, 0.09, 0.03]
        
        women_by_age = [total_women * dist for dist in age_distribution]
        men_by_age = [-total_men * dist for dist in age_distribution]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=age_groups,
            x=women_by_age,
            name='Mujeres',
            orientation='h',
            marker_color='#FF69B4',
            text=[f'{val:,.0f}' for val in women_by_age],
            textposition='inside'
        ))
        
        fig.add_trace(go.Bar(
            y=age_groups,
            x=men_by_age,
            name='Hombres',
            orientation='h',
            marker_color='#4169E1',
            text=[f'{abs(val):,.0f}' for val in men_by_age],
            textposition='inside'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Población",
            yaxis_title="Grupos de Edad",
            barmode='relative',
            height=500,
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    
    def create_housing_analysis(self, df):
        """Análisis detallado de vivienda por municipio"""
        housing_stats = df.groupby('municipio').agg({
            'total_viviendas': 'sum',
            'viviendas_habitadas': 'sum',
            'viviendas_particulares': 'sum',
            'pob_total': 'sum'
        }).reset_index()
        
        housing_stats['porcentaje_ocupacion'] = (housing_stats['viviendas_habitadas'] / housing_stats['total_viviendas'] * 100).round(2)
        housing_stats['personas_por_vivienda'] = (housing_stats['pob_total'] / housing_stats['viviendas_habitadas']).round(2)
        housing_stats['viviendas_desocupadas'] = housing_stats['total_viviendas'] - housing_stats['viviendas_habitadas']
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Total de Viviendas por Municipio', 
                          'Porcentaje de Ocupación',
                          'Personas por Vivienda',
                          'Viviendas Desocupadas'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Ordenar por total de viviendas
        housing_sorted = housing_stats.sort_values('total_viviendas', ascending=True)
        
        # Gráfico 1: Total viviendas
        fig.add_trace(
            go.Bar(y=housing_sorted['municipio'], 
                   x=housing_sorted['total_viviendas'],
                   name='Total Viviendas', marker_color='#3498db', orientation='h'),
            row=1, col=1
        )
        
        # Gráfico 2: % Ocupación
        occupancy_sorted = housing_stats.sort_values('porcentaje_ocupacion', ascending=True)
        fig.add_trace(
            go.Bar(y=occupancy_sorted['municipio'], 
                   x=occupancy_sorted['porcentaje_ocupacion'],
                   name='% Ocupación', marker_color='#2ecc71', orientation='h'),
            row=1, col=2
        )
        
        # Gráfico 3: Personas por vivienda
        density_sorted = housing_stats.sort_values('personas_por_vivienda', ascending=True)
        fig.add_trace(
            go.Bar(y=density_sorted['municipio'], 
                   x=density_sorted['personas_por_vivienda'],
                   name='Personas/Vivienda', marker_color='#f39c12', orientation='h'),
            row=2, col=1
        )
        
        # Gráfico 4: Viviendas desocupadas
        empty_sorted = housing_stats.sort_values('viviendas_desocupadas', ascending=True)
        fig.add_trace(
            go.Bar(y=empty_sorted['municipio'], 
                   x=empty_sorted['viviendas_desocupadas'],
                   name='Viviendas Vacías', marker_color='#e74c3c', orientation='h'),
            row=2, col=2
        )
        
        fig.update_layout(height=800, showlegend=False, template="plotly_white",
                         title_text="Análisis de Vivienda por Municipio")
        
        return fig
    
    def create_top_localities_table(self, df, metric='pob_total', top_n=20):
        """Crea una tabla con las principales localidades según una métrica"""
        metric_names = {
            'pob_total': 'Población Total',
            'escolaridad_promedio': 'Escolaridad Promedio',
            'porcentaje_indigena': '% Población Indígena',
            'porcentaje_sin_salud': '% Sin Servicios de Salud',
            'personas_por_vivienda': 'Personas por Vivienda'
        }
        
        top_localities = df.nlargest(top_n, metric)[
            ['municipio', 'localidad', 'pob_total', 'escolaridad_promedio', 
             'porcentaje_indigena', 'porcentaje_sin_salud', 'personas_por_vivienda']
        ].round(2)
        
        top_localities.columns = ['Municipio', 'Localidad', 'Población', 'Escolaridad', 
                                 '% Indígena', '% Sin Salud', 'Personas/Vivienda']
        
        return top_localities

def main():
    """Función principal del dashboard"""
    
    # Título principal
    st.title("🏖️ Dashboard Demográfico de Nayarit")
    st.markdown("*Análisis detallado por municipios y localidades*")
    st.markdown("---")
    
    # Inicializar el dashboard
    dashboard = NayaritDashboard()
    
    # Sidebar para carga de archivo
    st.sidebar.header("📊 Configuración")
    uploaded_file = st.sidebar.file_uploader(
        "Sube tu archivo Excel con datos de Nayarit",
        type=['xlsx', 'xls'],
        help="Archivo debe contener datos demográficos de municipios y localidades de Nayarit"
    )
    
    if uploaded_file is not None:
        # Cargar datos
        with st.spinner('Cargando y procesando datos de Nayarit...'):
            df = dashboard.load_data(uploaded_file)
        
        if df is not None:
            st.success(f"✅ Datos cargados exitosamente: {len(df):,} localidades en {df['municipio'].nunique()} municipios")
            
            # Filtros en el sidebar
            st.sidebar.markdown("---")
            st.sidebar.header("🔍 Filtros")
            
            # Filtro por municipio
            try:
                unique_municipalities = df['municipio'].dropna().unique()
                unique_municipalities = [mun for mun in unique_municipalities if isinstance(mun, str) and mun.strip() != '']
                municipalities = ["Todos los municipios"] + sorted(unique_municipalities)
            except Exception as e:
                st.error(f"Error al procesar los municipios: {e}")
                municipalities = ["Todos los municipios"]
            
            selected_municipality = st.sidebar.selectbox("Selecciona un municipio:", municipalities)
            
            # Filtrar datos según selección
            if selected_municipality != "Todos los municipios":
                df_filtered = df[df['municipio'] == selected_municipality]
                st.info(f"Mostrando datos para: **{selected_municipality}** ({len(df_filtered)} localidades)")
            else:
                df_filtered = df
            
            # Métricas generales
            st.header("📈 Resumen de Nayarit")
            dashboard.show_overview_metrics(df)
            
            st.markdown("---")
            
            # Tabs para organizar el contenido
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "🏛️ Municipios", 
                "🏘️ Localidades", 
                "👥 Demografía", 
                "🏠 Vivienda",
                "📊 Rankings",
                "📋 Datos"
            ])
            
            with tab1:
                st.header("Análisis por Municipios")
                municipality_fig = dashboard.create_municipality_ranking(df)
                st.plotly_chart(municipality_fig, use_container_width=True)
                
                # Tabla resumen de municipios
                st.subheader("📊 Resumen por Municipios")
                municipality_summary = df.groupby('municipio').agg({
                    'localidad': 'count',
                    'pob_total': 'sum',
                    'escolaridad_promedio': 'mean',
                    'porcentaje_indigena': 'mean',
                    'porcentaje_sin_salud': 'mean'
                }).round(2)
                municipality_summary.columns = ['Localidades', 'Población', 'Escolaridad Prom.', '% Indígena Prom.', '% Sin Salud Prom.']
                municipality_summary = municipality_summary.sort_values('Población', ascending=False)
                st.dataframe(municipality_summary, use_container_width=True)
            
            with tab2:
                st.header("Análisis de Localidades")
                locality_fig = dashboard.create_locality_analysis(df, selected_municipality)
                st.plotly_chart(locality_fig, use_container_width=True)
                
                if selected_municipality != "Todos los municipios":
                    st.markdown(f"""
                    **💡 Análisis de {selected_municipality}:**
                    - El gráfico de la izquierda muestra las localidades más pobladas
                    - El gráfico de la derecha relaciona educación con acceso a salud
                    - El tamaño de los puntos representa la población
                    - El color indica el porcentaje de población indígena
                    """)
            
            with tab3:
                st.header("Análisis Demográfico")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Pirámide poblacional
                    pyramid_fig = dashboard.create_demographic_pyramid(df, selected_municipality)
                    st.plotly_chart(pyramid_fig, use_container_width=True)
                
                with col2:
                    # Distribución por género en el área seleccionada
                    total_women = df_filtered['pob_femenina'].sum()
                    total_men = df_filtered['pob_masculina'].sum()
                    
                    gender_fig = px.pie(
                        values=[total_women, total_men],
                        names=['Mujeres', 'Hombres'],
                        title=f"Distribución por Género - {selected_municipality if selected_municipality != 'Todos los municipios' else 'Nayarit'}",
                        color_discrete_sequence=['#FF69B4', '#4169E1']
                    )
                    st.plotly_chart(gender_fig, use_container_width=True)
                
                # Métricas demográficas adicionales
                col3, col4, col5 = st.columns(3)
                with col3:
                    indigenous_pct = (df_filtered['pob_indigena'].sum() / df_filtered['pob_total'].sum() * 100)
                    st.metric("🏺 Población Indígena", f"{indigenous_pct:.1f}%")
                
                with col4:
                    disability_pct = (df_filtered['pob_discapacidad'].sum() / df_filtered['pob_total'].sum() * 100)
                    st.metric("♿ Población con Discapacidad", f"{disability_pct:.1f}%")
                
                with col5:
                    active_pct = (df_filtered['pob_economicamente_activa'].sum() / df_filtered['pob_total'].sum() * 100)
                    st.metric("💼 Población Económicamente Activa", f"{active_pct:.1f}%")
            
            with tab4:
                st.header("Análisis de Vivienda")
                housing_fig = dashboard.create_housing_analysis(df)
                st.plotly_chart(housing_fig, use_container_width=True)
            
            with tab5:
                st.header("Rankings y Top Localidades")
                
                # Selector de métrica para ranking
                metric_options = {
                    'pob_total': 'Población Total',
                    'escolaridad_promedio': 'Escolaridad Promedio',
                    'porcentaje_indigena': '% Población Indígena',
                    'porcentaje_sin_salud': '% Sin Servicios de Salud',
                    'personas_por_vivienda': 'Personas por Vivienda'
                }
                
                selected_metric = st.selectbox(
                    "Selecciona la métrica para el ranking:",
                    options=list(metric_options.keys()),
                    format_func=lambda x: metric_options[x]
                )
                
                top_n = st.slider("Número de localidades a mostrar:", 10, 50, 20)
                
                # Crear tabla de ranking
                top_table = dashboard.create_top_localities_table(df, selected_metric, top_n)
                st.subheader(f"🏆 Top {top_n} Localidades por {metric_options[selected_metric]}")
                st.dataframe(top_table, use_container_width=True)
            
            with tab6:
                st.header("Explorador de Datos")
                
                # Filtros adicionales
                col1, col2 = st.columns(2)
                with col1:
                    min_population = st.number_input("Población mínima:", 0, int(df['pob_total'].max()), 0)
                with col2:
                    num_records = st.selectbox("Registros a mostrar:", [25, 50, 100, 500, 1000])
                
                # Filtrar por población mínima
                df_display = df_filtered[df_filtered['pob_total'] >= min_population]
                
                st.subheader(f"Datos de {selected_municipality if selected_municipality != 'Todos los municipios' else 'Nayarit'}")
                st.write(f"Mostrando {min(len(df_display), num_records)} de {len(df_display)} registros")
                
                # Seleccionar columnas a mostrar
                available_columns = {
                    'municipio': 'Municipio',
                    'localidad': 'Localidad',
                    'pob_total': 'Población Total',
                    'pob_femenina': 'Población Femenina',
                    'pob_masculina': 'Población Masculina',
                    'escolaridad_promedio': 'Escolaridad Promedio',
                    'pob_indigena': 'Población Indígena',
                    'pob_discapacidad': 'Población con Discapacidad',
                    'pob_economicamente_activa': 'Población Económicamente Activa',
                    'pob_sin_salud': 'Sin Servicios de Salud',
                    'pob_con_salud': 'Con Servicios de Salud',
                    'total_viviendas': 'Total Viviendas',
                    'viviendas_habitadas': 'Viviendas Habitadas',
                    'personas_por_vivienda': 'Personas por Vivienda',
                    'porcentaje_mujeres': '% Mujeres',
                    'porcentaje_hombres': '% Hombres',
                    'porcentaje_indigena': '% Población Indígena',
                    'porcentaje_discapacidad': '% Población con Discapacidad',
                    'porcentaje_sin_salud': '% Sin Servicios de Salud',
                    'porcentaje_con_salud': '% Con Servicios de Salud'
                }
                
                selected_columns = st.multiselect(
                    "Selecciona las columnas a mostrar:",
                    options=list(available_columns.keys()),
                    default=['municipio', 'localidad', 'pob_total', 'escolaridad_promedio', 'porcentaje_indigena'],
                    format_func=lambda x: available_columns[x]
                )
                
                if selected_columns:
                    # Mostrar datos
                    display_df = df_display[selected_columns].head(num_records)
                    
                    # Formatear nombres de columnas
                    display_df.columns = [available_columns[col] for col in selected_columns]
                    
                    st.dataframe(display_df, use_container_width=True)
                    
                    # Estadísticas descriptivas
                    st.subheader("📊 Estadísticas Descriptivas")
                    numeric_cols = display_df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        stats_df = display_df[numeric_cols].describe().round(2)
                        st.dataframe(stats_df, use_container_width=True)
                    
                    # Botón para descargar datos
                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Descargar datos como CSV",
                        data=csv,
                        file_name=f"datos_nayarit_{selected_municipality.replace(' ', '_') if selected_municipality != 'Todos los municipios' else 'completo'}.csv",
                        mime='text/csv'
                    )
                else:
                    st.warning("Por favor selecciona al menos una columna para mostrar.")
            
            # Información adicional en el sidebar
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 📊 Información del Dataset")
            st.sidebar.info(f"""
            **Total de registros:** {len(df):,}
            
            **Municipios:** {df['municipio'].nunique()}
            
            **Localidades:** {df['localidad'].nunique()}
            
            **Población total:** {df['pob_total'].sum():,}
            
            **Promedio de escolaridad:** {df['escolaridad_promedio'].mean():.1f} años
            """)
            
            # Footer con información adicional
            st.sidebar.markdown("---")
            st.sidebar.markdown("### ℹ️ Acerca de")
            st.sidebar.markdown("""
            Este dashboard presenta análisis demográficos detallados del estado de Nayarit, México.
            
            **Funcionalidades:**
            - Análisis por municipios y localidades
            - Visualizaciones interactivas
            - Métricas demográficas clave
            - Análisis de vivienda
            - Rankings personalizables
            - Explorador de datos completo
            
            **Datos:** Censo de Población y Vivienda - INEGI
            """)
            
        else:
            st.error("❌ Error al cargar los datos. Por favor verifica el formato del archivo.")
            st.markdown("""
            ### 📋 Formato esperado del archivo:
            
            El archivo Excel debe contener las siguientes columnas:
            - Clave de entidad federativa
            - Nombre de la entidad
            - Clave de municipio o demarcación territorial
            - Nombre del municipio o demarcación territorial
            - Clave de localidad
            - Nombre de la localidad
            - Población total
            - Población femenina
            - Población masculina
            - Población de 3 años y más que habla alguna lengua indígena
            - Población con discapacidad
            - Grado promedio de escolaridad
            - Población de 12 años y más económicamente activa
            - Población sin afiliación a servicios de salud
            - Población afiliada a servicios de salud
            - Total de viviendas
            - Total de viviendas habitadas
            - Total de viviendas particulares
            """)
    
    else:
        # Pantalla de bienvenida
        st.markdown("""
        ## 👋 Bienvenido al Dashboard Demográfico de Nayarit
        
        Este dashboard te permite analizar datos demográficos detallados del estado de Nayarit, México.
        
        ### 🚀 Para comenzar:
        1. **Sube tu archivo Excel** usando el panel lateral
        2. **Explora los datos** a través de las diferentes pestañas
        3. **Filtra por municipio** para análisis específicos
        4. **Descarga resultados** en formato CSV
        
        ### 📊 Análisis disponibles:
        - **Municipios**: Comparativas entre municipios
        - **Localidades**: Análisis detallado por localidad
        - **Demografía**: Pirámides poblacionales y distribuciones
        - **Vivienda**: Estadísticas de vivienda y ocupación
        - **Rankings**: Top de localidades por diferentes métricas
        - **Datos**: Explorador completo de la información
        
        ### 📁 Formato de archivo:
        - **Tipo**: Excel (.xlsx o .xls)
        - **Fuente recomendada**: Datos del INEGI (Censo de Población y Vivienda)
        - **Estructura**: Datos por localidad con información demográfica completa
        
        ---
        
        ### 🏖️ Sobre Nayarit
        
        Nayarit es un estado ubicado en la región occidental de México, conocido por:
        - Sus hermosas costas en el Pacífico
        - Su rica diversidad cultural
        - Sus tradiciones indígenas (Huichol, Cora, Tepehuán)
        - Su economía basada en turismo, agricultura y pesca
        
        **¡Comienza subiendo tu archivo de datos para explorar la riqueza demográfica de Nayarit!**
        """)
        
        # Mostrar imagen de ejemplo o información adicional
        st.info("💡 **Tip**: Puedes obtener datos demográficos oficiales desde el sitio web del INEGI (www.inegi.org.mx)")

if __name__ == "__main__":
    main()