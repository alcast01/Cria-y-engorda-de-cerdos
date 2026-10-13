import numpy as np
import pandas as pd
from scipy.optimize import linprog
import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Porcidex | Nutrición y Producción Porcina de Precisión",
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
# PANEL IZQUIERDO: VARIABLES DE PRODUCCIÓN CIENTÍFICA
# ==========================================
st.sidebar.header("🔬 Panel de Variables Zootécnicas y Ambientales")
st.sidebar.markdown(
    "*Parámetros basados en normativas y literatura científica internacional de porcicultura.*"
)

# 1. Selección de Módulo Principal
modulo_activo = st.sidebar.selectbox(
    "Seleccionar Módulo Operativo",
    [
        "📈 Engorda y Control Ambiental",
        "🧮 Formulación al Mínimo Costo",
        "🍼 Cerdas en Lactancia y Cría",
    ],
)

st.sidebar.markdown("---")
st.sidebar.subheader("🌡️ Ambiente y Estrés Térmico (ITH / THI)")
temp_amb = st.sidebar.slider(
    "Temperatura Ambiental (°C)", 10.0, 38.0, 24.0, 0.5
)
hum_relativa = st.sidebar.slider("Humedad Relativa (%)", 20.0, 95.0, 65.0, 5.0)
vel_aire = st.sidebar.slider(
    "Velocidad del Viento / Ventilación (m/s)", 0.0, 2.5, 0.3, 0.1
)

# Cálculo científico del Índice Temperatura-Humedad (THI adaptado para cerdos)
# THI = Temp - [0.55 - (0.55 * Humedad/100)] * (Temp - 14.4)
thi_calculado = temp_amb - (0.55 - (0.55 * (hum_relativa / 100.0))) * (
    temp_amb - 14.4
)
st.sidebar.info(
    f"📊 **Índice THI Estimado:** `{thi_calculado:.1f}`\n\n"
    f"*Interpretación:* {'⚠️ Estrés Calórico Severo' if thi_calculado > 78 else ('⚠️ Estrés Moderado' if thi_calculado > 74 else '✅ Confort Térmico')}"
)

st.sidebar.markdown("---")
st.sidebar.subheader("🏠 Alojamiento y Bioseguridad")
densidad_alojamiento = st.sidebar.selectbox(
    "Densidad de Alojamiento (Espacio por animal)",
    [
        "Óptimo (> 0.85 m²/cerdo finalización)",
        "Moderado (0.70 - 0.85 m²/cerdo)",
        "Hacinamiento / Alto (< 0.70 m²/cerdo)",
    ],
)
estatus_sanitario = st.sidebar.selectbox(
    "Estatus de Reto Sanitario en Granja",
    [
        "Alto Estatus / Alta Bioseguridad (Libre de patógenos respiratorios mayores)",
        "Medio (Reto endémico controlado por vacunación)",
        "Bajo (Presencia activa de PRRS / Complejo Respiratorio Porcino)",
    ],
)

# --- NAVEGACIÓN POR PESTAÑAS PRINCIPALES ---
tab_engorda, tab_formulacion, tab_lactancia = st.tabs(
    [
        "📈 Engorda y Control Ambiental",
        "🧮 Formulación al Mínimo Costo",
        "🍼 Cerdas en Lactancia y Cría",
    ]
)

