import numpy as np
import pandas as pd
import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="PorcinoMetrics | Engorda Porcina", page_icon="🐖", layout="wide"
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #1f4e78;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #595959;
    }
    .creator-tag {
        font-style: italic;
        color: #2e7d32;
        font-weight: bold;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- ENCABEZADO Y CRÉDITOS ---
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.markdown("<h1>🐖📊</h1>", unsafe_allow_html=True)
with col_title:
    st.markdown(
        '<p class="main-header">PorcinoMetrics: Módulo de Engorda Porcina</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="sub-header">"Nutrición de precisión y control ambiental para la máxima eficiencia zootécnica"</p>',
        unsafe_allow_html=True,
    )

st.markdown("---")
st.markdown(
    '<p class="creator-tag">Creado y desarrollado por el Dr. Alejandro Castañeda Correa</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# --- BARRA LATERAL: PARÁMETROS DE ENTRADA ---
st.sidebar.header("🎛️ Parámetros del Lote y Ambientales")

# 1. Etapa Productiva
etapa = st.sidebar.selectbox(
    "Etapa Productiva", ["Iniciación", "Desarrollo y Crecimiento", "Finalización"]
)

# 2. Variables de Raza y Genética
raza = st.sidebar.selectbox(
    "Perfil Genético / Raza",
    [
        "Comercial / Híbrido (Yorkshire x Landrace x Duroc)",
        "Línea Materna (Landrace / Large White)",
        "Línea Paterna (Duroc / Pietrain)",
    ],
)

# 3. Variables Ambientales y Estrés Térmico
st.sidebar.subheader("🌡️ Ambiente y Estrés Térmico")
temp_amb = st.sidebar.slider(
    "Temperatura Ambiental Promedio (°C)", 10.0, 38.0, 24.0, 0.5
)
humedad = st.sidebar.slider("Humedad Relativa (%)", 30.0, 90.0, 65.0, 5.0)

# 4. Datos del Lote
peso_inicial = st.sidebar.number_input(
    "Peso Inicial Promedio (kg)",
    min_value=7.0,
    max_value=110.0,
    value=(
        15.0
        if etapa == "Iniciación"
        else (35.0 if etapa == "Desarrollo y Crecimiento" else 70.0)
    ),
)
peso_objetivo = st.sidebar.number_input(
    "Peso Objetivo / Salida (kg)",
    min_value=10.0,
    max_value=130.0,
    value=(
        35.0
        if etapa == "Iniciación"
        else (70.0 if etapa == "Desarrollo y Crecimiento" else 115.0)
    ),
)
num_animales = st.sidebar.number_input(
    "Número de Animales en el Lote", min_value=1, max_value=2000, value=100
)

# --- MODELO DE CÁLCULO Y AJUSTE POR ESTRÉS TÉRMICO ---

# Rango de confort térmico según etapa
if etapa == "Iniciación":
    temp_optima = 24.0
    base_gdp = 0.65  # Ganancia Diaria de Peso base (kg/día)
    base_ca = 1.55  # Conversión Alimenticia base
    base_pc = 21.0  # Proteína Cruda sugerida (%)
    base_em = 3300  # Energía Metabolizable (kcal/kg)
elif etapa == "Desarrollo y Crecimiento":
    temp_optima = 20.0
    base_gdp = 0.90
    base_ca = 2.30
    base_pc = 17.5
    base_em = 3200
else:  # Finalización
    temp_optima = 18.0
    base_gdp = 1.05
    base_ca = 2.85
    base_pc = 14.5
    base_em = 3100

# Cálculo del factor de estrés térmico (reducción de consumo y ganancia por calor)
diff_temp = temp_amb - temp_optima
factor_estres = 1.0

if diff_temp > 2.0:
    # Estrés calórico: disminuye consumo de alimento y tasa de crecimiento
    factor_estres = max(0.70, 1.0 - ((diff_temp - 2.0) * 0.03))
elif diff_temp < -3.0:
    # Estrés por frío: aumenta requerimiento de energía de mantenimiento
    factor_estres = max(0.85, 1.0 - (abs(diff_temp + 3.0) * 0.015))

# Ajustes genéticos en parámetros
if "Paterna" in raza:
    base_gdp *= 1.08
    base_ca *= 0.95  # Mejor conversión
elif "Materna" in raza:
    base_gdp *= 0.96

# Resultados ajustados
gdp_ajustada = base_gdp * factor_estres
ca_ajustada = base_ca / factor_estres
dias_estudio = max(
    1, round((peso_objetivo - peso_inicial) / max(0.1, gdp_ajustada))
)
consumo_diario_estimado = (
    gdp_ajustada * ca_ajustada
)  # kg de alimento por cerdo/día
consumo_total_lote = consumo_diario_estimado * dias_estudio * num_animales

# --- CUERPO PRINCIPAL DE LA APLICACIÓN ---

st.markdown(f"### 📋 Resultados de Modelación para Etapa: **{etapa}**")

# Métricas Principales en Columnas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Ganancia Diaria (GDP)",
        value=f"{gdp_ajustada:.2f} kg/día",
        delta=f"{((gdp_ajustada - base_gdp)/base_gdp)*100:.1f}% por ambiente",
    )

with col2:
    st.metric(
        label="Conversión Alimenticia (CA)",
        value=f"{ca_ajustada:.2f}",
        delta=f"{((ca_ajustada - base_ca)/base_ca)*100:.1f}%",
        delta_color="inverse",
    )

with col3:
    st.metric(label="Duración Estimada Etapa", value=f"{dias_estudio} días")

with col4:
    st.metric(
        label="Consumo Diario / Cerdo",
        value=f"{consumo_diario_estimado:.2f} kg",
    )

st.markdown("---")

# --- SECCIÓN DE REQUERIMIENTOS NUTRICIONALES Y DIAGNÓSTICO AMBIENTAL ---
col_nutri, col_amb = st.columns(2)

with col_nutri:
    st.subheader("🧬 Especificaciones Nutricionales Sugeridas")
    sacos_totales = round(consumo_total_lote / 40)
    st.info(
        f"""
    * **Proteína Cruda (PC):** {base_pc:.1f} %
    * **Energía Metabolizable (EM):** {base_em} kcal/kg
    * **Consumo Total de Alimento por Lote:** {consumo_total_lote:,.1f} kg
    * **Cantidad Total de Sacos (40 kg):** {sacos_totales} sacos
    """
    )

with col_amb:
    st.subheader("🌡️ Diagnóstico de Confort y Estrés Térmico")
    if diff_temp > 3.0:
        st.warning(
            f"⚠️ **Alerta de Estrés Calórico:** La temperatura ({temp_amb}°C) supera la zona de confort ({temp_optima}°C). Se espera reducción en el consumo y eficiencia. Se recomienda aumentar densidad energética de la dieta o activar ventilación/nebulización."
        )
    elif diff_temp < -3.0:
        st.info(
            f"❄️ **Alerta de Estrés por Frío:** Temperatura baja ({temp_amb}°C). Los animales incrementarán su consumo para termorregulación, elevando la conversión."
        )
    else:
        st.success(
            "✅ **Zona de Confort Óptima:** Las condiciones ambientales favorecen el desempeño zootécnico esperado."
        )

# --- TABLA DE PROYECCIÓN DE CRECIMIENTO ---
st.markdown("---")
st.subheader("📈 Proyección de Crecimiento del Lote")

# Generar datos simulados semana a semana
semanas = np.arange(1, dias_estudio + 1, 7)
pesos_proyectados = [
    min(peso_objetivo, peso_inicial + (gdp_ajustada * d)) for d in semanas
]

df_proyeccion = pd.DataFrame(
    {
        "Día": semanas,
        "Peso Promedio Proyectado (kg)": [round(p, 2) for p in pesos_proyectados],
        "Consumo Acumulado por Animal (kg)": [
            round(consumo_diario_estimado * d, 2) for d in semanas
        ],
    }
)

st.line_chart(
    df_proyeccion.set_index("Día"),
    y=["Peso Promedio Proyectado (kg)"],
    color=["#1f4e78"],
)

st.markdown("---")
st.caption(
    "PorcinoMetrics v1.0 | Creado y desarrollado por el Dr. Alejandro Castañeda Correa"
)
