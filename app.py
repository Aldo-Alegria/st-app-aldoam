import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, roc_curve, auc

# ---------------------------------------------------------
# CONFIGURACIÓN Y ESTILO CORPORATIVO AVANZADO
# ---------------------------------------------------------
st.set_page_config(
    page_title="Predictor360 - Analítica Predictiva",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo visual moderno y limpio (modo ejecutivo)
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #0d6efd;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #111827 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        background: #0d6efd;
        color: #ffffff;
        font-weight: bold;
        border-radius: 6px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: #0b5ed7;
        box-shadow: 0px 4px 10px rgba(13, 110, 253, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# GENERACIÓN DE DATOS DE ENTRENAMIENTO (DATASET SIMULADO)
# ---------------------------------------------------------
@st.cache_data
def generar_datos_clientes():
    np.random.seed(42)
    n = 1000
    edad = np.random.randint(18, 70, size=n)
    antiguedad = np.random.randint(1, 10, size=n)
    gasto_mensual = np.random.uniform(20.0, 250.0, size=n)
    soporte_llamadas = np.random.randint(0, 8, size=n)
    contrato_anual = np.random.choice([0, 1], size=n, p=[0.4, 0.6])
    
    # Lógica de probabilidad de churn basada en factores de negocio
    probabilidad = (
        (edad < 25) * 0.2 +
        (soporte_llamadas > 4) * 0.4 +
        (gasto_mensual > 180) * 0.15 -
        (contrato_anual * 0.3) -
        (antiguedad * 0.03) + 0.1
    )
    probabilidad = np.clip(probabilidad, 0, 1)
    churn = np.random.binomial(1, probabilidad)
    
    df = pd.DataFrame({
        'Edad': edad,
        'Antiguedad_Anos': antiguedad,
        'Gasto_Mensual': gasto_mensual,
        'Llamadas_Soporte': soporte_llamadas,
        'Contrato_Anual': contrato_anual,
        'Churn': churn
    })
    return df

df_base = generar_datos_clientes()

# ---------------------------------------------------------
# BARRA LATERAL Y NAVEGACIÓN
# ---------------------------------------------------------
st.sidebar.title("📊 Predictor360")
st.sidebar.caption("Plataforma de Machine Learning y Predicción")
st.sidebar.markdown("---")

seccion = st.sidebar.radio(
    "Selecciona un Módulo:",
    [
        "⚙️ Entrenamiento y Modelo", 
        "🎯 Simulador de Predicción", 
        "📈 Análisis Exploratorio (EDA)", 
        "📋 Evaluación de Rendimiento"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Nota:** Este motor entrena un algoritmo de Random Forest utilizando scikit-learn en tiempo real.")

# ---------------------------------------------------------
# ENTRENAMIENTO DEL MODELO (CACHE / ESTADO)
# ---------------------------------------------------------
X = df_base.drop(columns=['Churn'])
y = df_base['Churn']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entrenar modelo por defecto
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

# ---------------------------------------------------------
# MÓDULO 1: ENTRENAMIENTO Y CONFIGURACIÓN DEL MODELO
# ---------------------------------------------------------
if seccion == "⚙️ Entrenamiento y Modelo":
    st.title("⚙️ Configuración y Entrenamiento del Modelo Predictivo")
    st.markdown("Ajusta los hiperparámetros del algoritmo de clasificación para optimizar la capacidad de predicción.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Parámetros del Algoritmo")
        n_est = st.slider("Número de Árboles (n_estimators):", 10, 300, 100, 10)
        max_d = st.slider("Profundidad Máxima (max_depth):", 2, 20, 5, 1)
        test_size_pct = st.slider("Porcentaje de Datos para Prueba (%):", 10, 40, 20, 5) / 100.0
        
        # Re-entrenar con parámetros personalizados
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=test_size_pct, random_state=42)
        modelo_custom = RandomForestClassifier(n_estimators=n_est, max_depth=max_d, random_state=42)
        modelo_custom.fit(X_tr, y_tr)
        
        y_pred = modelo_custom.predict(X_te)
        acc = accuracy_score(y_te, y_pred)
        prec = precision_score(y_te, y_pred)
        rec = recall_score(y_te, y_pred)
        
        st.success("¡Modelo entrenado con éxito con los nuevos parámetros!")

    with col2:
        st.subheader("Métricas de Validación del Modelo")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Precisión (Accuracy)", f"{acc*100:.1f}%")
        with m2:
            st.metric("Precision Score", f"{prec*100:.1f}%")
        with m3:
            st.metric("Recall Score", f"{rec*100:.1f}%")
            
        st.markdown("### Importancia de las Variables (Feature Importance)")
        importancias = pd.DataFrame({
            'Variable': X.columns,
            'Importancia': modelo_custom.feature_importances_
        }).sort_values(by='Importancia', ascending=True)
        
        fig_imp = px.bar(importancias, x='Importancia', y='Variable', orientation='h', template='plotly_white')
        st.plotly_chart(fig_imp, use_container_width=True)

# ---------------------------------------------------------
# MÓDULO 2: SIMULADOR DE PREDICCIÓN INDIVIDUAL
# ---------------------------------------------------------
elif seccion == "🎯 Simulador de Predicción":
    st.title("🎯 Simulador de Abandono de Clientes (Churn Prediction)")
    st.markdown("Ingresa los datos de un cliente específico para calcular su **probabilidad estimada de cancelación** en tiempo real.")
    
    col_input, col_result = st.columns([1, 1])
    
    with col_input:
        st.subheader("Perfil del Cliente")
        edad_ing = st.slider("Edad:", 18, 80, 35)
        antiguedad_ing = st.slider("Antigüedad (Años):", 1, 10, 3)
        gasto_ing = st.number_input("Gasto Mensual ($):", min_value=10.0, max_value=500.0, value=75.0)
        llamadas_ing = st.slider("Llamadas a Soporte (últimos meses):", 0, 10, 2)
        contrato_ing = st.selectbox("¿Tiene contrato anual?", ["No (Mes a Mes)", "Sí"])
        
        val_contrato = 1 if contrato_ing == "Sí" else 0
        
        btn_predecir = st.button("Ejecutar Predicción", type="primary")

    with col_result:
        st.subheader("Resultado del Análisis Predictivo")
        if btn_predecir:
            # Vector de entrada
            cliente_nuevo = np.array([[edad_ing, antiguedad_ing, gasto_ing, llamadas_ing, val_contrato]])
            probabilidad_churn = modelo.predict_proba(cliente_nuevo)[0][1]
            prediccion = modelo.predict(cliente_nuevo)[0]
            
            # Mostrar resultado visual
            if probabilidad_churn > 0.6:
                st.error(f"⚠️ **Riesgo Alto de Abandono**")
            elif probabilidad_churn > 0.3:
                st.warning(f"⚡ **Riesgo Moderado**")
            else:
                st.success(f"✅ **Cliente Fiel (Bajo Riesgo)**")
                
            st.metric("Probabilidad Estimada de Churn", f"{probabilidad_churn*100:.1f}%")
            
            # Recomendaciones automáticas basadas en el modelo
            st.markdown("### 💡 Acciones Recomendadas:")
            if llamadas_ing > 4:
                st.write("- El cliente registra alta fricción en soporte técnico. Asignar un ejecutivo prioritario.")
            if gasto_ing > 150:
                st.write("- Es un cliente de alto valor. Ofrecerle un descuento por fidelidad o contrato anual.")
            if contrato_ing == "No (Mes a Mes)":
                st.write("- Incentivar la migración a un plan anual con beneficios exclusivos.")
        else:
            st.info("Completa los parámetros del cliente en el panel izquierdo y haz clic en **Ejecutar Predicción**.")

# ---------------------------------------------------------
# MÓDULO 3: ANÁLISIS EXPLORATORIO (EDA)
# ---------------------------------------------------------
elif seccion == "📈 Análisis Exploratorio (EDA)":
    st.title("📈 Análisis Exploratorio de Datos (EDA)")
    st.markdown("Visualiza las correlaciones y comportamientos históricos de la base de datos analizada.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Distribución del Gasto Mensual según Churn**")
        fig_box = px.box(df_base, x='Churn', y='Gasto_Mensual', color='Churn', template='plotly_white', labels={'0': 'Retenido', '1': 'Abandonó'})
        st.plotly_chart(fig_box, use_container_width=True)
        
    with c2:
        st.markdown("**Relación entre Llamadas a Soporte y Abandono**")
        df_soporte = df_base.groupby('Llamadas_Soporte')['Churn'].mean().reset_index()
        fig_line = px.line(df_soporte, x='Llamadas_Soporte', y='Churn', markers=True, template='plotly_white', labels={'Churn': 'Tasa de Abandono'})
        st.plotly_chart(fig_line, use_container_width=True)

# ---------------------------------------------------------
# MÓDULO 4: EVALUACIÓN DE RENDIMIENTO
# ---------------------------------------------------------
elif seccion == "📋 Evaluación de Rendimiento":
    st.title("📋 Matriz de Confusión y Curva ROC")
    st.markdown("Evaluación técnica detallada del desempeño del clasificador en el conjunto de prueba.")
    
    y_pred_full = modelo.predict(X_test)
    y_prob_full = modelo.predict_proba(X_test)[:, 1]
    
    cm = confusion_matrix(y_test, y_pred_full)
    fpr, tpr, _ = roc_curve(y_test, y_prob_full)
    roc_auc = auc(fpr, tpr)
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Matriz de Confusión")
        fig_cm = px.imshow(cm, text_auto=True, color_continuous_scale="Blues", labels=dict(x="Predicción", y="Valor Real", color="Cantidad"))
        st.plotly_chart(fig_cm, use_container_width=True)
        
    with c2:
        st.subheader(f"Curva ROC (AUC = {roc_auc:.3f})")
        fig_roc = px.area(x=fpr, y=tpr, title=f'Curva ROC (AUC={roc_auc:.3f})', labels=dict(x='Tasa de Falsos Positivos', y='Tasa de Verdaderos Positivos'))
        fig_roc.add_shape(type='line', line=dict(dash='dash'), x0=0, x1=1, y0=0, y1=1)
        st.plotly_chart(fig_roc, use_container_width=True)

# ---------------------------------------------------------
# PIE DE PÁGINA
# ---------------------------------------------------------
st.markdown("---")
st.caption("Predictor360 | Plataforma de Analítica Predictiva y Machine Learning | 2026")
