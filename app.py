import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA Y ESTILO INDUSTRIAL
# ---------------------------------------------------------
st.set_page_config(
    page_title="LogiControl 360 - Gestión de Logística",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo visual ejecutivo industrial / logístico
st.markdown("""
    <style>
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #f59e0b;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        background: #d97706;
        color: #ffffff;
        font-weight: bold;
        border-radius: 6px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: #b45309;
        box-shadow: 0px 0px 10px #f59e0b;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# GENERACIÓN DE DATOS DE FLOTA Y ENVÍOS (SIMULACIÓN)
# ---------------------------------------------------------
@st.cache_data
def generar_datos_logistica(n_envios=1200):
    np.random.seed(42)
    
    ciudades = ["Lima", "Arequipa", "Trujillo", "Cusco", "Piura", "Chiclayo", "Ica"]
    estados = ["En Tránsito", "Entregado", "Retrasado", "Pendiente"]
    vehiculos = [f"Camión-{i:02d}" for i in range(1, 21)]
    
    fechas = [datetime.now() - timedelta(hours=int(x)) for x in np.random.randint(0, 168, size=n_envios)]
    origen = np.random.choice(ciudades, size=n_envios)
    destino = np.random.choice(ciudades, size=n_envios)
    
    # Asegurar que origen y destino no sean iguales
    destino = np.where(origen == destino, "Arequipa", destino)
    
    estado_envio = np.random.choice(estados, size=n_envios, p=[0.35, 0.50, 0.10, 0.05])
    distancia_km = np.random.uniform(50.0, 1200.0, size=n_envios)
    consumo_combustible_litros = distancia_km * np.random.uniform(0.25, 0.40, size=n_envios)
    costo_envio = distancia_km * np.random.uniform(2.5, 5.0, size=n_envios)
    tiempo_estimado_hrs = distancia_km / np.random.uniform(50.0, 80.0, size=n_envios)
    
    df = pd.DataFrame({
        'ID_Envio': [f"ENV-{1000+i}" for i in range(n_envios)],
        'Fecha': fechas,
        'Origen': origen,
        'Destino': destino,
        'Estado': estado_envio,
        'Vehiculo': np.random.choice(vehiculos, size=n_envios),
        'Distancia_KM': np.round(distancia_km, 1),
        'Combustible_L': np.round(consumo_combustible_litros, 1),
        'Costo_USD': np.round(costo_envio, 2),
        'Tiempo_Est_Hrs': np.round(tiempo_estimado_hrs, 1)
    })
    return df.sort_values(by='Fecha', ascending=False).reset_index(drop=True)

if 'envios' not in st.session_state:
    st.session_state.envios = generar_datos_logistica()

df_envios = st.session_state.envios

# ---------------------------------------------------------
# BARRA LATERAL
# ---------------------------------------------------------
st.sidebar.title("🚚 LogiControl 360")
st.sidebar.caption("Sistema de Control Logístico y Flotas")
st.sidebar.markdown("---")

modulo = st.sidebar.radio(
    "Módulos Operativos:",
    [
        "📊 Dashboard Ejecutivo (KPIs)", 
        "🗺️ Análisis de Rutas y Envíos", 
        "⛽ Consumo y Eficiencia de Flota", 
        "📦 Control de Inventario y Almacén"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Estado del Sistema:** Flota activa en carretera. Datos sincronizados.")

# ---------------------------------------------------------
# MÓDULO 1: DASHBOARD EJECUTIVO (KPIS)
# ---------------------------------------------------------
if modulo == "📊 Dashboard Ejecutivo (KPIs)":
    st.title("📊 Centro de Control Logístico")
    st.markdown("Indicadores clave de rendimiento (KPIs) de la cadena de suministro en tiempo real.")

    # KPIs principales
    total_envios = len(df_envios)
    entregados_tiempo = len(df_envios[df_envios['Estado'] == 'Entregado'])
    retrasados = len(df_envios[df_envios['Estado'] == 'Retrasado'])
    eficiencia_entrega = (entregados_tiempo / total_envios) * 100
    costo_total = df_envios['Costo_USD'].sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Envíos", f"{total_envios:,}")
    with col2:
        st.metric("Tasa de Entrega a Tiempo", f"{eficiencia_entrega:.1f}%")
    with col3:
        st.metric("Envíos Retrasados", f"{retrasados}", delta=f"-{retrasados}", delta_color="inverse")
    with col4:
        st.metric("Costo Operativo Total", f"${costo_total:,.2f}")

    st.markdown("---")

    # Gráficos
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Estado de Envíos en Tiempo Real")
        df_est = df_envios['Estado'].value_counts().reset_index()
        df_est.columns = ['Estado', 'Cantidad']
        fig_est = px.pie(
            df_est, 
            values='Cantidad', 
            names='Estado', 
            hole=0.4,
            color='Estado',
            color_discrete_map={'Entregado': '#10b981', 'En Tránsito': '#3b82f6', 'Retrasado': '#ef4444', 'Pendiente': '#f59e0b'},
            template="plotly_dark"
        )
        st.plotly_chart(fig_est, use_container_width=True)

    with c2:
        st.subheader("Costo Operativo por Destino ($)")
        df_costo_dest = df_envios.groupby('Destino')['Costo_USD'].sum().reset_index()
        fig_costo = px.bar(
            df_costo_dest, 
            x='Destino', 
            y='Costo_USD', 
            color='Costo_USD',
            template="plotly_dark",
            color_continuous_scale="Oranges"
        )
        st.plotly_chart(fig_costo, use_container_width=True)

# ---------------------------------------------------------
# MÓDULO 2: ANÁLISIS DE RUTAS Y ENVÍOS
# ---------------------------------------------------------
elif modulo == "🗺️ Análisis de Rutas y Envíos":
    st.title("🗺️ Análisis de Rutas y Tiempos de Entrega")
    st.markdown("Evaluación del tráfico entre orígenes y destinos clave.")

    # Matriz de volumen entre origen y destino
    df_rutas = df_envios.groupby(['Origen', 'Destino']).size().reset_index(name='Total_Envíos')

    st.subheader("Mapa de Calor de Rutas Más Frecuentes")
    df_pivot = df_rutas.pivot(index='Origen', columns='Destino', values='Total_Envíos').fillna(0)
    
    fig_heatmap = px.imshow(
        df_pivot, 
        text_auto=True, 
        color_continuous_scale="YlOrRd",
        template="plotly_dark",
        labels=dict(x="Ciudad Destino", y="Ciudad Origen", color="Frecuencia")
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

# ---------------------------------------------------------
# MÓDULO 3: CONSUMO Y EFICIENCIA DE FLOTA
# ---------------------------------------------------------
elif modulo == "⛽ Consumo y Eficiencia de Flota":
    st.title("⛽ Análisis de Consumo de Combustible y Rendimiento")
    st.markdown("Rendimiento por unidad de transporte (km por litro).")

    df_vehiculos = df_envios.groupby('Vehiculo').agg({
        'Distancia_KM': 'sum',
        'Combustible_L': 'sum',
        'Costo_USD': 'sum'
    }).reset_index()

    df_vehiculos['Rendimiento_KM_L'] = df_vehiculos['Distancia_KM'] / df_vehiculos['Combustible_L']

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Rendimiento Promedio de Combustible (KM/L)")
        fig_rend = px.bar(
            df_vehiculos, 
            x='Vehiculo', 
            y='Rendimiento_KM_L', 
            color='Rendimiento_KM_L',
            template="plotly_dark",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_rend, use_container_width=True)

    with col2:
        st.subheader("Consumo Total de Combustible por Vehículo (Litros)")
        fig_l = px.bar(
            df_vehiculos, 
            x='Vehiculo', 
            y='Combustible_L', 
            template="plotly_dark",
            color_discrete_sequence=['#f59e0b']
        )
        st.plotly_chart(fig_l, use_container_width=True)

# ---------------------------------------------------------
# MÓDULO 4: CONTROL DE INVENTARIO Y ALMACÉN
# ---------------------------------------------------------
elif modulo == "📦 Control de Inventario y Almacén":
    st.title("📦 Nivel de Stock y Capacidad de Almacén")
    st.markdown("Simulación de capacidad disponible en centros de distribución regionales.")

    np.random.seed(99)
    almacenes = ["Almacén Central Lima", "CD Arequipa", "CD Trujillo", "CD Cusco"]
    capacidad_total = [10000, 5000, 4000, 3000]
    ocupacion_actual = [8200, 4100, 2100, 2800]

    df_almacen = pd.DataFrame({
        'Almacén': almacenes,
        'Capacidad_Total': capacidad_total,
        'Ocupación_Actual': ocupacion_actual
    })
    df_almacen['Porcentaje_Uso'] = (df_almacen['Ocupación_Actual'] / df_almacen['Capacidad_Total']) * 100

    for idx, row in df_almacen.iterrows():
        st.subheader(f"🏬 {row['Almacén']}")
        pct = row['Porcentaje_Uso'] / 100
        st.progress(pct, text=f"Capacidad Utilizada: {row['Ocupación_Actual']:,} / {row['Capacidad_Total']:,} unidades ({row['Porcentaje_Uso']:.1f}%)")
        if row['Porcentaje_Uso'] > 85:
            st.warning("⚠️ Almacén con capacidad crítica (próximo a saturarse).")

# ---------------------------------------------------------
# PIE DE PÁGINA
# ---------------------------------------------------------
st.markdown("---")
st.caption("LogiControl 360 | Plataforma de Inteligencia Logística | Desarrollado con Streamlit, Pandas, NumPy y Plotly | 2026")
