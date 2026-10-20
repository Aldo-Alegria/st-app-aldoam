import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from PIL import Image, ImageOps

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA Y ESTILO DARK
# ---------------------------------------------------------
st.set_page_config(
    page_title="Galaxia Visual - Analizador de Imágenes",
    page_icon="🌌",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #0b0d17;
        color: #e0e6ed;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #38bdf8;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Segoe UI', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.title("🌌 Galaxia Visual: Analizador Espectral de Imágenes")
st.markdown("Explora, procesa y analiza componentes cromáticos e histogramas de imágenes espaciales o científicas en tiempo real.")
st.markdown("---")

# ---------------------------------------------------------
# BARRA LATERAL: CONTROLES Y CARGA DE ARCHIVOS
# ---------------------------------------------------------
st.sidebar.header("🎛️ Panel de Control")
opcion_imagen = st.sidebar.selectbox(
    "Selecciona una imagen de muestra:",
    ["Nebulosa de Carina (Simulada)", "Superficie Planetaria", "Cúmulo Estelar"]
)

# Generar imágenes sintéticas científicas de ejemplo con NumPy y PIL
def generar_imagen_sintetica(tipo):
    np.random.seed(42)
    ancho, alto = 400, 400
    x, y = np.meshgrid(np.linspace(-2, 2, ancho), np.linspace(-2, 2, alto))
    
    if tipo == "Nebulosa de Carina (Simulada)":
        z = np.sin(x*3) * np.cos(y*3) + np.sin(x*y)
        arr = ((z - z.min()) / (z.max() - z.min()) * 255).astype(np.uint8)
        img = Image.fromarray(arr).convert("RGB")
        img = ImageOps.colorize(img.convert("L"), black="#0b0d17", white="#ff4b4b")
    elif tipo == "Superficie Planetaria":
        z = np.random.randn(alto, ancho).cumsum(axis=0)
        arr = ((z - z.min()) / (z.max() - z.min()) * 255).astype(np.uint8)
        img = Image.fromarray(arr).convert("RGB")
        img = ImageOps.colorize(img.convert("L"), black="#1e1b4b", white="#38bdf8")
    else:
        z = np.exp(-(x**2 + y**2)*2) * np.sin(x*10)
        arr = ((z - z.min()) / (z.max() - z.min()) * 255).astype(np.uint8)
        img = Image.fromarray(arr).convert("RGB")
        img = ImageOps.colorize(img.convert("L"), black="#000000", white="#facc15")
        
    return img

imagen_actual = generar_imagen_sintetica(opcion_imagen)

# Opción para que el usuario cargue su propia imagen
archivo_subido = st.sidebar.file_uploader("O sube tu propia imagen:", type=["jpg", "png", "jpeg"])
if archivo_subido is not None:
    imagen_actual = Image.open(archivo_subido)

# ---------------------------------------------------------
# LAYOUT PRINCIPAL: VISUALIZACIÓN Y ANALÍTICA
# ---------------------------------------------------------
col_img, col_analisis = st.columns(2)

with col_img:
    st.subheader("🖼️ Vista Previa de la Imagen")
    st.image(imagen_actual, caption="Imagen Activa en el Sistema", use_container_width=True)

with col_analisis:
    st.subheader("📊 Análisis Espectral y Histograma RGB")
    
    # Procesamiento matricial con NumPy
    img_array = np.array(imagen_actual)
    
    if len(img_array.shape) == 3:
        r_channel = img_array[:, :, 0].flatten()
        g_channel = img_array[:, :, 1].flatten()
        b_channel = img_array[:, :, 2].flatten()
        
        # Agrupar datos en un DataFrame para visualización con Plotly
        df_hist = pd.DataFrame({
            'Valor': np.concatenate([r_channel, g_channel, b_channel]),
            'Canal': ['Rojo']*len(r_channel) + ['Verde']*len(g_channel) + ['Azul']*len(b_channel)
        })
        
        fig_hist = px.histogram(
            df_hist, 
            x="Valor", 
            color="Canal", 
            barmode="overlay",
            color_discrete_map={'Rojo': '#ff4b4b', 'Verde': '#22c55e', 'Azul': '#38bdf8'},
            template="plotly_dark",
            title="Distribución de Canales de Color"
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("La imagen seleccionada se encuentra en escala de grises.")

# ---------------------------------------------------------
# MÉTRICAS TÉCNICAS
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📋 Propiedades Técnicas de la Imagen")
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Resolución", f"{imagen_actual.size[0]} x {imagen_actual.size[1]} px")
with m2:
    st.metric("Formato / Modo", imagen_actual.mode)
with m3:
    st.metric("Peso en Memoria", f"{img_array.nbytes / 1024:.1f} KB")

# Pie de página
st.markdown("---")
st.caption("Galaxia Visual | Analizador de Imágenes con Streamlit, NumPy, Pandas y Plotly | 2026")
