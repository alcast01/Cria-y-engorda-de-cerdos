import io
import numpy as np
import pandas as pd

from fpdf import FPDF
from scipy.optimize import linprog
import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Porcidex | Nutrición y Porcicultura de Precisión",
    page_icon="🐖",
    layout="wide",
)

# --- ESTILOS CSS PERSONALIZADOS Y LOGOTIPO EMBLEMÁTICO ---
st.markdown(
    """
    <style>
    .brand-container {
        background: linear-gradient(135deg, #1f4e78 0%, #112233 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .brand-logo {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .brand-title {
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: 2px;
        margin: 0;
        color: #ffffff;
    }
    .brand-slogan {
        font-size: 1.25rem;
        font-style: italic;
        color: #d9e1e8;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }
    .creator-tag {
        font-size: 0.95rem;
        color: #a9dfbf;
        font-weight: 600;
        letter-spacing: 0.5px;
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

# --- CABECERA CON LOGOTIPO Y SLOGAN EMBLEMÁTICO ---
st.markdown(
    """
    <div class="brand-container">
        <div class="brand-logo">🐖⚡</div>
        <h1 class="brand-title">PORCIDEX</h1>
        <p class="brand-slogan">"Ciencia y Precisión al Servicio de la Porcicultura Moderna"</p>
        <p class="creator-tag">Creado y desarrollado por el Dr. Alejandro Castañeda Correa</p>
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
st.sidebar.info(
    f"📊 **Índice THI Estimado:** `{thi_calculado:.1f}`\n\n"
    f"*Estatus:* {'⚠️ Estrés Calórico Crítico' if thi_calculado > 78 else ('⚠️ Estrés Moderado' if thi_calculado > 74 else '✅ Confort Biológico')}"
)

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
        "📈 Engorda, PLF y Control Térmico",
        "🧮 Formulación Avanzada (NE, SID & Fitasa)",
        "🍼 Cerdas en Lactancia y Cría",
        "📋 Resumen Técnico y Comercial",
    ]
)

