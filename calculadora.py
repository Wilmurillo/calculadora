import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ---------- CONFIGURACIÓN INICIAL ----------
st.set_page_config(
    page_title="Calculadora de Presupuesto Universitario",
    page_icon="💰",
    layout="wide"
)

# ---------- FUNCIONES ----------
def agregar_gasto(categoria, descripcion, monto, frecuencia):
    """Agrega un nuevo gasto a la tabla"""
    if monto <= 0:
        st.warning("El monto debe ser mayor a 0")
        return False
    
    if categoria.strip() == "":
        st.warning("Debe ingresar una categoría")
        return False
    
    # Calcular gasto mensual según frecuencia
    if frecuencia == "Diario":
        monto_mensual = monto * 30
    elif frecuencia == "Semanal":
        monto_mensual = monto * 4
    elif frecuencia == "Quincenal":
        monto_mensual = monto * 2
    else:  # Mensual
        monto_mensual = monto
    
    nueva_fila = {
        "Categoría": categoria,
        "Descripción": descripcion,
        "Monto": monto,
        "Frecuencia": frecuencia,
        "Monto Mensual": monto_mensual,
        "Fecha": datetime.now().strftime("%Y-%m-%d")
    }
    
    st.session_state.gastos = pd.concat(
        [st.session_state.gastos, pd.DataFrame([nueva_fila])],
        ignore_index=True
    )
    return True

def calcular_balance(ingresos_totales, gastos_totales):
    """Calcula el balance y devuelve análisis"""
    balance = ingresos_totales - gastos_totales
    porcentaje_gasto = (gastos_totales / ingresos_totales * 100) if ingresos_totales > 0 else 100
    
    # Análisis de la situación financiera
    if ingresos_totales == 0:
        mensaje = "⚠️ No has registrado ingresos"
        color = "#FF6B6B"
        recomendacion = "Registra tus ingresos para comenzar el análisis"
    elif balance > (ingresos_totales * 0.2):
        mensaje = "✅ Excelente! Tienes un buen margen de ahorro"
        color = "#1DB954"
        recomendacion = "Considera invertir parte de tu ahorro o crear un fondo de emergencia"
    elif balance > 0:
        mensaje = "⚠️ Cuidado! Tu margen de ahorro es ajustado"
        color = "#FFA500"
        recomendacion = "Revisa tus gastos discrecionales para aumentar tu capacidad de ahorro"
    elif balance == 0:
        mensaje = "⚠️ Estás en equilibrio, pero sin capacidad de ahorro"
        color = "#FFA500"
        recomendacion = "Busca formas de aumentar ingresos o reducir gastos menores"
    else:
        mensaje = "❌ Alerta! Estás gastando más de lo que ingresas"
        color = "#FF6B6B"
        recomendacion = "Revisa urgentemente tus gastos y considera reducir costos no esenciales"
    
    return {
        "balance": balance,
        "porcentaje_gasto": porcentaje_gasto,
        "mensaje": mensaje,
        "color": color,
        "recomendacion": recomendacion
    }

# ---------- SESSION STATE ----------
if "gastos" not in st.session_state:
    st.session_state.gastos = pd.DataFrame(
        columns=["Categoría", "Descripción", "Monto", "Frecuencia", "Monto Mensual", "Fecha"]
    )

# ---------- INTERFAZ PRINCIPAL ----------
st.title("💰 Calculadora Inteligente de Presupuesto Universitario")
st.markdown("### Gestiona tus finanzas personales como estudiante")

# Crear columnas para mejor organización
col1, col2 = st.columns([2, 3])

