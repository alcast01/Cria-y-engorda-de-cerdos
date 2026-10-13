import numpy as np
import pandas as pd
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

modulo_activo = st.sidebar.selectbox(
    "Seleccionar Módulo Operativo",
    [
        "📈 Engorda, PLF y Control Térmico",
        "🧮 Formulación Avanzada (NE, SID & Fitasa)",
        "🍼 Cerdas en Lactancia y Cría",
    ],
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

# Cálculo científico del Índice Temperatura-Humedad (THI)
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

# --- NAVEGACIÓN PRINCIPAL ---
tab_engorda, tab_formulacion, tab_lactancia = st.tabs(
    [
        "📈 Engorda, PLF y Control Térmico",
        "🧮 Formulación Avanzada (NE, SID & Fitasa)",
        "🍼 Cerdas en Lactancia y Cría",
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
        # Valores base fisiológicos
        if etapa_eng == "Iniciación":
            temp_optima = 24.0
            base_gdp = 0.68
            base_ca = 1.50
            base_pc = 20.5
            base_ne = 2550  # kcal NE/kg
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

        # Algoritmo de estrés térmico dinámico con velocidad de aire
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

        # Ajuste por densidad y espacio vital
        if "Estándar" in espacio_vital:
            base_gdp *= 0.97
        elif "Hacinamiento" in espacio_vital:
            base_gdp *= 0.88
            base_ca *= 1.12

        # Ajuste por estatus inmunitario (costo de nutrientes en fase aguda)
        if "Medio" in estatus_inmunologico:
            base_gdp *= 0.94
            base_ca *= 1.05
        elif "Bajo" in estatus_inmunologico:
            base_gdp *= 0.82
            base_ca *= 1.20

        # Ajustes por tecnología PFS y Visión 3D
        if uso_pfs:
            base_ca *= 0.92  # Mejora del 8% en conversión por eliminación de sobre-alimentación
        if uso_vision_3d:
            # Precisión en la salida al rastro optimiza peso de venta en 2.5%
            base_gdp *= 1.03

        gdp_ajustada = base_gdp * factor_estres
        ca_ajustada = base_ca / factor_estres
        dias_estudio = max(
            1, round((peso_objetivo - peso_inicial) / max(0.1, gdp_ajustada))
        )
        consumo_diario = gdp_ajustada * ca_ajustada
        consumo_total_lote = consumo_diario * dias_estudio * num_animales

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
# PESTAÑA 2: FORMULACIÓN AVANZADA (NE, SID & FITASA)
# ==========================================
with tab_formulacion:
    st.subheader("🧮 Optimización Lineal por Energía Neta (NE) y Proteína Ideal SID")
    st.markdown(
        "Formulación matemática de precisión utilizando sistemas de **Energía Neta**, perfiles de **Aminoácidos Digestibles Estandarizados (SID)** con referencia a Lisina, y matriz de liberación por **Fitases de Nueva Generación**."
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
        )

    # Requerimientos según literatura científica actual
    if "Iniciación" in etapa_form:
        min_ne, min_sid_lys, max_fibra = 2500.0, 1.15, 3.5
    elif "Desarrollo" in etapa_form:
        min_ne, min_sid_lys, max_fibra = 2450.0, 0.98, 5.0
    elif "Finalización" in etapa_form:
        min_ne, min_sid_lys, max_fibra = 2400.0, 0.82, 6.5
    else:
        min_ne, min_sid_lys, max_fibra = 2380.0, 0.75, 7.5

    st.markdown("### 💰 Costos Unitarios de Materias Primas ($ / kg)")
    ic1, ic2, ic3 = st.columns(3)
    p_maiz = ic1.number_input("Maíz Grano ($/kg)", 2.0, 15.0, 5.50)
    p_soya = ic2.number_input("Pasta de Soya 48% ($/kg)", 5.0, 25.0, 12.00)
    p_canola = ic3.number_input("Pasta de Canola ($/kg)", 4.0, 20.0, 8.50)

    ic4, ic5, ic6 = st.columns(3)
    p_salvado = ic4.number_input("Salvado de Trigo ($/kg)", 1.5, 10.0, 4.00)
    p_aceite = ic5.number_input(
        "Aceite Vegetal / Grasa de Soya ($/kg)", 10.0, 40.0, 22.00
    )
    p_nucleo = ic6.number_input(
        "Núcleo Vitamínico-Mineral + Fitasa ($/kg)", 10.0, 80.0, 38.00
    )

    if st.button("🚀 Calcular Dieta de Mínimo Costo (NE & SID)"):
        # Ingredientes: [Maíz, Soya, Canola, Salvado, Aceite, Núcleo]
        c = [p_maiz, p_soya, p_canola, p_salvado, p_aceite, p_nucleo]

        # Restricciones nutricionales basadas en Energía Neta (NE kcal/kg), Lisina SID (%) y Fibra (%)
        # [Maiz, Soya, Canola, Salvado, Aceite, Núcleo]
        A_ub = [
            [-2650.0, -2240.0, -2050.0, -1700.0, -5800.0, 0.0],  # -NE >= min_ne
            [-0.26, -2.85, -2.10, -0.65, 0.0, 0.0],  # -SID Lys >= min_sid_lys
            [2.0, 7.0, 11.5, 11.0, 0.0, 0.0],  # Fibra <= max_fibra
        ]
        b_ub = [-min_ne, -min_sid_lys, max_fibra]

        A_eq = [[1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
        b_eq = [100.0]

        bounds = [
            (45.0, 82.0),  # Maíz
            (8.0, 38.0),  # Soya
            (0.0, 18.0),  # Canola
            (0.0, 15.0),  # Salvado
            (0.5, 5.0),  # Aceite
            (2.0, 3.5),  # Núcleo con Fitasa
        ]

        res = linprog(
            c,
            A_ub=A_ub,
            b_ub=b_ub,
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=bounds,
            method="highs",
        )

        if res.success:
            props = res.x
            costo_kg = res.fun / 100.0
            st.success(
                "✅ ¡Formulación por Energía Neta y Proteína Ideal completada!"
            )

            df_formula = pd.DataFrame(
                {
                    "Ingrediente / Materia Prima": [
                        "Maíz Grano",
                        "Pasta de Soya 48%",
                        "Pasta de Canola",
                        "Salvado de Trigo",
                        "Aceite Vegetal / Grasa",
                        "Núcleo con Fitasa de Nueva Generación",
                    ],
                    "Inclusión (%)": [round(p, 2) for p in props],
                    "Kg por Tonelada": [round(p * 10, 2) for p in props],
                }
            )
            df_form_filt = df_formula[df_formula["Inclusión (%)"] > 0.05]
            st.table(df_form_filt)

            m_c1, m_c2 = st.columns(2)
            m_c1.metric(
                "Costo de la Dieta", f"${costo_kg:.2f} MXN / kg de alimento"
            )
            m_c2.metric(
                "Costo por Tonelada", f"${costo_kg * 1000:,.2f} MXN / Ton"
            )

            st.markdown(
                "**Perfil de Aminoácidos Ideales SID (Referencia Lisina 100%):**"
            )
            st.info(
                "• Metionina + Cisteína: 58% | • Treonina: 65% | • Triptófano: 18% | • Valina: 70% | • Isoleucina: 60%"
            )
        else:
            st.error(
                "⚠️ No se encontró solución factible con los precios o restricciones energéticas actuales. Relaje los límites de inclusión o ajuste los costos."
            )

# ==========================================
# PESTAÑA 3: CERDAS EN LACTANCIA Y CRÍA
# ==========================================
with tab_lactancia:
    st.subheader(
        "🍼 Módulo de Nutrición, Cría y Soporte Metabólico en Cerdas Lactantes"
    )
    st.markdown(
        "Optimización del rendimiento reproductivo y lácteo de la cerda, integrando paridad, balance energético y supervivencia de la camada."
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

    st.markdown("---")
    st.markdown(
        "### 💡 Recomendaciones Científicas para la Supervivencia de la Cría"
    )

    col_rc1, col_rc2 = st.columns(2)
    with col_rc1:
        st.info(
            """
        * **Nutrición Proteica y Energética en Lactancia:**
          * **Lisina SID:** Mínimo 1.05% para evitar catabolismo excesivo de masa muscular.
          * **Energía Neta:** 2,550 kcal NE/kg para sostener la síntesis láctea.
          * **Fibra Funcional:** 6% de fibra soluble/insoluble para prevenir endotoxemia y estreñimiento periparto.
        """
        )
    with col_rc2:
        st.success(
            """
        * **Manejo Ambiental y del Lechón:**
          * **Temperatura en Nido:** 32°C a 34°C en la primera semana de vida.
          * **Consumo de Calostro:** Garantizar ≥ 250 g por lechón en las primeras 6 horas post-parto.
          * **Agua Ad Libitum:** Suministro de 25 a 35 litros diarios de agua fresca para la eyección láctea.
        """
        )

st.markdown("---")
st.caption(
    "Porcidex v5.0 | Creado y desarrollado por el Dr. Alejandro Castañeda Correa"
)
