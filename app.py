import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA Y ESTILO CLÍNICO/MÉDICO
# ---------------------------------------------------------
st.set_page_config(
    page_title="CardioPredict 360 - Evaluación de Riesgo Cardíaco",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo visual clínico en tono oscuro y acentos rojos/azules
st.markdown("""
    <style>
    .stApp {
        background-color: #0b132b;
        color: #e0e6ed;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #ff4d6d;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        background: #c1121f;
        color: #ffffff;
        font-weight: bold;
        border-radius: 6px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: #780000;
        box-shadow: 0px 0px 10px #ff4d6d;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNCIÓN MATEMÁTICA DE PREDICCIÓN (MODELO DE RIESGO)
# ---------------------------------------------------------
def calcular_riesgo_cardiaco(edad, sexo, presion, colesterol, hdl, max_hr, fumador, diabetes):
    """
    Simulación de una función lógica/algoritmo Framingham de riesgo cardiovascular.
    Retorna la probabilidad (0-1) y la categoría de riesgo.
    """
    # Coeficientes base ajustados
    p_base = -5.0
    
    # Impacto de edad y sexo
    p_base += (edad * 0.04)
    if sexo == "Masculino":
        p_base += 0.35
        
    # Presión arterial y colesterol
    p_base += ((presion - 120) * 0.025) if presion > 120 else 0
    p_base += ((colesterol - 200) * 0.015) if colesterol > 200 else 0
    p_base -= ((hdl - 50) * 0.02) # HDL es protector
    
    # Frecuencia cardíaca máxima (menor capacidad = mayor riesgo)
    p_base += ((180 - max_hr) * 0.015) if max_hr < 180 else 0
    
    # Estilo de vida y comorbilidades
    if fumador:
        p_base += 0.65
    if diabetes:
        p_base += 0.80
        
    # Función sigmoide para convertir a probabilidad [0, 1]
    probabilidad = 1 / (1 + np.exp(-p_base))
    return probabilidad

# ---------------------------------------------------------
# GENERACIÓN DE BASE DE DATOS SINTÉTICA PARA ANÁLISIS
# ---------------------------------------------------------
@st.cache_data
def generar_dataset_pacientes(n=1000):
    np.random.seed(42)
    edades = np.random.randint(30, 80, size=n)
    sexos = np.random.choice(["Masculino", "Femenino"], size=n)
    presiones = np.random.normal(130, 20, size=n).astype(int)
    colesteroles = np.random.normal(210, 35, size=n).astype(int)
    hdls = np.random.normal(50, 12, size=n).astype(int)
    max_hrs = np.random.normal(150, 22, size=n).astype(int)
    fumadores = np.random.choice([True, False], size=n, p=[0.25, 0.75])
    diabetes_list = np.random.choice([True, False], size=n, p=[0.15, 0.85])
    
    probs = []
    for i in range(n):
        p = calcular_riesgo_cardiaco(
            edades[i], sexos[i], presiones[i], colesteroles[i], 
            hdls[i], max_hrs[i], fumadores[i], diabetes_list[i]
        )
        probs.append(p)
        
    df = pd.DataFrame({
        'Edad': edades,
        'Sexo': sexos,
        'Presion_Sistolica': presiones,
        'Colesterol_Total': colesteroles,
        'HDL': hdls,
        'FC_Max': max_hrs,
        'Fumador': fumadores,
        'Diabetes': diabetes_list,
        'Probabilidad_Riesgo': probs
    })
    
    df['Categoria_Riesgo'] = pd.cut(
        df['Probabilidad_Riesgo'], 
        bins=[-0.1, 0.2, 0.5, 1.0], 
        labels=['Bajo Riesgo', 'Riesgo Moderado', 'Alto Riesgo']
    )
    return df

df_pacientes = generar_dataset_pacientes()

# ---------------------------------------------------------
# BARRA LATERAL Y NAVEGACIÓN
# ---------------------------------------------------------
st.sidebar.title("🫀 CardioPredict 360")
st.sidebar.caption("Sistema de Diagnóstico Predictivo Coronario")
st.sidebar.markdown("---")

modulo = st.sidebar.radio(
    "Selecciona un Módulo:",
    [
        "🩺 Simulador de Evaluación Paciente", 
        "📊 Epidemiología y Población", 
        "🔍 Análisis de Factores de Riesgo",
        "📋 Historial de Expedientes"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("🏥 **Uso Médico:** Herramienta de apoyo a la decisión clínica basada en algoritmos estadísticos de riesgo cardiovascular.")

# ---------------------------------------------------------
# MÓDULO 1: SIMULADOR DE EVALUACIÓN INDIVIDUAL
# ---------------------------------------------------------
if modulo == "🩺 Simulador de Evaluación Paciente":
    st.title("🩺 Evaluador Individual de Riesgo Cardíaco")
    st.markdown("Ingresa las métricas fisiológicas del paciente para predecir el riesgo de sufrir un **evento cardíaco en los próximos 5 años**.")

    col_inputs, col_results = st.columns([1, 1])

    with col_inputs:
        st.subheader("📋 Datos Clínicos del Paciente")
        
        c_edad, c_sexo = st.columns(2)
        with c_edad:
            edad_p = st.number_input("Edad (años):", min_value=18, max_value=95, value=52)
        with c_sexo:
            sexo_p = st.selectbox("Sexo Biológico:", ["Masculino", "Femenino"])
            
        c_pa, c_col = st.columns(2)
        with c_pa:
            presion_p = st.slider("Presión Sistólica (mmHg):", 90, 200, 135)
        with c_col:
            colesterol_p = st.slider("Colesterol Total (mg/dL):", 120, 350, 220)
            
        c_hdl, c_fc = st.columns(2)
        with c_hdl:
            hdl_p = st.slider("Colesterol HDL (mg/dL):", 20, 100, 45)
        with c_fc:
            fc_max_p = st.slider("Frecuencia Cardíaca Máx (BPM):", 80, 210, 145)
            
        st.markdown("**Comorbilidades y Hábitos:**")
        c_fum, c_diab = st.columns(2)
        with c_fum:
            fumador_p = st.checkbox("¿Es Fumador Activo?")
        with c_diab:
            diabetes_p = st.checkbox("¿Diagnóstico de Diabetes?")
            
        btn_evaluar = st.button("Ejecutar Modelo Predictivo", type="primary")

    with col_results:
        st.subheader("🎯 Resultado del Diagnóstico Predictivo")
        
        # Calcular predicción
        prob_riesgo = calcular_riesgo_cardiaco(
            edad_p, sexo_p, presion_p, colesterol_p, hdl_p, fc_max_p, fumador_p, diabetes_p
        )
        pct_riesgo = prob_riesgo * 100

        # Gráfico Gauge / Tacómetro
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = pct_riesgo,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Probabilidad de Evento Cardíaco (%)"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#ffffff"},
                'steps': [
                    {'range': [0, 20], 'color': "#22c55e"},
                    {'range': [20, 50], 'color': "#facc15"},
                    {'range': [50, 100], 'color': "#ef4444"}
                ],
            }
        ))
        fig_gauge.update_layout(paper_bgcolor="#0b132b", font={'color': "#ffffff"}, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

        if pct_riesgo < 20:
            st.success("🟢 **Bajo Riesgo:** Mantener hábitos saludables y revisiones anuales.")
        elif pct_riesgo < 50:
            st.warning("🟡 **Riesgo Moderado:** Se recomienda ajuste de dieta, ejercicio y control de presión arterial.")
        else:
            st.error("🔴 **Alto Riesgo:** Intervención médica sugerida. Monitoreo farmacológico preventivo.")

# ---------------------------------------------------------
# MÓDULO 2: EPIDEMIOLOGÍA Y POBLACIÓN
# ---------------------------------------------------------
elif modulo == "📊 Epidemiología y Población":
    st.title("📊 Análisis Epidemiológico de la Población de Estudio")
    st.markdown("Distribución global de los niveles de riesgo según variables demográficas en la cohorte analizada.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Prevalencia de Categorías de Riesgo")
        df_cat = df_pacientes['Categoria_Riesgo'].value_counts().reset_index()
        df_cat.columns = ['Categoría', 'Total']
        fig_pie = px.pie(
            df_cat, 
            names='Categoría', 
            values='Total', 
            hole=0.4,
            color='Categoría',
            color_discrete_map={'Bajo Riesgo': '#22c55e', 'Riesgo Moderado': '#facc15', 'Alto Riesgo': '#ef4444'},
            template="plotly_dark"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader("Riesgo Promedio por Grupo de Edad")
        df_pacientes['Rango_Edad'] = pd.cut(df_pacientes['Edad'], bins=[20, 40, 60, 80], labels=['20-40', '41-60', '61-80'])
        df_edad_g = df_pacientes.groupby('Rango_Edad')['Probabilidad_Riesgo'].mean().reset_index()
        df_edad_g['Riesgo_%'] = df_edad_g['Probabilidad_Riesgo'] * 100
        
        fig_bar = px.bar(
            df_edad_g, 
            x='Rango_Edad', 
            y='Riesgo_%', 
            color='Riesgo_%',
            color_continuous_scale="Reds",
            template="plotly_dark",
            title="Riesgo Promedio (%) por Rango Etario"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ---------------------------------------------------------
# MÓDULO 3: ANÁLISIS DE FACTORES DE RIESGO
# ---------------------------------------------------------
elif modulo == "🔍 Análisis de Factores de Riesgo":
    st.title("🔍 Correlación entre Factores Clínicos y Riesgo")
    st.markdown("Exploración multivariada para identificar biomarcadores con mayor peso predicitvo.")

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("Presión Arterial vs. Colesterol Total")
        fig_scatter = px.scatter(
            df_pacientes, 
            x='Presion_Sistolica', 
            y='Colesterol_Total', 
            color='Categoria_Riesgo',
            color_discrete_map={'Bajo Riesgo': '#22c55e', 'Riesgo Moderado': '#facc15', 'Alto Riesgo': '#ef4444'},
            template="plotly_dark",
            labels={'Presion_Sistolica': 'Presión Sistólica (mmHg)', 'Colesterol_Total': 'Colesterol (mg/dL)'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_g2:
        st.subheader("Impacto del Tabaquismo y Diabetes")
        df_hab = df_pacientes.groupby(['Fumador', 'Diabetes'])['Probabilidad_Riesgo'].mean().reset_index()
        df_hab['Riesgo_%'] = df_hab['Probabilidad_Riesgo'] * 100
        df_hab['Fumador'] = df_hab['Fumador'].map({True: 'Fumador', False: 'No Fumador'})
        df_hab['Diabetes'] = df_hab['Diabetes'].map({True: 'Con Diabetes', False: 'Sin Diabetes'})

        fig_hab = px.bar(
            df_hab, 
            x='Fumador', 
            y='Riesgo_%', 
            color='Diabetes', 
            barmode='group',
            template="plotly_dark"
        )
        st.plotly_chart(fig_hab, use_container_width=True)

# ---------------------------------------------------------
# MÓDULO 4: HISTORIAL DE EXPEDIENTES
# ---------------------------------------------------------
elif modulo == "📋 Historial de Expedientes":
    st.title("📋 Registro de Expedientes y Cohorte de Estudio")
    st.markdown("Exploración de la base de datos anonimizada de pacientes procesados.")

    # Filtros
    filtro_cat = st.selectbox("Filtrar por Categoria de Riesgo:", ["Todas", "Bajo Riesgo", "Riesgo Moderado", "Alto Riesgo"])
    
    df_f = df_pacientes.copy()
    if filtro_cat != "Todas":
        df_f = df_f[df_f['Categoria_Riesgo'] == filtro_cat]

    st.dataframe(df_f, use_container_width=True)

    # Descargar CSV
    csv_exp = df_f.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exportar Base de Datos (CSV)",
        data=csv_exp,
        file_name="pacientes_riesgo_cardiaco.csv",
        mime="text/csv"
    )

# ---------------------------------------------------------
# PIE DE PÁGINA
# ---------------------------------------------------------
st.markdown("---")
st.caption("CardioPredict 360 | Plataforma de Analítica Predictiva de Salud Cardiovascular | Desarrollado con Streamlit, Pandas, NumPy y Plotly | 2026")
