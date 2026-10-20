import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="QuantLab - Analítica Avanzada y Simulación",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo visual ejecutivo / analítico
st.markdown("""
    <style>
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #38bdf8;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        background: #0284c7;
        color: #ffffff;
        font-weight: bold;
        border-radius: 6px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background: #0369a1;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# GENERACIÓN DE DATOS ESTOCÁSTICOS (SERIES TEMPORALES)
# ---------------------------------------------------------
@st.cache_data
def generar_serie_temporal(dias=365):
    np.random.seed(42)
    fechas = [datetime.today() - timedelta(days=i) for i in range(dias)]
    fechas.reverse()
    
    # Movimiento browniano geométrico simulado para activos o métricas de negocio
    retornos_1 = np.random.normal(loc=0.0005, scale=0.015, size=dias)
    retornos_2 = np.random.normal(loc=0.0003, scale=0.022, size=dias)
    retornos_3 = np.random.normal(loc=0.0007, scale=0.010, size=dias)
    
    precio_1 = 100 * np.cumprod(1 + retornos_1)
    precio_2 = 150 * np.cumprod(1 + retornos_2)
    volumen = np.random.randint(1000, 50000, size=dias)
    
    df = pd.DataFrame({
        'Fecha': fechas,
        'Activo_Alpha': precio_1,
        'Activo_Beta': precio_2,
        'Volumen_Transaccional': volumen,
        'Retorno_Diario': retornos_1
    })
    return df

df_data = generar_serie_temporal(500)

# ---------------------------------------------------------
# BARRA LATERAL Y NAVEGACIÓN
# ---------------------------------------------------------
st.sidebar.title("🔬 QuantLab Analytics")
st.sidebar.caption("Motor de Simulación y Series Temporales")
st.sidebar.markdown("---")

modulo = st.sidebar.radio(
    "Selecciona el Módulo Analítico:",
    [
        "🎲 Simulación de Monte Carlo", 
        "📊 Análisis de Volatilidad y Tendencias", 
        "📉 Matriz de Correlación y Distribución"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Librerías activas:** Pandas para manipulación tabular, NumPy para cálculos vectorizados y matrices estocásticas, Plotly para visualización interactiva.")

# ---------------------------------------------------------
# MÓDULO 1: SIMULACIÓN DE MONTE CARLO
# ---------------------------------------------------------
if modulo == "🎲 Simulación de Monte Carlo":
    st.title("🎲 Simulación de Monte Carlo (Proyección de Escenarios)")
    st.markdown("Modela múltiples trayectorias futuras posibles utilizando distribuciones probabilísticas basadas en la volatilidad histórica con NumPy.")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        dias_proyeccion = st.slider("Días a proyectar:", 30, 365, 90)
    with col_c2:
        num_simulaciones = st.slider("Número de simulaciones (trayectorias):", 50, 500, 200, 50)
    with col_c3:
        volatilidad_extra = st.slider("Factor de Volatilidad:", 0.5, 2.0, 1.0, 0.1)

    # Cálculo estocástico con NumPy
    ultimo_valor = df_data['Activo_Alpha'].iloc[-1]
    media_retorno = df_data['Retorno_Diario'].mean()
    desv_est = df_data['Retorno_Diario'].std() * volatilidad_extra
    
    # Matriz de simulaciones (dias x simulaciones)
    np.random.seed(100)
    retornos_simulados = np.random.normal(media_retorno, desv_est, (dias_proyeccion, num_simulaciones))
    trayectorias = ultimo_valor * np.cumprod(1 + retornos_simulados, axis=0)
    
    # Crear DataFrame para Plotly
    df_trayectorias = pd.DataFrame(trayectorias)
    df_trayectorias['Dia'] = range(dias_proyeccion)
    df_melted = df_trayectorias.melt(id_vars=['Dia'], var_name='Simulacion', value_name='Valor')

    # Gráfico de líneas interactivas con Plotly
    fig_mc = px.line(
        df_melted, 
        x='Dia', 
        y='Valor', 
        color='Simulacion',
        title=f"Proyección Estocástica a {dias_proyeccion} Días ({num_simulaciones} escenarios)",
        template="plotly_dark"
    )
    fig_mc.update_layout(showlegend=False, xaxis_title="Días Futuros", yaxis_title="Valor Proyectado ($)")
    st.plotly_chart(fig_mc, use_container_width=True)

    # Métricas de riesgo de los resultados simulados
    valores_finales = trayectorias[-1, :]
    st.subheader("📊 Análisis de Riesgo del Resultado Final")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Valor Esperado (Media)", f"${np.mean(valores_finales):,.2f}")
    with m2:
        st.metric("Peor Escenario (VaR 95%)", f"${np.percentile(valores_finales, 5):,.2f}")
    with m3:
        st.metric("Mejor Escenario (Percentil 95)", f"${np.percentile(valores_finales, 95):,.2f}")

# ---------------------------------------------------------
# MÓDULO 2: ANÁLISIS DE VOLATILIDAD Y TENDENCIAS
# ---------------------------------------------------------
elif modulo == "📊 Análisis de Volatilidad y Tendencias":
    st.title("📊 Análisis de Series Temporales y Bandas Móviles")
    st.markdown("Descomposición analítica de tendencias mediante medias móviles ponderadas y cálculo de bandas de volatilidad con Pandas.")

    # Controles de ventana
    ventana = st.slider("Ventana de Media Móvil (Días):", 5, 60, 20)

    # Procesamiento con Pandas
    df_analisis = df_data.copy()
    df_analisis['Media_Movil'] = df_analisis['Activo_Alpha'].rolling(window=ventana).mean()
    df_analisis['Banda_Superior'] = df_analisis['Media_Movil'] + (df_analisis['Activo_Alpha'].rolling(window=ventana).std() * 2)
    df_analisis['Banda_Inferior'] = df_analisis['Media_Movil'] - (df_analisis['Activo_Alpha'].rolling(window=ventana).std() * 2)

    # Gráfico avanzado con Plotly Graph Objects
    fig_vol = go.Figure()
    fig_vol.add_trace(go.Scatter(x=df_analisis['Fecha'], y=df_analisis['Activo_Alpha'], name='Precio Real', line=dict(color='#38bdf8', width=1.5)))
    fig_vol.add_trace(go.Scatter(x=df_analisis['Fecha'], y=df_analisis['Media_Movil'], name=f'Media Móvil ({ventana}d)', line=dict(color='#facc15', width=2)))
    fig_vol.add_trace(go.Scatter(x=df_analisis['Fecha'], y=df_analisis['Banda_Superior'], name='Banda Superior (+2σ)', line=dict(color='rgba(255,255,255,0.2)', width=1), fill=None))
    fig_vol.add_trace(go.Scatter(x=df_analisis['Fecha'], y=df_analisis['Banda_Inferior'], name='Banda Inferior (-2σ)', line=dict(color='rgba(255,255,255,0.2)', width=1), fill='tonexty', fillcolor='rgba(56, 189, 248, 0.05'))

    fig_vol.update_layout(
        title="Bandas de Volatilidad y Tendencia Histórica",
        template="plotly_dark",
        xaxis_title="Fecha",
        yaxis_title="Precio / Valor"
    )
    st.plotly_chart(fig_vol, use_container_width=True)

# ---------------------------------------------------------
# MÓDULO 3: MATRIZ DE CORRELACIÓN Y DISTRIBUCIÓN
# ---------------------------------------------------------
elif modulo == "📉 Matriz de Correlación y Distribución":
    st.title("📉 Analítica Multivariada y Correlaciones")
    st.markdown("Evaluación estadística de la relación entre variables cuantitativas utilizando matrices de correlación de Pearson.")

    col_m1, col_m2 = st.columns(2)

    with col_m1:
        st.subheader("Matriz de Correlación (Pearson)")
        # Calcular correlación con pandas
        df_corr = df_data[['Activo_Alpha', 'Activo_Beta', 'Volumen_Transaccional', 'Retorno_Diario']].corr()
        
        fig_corr = px.imshow(
            df_corr,
            text_auto=True,
            color_continuous_scale="Blues",
            template="plotly_dark"
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    with col_m2:
        st.subheader("Distribución de Retornos Diarios")
        fig_hist = px.histogram(
            df_data, 
            x="Retorno_Diario", 
            nbins=40, 
            title="Histograma de Densidad de Retornos",
            template="plotly_dark",
            color_discrete_sequence=['#38bdf8']
        )
        st.plotly_chart(fig_hist, use_container_width=True)

# ---------------------------------------------------------
# PIE DE PÁGINA
# ---------------------------------------------------------
st.markdown("---")
st.caption("QuantLab Analytics | Desarrollado con Pandas, NumPy, Plotly y Streamlit | 2026")