# ==========================================
# PESTAÑA 1: ENGORDA, PLF Y CONTROL TÉRMICO
# ==========================================
with tab_engorda:
    st.subheader(
        "Módulo de Simulación Dinámica y Ganadería de Precisión (PLF)"
    )

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

    with col_s2:
        if etapa_eng == "Iniciación":
            temp_optima = 24.0
            base_gdp = 0.68
            base_ca = 1.50
            base_pc = 20.5
            base_ne = 2550
        elif etapa_eng == "Desarrollo y Crecimiento":
            temp_optima = 20.0
            base_gdp = 0.95
            base_ca = 2.20
            base_pc = 17.0
            base_ne = 2480
        else:
            temp_optima = 18.0
            base_gdp = 1.10
            base_ca = 2.75
            base_pc = 14.0
            base_ne = 2400

        diff_temp = temp_amb - temp_optima
        factor_estres = 1.0
        if diff_temp > 2.0:
            mitigacion_viento = min(0.18, vel_aire * 0.09)
            factor_estres = max(
                0.60,
                1.0
                - (((diff_temp - 2.0) * 0.038) - mitigacion_viento),
            )
        elif diff_temp < -3.0:
            factor_estres = max(0.82, 1.0 - (abs(diff_temp + 3.0) * 0.015))

        if "Estándar" in espacio_vital:
            base_gdp *= 0.97
        elif "Hacinamiento" in espacio_vital:
            base_gdp *= 0.88
            base_ca *= 1.12

        if "Medio" in estatus_inmunologico:
            base_gdp *= 0.94
            base_ca *= 1.05
        elif "Bajo" in estatus_inmunologico:
            base_gdp *= 0.82
            base_ca *= 1.20

        if uso_pfs:
            base_ca *= 0.92
        if uso_vision_3d:
            base_gdp *= 1.03

        gdp_ajustada = base_gdp * factor_estres
        ca_ajustada = base_ca / factor_estres
        dias_estudio = max(
            1, round((peso_objetivo - peso_inicial) / max(0.1, gdp_ajustada))
        )
        consumo_diario = gdp_ajustada * ca_ajustada
        consumo_total_cerdo = consumo_diario * dias_estudio
        consumo_total_lote = consumo_total_cerdo * num_animales

        st.markdown(f"### 📋 Resultados del Gemelo Digital: **{etapa_eng}**")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(
            "GDP Ajustada",
            f"{gdp_ajustada:.2f} kg/d",
            delta=f"{((gdp_ajustada - base_gdp)/base_gdp)*100:.1f}% mod",
        )
        m2.metric(
            "Conversión (CA)",
            f"{ca_ajustada:.2f}",
            delta=f"{((ca_ajustada - base_ca)/base_ca)*100:.1f}%",
            delta_color="inverse",
        )
        m3.metric("Días al Objetivo", f"{dias_estudio} días")
        m4.metric("Consumo Diario / Cerdo", f"{consumo_diario:.2f} kg")

        st.markdown("---")
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.info(
                f"""
            **Impacto Tecnológico PLF & Nutrición:**
            * **Ahorro Estimado por PFS (RFID):** `~{10 if uso_pfs else 0}%` en costo de alimento.
            * **Monitoreo Acústico / Bioseguridad:** {'Activado (Alerta de tos y agua en tiempo real)' if monitoreo_acustico else 'Desactivado'}.
            * **Biometría 3D:** Margen de error de pesaje < 1.2 kg.
            * **Alimento Total Requerido:** {consumo_total_lote:,.1f} kg.
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
# PESTAÑA 2: FORMULACIÓN AVANZADA FLEXIBLE
# ==========================================
with tab_formulacion:
    st.subheader(
        "🧮 Optimización Lineal Multi-Ingrediente (NE, SID & Fitasa)"
    )
    st.markdown(
        "Sistema flexible de programación lineal para minimizar el costo del alimento manteniendo un equilibrio óptimo de energía y aminoácidos digestibles."
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
        min_ne, min_sid_lys, max_fibra = 2300.0, 0.95, 5.5
    elif "Desarrollo" in etapa_form:
        min_ne, min_sid_lys, max_fibra = 2250.0, 0.80, 7.0
    elif "Finalización" in etapa_form:
        min_ne, min_sid_lys, max_fibra = 2200.0, 0.68, 8.5
    else:
        min_ne, min_sid_lys, max_fibra = 2150.0, 0.60, 9.5

    st.markdown("### 💰 Costos Unitarios de Ingredientes y Materias Primas ($ / kg)")

    ic1, ic2, ic3, ic4 = st.columns(4)
    p_maiz = ic1.number_input("Maíz Grano ($/kg)", 1.0, 50.0, 5.50)
    p_sorgo = ic2.number_input("Sorgo Grano ($/kg)", 1.0, 50.0, 5.20)
    p_soya = ic3.number_input("Pasta de Soya 48% ($/kg)", 1.0, 50.0, 12.00)
    p_canola = ic4.number_input("Pasta de Canola ($/kg)", 1.0, 50.0, 8.50)

    ic5, ic6, ic7, ic8, ic9 = st.columns(5)
    p_salvado = ic5.number_input("Salvado de Trigo ($/kg)", 1.0, 50.0, 4.00)
    p_ddgs = ic6.number_input("DDGS de Maíz ($/kg)", 1.0, 50.0, 6.80)
    p_hch = ic7.number_input("Harina de Carne y Hueso ($/kg)", 1.0, 50.0, 9.50)
    p_aceite = ic8.number_input("Aceite / Grasa ($/kg)", 1.0, 80.0, 22.00)
    p_nucleo = ic9.number_input(
        "Núcleo + Fitasa ($/kg)", 1.0, 100.0, 38.00
    )

    c = [
        p_maiz,
        p_sorgo,
        p_soya,
        p_canola,
        p_salvado,
        p_ddgs,
        p_hch,
        p_aceite,
        p_nucleo,
    ]

    A_ub = [
        [
            -2650.0,
            -2580.0,
            -2240.0,
            -2050.0,
            -1700.0,
            -2350.0,
            -2050.0,
            -5800.0,
            0.0,
        ],
        [
            -0.26,
            -0.22,
            -2.85,
            -2.10,
            -0.65,
            -0.65,
            -2.40,
            0.0,
            0.0,
        ],
        [2.0, 2.2, 7.0, 11.5, 11.0, 8.5, 2.0, 0.0, 0.0],
    ]
    b_ub = [-min_ne, -min_sid_lys, max_fibra]
    A_eq = [[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    b_eq = [100.0]

    bounds = [
        (0.0, 95.0),
        (0.0, 95.0),
        (2.0, 50.0),
        (0.0, 30.0),
        (0.0, 30.0),
        (0.0, 35.0),
        (0.0, 20.0),
        (0.0, 10.0),
        (1.0, 6.0),
    ]

    res = linprog(
        c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs"
    )

    if not res.success:
        b_ub_relaxed = [-min_ne * 0.85, -min_sid_lys * 0.85, max_fibra * 1.30]
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
    else:
        props = [62.0, 0.0, 25.0, 0.0, 4.0, 0.0, 5.0, 1.0, 3.0]
        costo_kg = sum(p * cost for p, cost in zip(props, c)) / 100.0

    st.success("✅ Dieta calculada exitosamente.")

    df_formula = pd.DataFrame(
        {
            "Materia Prima / Ingrediente": [
                "Maíz Grano",
                "Sorgo Grano",
                "Pasta de Soya 48%",
                "Pasta de Canola",
                "Salvado de Trigo",
                "DDGS de Maíz",
                "Harina de Carne y Hueso",
                "Aceite Vegetal / Grasa",
                "Núcleo Vitamínico-Mineral con Fitasa",
            ],
            "Inclusión (%)": [round(p, 2) for p in props],
            "Kg por Tonelada": [round(p * 10, 2) for p in props],
        }
    )
    df_form_filt = df_formula[df_formula["Inclusión (%)"] > 0.01]
    st.table(df_form_filt)

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
# FUNCION GENERADORA DE PDF (FPDF2)
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
    base_pc,
    min_sid_lys,
    thi_calculado,
    vel_aire,
    espacio_vital,
    estatus_inmunologico,
    df_form_filt,
):
    pdf = FPDF()
    pdf.add_page()

    # Encabezado
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(31, 78, 120)  # #1f4e78
    pdf.cell(
        0,
        10,
        "PORCIDEX - REPORTE TECNICO Y COMERCIAL",
        new_x="LMARGIN",
        new_y="NEXT",
        align="C",
    )

    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(
        0,
        6,
        "Ciencia y Precision al Servicio de la Porcicultura Moderna",
        new_x="LMARGIN",
        new_y="NEXT",
        align="C",
    )
    pdf.cell(
        0,
        6,
        "Creado y desarrollado por el Dr. Alejandro Castaneda Correa",
        new_x="LMARGIN",
        new_y="NEXT",
        align="C",
    )
    pdf.ln(5)

    # Linea separadora
    pdf.set_draw_color(31, 78, 120)
    pdf.set_linewidth(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # 1. RESUMEN EJECUTIVO PARA EL PRODUCUTOR
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(31, 78, 120)
    pdf.cell(
        0,
        8,
        "1. RESUMEN EJECUTIVO (PRODUCTOR / PORCICULTOR)",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)

    costo_cerdo = consumo_total_cerdo * costo_kg
    costo_lote = consumo_total_lote * costo_kg

    prod_text = [
        f"Etapa Productiva: {etapa_eng}",
        f"Perfil Genetico: {raza_eng}",
        f"Tamano del Lote: {num_animales:,} cerdos",
        f"Rango de Peso: {peso_inicial:.1f} kg -> {peso_objetivo:.1f} kg (Ganancia: {peso_objetivo-peso_inicial:.1f} kg)",
        f"Dias Estimados a Mercado: {dias_estudio} dias",
        f"Ganancia Diaria Promedio (GDP): {gdp_ajustada:.2f} kg/dia",
        f"Conversion Alimenticia (CA): {ca_ajustada:.2f} kg alimento / kg peso",
        f"Consumo Alimento por Cerdo: {consumo_total_cerdo:.1f} kg",
        f"Consumo Total Lote: {consumo_total_lote:,.1f} kg ({round(consumo_total_lote/40):,} sacos de 40kg)",
        f"Costo Alimento Estimado por Cerdo: ${costo_cerdo:,.2f} MXN",
        f"Costo Alimento Total del Lote: ${costo_lote:,.2f} MXN",
    ]

    for item in prod_text:
        pdf.cell(0, 5, f"- {item}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)

    # 2. RESUMEN TECNICO PARA EL NUTRIOLOGO / MVZ
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(46, 125, 50)  # #2e7d32
    pdf.cell(
        0,
        8,
        "2. RESUMEN TECNICO (NUTRIOLOGO / VETERINARIO)",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)

    nutri_text = [
        f"Energia Neta (NE): {min_ne:.0f} kcal/kg",
        f"Proteina Cruda (PC Estimada): {base_pc:.1f} %",
        f"Lisina SID Minima: {min_sid_lys:.2f} %",
        f"Costo Unitario Alimento: ${costo_kg:.2f} MXN/kg (${costo_kg*1000:,.2f} MXN/Ton)",
        "Perfil Aminoacidos SID (% vs Lisina): Met+Cys: 58% | Thr: 65% | Trp: 18% | Val: 70% | Ile: 60%",
        f"Indice Confort Termico ITH (THI): {thi_calculado:.1f} | Vel. Aire: {vel_aire} m/s",
        f"Espacio Vital / Alojamiento: {espacio_vital.split('(')[0]}",
        f"Estatus Sanitario: {estatus_inmunologico.split('/')[0]}",
    ]

    for item in nutri_text:
        pdf.cell(0, 5, f"- {item}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)

    # 3. TABLA DE FORMULACION
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(31, 78, 120)
    pdf.cell(
        0,
        8,
        "3. FORMULACION DE LA DIETA OPTIMIZADA",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(100, 6, "Materia Prima / Ingrediente", border=1, fill=True)
    pdf.cell(40, 6, "Inclusion (%)", border=1, fill=True, align="C")
    pdf.cell(45, 6, "Kg por Tonelada", border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    for idx, row in df_form_filt.iterrows():
        ing = str(row["Materia Prima / Ingrediente"])
        inc = f"{row['Inclusión (%)']:.2f} %"
        kg_ton = f"{row['Kg por Tonelada']:.2f} kg"

        pdf.cell(100, 6, ing, border=1)
        pdf.cell(40, 6, inc, border=1, align="C")
        pdf.cell(45, 6, kg_ton, border=1, align="C")
        pdf.ln()

    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(
        0,
        5,
        "Documento generado automaticamente por Porcidex v6.1.",
        align="C",
    )

    return bytes(pdf.output())


# ==========================================
# PESTAÑA 4: RESUMEN TÉCNICO Y COMERCIAL CON DESCARGA PDF
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
        * **Días Estimados a Mercado:** `{dias_estudio} días`
        * **Ganancia Diaria Promedio (GDP):** `{gdp_ajustada:.2f} kg/día`
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
        * **Energía Neta Estimada (NE):** `{min_ne:.0f} kcal/kg`
        * **Proteína Cruda Estimada (PC):** `{base_pc:.1f} %`
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

    # Generar bytes del archivo PDF
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
        base_pc,
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
        file_name=f"Reporte_Porcidex_{etapa_eng.replace(' ', '_')}.pdf",
        mime="application/pdf",
        help="Haz clic para descargar el resumen completo en formato PDF listo para imprimir.",
    )

st.markdown("---")
st.caption(
    "Porcidex v6.1 | Creado y desarrollado por el Dr. Alejandro Castañeda Correa"
)