# ==========================================
# PESTAÑA 1: ENGORDA Y CONTROL AMBIENTAL
# ==========================================
with tab_engorda:
    st.subheader(
        "Módulo de Modelación Zootécnica para Cerdos en Crecimiento y Finalización"
    )

    col_s1, col_s2 = st.columns([1, 2])

    with col_s1:
        st.markdown("### 📋 Configuración del Lote")
        etapa_eng = st.selectbox(
            "Etapa Productiva",
            ["Iniciación", "Desarrollo y Crecimiento", "Finalización"],
        )
        raza_eng = st.selectbox(
            "Perfil Genético / Raza",
            [
                "Comercial / Híbrido (Yorkshire x Landrace x Duroc)",
                "Línea Materna (Landrace / Large White)",
                "Línea Paterna (Duroc / Pietrain)",
            ],
        )

        peso_inicial = st.number_input(
            "Peso Inicial Promedio (kg)",
            min_value=7.0,
            max_value=110.0,
            value=(
                15.0
                if etapa_eng == "Iniciación"
                else (
                    35.0 if etapa_eng == "Desarrollo y Crecimiento" else 70.0
                )
            ),
        )
        peso_objetivo = st.number_input(
            "Peso Objetivo / Salida (kg)",
            min_value=10.0,
            max_value=130.0,
            value=(
                35.0
                if etapa_eng == "Iniciación"
                else (
                    70.0 if etapa_eng == "Desarrollo y Crecimiento" else 115.0
                )
            ),
        )
        num_animales = st.number_input(
            "Número de Animales en el Lote", min_value=1, max_value=2000, value=100
        )

    with col_s2:
        # Valores base según etapa
        if etapa_eng == "Iniciación":
            temp_optima = 24.0
            base_gdp = 0.65
            base_ca = 1.55
            base_pc = 21.0
            base_em = 3300
        elif etapa_eng == "Desarrollo y Crecimiento":
            temp_optima = 20.0
            base_gdp = 0.90
            base_ca = 2.30
            base_pc = 17.5
            base_em = 3200
        else:
            temp_optima = 18.0
            base_gdp = 1.05
            base_ca = 2.85
            base_pc = 14.5
            base_em = 3100

        # Ajuste multivariable científico por Estrés Térmico (THI) y Ventilación
        diff_temp = temp_amb - temp_optima
        factor_estres = 1.0
        if diff_temp > 2.0:
            # Reducción de consumo y ganancia por calor ajustado por velocidad del aire
            mitigacion_viento = min(0.15, vel_aire * 0.08)
            factor_estres = max(
                0.65,
                1.0
                - (((diff_temp - 2.0) * 0.035) - mitigacion_viento),
            )
        elif diff_temp < -3.0:
            factor_estres = max(0.85, 1.0 - (abs(diff_temp + 3.0) * 0.015))

        # Ajustes por Densidad de Alojamiento
        if "Moderado" in densidad_alojamiento:
            base_gdp *= 0.97
        elif "Hacinamiento" in densidad_alojamiento:
            base_gdp *= 0.90
            base_ca *= 1.08   empeora conversión

        # Ajustes por Estatus Sanitario
        if "Medio" in estatus_sanitario:
            base_gdp *= 0.95
        elif "Bajo" in estatus_sanitario:
            base_gdp *= 0.85
            base_ca *= 1.15

        # Ajustes Genéticos
        if "Paterna" in raza_eng:
            base_gdp *= 1.08
            base_ca *= 0.95
        elif "Materna" in raza_eng:
            base_gdp *= 0.96

        gdp_ajustada = base_gdp * factor_estres
        ca_ajustada = base_ca / factor_estres
        dias_estudio = max(
            1, round((peso_objetivo - peso_inicial) / max(0.1, gdp_ajustada))
        )
        consumo_diario_estimado = gdp_ajustada * ca_ajustada
        consumo_total_lote = (
            consumo_diario_estimado * dias_estudio * num_animales
        )

        st.markdown(f"### 📋 Resultados Ajustados: **{etapa_eng}**")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(
            "Ganancia Diaria (GDP)",
            f"{gdp_ajustada:.2f} kg/d",
            delta=f"{((gdp_ajustada - base_gdp)/base_gdp)*100:.1f}% multifactorial",
        )
        m2.metric(
            "Conversión (CA)",
            f"{ca_ajustada:.2f}",
            delta=f"{((ca_ajustada - base_ca)/base_ca)*100:.1f}%",
            delta_color="inverse",
        )
        m3.metric("Duración Estimada", f"{dias_estudio} días")
        m4.metric("Consumo Diario / Cerdo", f"{consumo_diario_estimado:.2f} kg")

        st.markdown("---")
        c_nutri, c_amb = st.columns(2)
        with c_nutri:
            st.info(
                f"""
            **Perfil Nutricional Recomendado:**
            * **Proteína Cruda:** {base_pc:.1f}%
            * **Energía Metabolizable:** {base_em} kcal/kg
            * **Alimento Total Requerido:** {consumo_total_lote:,.1f} kg ({round(consumo_total_lote/40)} sacos de 40 kg)
            """
            )
        with c_amb:
            if thi_calculado > 76:
                st.warning(
                    f"⚠️ **Alerta Biológica (THI {thi_calculado:.1f}):** Alto riesgo de estrés calórico. Se recomienda elevar densidad energética de la dieta y optimizar velocidad de aire (>1.5 m/s)."
                )
            else:
                st.success(
                    f"✅ **Condiciones Óptimas (THI {thi_calculado:.1f}):** El entorno zootécnico favorece el desempeño del lote."
                )

        st.markdown("### 📈 Proyección de Crecimiento Semanal")
        semanas = np.arange(1, dias_estudio + 1, 7)
        pesos_proyectados = [
            min(peso_objetivo, peso_inicial + (gdp_ajustada * d)) for d in semanas
        ]
        df_proy = pd.DataFrame(
            {
                "Día": semanas,
                "Peso Proyectado (kg)": [round(p, 2) for p in pesos_proyectados],
            }
        )
        st.line_chart(df_proy.set_index("Día"), color=["#1f4e78"])

