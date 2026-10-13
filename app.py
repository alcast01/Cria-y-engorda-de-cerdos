import numpy as np
import pandas as pd
from scipy.optimize import linprog
import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="PorcinoMetrics | Nutrición y Producción Porcina",
    page_icon="🐖",
    layout="wide",
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
        '<p class="main-header">PorcinoMetrics: Sistema Integral Porcino</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="sub-header">"Nutrición de precisión, optimización de costos y manejo reproductivo"</p>',
        unsafe_allow_html=True,
    )

st.markdown("---")
st.markdown(
    '<p class="creator-tag">Creado y desarrollado por el Dr. Alejandro Castañeda Correa</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# --- NAVEGACIÓN POR PESTAÑAS ---
tab_engorda, tab_formulacion, tab_lactancia = st.tabs(
    [
        "📈 Engorda y Control Ambiental",
        "🧮 Formulación al Mínimo Costo",
        "🍼 Cerdas en Lactancia",
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
        st.markdown("### 🎛️ Parámetros del Lote")
        etapa = st.selectbox(
            "Etapa Productiva",
            ["Iniciación", "Desarrollo y Crecimiento", "Finalización"],
            key="etapa_eng",
        )
        raza = st.selectbox(
            "Perfil Genético / Raza",
            [
                "Comercial / Híbrido (Yorkshire x Landrace x Duroc)",
                "Línea Materna (Landrace / Large White)",
                "Línea Paterna (Duroc / Pietrain)",
            ],
            key="raza_eng",
        )

        st.markdown("### 🌡️ Ambiente y Estrés Térmico")
        temp_amb = st.slider(
            "Temperatura Ambiental Promedio (°C)",
            10.0,
            38.0,
            24.0,
            0.5,
            key="temp_eng",
        )
        humedad = st.slider(
            "Humedad Relativa (%)", 30.0, 90.0, 65.0, 5.0, key="hum_eng"
        )

        peso_inicial = st.number_input(
            "Peso Inicial Promedio (kg)",
            min_value=7.0,
            max_value=110.0,
            value=(
                15.0
                if etapa == "Iniciación"
                else (35.0 if etapa == "Desarrollo y Crecimiento" else 70.0)
            ),
            key="pi_eng",
        )
        peso_objetivo = st.number_input(
            "Peso Objetivo / Salida (kg)",
            min_value=10.0,
            max_value=130.0,
            value=(
                35.0
                if etapa == "Iniciación"
                else (70.0 if etapa == "Desarrollo y Crecimiento" else 115.0)
            ),
            key="pf_eng",
        )
        num_animales = st.number_input(
            "Número de Animales en el Lote",
            min_value=1,
            max_value=2000,
            value=100,
            key="n_eng",
        )

    with col_s2:
        # Modelo de cálculo zootécnico
        if etapa == "Iniciación":
            temp_optima = 24.0
            base_gdp = 0.65
            base_ca = 1.55
            base_pc = 21.0
            base_em = 3300
        elif etapa == "Desarrollo y Crecimiento":
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

        diff_temp = temp_amb - temp_optima
        factor_estres = 1.0
        if diff_temp > 2.0:
            factor_estres = max(0.70, 1.0 - ((diff_temp - 2.0) * 0.03))
        elif diff_temp < -3.0:
            factor_estres = max(0.85, 1.0 - (abs(diff_temp + 3.0) * 0.015))

        if "Paterna" in raza:
            base_gdp *= 1.08
            base_ca *= 0.95
        elif "Materna" in raza:
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

        st.markdown(f"### 📋 Resultados de Modelación: **{etapa}**")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(
            "Ganancia Diaria (GDP)",
            f"{gdp_ajustada:.2f} kg/d",
            delta=f"{((gdp_ajustada - base_gdp)/base_gdp)*100:.1f}% amb",
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
            **Nutrición Sugerida:**
            * **Proteína Cruda:** {base_pc:.1f}%
            * **Energía Metabolizable:** {base_em} kcal/kg
            * **Alimento Total Lote:** {consumo_total_lote:,.1f} kg ({round(consumo_total_lote/40)} sacos de 40kg)
            """
            )
        with c_amb:
            if diff_temp > 3.0:
                st.warning(
                    f"⚠️ **Alerta Estrés Calórico:** Temperatura ({temp_amb}°C) sobre confort ({temp_optima}°C). Evaluar ventilación o densidad energética."
                )
            elif diff_temp < -3.0:
                st.info(
                    f"❄️ **Alerta Estrés por Frío:** Temperatura baja ({temp_amb}°C). Mayor demanda energética."
                )
            else:
                st.success("✅ **Zona de Confort Óptima**")

        st.markdown("### 📈 Proyección de Crecimiento")
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
        "Este modelo utiliza programación lineal para resolver la mezcla óptima de ingredientes al menor costo posible, satisfaciendo los requerimientos mínimos y máximos nutricionales para la etapa seleccionada."
    )

    # Corregido: se usa st.columns(2) para que coincida con el desempaquetado
    col_f1, col_f2 = st.columns(2)

    with col_f1:
        req_etapa = st.selectbox(
            "Seleccionar Etapa para Formulación",
            ["Iniciación", "Desarrollo", "Finalización"],
        )

    if req_etapa == "Iniciación":
        min_pc, min_em, max_fibra = 21.0, 3250.0, 3.5
    elif req_etapa == "Desarrollo":
        min_pc, min_em, max_fibra = 17.5, 3150.0, 5.0
    else:
        min_pc, min_em, max_fibra = 14.5, 3050.0, 6.0

    st.markdown("### 💰 Ingrese Costos Unitarios de Ingredientes ($ / kg)")
    c_col1, c_col2, c_col3, c_col4 = st.columns(4)
    precio_maiz = c_col1.number_input("Maíz Grano ($/kg)", 2.0, 15.0, 5.50)
    precio_soya = c_col2.number_input(
        "Pasta de Soya 48% ($/kg)", 5.0, 25.0, 12.00
    )
    precio_salvado = c_col3.number_input("Salvado de Trigo ($/kg)", 1.5, 10.0, 4.00)
    precio_aceite = c_col4.number_input(
        "Aceite Vegetal / Grasa ($/kg)", 10.0, 40.0, 22.00
    )

    if st.button("🚀 Optimizar Dieta al Mínimo Costo"):
        c = [precio_maiz, precio_soya, precio_salvado, precio_aceite]

        A_ub = [
            [-9.0, -48.0, -15.0, 0.0],
            [-3350.0, -3200.0, -2500.0, -8500.0],
            [2.0, 7.0, 11.0, 0.0],
        ]
        b_ub = [-min_pc, -min_em, max_fibra]

        A_eq = [[1.0, 1.0, 1.0, 1.0]]
        b_eq = [100.0]

        bounds = [(0, 85), (5, 45), (0, 25), (0, 6)]

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

            st.success("✅ ¡Optimización calculada exitosamente!")

            res_df = pd.DataFrame(
                {
                    "Ingrediente": [
                        "Maíz Grano",
                        "Pasta de Soya 48%",
                        "Salvado de Trigo",
                        "Aceite Vegetal / Grasa",
                    ],
                    "Inclusión (%)": [round(p, 2) for p in proporciones],
                    "Cantidad por Tonelada (kg)": [
                        round(p * 10, 2) for p in proporciones
                    ],
                }
            )

            st.table(res_df)
            st.metric(
                label="Costo Estimado de la Dieta",
                value=f"${costo_total_kg:.2f} MXN / kg",
            )
        else:
            st.error(
                "⚠️ No se encontró solución factible con los precios o restricciones actuales. Ajuste los requerimientos o márgenes de ingredientes."
            )

# ==========================================
# PESTAÑA 3: CERDAS EN LACTANCIA
# ==========================================
with tab_lactancia:
    st.subheader("🍼 Módulo de Nutrición y Manejo de Cerdas en Lactancia")
    st.markdown(
        "Garantiza el éxito de la camada mediante el soporte metabólico de la cerda lactante, previniendo la pérdida excesiva de condición corporal y maximizando la producción láctea."
    )

    col_l1, col_l2 = st.columns(2)

    with col_l1:
        st.markdown("### 📋 Datos del Parto y Camada")
        num_nacidos_vivos = st.number_input(
            "Lechones Nacidos Vivos", min_value=4, max_value=22, value=12
        )
        dias_lactancia = st.slider(
            "Duración de la Lactancia (Días)", 14, 35, 21
        )
        peso_destete_objetivo = st.number_input(
            "Peso Objetivo por Lechón al Destete (kg)", 5.0, 9.0, 6.5
        )
        temp_sala_parto = st.slider(
            "Temperatura en Sala de Parto (°C)", 18.0, 28.0, 22.0, 0.5
        )

    with col_l2:
        st.markdown("### 📊 Estimación de Requerimientos y Consumo")

        consumo_diario_cerda = 2.0 + (num_nacidos_vivos * 0.42)
        if temp_sala_parto > 24.0:
            consumo_diario_cerda *= 1.0 - ((temp_sala_parto - 24.0) * 0.04)

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
    st.markdown("### 💡 Recomendaciones Clave para la Supervivencia de la Cría")

    col_rec1, col_rec2 = st.columns(2)
    with col_rec1:
        st.info(
            """
        * **Perfil Nutricional en Lactancia:**
          * **Proteína Cruda:** 17.0% - 18.5% (con mínimo 0.95% de Lisina digestible).
          * **Energía Metabolizable:** 3,300 - 3,400 kcal/kg para evitar catabolismo excesivo de reservas corporales.
          * **Fibra Funcional:** 5% a 6% para prevenir estreñimiento periparto y fomentar motilidad intestinal.
        """
        )
    with col_rec2:
        st.success(
            """
        * **Manejo Ambiental y del Lechón:**
          * **Zona de Confort del Lechón:** Mantener nidos con lámparas o placas térmicas a **32°C - 34°C** la primera semana, reduciendo gradualmente.
          * **Agua Ad Libitum:** Una cerda lactante requiere de **25 a 35 litros de agua fresca diarios** para un óptimo reflejo de eyección láctea.
          * **Fraccionamiento:** Suministrar alimento mínimo 3 a 4 veces al día para estimular el apetito en climas cálidos.
        """
        )

st.markdown("---")
st.caption(
    "PorcinoMetrics v2.0 | Creado y desarrollado por el Dr. Alejandro Castañeda Correa"
)
