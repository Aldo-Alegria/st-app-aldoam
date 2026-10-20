import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# Configuración de la página
st.set_page_config(
    page_title="Gestor de Finanzas Interactivo",
    page_icon="⚡",
    layout="wide"
)

# Inicializar el estado de sesión
if 'transacciones' not in st.session_state:
    st.session_state.transacciones = [
        {"id": 1, "fecha": date(2026, 10, 1), "tipo": "Ingreso", "categoria": "Salario", "monto": 3500.0, "descripcion": "Pago mensual"},
        {"id": 2, "fecha": date(2026, 10, 5), "tipo": "Gasto", "categoria": "Alimentación", "monto": 250.0, "descripcion": "Supermercado"},
        {"id": 3, "fecha": date(2026, 10, 10), "tipo": "Gasto", "categoria": "Vivienda", "monto": 1200.0, "descripcion": "Alquiler"},
        {"id": 4, "fecha": date(2026, 10, 12), "tipo": "Gasto", "categoria": "Transporte", "monto": 80.0, "descripcion": "Gasolina"}
    ]

if 'presupuesto_limite' not in st.session_state:
    st.session_state.presupuesto_limite = 2000.0

# Título principal
st.title("⚡ Gestor de Finanzas Interactivo y Dinámico")
st.markdown("Administra tus ingresos, gastos y metas presupuestarias en tiempo real.")
st.markdown("---")

# Panel lateral: Configuración y Registro
st.sidebar.header("🎛️ Panel de Control")

# 1. Configuración de Presupuesto
st.sidebar.subheader("🎯 Meta de Presupuesto")
st.session_state.presupuesto_limite = st.sidebar.number_input(
    "Límite de gastos mensual ($):", 
    min_value=100.0, 
    step=100.0, 
    value=st.session_state.presupuesto_limite
)

st.sidebar.markdown("---")

# 2. Formulario de Registro
st.sidebar.subheader("➕ Nuevo Movimiento")
with st.sidebar.form("form_interactivo", clear_on_submit=True):
    tipo = st.selectbox("Tipo:", ["Gasto", "Ingreso"])
    
    if tipo == "Gasto":
        categoria = st.selectbox("Categoría:", ["Alimentación", "Vivienda", "Transporte", "Entretenimiento", "Salud", "Otros"])
    else:
        categoria = st.selectbox("Categoría:", ["Salario", "Inversiones", "Freelance", "Regalos", "Otros"])
        
    monto = st.number_input("Monto ($):", min_value=0.01, step=10.0, value=50.0)
    fecha = st.date_input("Fecha:", value=date.today())
    descripcion = st.text_input("Descripción:")
    
    submitted = st.form_submit_button("Agregar Registro", type="primary")
    
    if submitted:
        nuevo_id = len(st.session_state.transacciones) + 1
        nuevo_registro = {
            "id": nuevo_id,
            "fecha": fecha,
            "tipo": tipo,
            "categoria": categoria,
            "monto": monto,
            "descripcion": descripcion if descripcion else "Sin descripción"
        }
        st.session_state.transacciones.append(nuevo_registro)
        st.sidebar.success("¡Movimiento agregado!")
        st.rerun()

# Convertir a DataFrame
df = pd.DataFrame(st.session_state.transacciones)

if not df.empty:
    # --- FILTROS INTERACTIVOS EN LA BARRA LATERAL ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filtros de Visualización")
    filtro_tipo = st.sidebar.selectbox("Filtrar por tipo:", ["Todos", "Ingreso", "Gasto"])
    
    categorias_disponibles = ["Todas"] + list(df["categoria"].unique())
    filtro_categoria = st.sidebar.selectbox("Filtrar por categoría:", categorias_disponibles)

    # Aplicar filtros
    df_filtrado = df.copy()
    if filtro_tipo != "Todos":
        df_filtrado = df_filtrado[df_filtrado["tipo"] == filtro_tipo]
    if filtro_categoria != "Todas":
        df_filtrado = df_filtrado[df_filtrado["categoria"] == filtro_categoria]

    # --- MÉTRICAS Y PROGRESO ---
    total_ingresos = df[df["tipo"] == "Ingreso"]["monto"].sum()
    total_gastos = df[df["tipo"] == "Gasto"]["monto"].sum()
    balance = total_ingresos - total_gastos

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💵 Ingresos Totales", f"${total_ingresos:,.2f}")
    with col2:
        st.metric("🛒 Gastos Totales", f"${total_gastos:,.2f}", delta=f"-${total_gastos:,.2f}", delta_color="inverse")
    with col3:
        st.metric("💡 Balance Neto", f"${balance:,.2f}")

    # Barra de progreso interactiva para el presupuesto
    st.subheader("📊 Control de Presupuesto de Gastos")
    porcentaje_gasto = min(total_gastos / st.session_state.presupuesto_limite, 1.0)
    st.progress(porcentaje_gasto, text=f"Gastado: ${total_gastos:,.2f} de ${st.session_state.presupuesto_limite:,.2f} ({porcentaje_gasto*100:.1f}%)")
    
    if total_gastos > st.session_state.presupuesto_limite:
        st.error("⚠️ ¡Has superado tu límite de presupuesto establecido!")

    st.markdown("---")

    # --- PESTAÑAS DE CONTENIDO ---
    tab1, tab2, tab3 = st.tabs(["📈 Análisis Gráfico", "📋 Datos Filtrados y Edición", "⚙️ Ajustes del Sistema"])

    with tab1:
        st.subheader("Visualización Dinámica")
        df_gastos = df[df["tipo"] == "Gasto"]
        
        if not df_gastos.empty:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Distribución de Gastos**")
                fig_donut = px.pie(df_gastos, values='monto', names='categoria', hole=0.5)
                st.plotly_chart(fig_donut, use_container_width=True)
            with c2:
                st.markdown("**Gastos por Día**")
                df_g_fecha = df_gastos.groupby("fecha")["monto"].sum().reset_index()
                fig_bar = px.bar(df_g_fecha, x='fecha', y='monto', color_discrete_sequence=['#FF4B4B'])
                st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No hay suficientes datos de gastos para mostrar gráficos.")

    with tab2:
        st.subheader("Tabla Interactiva de Movimientos")
        st.dataframe(df_filtrado.sort_values(by="fecha", ascending=False), use_container_width=True)
        
        # Sección interactiva para eliminar un registro por ID
        st.markdown("### 🗑️ Eliminar un Movimiento")
        ids_disponibles = df["id"].tolist()
        if ids_disponibles:
            id_a_borrar = st.selectbox("Selecciona el ID del registro a eliminar:", ids_disponibles)
            if st.button("Eliminar Registro Seleccionado"):
                st.session_state.transacciones = [t for t in st.session_state.transacciones if t["id"] != id_a_borrar]
                st.success(f"Registro con ID {id_a_borrar} eliminado.")
                st.rerun()

    with tab3:
        st.subheader("Gestión de Base de Datos")
        if st.button("🧹 Restablecer Datos de Fábrica"):
            st.session_state.transacciones = []
            st.rerun()
            
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar Datos a CSV",
            data=csv_data,
            file_name="finanzas_personales.csv",
            mime="text/csv"
        )
else:
    st.info("No hay registros en este momento. Agrega uno nuevo desde el panel lateral.")
