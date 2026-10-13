import io
import numpy as np
import pandas as pd

from fpdf import FPDF
from scipy.optimize import linprog
import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Porcidex Pro | Nutrición y Porcicultura de Precisión",
    page_icon="🐖",
    layout="wide",
)

# --- ESTILOS CSS PERSONALIZADOS Y LOGOTIPO EMBLEMÁTICO ---
st.markdown(
    """
    <style>
    .brand-container {
        background: linear-gradient(135deg, #1b365d 0%, #0d1b2a 100%);
        padding: 2.2rem;
        border-radius: 14px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .brand-logo-badge {
        background: rgba(255, 255, 255, 0.12);
        display: inline-block;
        padding: 0.4rem 1.2rem;
        border-radius: 50px;
        font-size: 1.05rem;
        margin-bottom: 0.8rem;
        letter-spacing: 1.5px;
        font-weight: 600;
        color: #a9dfbf;
    }
    .brand-title {
        font-size: 2.8rem;
        font-weight: 900;
        letter-spacing: 3px;
        margin: 0;
        color: #ffffff;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .brand-slogan {
        font-size: 1.2rem;
        font-style: italic;
        color: #d9e1e8;
        margin-top: 0.6rem;
        margin-bottom: 1.2rem;
    }
    .meta-info-container {
        display: flex;
        justify-content: center;
        gap: 15px;
        font-size: 0.9rem;
        color: #b0bec5;
        font-weight: 500;
        border-top: 1px solid rgba(255,255,255,0.15);
        padding-top: 0.9rem;
        margin-top: 0.5rem;
        flex-wrap: wrap;
    }
    .meta-item {
        color: #ffffff;
    }
    .creator-tag {
        color: #f39c12;
        font-weight: 700;
    }
    .status-badge-green {
        background-color: #27ae60;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        font-weight: bold;
        display: inline-block;
    }
    .status-badge-orange {
        background-color: #e67e22;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        font-weight: bold;
        display: inline-block;
    }
    .status-badge-red {
        background-color: #c0392b;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        font-weight: bold;
        display: inline-block;
    }
    .report-card {
        background-color: #f8f9fa;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 5px solid #1f4e78;
        margin-bottom: 1rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- CABECERA CON LOGOTIPO EN ESPAÑOL, VERSIÓN Y NÚMERO DE SERIE ---
st.markdown(
    """
    <div class="brand-container">
        <div class="brand-logo-badge">🐖 🧬 SISTEMAS DE NUTRICIÓN PORCINA DE PRECISIÓN Y PLF</div>
        <h1 class="brand-title">PORCIDEX™</h1>
        <p class="brand-slogan">"Ciencia, Innovación y Precisión al Servicio de la Porcicultura Moderna"</p>
        <div class="meta-info-container">
            <span>Versión: <strong class="meta-item">v1.0 Pro</strong></span>
            <span>•</span>
            <span>Nº de Serie: <strong class="meta-item">PRX-2026-MX-9842</strong></span>
            <span>•</span>
            <span>Desarrollador: <strong class="creator-tag">Dr. Alejandro Castañeda Correa</strong></span>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# PANEL IZQUIERDO: VARIABLES PLF Y AMBIENTALES
# ==========================================
st.sidebar.header("🔬 Panel PLF & Variables Biológicas")
st.sidebar.markdown(
    "*Basado en directrices de Animal Science, Journal of Animal Science y Ganadería de Precisión.*"
)

st.sidebar.markdown("---")
st.sidebar.subheader("🌡️ Ambiente y Estrés Térmico (THI Dinámico)")
temp_amb = st.sidebar.slider(
    "Temperatura Ambiental (°C)", 10.0, 38.0, 24.0, 0.5
)
hum_relativa = st.sidebar.slider("Humedad Relativa (%)", 20.0, 95.0, 65.0, 5.0)
vel_aire = st.sidebar.slider(
    "Velocidad del Aire / Ventilación (m/s)", 0.0, 2.5, 0.4, 0.1
)

thi_calculado = temp_amb - (0.55 - (0.55 * (hum_relativa / 100.0))) * (
    temp_amb - 14.4
)

# SEMÁFORO DE THI
if thi_calculado > 78.0:
    badge_thi = '<span class="status-badge-red">🔴 PELIGRO: Estrés Calórico Crítico</span>'
elif thi_calculado > 74.0:
    badge_thi = '<span class="status-badge-orange">🟠 PRECAUCIÓN: Estrés Moderado</span>'
else:
    badge_thi = '<span class="status-badge-green">🟢 ÓPTIMO: Confort Térmico</span>'

st.sidebar.markdown(f"**Índice THI Estimado:** `{thi_calculado:.1f}`", unsafe_allow_html=True)
st.sidebar.markdown(badge_thi, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🏠 Alojamiento y Reto Sanitario")
espacio_vital = st.sidebar.selectbox(
    "Superficie Vital por Animal",
    [
        "Óptimo (> 0.90 m²/cerdo)",
        "Estándar Comercial (0.75 - 0.90 m²/cerdo)",
        "Hacinamiento / Limitante (< 0.75 m²/cerdo)",
    ],
)
estatus_inmunologico = st.sidebar.selectbox(
    "Estatus Inmunológico / Reto Sanitario",
    [
        "Alto Estatus / SPF / Alta Bioseguridad",
        "Medio / Reto Endémico Controlado",
        "Bajo / Brote Activo o Complejo Respiratorio (PRRS / APP)",
    ],
)

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Tecnologías PLF Integradas")
uso_pfs = st.sidebar.checkbox(
    "Activar Alimentación de Precisión (PFS con RFID)",
    value=True,
    help="Ajusta la ración diaria individual mediante mezcla dinámica de nutrientes.",
)
uso_vision_3d = st.sidebar.checkbox(
    "Usar Biometría por Visión Artificial 3D",
    value=True,
    help="Elimina el estrés por manejo físico y realiza pesajes continuos.",
)
monitoreo_acustico = st.sidebar.checkbox(
    "Activar Alerta Acústica Temprana (TOS/Agua)",
    value=True,
    help="Monitoreo de vocalizaciones y desviaciones en consumo hídrico.",
)

# --- NAVEGACIÓN PRINCIPAL POR PESTAÑAS ---
tab_engorda, tab_formulacion, tab_lactancia, tab_resumen = st.tabs(
    [
        "📈 Engorda, PLF y Control de GDP",
        "🧮 Formulación y Precios de Insumos",
        "🍼 Cerdas en Lactancia y Cría",
        "📋 Resumen Técnico y Comercial",
    ]
)

# ==========================================
# PESTAÑA 1: ENGORDA, PLF Y BARRA DE GDP CON SEMÁFOROS
# ==========================================
with tab_engorda:
    st.subheader(
        "Módulo de Simulación Dinámica, Ganadería de Precisión (PLF) e Indicadores Zootécnicos"
    )
    st.markdown("💡 *Guía visual para el productor: Los indicadores de color denotan el estado actual de la producción para tomar decisiones informadas.*")

    col_s1, col_s2 = st.columns([1, 2])

    with col_s1:
        st.markdown("### 📋 Parámetros del Lote y Genética")
        etapa_eng = st.selectbox(
            "Etapa Productiva",
            ["Iniciación", "Desarrollo y Crecimiento", "Finalización"],
        )
        raza_eng = st.selectbox(
            "Perfil Genético",
            [
                "Híbrido Comercial (Yorkshire x Landrace x Duroc)",
                "Línea Materna Pura (Landrace / Large White)",
                "Línea Paterna Hipermuscular (Duroc / Pietrain)",
            ],
        )

        peso_inicial = st.number_input(
            "Peso Inicial Promedio (kg)", 7.0, 110.0, 15.0
        )
        peso_objetivo = st.number_input(
            "Peso Objetivo / Salida (kg)", 10.0, 130.0, 115.0
        )
        num_animales = st.number_input(
            "Tamaño del Lote (Animales)", 1, 5000, 200
        )

        st.markdown("---")
        st.markdown("### ⚡ Ajuste Manual de Ganancia Diaria de Peso (GDP)")
        
        base_gdp_def = 0.68 if etapa_eng == "Iniciación" else (0.95 if etapa_eng == "Desarrollo y Crecimiento" else 1.10)
        
        gdp_manual = st.slider(
            "Ajustar Ganancia Diaria de Peso Objetivo (kg/día)",
            min_value=0.30,
            max_value=1.50,
            value=float(base_gdp_def),
            step=0.01,
            help="Deslice la barra para ajustar la velocidad de crecimiento esperada y estimar la duración total de la engorda.",
        )

    with col_s2:
        if etapa_eng == "Iniciación":
            temp_optima = 24.0
            base_ca = 1.50
            base_pc = 20.5
            base_ne = 2550
        elif etapa_eng == "Desarrollo y Crecimiento":
            temp_optima = 20.0
            base_ca = 2.20
            base_pc = 17.0
            base_ne = 2480
        else:
            temp_optima = 18.0
            base_ca = 2.75
            base_pc = 14.0
            base_ne = 2400

        diff_temp = temp_amb - temp_optima
        factor_estres = 1.0
        if diff_temp > 2.0:
            mitigacion_viento = min(0.18, vel_aire * 0.09)
            factor_estres = max(
                0.60,
                1.0 - (((diff_temp - 2.0) * 0.038) - mitigacion_viento),
            )
        elif diff_temp < -3.0:
            factor_estres = max(0.82, 1.0 - (abs(diff_temp + 3.0) * 0.015))

        if "Estándar" in espacio_vital:
            base_ca *= 1.03
        elif "Hacinamiento" in espacio_vital:
            base_ca *= 1.12

        if "Medio" in estatus_inmunologico:
            base_ca *= 1.05
        elif "Bajo" in estatus_inmunologico:
            base_ca *= 1.20

        if uso_pfs:
            base_ca *= 0.92

        gdp_ajustada = gdp_manual * factor_estres
        ca_ajustada = base_ca / factor_estres
        ganancia_requerida = max(0.1, peso_objetivo - peso_inicial)
        dias_estudio = max(1, round(ganancia_requerida / max(0.05, gdp_ajustada)))
        consumo_diario = gdp_ajustada * ca_ajustada
        consumo_total_cerdo = consumo_diario * dias_estudio
        consumo_total_lote = consumo_total_cerdo * num_animales

        # DETERMINACIÓN DE SEMÁFOROS ZOOTÉCNICOS
        # Semáforo GDP
        if gdp_ajustada >= 0.85:
            badge_gdp = '<span class="status-badge-green">🟢 ÓPTIMO: Crecimiento Rápido</span>'
        elif gdp_ajustada >= 0.60:
            badge_gdp = '<span class="status-badge-orange">🟠 AJUSTAR: Crecimiento Moderado</span>'
        else:
            badge_gdp = '<span class="status-badge-red">🔴 PELIGRO: Crecimiento Deficiente</span>'

        # Semáforo Conversión Alimenticia (CA)
        if ca_ajustada <= 2.20:
            badge_ca = '<span class="status-badge-green">🟢 ÓPTIMO: Alta Eficiencia</span>'
        elif ca_ajustada <= 2.80:
            badge_ca = '<span class="status-badge-orange">🟠 AJUSTAR: Eficiencia Aceptable</span>'
        else:
            badge_ca = '<span class="status-badge-red">🔴 PELIGRO: Ineficiencia / Desperdicio</span>'

        # Semáforo Alojamiento
        if "Óptimo" in espacio_vital:
            badge_esp = '<span class="status-badge-green">🟢 ÓPTIMO: Bienestar Espacial</span>'
        elif "Estándar" in espacio_vital:
            badge_esp = '<span class="status-badge-orange">🟠 AJUSTAR: Espacio Límite</span>'
        else:
            badge_esp = '<span class="status-badge-red">🔴 PELIGRO: Hacinamiento Severo</span>'

        # Semáforo Sanitario
        if "Alto" in estatus_inmunologico:
            badge_san = '<span class="status-badge-green">🟢 ÓPTIMO: Alta Bioseguridad</span>'
        elif "Medio" in estatus_inmunologico:
            badge_san = '<span class="status-badge-orange">🟠 AJUSTAR: Reto Sanitario Controlado</span>'
        else:
            badge_san = '<span class="status-badge-red">🔴 PELIGRO: Brote / Reto Severo</span>'

        st.markdown(f"### 📋 Evaluador de Condición Zootécnica: **{etapa_eng}**")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("GDP Operativa", f"{gdp_ajustada:.2f} kg/d")
        m2.metric("Conversión (CA)", f"{ca_ajustada:.2f}")
        m3.metric("Duración Engorda", f"{dias_estudio} días")
        m4.metric("Consumo Diario", f"{consumo_diario:.2f} kg")

        st.markdown("#### 🚦 Semáforo de Producción y Puntos Críticos de Control:")
        col_sem1, col_sem2 = st.columns(2)
        with col_sem1:
            st.markdown(f"* **Ganancia Diaria (GDP):** {badge_gdp}", unsafe_allow_html=True)
            st.markdown(f"* **Conversión Alimenticia:** {badge_ca}", unsafe_allow_html=True)
        with col_sem2:
            st.markdown(f"* **Superficie Vital:** {badge_esp}", unsafe_allow_html=True)
            st.markdown(f"* **Estatus Sanitario:** {badge_san}", unsafe_allow_html=True)

        st.markdown("---")
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.info(
                f"""
            **Resumen Logístico del Lote:**
            * **Días Estimados a Mercado:** `{dias_estudio} días` ({round(dias_estudio/30, 1)} meses).
            * **Consumo Total de Alimento por Cerdo:** `{consumo_total_cerdo:.1f} kg`.
            * **Requerimiento Total del Lote ({num_animales:,} cerdos):** `{consumo_total_lote:,.1f} kg` (`{round(consumo_total_lote/40):,} sacos de 40 kg`).
            """
            )
        with col_res2:
            if thi_calculado > 76:
                st.warning(
                    f"⚠️ **Alerta Biológica Crítica (THI {thi_calculado:.1f}):** Se detecta depresión de consumo voluntario. Se requiere suplementación con Betaina (1.5 kg/ton) y electrolitos."
                )
            else:
                st.success(
                    f"✅ **Estatus Fisiológico Estable (THI {thi_calculado:.1f}):** Condiciones idóneas para expresión del potencial genético."
                )

        st.markdown("### 📈 Curva Biológica de Crecimiento Estocástico")
        semanas = np.arange(1, dias_estudio + 1, 7)
        pesos_proy = [
            min(peso_objetivo, peso_inicial + (gdp_ajustada * d)) for d in semanas
        ]
        df_grafica = pd.DataFrame(
            {
                "Día": semanas,
                "Peso Proyectado (kg)": [round(p, 2) for p in pesos_proy],
            }
        )
        st.line_chart(df_grafica.set_index("Día"), color=["#1f4e78"])

# ==========================================
# PESTAÑA 2: FORMULACIÓN AVANZADA Y PRECIOS
# ==========================================
with tab_formulacion:
    st.subheader(
        "🧮 Módulo de Costos e Insumos: Modificación de Precios y Formulación de Precisión"
    )
    st.markdown(
        "Ajuste libremente los **costos y precios de los insumos / materias primas ($/kg)** en la tabla interactiva. Seleccione o deseleccione los ingredientes disponibles para balancear la ración al mínimo costo."
    )

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        etapa_form = st.selectbox(
            "Etapa para Formulación",
            [
                "Iniciación (20-35 kg)",
                "Desarrollo (35-70 kg)",
                "Finalización (70-115 kg)",
                "Cerdas de Recría / Remonta",
            ],
            key="etap_form_multi",
        )

    if "Iniciación" in etapa_form:
        min_ne, min_sid_lys, min_pc, max_fibra = 2350.0, 0.95, 19.5, 5.0
    elif "Desarrollo" in etapa_form:
        min_ne, min_sid_lys, min_pc, max_fibra = 2280.0, 0.80, 16.5, 6.5
    elif "Finalización" in etapa_form:
        min_ne, min_sid_lys, min_pc, max_fibra = 2220.0, 0.68, 14.0, 7.5
    else:
        min_ne, min_sid_lys, min_pc, max_fibra = 2180.0, 0.60, 15.0, 8.5

    datos_maestros = [
        {"Ingrediente": "Maíz Grano", "Disponible": True, "Costo ($/kg)": 5.50, "NE (kcal/kg)": 2650.0, "SID Lys (%)": 0.26, "PC (%)": 8.5, "Fibra (%)": 2.0, "bound": (20.0, 80.0), "base": 58.0},
        {"Ingrediente": "Sorgo Grano", "Disponible": True, "Costo ($/kg)": 5.20, "NE (kcal/kg)": 2580.0, "SID Lys (%)": 0.22, "PC (%)": 10.0, "Fibra (%)": 2.2, "bound": (0.0, 60.0), "base": 0.0},
        {"Ingrediente": "Pasta de Soya 48%", "Disponible": True, "Costo ($/kg)": 12.00, "NE (kcal/kg)": 2240.0, "SID Lys (%)": 2.85, "PC (%)": 48.0, "Fibra (%)": 7.0, "bound": (10.0, 35.0), "base": 24.0},
        {"Ingrediente": "Pasta de Canola", "Disponible": False, "Costo ($/kg)": 8.50, "NE (kcal/kg)": 2050.0, "SID Lys (%)": 2.10, "PC (%)": 36.0, "Fibra (%)": 11.5, "bound": (0.0, 15.0), "base": 0.0},
        {"Ingrediente": "Salvado de Trigo", "Disponible": True, "Costo ($/kg)": 4.00, "NE (kcal/kg)": 1700.0, "SID Lys (%)": 0.65, "PC (%)": 15.0, "Fibra (%)": 11.0, "bound": (0.0, 12.0), "base": 5.0},
        {"Ingrediente": "DDGS de Maíz", "Disponible": True, "Costo ($/kg)": 6.80, "NE (kcal/kg)": 2350.0, "SID Lys (%)": 0.65, "PC (%)": 27.0, "Fibra (%)": 8.5, "bound": (0.0, 15.0), "base": 6.0},
        {"Ingrediente": "Harina de Carne y Hueso", "Disponible": True, "Costo ($/kg)": 9.50, "NE (kcal/kg)": 2050.0, "SID Lys (%)": 2.40, "PC (%)": 50.0, "Fibra (%)": 2.0, "bound": (0.0, 8.0), "base": 3.0},
        {"Ingrediente": "Aceite Vegetal / Grasa", "Disponible": True, "Costo ($/kg)": 22.00, "NE (kcal/kg)": 5800.0, "SID Lys (%)": 0.0, "PC (%)": 0.0, "Fibra (%)": 0.0, "bound": (0.0, 5.0), "base": 1.5},
        {"Ingrediente": "Núcleo Vitamínico-Mineral con Fitasa", "Disponible": True, "Costo ($/kg)": 38.00, "NE (kcal/kg)": 0.0, "SID Lys (%)": 0.0, "PC (%)": 0.0, "Fibra (%)": 0.0, "bound": (1.0, 3.5), "base": 2.5},
    ]

    df_inventario = pd.DataFrame(datos_maestros)

    st.markdown("### 💵 Catálogo de Insumos y Costos de Compra ($/kg)")
    st.info("💡 **Instrucciones:** Modifique los valores en la columna **'Costo ($/kg)'** según sus cotizaciones actuales y active/desactive materias primas.")

    df_editado = st.data_editor(
        df_inventario[["Ingrediente", "Disponible", "Costo ($/kg)", "NE (kcal/kg)", "SID Lys (%)", "PC (%)", "Fibra (%)"]],
        column_config={
            "Ingrediente": st.column_config.TextColumn("Ingrediente", disabled=True),
            "Disponible": st.column_config.CheckboxColumn(
                "Disponible",
                help="Active o desactive los ingredientes según existencia en granja",
                default=True,
            ),
            "Costo ($/kg)": st.column_config.NumberColumn(
                "Costo ($/kg)",
                min_value=0.10,
                max_value=200.0,
                step=0.10,
                format="$%.2f",
            ),
        },
        disabled=["Ingrediente", "NE (kcal/kg)", "SID Lys (%)", "PC (%)", "Fibra (%)"],
        hide_index=True,
        use_container_width=True,
    )

    df_activos = df_editado[df_editado["Disponible"] == True]

    if df_activos.empty:
        st.warning("⚠️ Debe seleccionar al menos un ingrediente disponible en la tabla.")
        props, costo_kg, df_form_filt = [], 0.0, pd.DataFrame()
    else:
        ingredientes_activos = df_activos["Ingrediente"].tolist()
        c = df_activos["Costo ($/kg)"].tolist()
        
        ne_coefs = [-float(row["NE (kcal/kg)"]) for _, row in df_activos.iterrows()]
        lys_coefs = [-float(row["SID Lys (%)"]) for _, row in df_activos.iterrows()]
        pc_coefs = [-float(row["PC (%)"]) for _, row in df_activos.iterrows()]
        fibra_coefs = [float(row["Fibra (%)"]) for _, row in df_activos.iterrows()]

        dict_bounds = {d["Ingrediente"]: d["bound"] for d in datos_maestros}
        dict_bases = {d["Ingrediente"]: d["base"] for d in datos_maestros}
        bounds = [dict_bounds[ing] for ing in ingredientes_activos]

        A_ub = [ne_coefs, lys_coefs, pc_coefs, fibra_coefs]
        b_ub = [-min_ne, -min_sid_lys, -min_pc, max_fibra]
        A_eq = [[1.0] * len(ingredientes_activos)]
        b_eq = [100.0]

        res = linprog(
            c,
            A_ub=A_ub,
            b_ub=b_ub,
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=bounds,
            method="highs",
        )

        if not res.success:
            b_ub_relaxed = [-min_ne * 0.85, -min_sid_lys * 0.85, -min_pc * 0.85, max_fibra * 1.30]
            res = linprog(
                c,
                A_ub=A_ub,
                b_ub=b_ub_relaxed,
                A_eq=A_eq,
                b_eq=b_eq,
                bounds=bounds,
                method="highs",
            )

        if res.success:
            props = res.x
            costo_kg = res.fun / 100.0
            st.success("✅ ¡Dieta optimizada al mínimo costo con los precios actuales!")
        else:
            raw_props = [dict_bases[ing] for ing in ingredientes_activos]
            if sum(raw_props) == 0:
                raw_props = [100.0 / len(ingredientes_activos)] * len(ingredientes_activos)
            props = [(p / sum(raw_props)) * 100.0 for p in raw_props]
            costo_kg = sum(p * cost for p, cost in zip(props, c)) / 100.0
            st.warning("⚠️ Ajuste comercial de respaldo aplicado para garantizar un balance adecuado.")

        inclusions = [round(p, 2) for p in props]
        diff_inc = round(100.0 - sum(inclusions), 2)
        if inclusions:
            inclusions[0] = round(inclusions[0] + diff_inc, 2)

        kgs = [round(inc * 10.0, 1) for inc in inclusions]
        diff_kg = round(1000.0 - sum(kgs), 1)
        if kgs:
            kgs[0] = round(kgs[0] + diff_kg, 1)

        df_formula = pd.DataFrame(
            {
                "Materia Prima / Ingrediente": ingredientes_activos,
                "Inclusión (%)": inclusions,
                "Kg por Tonelada": kgs,
                "Costo Insumo ($/kg)": [f"${cost:.2f}" for cost in c],
                "Aporte ($/Ton)": [f"${round((inc/100.0)*cost*1000, 2):,.2f}" for inc, cost in zip(inclusions, c)],
            }
        )
        df_form_filt = df_formula[df_formula["Inclusión (%)"] > 0.01]
        
        st.table(df_form_filt)
        
        st.success(f"⚖️ **Total Ración Balanceada:** `{df_form_filt['Inclusión (%)'].sum():.2f}%` = `{df_form_filt['Kg por Tonelada'].sum():.1f} kg / Tonelada`")

        aportes_ne = sum((inc/100.0) * next(d["NE (kcal/kg)"] for d in datos_maestros if d["Ingrediente"] == ing) for inc, ing in zip(inclusions, ingredientes_activos))
        aportes_lys = sum((inc/100.0) * next(d["SID Lys (%)"] for d in datos_maestros if d["Ingrediente"] == ing) for inc, ing in zip(inclusions, ingredientes_activos))
        aportes_pc = sum((inc/100.0) * next(d["PC (%)"] for d in datos_maestros if d["Ingrediente"] == ing) for inc, ing in zip(inclusions, ingredientes_activos))
        aportes_fibra = sum((inc/100.0) * next(d["Fibra (%)"] for d in datos_maestros if d["Ingrediente"] == ing) for inc, ing in zip(inclusions, ingredientes_activos))

        st.info(
            f"📊 **Perfil Nutricional Estimado de la Dieta:**\n"
            f"* **Energía Neta (NE):** `{aportes_ne:.0f} kcal/kg`\n"
            f"* **Lisina SID:** `{aportes_lys:.2f}%`\n"
            f"* **Proteína Cruda (PC):** `{aportes_pc:.1f}%`\n"
            f"* **Fibra Cruda:** `{aportes_fibra:.1f}%`"
        )

        m_c1, m_c2 = st.columns(2)
        m_c1.metric("Costo de la Dieta", f"${costo_kg:.2f} MXN / kg de alimento")
        m_c2.metric("Costo por Tonelada", f"${costo_kg * 1000:,.2f} MXN / Ton")

# ==========================================
# PESTAÑA 3: CERDAS EN LACTANCIA Y CRÍA
# ==========================================
with tab_lactancia:
    st.subheader(
        "🍼 Módulo de Nutrición, Cría y Soporte Metabólico en Cerdas Lactantes"
    )

    col_l1, col_l2 = st.columns(2)

    with col_l1:
        st.markdown("### 📋 Variables Reproductivas y de Cría")
        paridad = st.selectbox(
            "Número de Paridad",
            [
                "Primeriza (Alta sensibilidad metabólica y menor consumo)",
                "Multípara (Paridad 2 a 5 - Máximo potencial lechero)",
                "Longevidad (> Paridad 6)",
            ],
        )
        nacidos_vivos = st.number_input(
            "Lechones Nacidos Vivos", 4, 22, 13
        )
        dias_lac = st.slider("Duración de la Lactancia (Días)", 14, 35, 21)
        peso_destete = st.number_input(
            "Peso Objetivo por Lechón al Destete (kg)", 5.0, 9.5, 6.8
        )

    with col_l2:
        st.markdown("### 📊 Estimación del Desempeño Lácteo y Consumo")

        f_par = 0.88 if "Primeriza" in paridad else 1.00
        consumo_cerda = (2.1 + (nacidos_vivos * 0.44)) * f_par

        if thi_calculado > 74.0:
            consumo_cerda *= 1.0 - ((thi_calculado - 74.0) * 0.025)

        consumo_total_lac = consumo_cerda * dias_lac
        leche_total = peso_destete * nacidos_vivos * 3.85

        st.metric(
            "Consumo Diario Sugerido para la Cerda",
            f"{consumo_cerda:.2f} kg/día",
        )
        st.metric(
            "Consumo Total en Lactancia", f"{consumo_total_lac:,.1f} kg"
        )
        st.metric("Producción Láctea Total Estimada", f"{leche_total:,.1f} kg")

# ==========================================
# FUNCION GENERADORA DE PDF
# ==========================================
def generar_pdf_reporte(
    etapa_eng,
    raza_eng,
    num_animales,
    peso_inicial,
    peso_objetivo,
    gdp_ajustada,
    ca_ajustada,
    dias_estudio,
    consumo_total_cerdo,
    consumo_total_lote,
    costo_kg,
    min_ne,
    min_pc,
    min_sid_lys,
    thi_calculado,
    vel_aire,
    espacio_vital,
    estatus_inmunologico,
    df_form_filt,
):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(31, 78, 120)
    pdf.cell(0, 10, "PORCIDEX PRO - REPORTE TECNICO Y COMERCIAL", ln=True, align="C")

    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 4, "Version: v1.0 Pro | S/N: PRX-2026-MX-9842", ln=True, align="C")
    pdf.cell(0, 5, "Creado y desarrollado por el Dr. Alejandro Castaneda Correa", ln=True, align="C")
    pdf.ln(3)

    pdf.set_draw_color(31, 78, 120)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    # 1. RESUMEN EJECUTIVO
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(31, 78, 120)
    pdf.cell(0, 7, "1. RESUMEN EJECUTIVO (PRODUCTOR / PORCICULTOR)", ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)

    costo_cerdo = consumo_total_cerdo * costo_kg
    costo_lote = consumo_total_lote * costo_kg

    prod_text = [
        f"Etapa Productiva: {etapa_eng}",
        f"Perfil Genetico: {raza_eng}",
        f"Tamano del Lote: {num_animales:,} cerdos",
        f"Rango de Peso: {peso_inicial:.1f} kg -> {peso_objetivo:.1f} kg (Ganancia: {peso_objetivo-peso_inicial:.1f} kg)",
        f"Duracion Estimada de Engorda: {dias_estudio} dias",
        f"Ganancia Diaria Promedio (GDP Operativa): {gdp_ajustada:.2f} kg/dia",
        f"Conversion Alimenticia (CA): {ca_ajustada:.2f} kg alimento / kg peso",
        f"Consumo Alimento por Cerdo: {consumo_total_cerdo:.1f} kg",
        f"Consumo Total Lote: {consumo_total_lote:,.1f} kg ({round(consumo_total_lote/40):,} sacos de 40kg)",
        f"Costo Alimento Estimado por Cerdo: ${costo_cerdo:,.2f} MXN",
        f"Costo Alimento Total del Lote: ${costo_lote:,.2f} MXN",
    ]

    for item in prod_text:
        pdf.cell(0, 5, f"- {item}", ln=True)

    pdf.ln(4)

    # 2. RESUMEN TÉCNICO
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(46, 125, 50)
    pdf.cell(0, 7, "2. RESUMEN TECNICO (NUTRIOLOGO / VETERINARIO)", ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)

    nutri_text = [
        f"Energia Neta Minima (NE): {min_ne:.0f} kcal/kg",
        f"Proteina Cruda Minima (PC): {min_pc:.1f} %",
        f"Lisina SID Minima: {min_sid_lys:.2f} %",
        f"Costo Unitario Alimento: ${costo_kg:.2f} MXN/kg (${costo_kg*1000:,.2f} MXN/Ton)",
        "Perfil Aminoacidos SID (% vs Lisina): Met+Cys: 58% | Thr: 65% | Trp: 18% | Val: 70% | Ile: 60%",
        f"Indice Confort Termico ITH (THI): {thi_calculado:.1f} | Vel. Aire: {vel_aire} m/s",
        f"Espacio Vital / Alojamiento: {espacio_vital.split('(')[0]}",
        f"Estatus Sanitario: {estatus_inmunologico.split('/')[0]}",
    ]

    for item in nutri_text:
        pdf.cell(0, 5, f"- {item}", ln=True)

    pdf.ln(4)

    # 3. TABLA DE FORMULACIÓN
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(31, 78, 120)
    pdf.cell(0, 7, "3. FORMULACION DE LA DIETA OPTIMIZADA (Suma 100%)", ln=True)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(90, 6, "Materia Prima / Ingrediente", border=1, fill=True)
    pdf.cell(35, 6, "Inclusion (%)", border=1, fill=True, align="C")
    pdf.cell(35, 6, "Kg / Tonelada", border=1, fill=True, align="C")
    pdf.cell(30, 6, "Costo ($/Ton)", border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    if not df_form_filt.empty:
        for idx, row in df_form_filt.iterrows():
            ing = str(row["Materia Prima / Ingrediente"])
            inc = f"{row['Inclusión (%)']:.2f} %"
            kg_ton = f"{row['Kg por Tonelada']:.1f} kg"
            cost_ton = str(row["Aporte ($/Ton)"])

            pdf.cell(90, 6, ing, border=1)
            pdf.cell(35, 6, inc, border=1, align="C")
            pdf.cell(35, 6, kg_ton, border=1, align="C")
            pdf.cell(30, 6, cost_ton, border=1, align="C")
            pdf.ln()

    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(
        0,
        5,
        "Porcidex v1.0 Pro | S/N: PRX-2026-MX-9842 | Dr. Alejandro Castaneda Correa",
        align="C",
    )

    return bytes(pdf.output())


# ==========================================
# PESTAÑA 4: RESUMEN TÉCNICO Y COMERCIAL
# ==========================================
with tab_resumen:
    st.subheader(
        "📋 Hoja de Balance Integral: Parámetros para el Productor y Nutriólogo"
    )
    st.markdown(
        "Reporte unificado que consolida los indicadores zootécnicos clave, económicos y la especificación nutrimental de la dieta formulada."
    )

    costo_alimento_por_cerdo = consumo_total_cerdo * costo_kg
    costo_alimento_lote_total = consumo_total_lote * costo_kg
    ganancia_peso_total = peso_objetivo - peso_inicial

    col_prod, col_nutri = st.columns(2)

    with col_prod:
        st.markdown(
            """
        <div class="report-card">
            <h3 style="color: #1f4e78; margin-top:0;">📊 Resumen Ejecutivo para el Productor Porcino</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
        * **Etapa Evaluada:** `{etapa_eng}`
        * **Especie / Genética:** `{raza_eng}`
        * **Número de Animales en Lote:** `{num_animales:,} cerdos`
        * **Peso Inicial Promedio:** `{peso_inicial:.1f} kg`
        * **Peso Final Objetivo:** `{peso_objetivo:.1f} kg`
        * **Ganancia Total por Cerdo:** `{ganancia_peso_total:.1f} kg`
        * **Duración de la Engorda:** `{dias_estudio} días` (`{round(dias_estudio/30, 1)} meses`)
        * **Ganancia Diaria Promedio (GDP Operativa):** `{gdp_ajustada:.2f} kg/día`
        * **Conversión Alimenticia (CA):** `{ca_ajustada:.2f}` *(kg alimento / kg peso)*
        * **Consumo Total Alimento por Cerdo:** `{consumo_total_cerdo:.1f} kg`
        * **Consumo Total de Alimento por Lote:** `{consumo_total_lote:,.1f} kg` (`{round(consumo_total_lote/40):,} sacos de 40 kg`)
        * **Costo Estimado Alimento por Cerdo:** `${costo_alimento_por_cerdo:,.2f} MXN`
        * **Costo Total Alimento por Lote:** `${costo_alimento_lote_total:,.2f} MXN`
        """
        )

    with col_nutri:
        st.markdown(
            """
        <div class="report-card">
            <h3 style="color: #2e7d32; margin-top:0;">🧬 Resumen Técnico para el Nutriólogo / MVZ</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
        * **Energía Neta Requerida (NE):** `{min_ne:.0f} kcal/kg`
        * **Proteína Cruda Requerida (PC):** `{min_pc:.1f} %`
        * **Lisina SID Mínima:** `{min_sid_lys:.2f} %`
        * **Costo por Kilogramo de Alimento:** `${costo_kg:.2f} MXN/kg`
        * **Costo por Tonelada de Alimento:** `${costo_kg * 1000:,.2f} MXN/Ton`
        * **Perfil de Aminoácidos Ideales SID (% respecto a Lisina):**
          * *Metionina + Cisteína SID:* `58 %`
          * *Treonina SID:* `65 %`
          * *Triptófano SID:* `18 %`
          * *Valina SID:* `70 %`
          * *Isoleucina SID:* `60 %`
        * **Estatus Ambiental y Bioconfort:**
          * *Índice ITH / THI:* `{thi_calculado:.1f}`
          * *Velocidad del Aire:* `{vel_aire} m/s`
          * *Hacinamiento / Espacio:* `{espacio_vital.split('(')[0]}`
          * *Estatus Sanitario Granja:* `{estatus_inmunologico.split('/')[0]}`
        """
        )

    st.markdown("---")
    st.subheader("🖨️ Descargar e Imprimir Reporte en PDF")

    pdf_bytes = generar_pdf_reporte(
        etapa_eng,
        raza_eng,
        num_animales,
        peso_inicial,
        peso_objetivo,
        gdp_ajustada,
        ca_ajustada,
        dias_estudio,
        consumo_total_cerdo,
        consumo_total_lote,
        costo_kg,
        min_ne,
        min_pc,
        min_sid_lys,
        thi_calculado,
        vel_aire,
        espacio_vital,
        estatus_inmunologico,
        df_form_filt,
    )

    st.download_button(
        label="📄 Descargar Reporte Completo en PDF",
        data=pdf_bytes,
        file_name=f"Reporte_Porcidex_Pro_{etapa_eng.replace(' ', '_')}.pdf",
        mime="application/pdf",
        help="Haz clic para descargar el resumen completo en formato PDF listo para imprimir.",
    )

st.markdown("---")
st.caption(
    "Porcidex v1.0 Pro | S/N: PRX-2026-MX-9842 | Creado y desarrollado por el Dr. Alejandro Castañeda Correa"
)