with col1:
    # ---------- SECCIÓN DE INGRESOS ----------
    st.subheader("📥 Ingresos Mensuales")
    
    with st.form("ingresos_form", clear_on_submit=False):
        trabajo = st.number_input(
            "Ingreso por trabajo (mensual)", 
            min_value=0.0, 
            value=0.0,
            format="%.2f",
            help="Ingreso mensual por trabajos o empleo"
        )
        
        apoyo_familiar = st.number_input(
            "Apoyo familiar (mensual)",
            min_value=0.0,
            value=0.0,
            format="%.2f",
            help="Dinero que recibes de tu familia"
        )
        
        becas = st.number_input(
            "Becas o ayudas (mensual)",
            min_value=0.0,
            value=0.0,
            format="%.2f",
            help="Becas estudiantiles o ayudas económicas"
        )
        
        otros_ingresos = st.number_input(
            "Otros ingresos (mensual)",
            min_value=0.0,
            value=0.0,
            format="%.2f",
            help="Ingresos adicionales (trabajos freelance, etc.)"
        )
        
        calcular_ingresos = st.form_submit_button("Calcular Ingresos Totales")
    
    # Calcular ingresos totales
    ingresos_totales = trabajo + apoyo_familiar + becas + otros_ingresos
    
    st.metric(
        label="**Ingresos Totales Mensuales**",
        value=f"${ingresos_totales:,.2f}",
        delta=None
    )
    
    # ---------- SECCIÓN PARA AGREGAR GASTOS ----------
    st.subheader("📤 Registrar Nuevo Gasto")
    
    with st.form("gasto_form", clear_on_submit=True):
        categoria = st.selectbox(
            "Categoría",
            ["Alimentación", "Transporte", "Materiales de Estudio", "Vivienda", 
             "Entretenimiento", "Servicios", "Salud", "Otros"]
        )
        
        descripcion = st.text_input("Descripción del gasto", placeholder="Ej: Comida en la cafetería")
        
        monto = st.number_input("Monto", min_value=0.0, format="%.2f", step=0.5)
        
        frecuencia = st.selectbox(
            "Frecuencia",
            ["Diario", "Semanal", "Quincenal", "Mensual"]
        )
        
        agregar = st.form_submit_button("➕ Agregar Gasto")
    
    if agregar:
        if agregar_gasto(categoria, descripcion, monto, frecuencia):
            st.success(f"Gasto de ${monto:.2f} agregado a {categoria}")
    
    # Botón para eliminar último gasto
    if st.button("🗑️ Eliminar último gasto", use_container_width=True):
        if not st.session_state.gastos.empty:
            st.session_state.gastos = st.session_state.gastos.iloc[:-1]
            st.success("Último gasto eliminado")
            st.rerun()
        else:
            st.warning("No hay gastos para eliminar")

with col2:
    # ---------- TABLA DE GASTOS ----------
    st.subheader("📋 Gastos Registrados")
    
    if not st.session_state.gastos.empty:
        # Formatear la tabla para mejor visualización
        df_display = st.session_state.gastos.copy()
        df_display["Monto"] = df_display["Monto"].apply(lambda x: f"${x:,.2f}")
        df_display["Monto Mensual"] = df_display["Monto Mensual"].apply(lambda x: f"${x:,.2f}")
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Categoría": st.column_config.Column(width="medium"),
                "Descripción": st.column_config.Column(width="large"),
                "Frecuencia": st.column_config.Column(width="small"),
            }
        )
        
        # Mostrar distribución de gastos con gráfico de barras de Streamlit
        if not st.session_state.gastos.empty:
            st.subheader("📊 Distribución de Gastos por Categoría")
            gastos_por_categoria = st.session_state.gastos.groupby("Categoría")["Monto Mensual"].sum()
            
            # Crear gráfico de barras usando Streamlit nativo
            chart_data = pd.DataFrame({
                "Categoría": gastos_por_categoria.index,
                "Monto Mensual": gastos_por_categoria.values
            })
            
            st.bar_chart(chart_data.set_index("Categoría"), use_container_width=True)
    else:
        st.info("No hay gastos registrados. Agrega tu primer gasto usando el formulario a la izquierda.")

# ---------- ANÁLISIS FINANCIERO ----------
st.divider()
st.header("📈 Análisis Financiero Mensual")

