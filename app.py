import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA Y ESTILO SOC DARK
# ---------------------------------------------------------
st.set_page_config(
    page_title="CyberGuard SOC - Centro de Operaciones",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo visual estilo Centro de Comando Ciberseguridad (Dark Theme con acentos de alerta)
st.markdown("""
    <style>
    .stApp {
        background-color: #030712;
        color: #f3f4f6;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #06b6d4;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Courier New', Courier, monospace;
    }
    .stButton>button {
        background: #0e7490;
        color: #ffffff;
        font-weight: bold;
        border-radius: 4px;
        border: 1px solid #22d3ee;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: #155e75;
        box-shadow: 0px 0px 10px #22d3ee;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# GENERACIÓN DE DATOS DE TELEMETRÍA Y LOGS DE RED (SIMULACIÓN)
# ---------------------------------------------------------
@st.cache_data
def generar_logs_red(n_registros=1500):
    np.random.seed(42)
    ips_origen = [f"192.168.1.{np.randint(2, 250)}" if np.random.rand() > 0.3 else f"{np.randint(45, 200)}.{np.randint(10, 250)}.{np.randint(1, 255)}.{np.randint(1, 255)}" for _ in range(n_registros)]
    puertos = np.random.choice([80, 443, 22, 21, 3389, 8080, 53], size=n_registros, p=[0.4, 0.3, 0.1, 0.05, 0.05, 0.05, 0.05])
    protocolos = np.random.choice(['TCP', 'UDP', 'ICMP', 'HTTPS'], size=n_registros, p=[0.5, 0.2, 0.1, 0.2])
    
    severidades = np.random.choice(['Baja', 'Media', 'Alta', 'Crítica'], size=n_registros, p=[0.6, 0.25, 0.1, 0.05])
    
    # Calcular latencia y bytes transferidos
    bytes_tx = np.random.exponential(scale=1500, size=n_registros).astype(int)
    
    fechas = [datetime.now() - timedelta(minutes=int(x)) for x in np.random.randint(0, 1440, size=n_registros)]
    
    df = pd.DataFrame({
        'Timestamp': fechas,
        'IP_Origen': ips_origen,
        'Puerto_Destino': puertos,
        'Protocolo': protocolos,
        'Severidad': severidades,
        'Bytes': bytes_tx,
        'Estado': np.random.choice(['Bloqueado', 'Permitido', 'Inspeccionando'], size=n_registros, p=[0.2, 0.7, 0.1])
    })
    return df.sort_values(by='Timestamp', ascending=False).reset_index(drop=True)

if 'logs' not in st.session_state:
    st.session_state.logs = generar_logs_red()

if 'ips_bloqueadas' not in st.session_state:
    st.session_state.ips_bloqueadas = ["185.220.101.5", "45.154.255.8"]

# ---------------------------------------------------------
# BARRA LATERAL DE CONTROL SOC
# ---------------------------------------------------------
st.sidebar.title("🛡️ CYBERGUARD SOC")
st.sidebar.caption("Centro de Monitoreo e Inteligencia de Amenazas")
st.sidebar.markdown("---")

modulo_soc = st.sidebar.radio(
    "Módulos Operativos:",
    [
        "🚨 Panel de Incidentes y KPIs", 
        "🔍 Análisis de Tráfico de Red", 
        "🧱 Firewall y Bloqueo de IPs", 
        "🤖 Detección de Anomalías (ML)",
        "📋 Auditoría de Logs en Vivo"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("🔒 **Estado del Sistema:** Perímetro asegurado. IDS/IPS Activo.")

df_logs = st.session_state.logs

# ---------------------------------------------------------
# MÓDULO 1: PANEL DE INCIDENTES Y KPIS
# ---------------------------------------------------------
if modulo_soc == "🚨 Panel de Incidentes y KPIs":
    st.title("🚨 Centro de Mando: Incidentes de Seguridad")
    st.markdown("Monitoreo en tiempo real de eventos de red, alertas críticas e indicadores clave de rendimiento (KPIs) del SOC.")

    # Métricas principales
    total_eventos = len(df_logs)
    incidentes_criticos = len(df_logs[df_logs['Severidad'] == 'Crítica'])
    ips_activas = df_logs['IP_Origen'].nunique()
    paquetes_bloqueados = len(df_logs[df_logs['Estado'] == 'Bloqueado'])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Eventos Registrados", f"{total_eventos:,}")
    with c2:
        st.metric("Alertas Críticas", f"{incidentes_criticos}", delta=f"+{int(incidentes_criticos*0.1)}%", delta_color="inverse")
    with c3:
        st.metric("IPs Únicas Monitoreadas", f"{ips_activas}")
    with c4:
        st.metric("Ataques Bloqueados (IPS)", f"{paquetes_bloqueados}")

    st.markdown("---")

    # Gráficos analíticos de incidentes
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("Distribución de Severidad de Alertas")
        df_sev = df_logs['Severidad'].value_counts().reset_index()
        df_sev.columns = ['Severidad', 'Cantidad']
        fig_sev = px.pie(
            df_sev, 
            values='Cantidad', 
            names='Severidad', 
            hole=0.5,
            color='Severidad',
            color_discrete_map={'Baja':'#38bdf8', 'Media':'#facc15', 'Alta':'#fb923c', 'Crítica':'#ef4444'},
            template="plotly_dark"
        )
        st.plotly_chart(fig_sev, use_container_width=True)

    with col_g2:
        st.subheader("Eventos de Red por Protocolo")
        df_proto = df_logs['Protocolo'].value_counts().reset_index()
        df_proto.columns = ['Protocolo', 'Conteo']
        fig_proto = px.bar(
            df_proto, 
            x='Protocolo', 
            y='Conteo', 
            color='Protocolo',
            template="plotly_dark",
            color_discrete_sequence=['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899']
        )
        st.plotly_chart(fig_proto, use_container_width=True)

# ---------------------------------------------------------
# MÓDULO 2: ANÁLISIS DE TRÁFICO DE RED
# ---------------------------------------------------------
elif modulo_soc == "🔍 Análisis de Tráfico de Red":
    st.title("🔍 Análisis Profundo de Tráfico y Ancho de Banda")
    st.markdown("Inspección de flujos de datos, puertos de destino y volumen de transferencia en la red corporativa.")

    # Agrupar por puerto
    df_puertos = df_logs.groupby('Puerto_Destino')['Bytes'].sum().reset_index()
    df_puertos['Puerto_Destino'] = df_puertos['Puerto_Destino'].astype(str)

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Transferencia de Bytes por Puerto")
        fig_bytes = px.bar(
            df_puertos, 
            x='Puerto_Destino', 
            y='Bytes', 
            title="Volumen de Bytes por Puerto de Destino",
            template="plotly_dark",
            color='Bytes',
            color_continuous_scale="Tealgrn"
        )
        st.plotly_chart(fig_bytes, use_container_width=True)

    with c2:
        st.subheader("Estado de las Solicitudes de Red")
        df_estado = df_logs['Estado'].value_counts().reset_index()
        df_estado.columns = ['Estado', 'Total']
        fig_est = px.pie(
            df_estado, 
            names='Estado', 
            values='Total', 
            template="plotly_dark",
            color_discrete_sequence=['#ef4444', '#10b981', '#f59e0b']
        )
        st.plotly_chart(fig_est, use_container_width=True)

# ---------------------------------------------------------
# MÓDULO 3: FIREWALL Y BLOQUEO DE IPS
# ---------------------------------------------------------
elif modulo_soc == "🧱 Firewall y Bloqueo de IPs":
    st.title("🧱 Gestión de Perímetro y Reglas de Firewall")
    st.markdown("Administra la lista negra de direcciones IP y aplica bloqueos automáticos en el perímetro de la red.")

    st.subheader("Listado Actual de IPs Bloqueadas (Blacklist)")
    
    # Mostrar tabla de IPs bloqueadas
    df_bloq = pd.DataFrame({"IP Bloqueada": st.session_state.ips_bloqueadas, "Motivo": ["Intrusión SSH (Brute Force)", "Escaneo de Puertos Nmap"]})
    st.dataframe(df_bloq, use_container_width=True)

    st.markdown("---")
    st.subheader("Agregar Nueva IP a la Lista Negra")
    
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        nueva_ip = st.text_input("Dirección IP a bloquear:", placeholder="Ej: 190.12.45.88")
    with col_f2:
        st.write("")
        st.write("")
        btn_bloquear = st.button("Bloquear IP Inmediatamente")

    if btn_bloquear and nueva_ip:
        if nueva_ip not in st.session_state.ips_bloqueadas:
            st.session_state.ips_bloqueadas.append(nueva_ip)
            # Actualizar estado en los logs simulados
            st.session_state.logs.loc[st.session_state.logs['IP_Origen'] == nueva_ip, 'Estado'] = 'Bloqueado'
            st.success(f"⚠️ IP {nueva_ip} añadida a la blacklist y bloqueada con éxito.")
            st.rerun()
        else:
            st.warning("Esta IP ya se encuentra bloqueada.")

# ---------------------------------------------------------
# MÓDULO 4: DETECCIÓN DE ANOMALÍAS (ML)
# ---------------------------------------------------------
elif modulo_soc == "🤖 Detección de Anomalías (ML)":
    st.title("🤖 Detección de Anomalías con Scikit-Learn y Pandas")
    st.markdown("Motor heurístico automatizado para identificar comportamientos inusuales en las transferencias de datos y posibles exfiltraciones.")

    # Análisis estadístico con NumPy
    bytes_media = df_logs['Bytes'].mean()
    bytes_std = df_logs['Bytes'].std()
    
    # Umbral de anomalía (Z-Score > 2.5)
    df_logs['Z_Score'] = (df_logs['Bytes'] - bytes_media) / bytes_std
    anomalias = df_logs[df_logs['Z_Score'] > 2.5]

    st.metric("Total de Anomalías Detectadas por Volumen", f"{len(anomalias)}")

    st.subheader("Eventos Clasificados como Anomalías de Red")
    if not anomalias.empty:
        st.dataframe(anomalias[['Timestamp', 'IP_Origen', 'Puerto_Destino', 'Bytes', 'Z_Score', 'Severidad']], use_container_width=True)
    else:
        st.info("No se han detectado anomalías de volumen en la ventana de tiempo actual.")

    # Gráfico de dispersión de anomalías
    fig_anom = px.scatter(
        df_logs, 
        x='Timestamp', 
        y='Bytes', 
        color=df_logs['Z_Score'] > 2.5,
        title="Detección de Valores Atípicos (Outliers de Tráfico)",
        template="plotly_dark",
        labels={'color': '¿Es Anomalía?'}
    )
    st.plotly_chart(fig_anom, use_container_width=True)

# ---------------------------------------------------------
# MÓDULO 5: AUDITORÍA DE LOGS EN VIVO
# ---------------------------------------------------------
elif modulo_soc == "📋 Auditoría de Logs en Vivo":
    st.title("📋 Visor General de Registros y Auditoría SOC")
    st.markdown("Consulta en crudo de la telemetría recolectada por los sensores de red.")

    # Filtros interactivos
    f_severidad = st.selectbox("Filtrar por Severidad:", ["Todas", "Baja", "Media", "Alta", "Crítica"])
    
    df_filtrado = df_logs.copy()
    if f_severidad != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Severidad'] == f_severidad]

    st.dataframe(df_filtrado, use_container_width=True)

    # Botón de descarga de reporte de seguridad
    csv_reporte = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exportar Reporte de Incidentes (CSV)",
        data=csv_reporte,
        file_name="reporte_incidentes_soc.csv",
        mime="text/csv"
    )

# ---------------------------------------------------------
# PIE DE PÁGINA DEL SISTEMA SOC
# ---------------------------------------------------------
st.markdown("---")
st.caption("CyberGuard SOC Operations Center | Infraestructura Protegida con Streamlit, Pandas, NumPy y Plotly | 2026")