# ==========================================
# PESTAÑA 2: FORMULACIÓN AL MÍNIMO COSTO
# ==========================================
with tab_formulacion:
    st.subheader(
        "🧮 Optimización Lineal de Dietas (Least-Cost Feed Formulation)"
    )
    st.markdown(
        "Sistema de programación lineal multivariable para calcular la ración óptima combinando múltiples materias primas al mínimo costo por kilogramo."
    )

    col_f1, col_f2 = st.columns(2)

    with col_f1:
        req_etapa = st.selectbox(
            "Seleccionar Etapa / Categoría para Formulación",
            [
                "Iniciación",
                "Desarrollo",
                "Finalización",
                "Cerdas de Recría (Desarrollo/Remonta)",
            ],
            key="req_form",
        )

    if req_etapa == "Iniciación":
        min_pc, min_em, max_fibra = 21.0, 3250.0, 3.5
    elif req_etapa == "Desarrollo":
        min_pc, min_em, max_fibra = 17.5, 3150.0, 5.0
    elif req_etapa == "Finalización":
        min_pc, min_em, max_fibra = 14.5, 3050.0, 6.0
    else:
        min_pc, min_em, max_fibra = 16.0, 3100.0, 7.5

    st.markdown("### 💰 Ingrese Costos Unitarios de Ingredientes ($ / kg)")

    c1, c2, c3 = st.columns(3)
    precio_maiz = c1.number_input("Maíz Grano ($/kg)", 2.0, 15.0, 5.50)
    precio_soya = c2.number_input("Pasta de Soya 48% ($/kg)", 5.0, 25.0, 12.00)
    precio_canola = c3.number_input("Pasta de Canola ($/kg)", 4.0, 20.0, 8.50)

    c4, c5, c6 = st.columns(3)
    precio_salvado = c4.number_input("Salvado de Trigo ($/kg)", 1.5, 10.0, 4.00)
    precio_aceite = c5.number_input(
        "Aceite Vegetal / Grasa ($/kg)", 10.0, 40.0, 22.00
    )
    precio_mineral = c6.number_input(
        "Núcleo Mineral / Vitamínico ($/kg)", 10.0, 80.0, 35.00
    )

    if st.button("🚀 Optimizar Dieta con Múltiples Ingredientes"):
        c = [
            precio_maiz,
            precio_soya,
            precio_canola,
            precio_salvado,
            precio_aceite,
            precio_mineral,
        ]

        A_ub = [
            [-8.5, -48.0, -36.0, -15.0, 0.0, 0.0],
            [-3350.0, -3200.0, -2800.0, -2500.0, -8500.0, 0.0],
            [2.0, 7.0, 11.5, 11.0, 0.0, 0.0],
        ]
        b_ub = [-min_pc, -min_em, max_fibra]

        A_eq = [[1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
        b_eq = [100.0]

        bounds = [
            (40.0, 85.0),
            (5.0, 40.0),
            (0.0, 20.0),
            (0.0, 20.0),
            (0.0, 5.0),
            (1.5, 3.5),
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
            proporciones = res.x
            costo_total_kg = res.fun / 100.0

            st.success("✅ ¡Dieta optimizada al mínimo costo con éxito!")

            res_df = pd.DataFrame(
                {
                    "Materia Prima / Ingrediente": [
                        "Maíz Grano",
                        "Pasta de Soya 48%",
                        "Pasta de Canola",
                        "Salvado de Trigo",
                        "Aceite Vegetal / Grasa",
                        "Núcleo Mineral / Vitamínico",
                    ],
                    "Inclusión en la Dieta (%)": [
                        round(p, 2) for p in proporciones
                    ],
                    "Cantidad por Tonelada (kg)": [
                        round(p * 10, 2) for p in proporciones
                    ],
                }
            )

            res_df_filtrado = res_df[res_df["Inclusión en la Dieta (%)"] > 0.05]

            st.table(res_df_filtrado)
            st.metric(
                label="Costo Estimado de la Fórmula",
                value=f"${costo_total_kg:.2f} MXN / kg",
            )
        else:
            st.error(
                "⚠️ No se encontró una solución factible con los precios o restricciones actuales. Intenta ajustar los rangos de costos o relajar ligeramente las restricciones de nutrientes."
            )

# ==========================================
# PESTAÑA 3: CERDAS EN LACTANCIA Y CRÍA
# ==========================================
with tab_lactancia:
    st.subheader(
        "🍼 Módulo de Nutrición, Cría y Soporte Metabólico en Cerdas Lactantes"
    )
    st.markdown(
        "Optimización del rendimiento reproductivo y lácteo de la cerda, integrando el impacto del entorno térmico sobre la supervivencia y ganancia de la camada."
    )

    col_l1, col_l2 = st.columns(2)

    with col_l1:
        st.markdown("### 📋 Variables Reproductivas y de Cría")
        paridad_cerda = st.selectbox(
            "Número de Paridad de la Cerda",
            [
                "Primeriza (Paridad 1 - Mayor sensibilidad metabólica)",
                "Multípara (Paridad 2 a 5 - Pico productivo)",
                "Longevidad (> Paridad 6)",
            ],
        )
        num_nacidos_vivos = st.number_input(
            "Lechones Nacidos Vivos en Camada",
            min_value=4,
            max_value=22,
            value=12,
        )
        dias_lactancia = st.slider(
            "Duración de la Lactancia (Días)", 14, 35, 21
        )
        peso_destete_objetivo = st.number_input(
            "Peso Objetivo por Lechón al Destete (kg)", 5.0, 9.0, 6.5
        )

    with col_l2:
        st.markdown("### 📊 Estimación Biológica y Ajuste por ITH")

        # Ajuste de consumo de la cerda por paridad y estrés térmico
        factor_paridad = 0.90 if "Primeriza" in paridad_cerda else 1.00
        consumo_diario_cerda = (2.0 + (num_nacidos_vivos * 0.42)) * factor_paridad

        if thi_calculado > 74.0:
            # Depresión de consumo por calor en lactancia
            consumo_diario_cerda *= 1.0 - ((thi_calculado - 74.0) * 0.025)

        consumo_total_lactancia = consumo_diario_cerda * dias_lactancia
        leche_producida_estimada = peso_destete_objetivo * num_nacidos_vivos * 3.8

        st.metric(
            label="Consumo Diario Sugerido para la Cerda",
            value=f"{consumo_diario_cerda:.2f} kg/día",
        )
        st.metric(
            label="Consumo Total Acumulado en Lactancia",
            value=f"{consumo_total_lactancia:,.1f} kg",
        )
        st.metric(
            label="Producción Láctea Estimada Total",
            value=f"{leche_producida_estimada:,.1f} kg de leche",
        )

    st.markdown("---")
    st.markdown(
        "### 💡 Recomendaciones Científicas para el Éxito de la Cría"
    )

    col_rec1, col_rec2 = st.columns(2)
    with col_rec1:
        st.info(
            """
        * **Nutrición de Precisión en Lactancia:**
          * **Proteína Cruda:** 17.5% - 18.5% (con mínimo 1.0% de Lisina estandarizada ileal digestible).
          * **Energía Metabolizable:** 3,350 kcal/kg para contrarrestar el balance energético negativo (BEN).
          * **Fibra Funcional:** 6% para estimular tránsito gastrointestinal y prevenir el síndrome MMA (Mastitis-Metritis-Agalactia).
        """
        )
    with col_rec2:
        st.success(
            """
        * **Manejo del Lechón y Bioseguridad:**
          * **Temperatura en Nido:** 32°C - 34°C en la primera semana de vida, con reducción gradual de 2°C por semana.
          * **Hidratación de la Cerda:** Suministro de **25 a 35 litros de agua fresca** al día para asegurar el reflejo de bajada de leche.
          * **Manejo de Calostro:** Garantizar una ingesta mínima de 200-250 g de calostro por lechón en sus primeras 6 horas de vida.
        """
        )

st.markdown("---")
st.caption(
    "Porcidex v4.0 | Creado y desarrollado por el Dr. Alejandro Castañeda Correa"
)