if not st.session_state.gastos.empty:
    # Calcular totales
    gastos_totales = st.session_state.gastos["Monto Mensual"].sum()
    
    # Calcular balance y obtener análisis
    analisis = calcular_balance(ingresos_totales, gastos_totales)
    
    # Crear métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="**Ingresos Totales**",
            value=f"${ingresos_totales:,.2f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="**Gastos Totales**",
            value=f"${gastos_totales:,.2f}",
            delta=f"-${gastos_totales:,.2f}" if gastos_totales > 0 else None
        )
    
    with col3:
        st.metric(
            label="**Balance Mensual**",
            value=f"${analisis['balance']:,.2f}",
            delta_color="inverse",
            delta=f"${analisis['balance']:,.2f}"
        )
    
    # Barra de progreso para porcentaje de gasto
    st.subheader("Porcentaje de Ingresos Destinado a Gastos")
    porcentaje = min(analisis['porcentaje_gasto'], 100)
    st.progress(int(porcentaje) / 100, text=f"{porcentaje:.1f}% de tus ingresos se destinan a gastos")
    
    # Mensaje interpretativo con estilo
    st.markdown(f"""
    <div style="background-color:{analisis['color']}20; padding:20px; border-radius:10px; border-left:5px solid {analisis['color']}; margin:20px 0;">
        <h4 style="color:{analisis['color']}; margin-top:0;">{analisis['mensaje']}</h4>
        <p style="color:#333; font-size:16px;"><strong>Recomendación:</strong> {analisis['recomendacion']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ---------- RECOMENDACIONES ESPECÍFICAS ----------
    st.subheader("💡 Recomendaciones Personalizadas")
    
    if not st.session_state.gastos.empty:
        # Análisis por categoría
        gastos_categoria = st.session_state.gastos.groupby("Categoría")["Monto Mensual"].sum()
        
        if not gastos_categoria.empty:
            categoria_mayor = gastos_categoria.idxmax()
            monto_mayor = gastos_categoria.max()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"**Mayor gasto:** {categoria_mayor} (${monto_mayor:,.2f}/mes)")
            
            with col2:
                if analisis['balance'] < 0:
                    st.error(f"**Acción inmediata:** Necesitas reducir gastos en ${abs(analisis['balance']):,.2f}/mes")
                elif monto_mayor > ingresos_totales * 0.4:
                    st.warning(f"**Atención:** Tu gasto en {categoria_mayor} es muy alto ({monto_mayor/ingresos_totales*100:.1f}% de ingresos)")
    
    # ---------- PROYECCIÓN DE AHORRO ----------
    if analisis['balance'] > 0:
        st.subheader("🎯 Proyección de Ahorro")
        
        meses = st.slider(
            "¿En cuántos meses quieres alcanzar tu meta?",
            min_value=1,
            max_value=24,
            value=6,
            help="Selecciona el número de meses para proyectar tu ahorro"
        )
        
        ahorro_mensual = analisis['balance']
        ahorro_total = ahorro_mensual * meses
        
        st.success(f"""
        **Proyección:**
        - Ahorro mensual estimado: **${ahorro_mensual:,.2f}**
        - En **{meses} meses** podrías ahorrar: **${ahorro_total:,.2f}**
        """)
        
        if ahorro_total >= 1000:
            st.balloons()

else:
    st.warning("Agrega algunos gastos para ver el análisis financiero.")

# ---------- INFORMACIÓN ADICIONAL ----------
with st.expander("ℹ️ ¿Cómo usar esta calculadora?"):
    st.markdown("""
    ### Guía de uso:
    
    1. **Registra tus ingresos**: Ingresa todas tus fuentes de ingreso mensual en la sección izquierda
    2. **Agrega tus gastos**: Clasifica cada gasto por categoría y frecuencia
    3. **Analiza tus finanzas**: Revisa el balance y las recomendaciones automáticas
    4. **Toma decisiones**: Usa los insights para ajustar tu presupuesto
    
    ### Consejos para estudiantes:
    - **Prioriza gastos esenciales**: Vivienda, alimentación y materiales de estudio
    - **Reduce gastos discrecionales**: Entretenimiento y comida fuera pueden acumularse
    - **Establece una meta de ahorro**: Aunque sea pequeña, crea el hábito
    - **Revisa semanalmente**: Mantén un control constante de tus gastos
    """)

# ---------- PIE DE PÁGINA ----------
st.divider()
st.caption("Desarrollado para apoyo en decisiones financieras estudiantiles | Calculadora Inteligente de Presupuesto")