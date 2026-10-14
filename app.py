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
    .pricing-card {
        background-color: #ffffff;
        border: 1px solid #dce2e6;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        transition: transform 0.2s;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# GESTIÓN DE ESTADOS Y AUTENTICACIÓN (MFA)
# ==========================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "fase_2fa" not in st.session_state:
    st.session_state.fase_2fa = False
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = ""
if "plan_suscripcion" not in st.session_state:
    st.session_state.plan_suscripcion = "Granja Comercial (Profesional)"

USUARIOS_DB = {
    "alejandro": {"password": "porcidex2026", "pin_2fa": "849201", "nombre": "Dr. Alejandro Castañeda Correa", "rol": "Administrador / Investigador"},
    "productor": {"password": "cerdos123", "pin_2fa": "123456", "nombre": "Productor Porcícola Zacatecas", "rol": "Productor Comercial"},
    "nutriologo": {"password": "nutricion", "pin_2fa": "654321", "nombre": "MVZ Nutrición Porcina", "rol": "Nutriólogo Asesor"},
}

# ==========================================
# PÁGINA DE INICIO: PLANES Y LOGIN (PRE-LOGIN)
# ==========================================
if not st.session_state.autenticado:
    st.markdown(
        """
        <div class="brand-container">
            <div class="brand-logo-badge">🐖 🧬 SISTEMAS DE NUTRICIÓN PORCINA DE PRECISIÓN Y PLF v3.0</div>
            <h1 class="brand-title">PORCIDEX™ PRO</h1>
            <p class="brand-slogan">"Inteligencia Artificial, Nutrición Dinámica y Rentabilidad Predictiva al Servicio de la Porcicultura"</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.subheader("💳 Elija el Plan de Suscripción Ideal para su Granja")
    st.markdown("Explore nuestras opciones diseñadas para pequeños productores, granjas comerciales e integradoras industriales:")

    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        st.markdown(
            """
            <div class="pricing-card">
                <h3>🌱 Productor Independiente</h3>
                <h2 style="color: #1f4e78;">$499 <small>MXN/mes</small></h2>
                <p><b>Para granjas familiares y lotes pequeños (< 500 cerdos)</b></p>
                <hr>
                <ul style="text-align: left; font-size: 0.9rem;">
                    <li>Simulador de Engorda y GDP</li>
                    <li>Evaluación de Rentabilidad Básica</li>
                    <li>Cálculo de Consumo de Alimento</li>
                    <li>Soporte Técnico vía Email</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Elegir Plan Básico", key="btn_p1_front", use_container_width=True):
            st.session_state.plan_suscripcion = "Productor Independiente (Básico)"
            st.success("✅ Plan Básico seleccionado. Proceda a iniciar sesión.")

    with col_p2:
        st.markdown(
            """
            <div class="pricing-card" style="border: 2px solid #27ae60;">
                <span class="status-badge-green" style="margin-bottom:0.5rem;">MÁS POPULAR</span>
                <h3>📈 Granja Comercial</h3>
                <h2 style="color: #27ae60;">$1,499 <small>MXN/mes</small></h2>
                <p><b>Para granjas medianas y comerciales (500 - 3,000 cerdos)</b></p>
                <hr>
                <ul style="text-align: left; font-size: 0.9rem;">
                    <li><b>Todo lo del Plan Básico +</b></li>
                    <li>Formulación por Programación Lineal</li>
                    <li>Módulo de Cerdas en Lactancia</li>
                    <li>Análisis Financiero Avanzado y ROI</li>
                    <li>Exportación de Reportes PDF Profesionales</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Elegir Plan Comercial", key="btn_p2_front", use_container_width=True):
            st.session_state.plan_suscripcion = "Granja Comercial (Profesional)"
            st.success("✅ Plan Comercial seleccionado. Proceda a iniciar sesión.")

    with col_p3:
        st.markdown(
            """
            <div class="pricing-card">
                <h3>🏭 Industrial & Integradoras</h3>
                <h2 style="color: #c0392b;">$3,899 <small>MXN/mes</small></h2>
                <p><b>Para empresas integradoras y macrogranjas (> 3,000 cerdos)</b></p>
                <hr>
                <ul style="text-align: left; font-size: 0.9rem;">
                    <li><b>Todo lo del Plan Comercial +</b></li>
                    <li>Conexión con Sensores PLF e IoT</li>
                    <li>Monitoreo Térmico THI en Tiempo Real</li>
                    <li>Permisos Multi-usuario por Granja</li>
                    <li>Soporte Técnico Prioritario 24/7</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Elegir Plan Industrial", key="btn_p3_front", use_container_width=True):
            st.session_state.plan_suscripcion = "Industrial & Integradoras (Enterprise)"
            st.success("✅ Plan Industrial seleccionado. Proceda a iniciar sesión.")

    st.markdown("---")
    
    # SECCIÓN DE LOGIN Y 2FA
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])

    with col_l2:
        st.markdown(f"### 🔐 Acceso de Usuario • Plan Seleccionado: **{st.session_state.plan_suscripcion}**")
        
        if not st.session_state.fase_2fa:
            with st.form("form_login"):
                usuario_input = st.text_input("Usuario", placeholder="Ej. alejandro, productor, nutriologo")
                password_input = st.text_input("Contraseña", type="password", placeholder="••••••••")
                btn_login = st.form_submit_button("Continuar a Verificación 2FA", use_container_width=True)

                if btn_login:
                    usuario_limpio = usuario_input.strip().lower()
                    if usuario_limpio in USUARIOS_DB and USUARIOS_DB[usuario_limpio]["password"] == password_input:
                        st.session_state.fase_2fa = True
                        st.session_state.usuario_temporal = usuario_limpio
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos.")
        else:
            st.info(f"📱 **Doble Factor de Autenticación (2FA):** Código PIN de seguridad (Demo PIN: `{USUARIOS_DB[st.session_state.usuario_temporal]['pin_2fa']}`).")
            with st.form("form_2fa"):
                pin_input = st.text_input("Ingrese PIN de 6 Dígitos", max_chars=6, type="password")
                btn_validar_2fa = st.form_submit_button("Verificar y Acceder a la Plataforma", use_container_width=True)
                btn_regresar = st.form_submit_button("Volver", use_container_width=True)

                if btn_validar_2fa:
                    if pin_input == USUARIOS_DB[st.session_state.usuario_temporal]["pin_2fa"]:
                        st.session_state.autenticado = True
                        st.session_state.usuario_actual = st.session_state.usuario_temporal
                        st.session_state.fase_2fa = False
                        st.rerun()
                    else:
                        st.error("❌ PIN de autenticación incorrecto.")
                if btn_regresar:
                    st.session_state.fase_2fa = False
                    st.rerun()

        st.markdown("💡 *Credenciales del Creador: Usuario: `alejandro` | Contraseña: `porcidex2026` | PIN: `849201`*")
    
    st.stop()

# ==========================================
# APLICACIÓN PRINCIPAL (UNA VEZ AUTENTICADO)
# ==========================================

st.markdown(
    f"""
    <div class="brand-container">
        <div class="brand-logo-badge">🐖 🧬 SISTEMAS DE NUTRICIÓN PORCINA DE PRECISIÓN Y PLF v3.0</div>
        <h1 class="brand-title">PORCIDEX™ PRO</h1>
        <p class="brand-slogan">"Inteligencia Artificial, Nutrición Dinámica y Rentabilidad Predictiva"</p>
        <div class="meta-info-container">
            <span>Usuario: <strong class="meta-item">{USUARIOS_DB[st.session_state.usuario_actual]['nombre']}</strong></span>
            <span>•</span>
            <span>Rol: <strong class="creator-tag">{USUARIOS_DB[st.session_state.usuario_actual]['rol']}</strong></span>
            <span>•</span>
            <span>Suscripción Activa: <strong class="meta-item">{st.session_state.plan_suscripcion}</strong></span>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

if st.sidebar.button("🚪 Cerrar Sesión Segura"):
    st.session_state.autenticado = False
    st.session_state.fase_2fa = False
    st.session_state.usuario_actual = ""
    st.rerun()

# ==========================================
# PANEL IZQUIERDO: VARIABLES PLF Y AMBIENTALES
# ==========================================
st.sidebar.header("🔬 Panel PLF & Variables Biológicas")

st.sidebar.markdown("---")
st.sidebar.subheader("🌡️ Ambiente y Estrés Térmico (THI Dinámico)")
temp_amb = st.sidebar.slider("Temperatura Ambiental (°C)", 10.0, 38.0, 24.0, 0.5)
hum_relativa = st.sidebar.slider("Humedad Relativa (%)", 20.0, 95.0, 65.0, 5.0)
vel_aire = st.sidebar.slider("Velocidad del Aire / Ventilación (m/s)", 0.0, 2.5, 0.4, 0.1)

thi_calculado = temp_amb - (0.55 - (0.55 * (hum_relativa / 100.0))) * (temp_amb - 14.4)

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
uso_pfs = st.sidebar.checkbox("Activar Alimentación de Precisión (PFS con RFID)", value=True)
uso_vision_3d = st.sidebar.checkbox("Usar Biometría por Visión Artificial 3D", value=True)
monitoreo_acustico = st.sidebar.checkbox("Activar Alerta Acústica Temprana (TOS/Agua)", value=True)

# --- NAVEGACIÓN PRINCIPAL POR PESTAÑAS ---
tab_engorda, tab_formulacion, tab_lactancia, tab_resumen = st.tabs(
    [
        "📈 Engorda, PLF y Finanzas",
        "🧮 Formulación y Precios",
        "🍼 Cerdas en Lactancia",
        "📋 Resumen Técnico y PDF",
    ]
)

# ==========================================
# PESTAÑA 1: ENGORDA, PLF Y FINANZAS
# ==========================================
with tab_engorda:
    st.subheader("Módulo de Simulación Dinámica, PLF y Rentabilidad Financiera")
    col_s1, col_s2 = st.columns([1, 2])

    with col_s1:
        st.markdown("### 📋 Parámetros del Lote y Genética")
        etapa_eng = st.selectbox("Etapa Productiva", ["Iniciación", "Desarrollo y Crecimiento", "Finalización"])
        raza_eng = st.selectbox("Perfil Genético", ["Híbrido Comercial (Yorkshire x Landrace x Duroc)", "Línea Materna Pura", "Línea Paterna Hipermuscular"])
        peso_inicial = st.number_input("Peso Inicial Promedio (kg)", 7.0, 110.0, 15.0)
        peso_objetivo = st.number_input("Peso Objetivo / Salida (kg)", 10.0, 130.0, 115.0)
        num_animales = st.number_input("Tamaño del Lote (Animales)", 1, 5000, 200)

        st.markdown("---")
        st.markdown("### ⚡ Ajuste Manual de GDP")
        base_gdp_def = 0.68 if etapa_eng == "Iniciación" else (0.95 if etapa_eng == "Desarrollo y Crecimiento" else 1.10)
        gdp_manual = st.slider("Ajustar Ganancia Diaria de Peso Objetivo (kg/día)", 0.30, 1.50, float(base_gdp_def), 0.01)

        st.markdown("---")
        st.markdown("### 💵 Parámetros Financieros y de Mercado")
        precio_venta_kg = st.number_input("Precio de Venta del Cerdo en Pie ($/kg vivo)", 20.0, 100.0, 48.0, step=0.5)
        costo_lechon_compra = st.number_input("Costo de Compra del Lechón/Cerdo ($/cabeza)", 0.0, 3000.0, 850.0, step=25.0)
        costo_sanidad_cerdo = st.number_input("Gastos de Sanidad y Vacunas ($/cerdo)", 0.0, 500.0, 65.0, step=5.0)
        costo_flete_cerdo = st.number_input("Flete y Logística Comercial ($/cerdo)", 0.0, 300.0, 40.0, step=5.0)
        costo_operativo_fijo = st.number_input("Mano de Obra y Servicios ($/cerdo)", 0.0, 1000.0, 120.0, step=10.0)

    with col_s2:
        if etapa_eng == "Iniciación":
            temp_optima, base_ca = 24.0, 1.50
        elif etapa_eng == "Desarrollo y Crecimiento":
            temp_optima, base_ca = 20.0, 2.20
        else:
            temp_optima, base_ca = 18.0, 2.75

        diff_temp = temp_amb - temp_optima
        factor_estres = 1.0
        if diff_temp > 2.0:
            factor_estres = max(0.60, 1.0 - (((diff_temp - 2.0) * 0.038) - min(0.18, vel_aire * 0.09)))
        elif diff_temp < -3.0:
            factor_estres = max(0.82, 1.0 - (abs(diff_temp + 3.0) * 0.015))

        if "Estándar" in espacio_vital: base_ca *= 1.03
        elif "Hacinamiento" in espacio_vital: base_ca *= 1.12

        if "Medio" in estatus_inmunologico: base_ca *= 1.05
        elif "Bajo" in estatus_inmunologico: base_ca *= 1.20

        if uso_pfs: base_ca *= 0.92

        gdp_ajustada = gdp_manual * factor_estres
        ca_ajustada = base_ca / factor_estres
        dias_estudio = max(1, round((peso_objetivo - peso_inicial) / max(0.05, gdp_ajustada)))
        consumo_diario = gdp_ajustada * ca_ajustada
        consumo_total_cerdo = consumo_diario * dias_estudio
        consumo_total_lote = consumo_total_cerdo * num_animales

        costo_alimento_kg = 6.80
        costo_alimento_cerdo = consumo_total_cerdo * costo_alimento_kg
        costo_total_cerdo = costo_alimento_cerdo + costo_lechon_compra + costo_sanidad_cerdo + costo_flete_cerdo + costo_operativo_fijo
        ingreso_bruto_cerdo = peso_objetivo * precio_venta_kg
        margen_neto_cerdo = ingreso_bruto_cerdo - costo_total_cerdo
        
        costo_total_lote = costo_total_cerdo * num_animales
        utilidad_neta_lote = margen_neto_cerdo * num_animales
        roi_porcentaje = (utilidad_neta_lote / max(1.0, costo_total_lote)) * 100.0
        punto_equilibrio_kg = costo_total_cerdo / max(1.0, peso_objetivo)

        st.markdown(f"### 📋 Evaluador de Condición Zootécnica y Financiera: **{etapa_eng}**")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("GDP Operativa", f"{gdp_ajustada:.2f} kg/d")
        m2.metric("Conversión (CA)", f"{ca_ajustada:.2f}")
        m3.metric("Duración Engorda", f"{dias_estudio} días")
        m4.metric("Consumo Diario", f"{consumo_diario:.2f} kg")

        st.markdown("---")
        st.markdown("### 💰 Análisis Financiero y Margen Económico del Lote")
        f1, f2, f3, f4 = st.columns(4)
        f1.metric("Costo Total / Cerdo", f"${costo_total_cerdo:,.2f} MXN")
        f2.metric("Ingreso Bruto / Cerdo", f"${ingreso_bruto_cerdo:,.2f} MXN")
        f3.metric("Margen Neto / Cerdo", f"${margen_neto_cerdo:,.2f} MXN", delta=f"ROI: {roi_porcentaje:.1f}%")
        f4.metric("Utilidad Neta del Lote", f"${utilidad_neta_lote:,.2f} MXN")

        st.markdown("### 📈 Curva Biológica de Crecimiento Estocástico")
        semanas = np.arange(1, dias_estudio + 1, 7)
        pesos_proy = [min(peso_objetivo, peso_inicial + (gdp_ajustada * d)) for d in semanas]
        df_grafica = pd.DataFrame({"Día": semanas, "Peso Proyectado (kg)": [round(p, 2) for p in pesos_proy]})
        st.line_chart(df_grafica.set_index("Día"), color=["#1f4e78"])

# ==========================================
# PESTAÑA 2: FORMULACIÓN AVANZADA
# ==========================================
with tab_formulacion:
    st.subheader("🧮 Módulo de Formulación de Precisión al Mínimo Costo")
    etapa_form = st.selectbox("Etapa para Formulación", ["Iniciación (20-35 kg)", "Desarrollo (35-70 kg)", "Finalización (70-115 kg)"], key="etap_form_multi")

    min_ne, min_sid_lys, min_pc, max_fibra = (2350.0, 0.95, 19.5, 5.0) if "Iniciación" in etapa_form else ((2280.0, 0.80, 16.5, 6.5) if "Desarrollo" in etapa_form else (2220.0, 0.68, 14.0, 7.5))

    datos_maestros = [
        {"Ingrediente": "Maíz Grano", "Disponible": True, "Costo ($/kg)": 5.50, "NE (kcal/kg)": 2650.0, "SID Lys (%)": 0.26, "PC (%)": 8.5, "Fibra (%)": 2.0, "bound": (20.0, 80.0), "base": 58.0},
        {"Ingrediente": "Pasta de Soya 48%", "Disponible": True, "Costo ($/kg)": 12.00, "NE (kcal/kg)": 2240.0, "SID Lys (%)": 2.85, "PC (%)": 48.0, "Fibra (%)": 7.0, "bound": (10.0, 35.0), "base": 24.0},
        {"Ingrediente": "Salvado de Trigo", "Disponible": True, "Costo ($/kg)": 4.00, "NE (kcal/kg)": 1700.0, "SID Lys (%)": 0.65, "PC (%)": 15.0, "Fibra (%)": 11.0, "bound": (0.0, 12.0), "base": 5.0},
        {"Ingrediente": "DDGS de Maíz", "Disponible": True, "Costo ($/kg)": 6.80, "NE (kcal/kg)": 2350.0, "SID Lys (%)": 0.65, "PC (%)": 27.0, "Fibra (%)": 8.5, "bound": (0.0, 15.0), "base": 6.0},
        {"Ingrediente": "Núcleo Vitamínico-Mineral", "Disponible": True, "Costo ($/kg)": 38.00, "NE (kcal/kg)": 0.0, "SID Lys (%)": 0.0, "PC (%)": 0.0, "Fibra (%)": 0.0, "bound": (1.0, 3.5), "base": 2.5},
    ]

    df_editado = st.data_editor(pd.DataFrame(datos_maestros)[["Ingrediente", "Disponible", "Costo ($/kg)"]], hide_index=True, use_container_width=True)
    df_activos = df_editado[df_editado["Disponible"] == True]

    if not df_activos.empty:
        ings = df_activos["Ingrediente"].tolist()
        c = df_activos["Costo ($/kg)"].tolist()
        res = linprog(c, A_ub=[[-d["NE (kcal/kg)"] for d in datos_maestros if d["Ingrediente"] in ings], [-d["SID Lys (%)"] for d in datos_maestros if d["Ingrediente"] in ings]], b_ub=[-min_ne, -min_sid_lys], A_eq=[[1.0]*len(ings)], b_eq=[100.0], method="highs")
        costo_kg = res.fun / 100.0 if res.success else 6.80
        st.success(f"⚖️ **Costo de Dieta Calculado:** `${costo_kg:.2f} MXN/kg` (`${costo_kg*1000:,.2f} MXN/Ton`)")

# ==========================================
# PESTAÑA 3: CERDAS EN LACTANCIA
# ==========================================
with tab_lactancia:
    st.subheader("🍼 Módulo Avanzado de Reproducción y Lactancia en Cerdas")
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        paridad = st.selectbox("Número de Paridad", ["Primeriza", "Multípara (2-5)", "Longevidad (>6)"])
        nacidos_vivos = st.number_input("Lechones Nacidos Vivos", 4, 22, 14)
        dias_lac = st.slider("Duración de la Lactancia (Días)", 18, 35, 21)
        peso_destete = st.number_input("Peso Objetivo por Lechón al Destete (kg)", 5.0, 9.5, 6.8)
    
    with col_l2:
        consumo_base = (2.1 + (nacidos_vivos * 0.44))
        leche_total = peso_destete * nacidos_vivos * 3.85 * 0.93
        st.metric("Consumo Diario Sugerido", f"{consumo_base:.2f} kg/día")
        st.metric("Producción Láctea Total Estimada", f"{leche_total:,.1f} kg")

# ==========================================
# FUNCION GENERADORA DE PDF
# ==========================================
def generar_pdf_reporte(etapa_eng, raza_eng, num_animales, peso_inicial, peso_objetivo, gdp_ajustada, ca_ajustada, dias_estudio, consumo_total_cerdo, consumo_total_lote, costo_total_cerdo, ingreso_bruto_cerdo, margen_neto_cerdo, utilidad_neta_lote, roi_porcentaje, punto_equilibrio_kg):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "PORCIDEX PRO v3.0 - REPORTE DE PRODUCCION", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 5, f"Plan: {st.session_state.plan_suscripcion} | Usuario: {USUARIOS_DB[st.session_state.usuario_actual]['nombre']}", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, f"- Etapa: {etapa_eng} | Animales: {num_animales:,} cerdos", ln=True)
    pdf.cell(0, 5, f"- Peso: {peso_inicial:.1f} kg -> {peso_objetivo:.1f} kg | Días: {dias_estudio} días", ln=True)
    pdf.cell(0, 5, f"- GDP Operativa: {gdp_ajustada:.2f} kg/día | Conversión: {ca_ajustada:.2f}", ln=True)
    pdf.cell(0, 5, f"- Costo Total por Cerdo: ${costo_total_cerdo:,.2f} MXN", ln=True)
    pdf.cell(0, 5, f"- Margen Neto por Cerdo: ${margen_neto_cerdo:,.2f} MXN", ln=True)
    pdf.cell(0, 5, f"- Utilidad Neta del Lote: ${utilidad_neta_lote:,.2f} MXN (ROI: {roi_porcentaje:.1f}%)", ln=True)
    pdf.cell(0, 5, f"- Punto de Equilibrio: ${punto_equilibrio_kg:.2f} MXN / kg vivo", ln=True)
    return bytes(pdf.output())

# ==========================================
# PESTAÑA 4: RESUMEN TÉCNICO Y PDF
# ==========================================
with tab_resumen:
    st.subheader("📋 Hoja de Balance Integral y Generación de Reporte PDF")
    
    col_prod, col_nutri = st.columns(2)
    with col_prod:
        st.markdown(
            f"""
        <div class="report-card">
            <h3 style="color: #1f4e78; margin-top:0;">📊 Resumen Ejecutivo y Financiero</h3>
            <ul>
                <li><b>Suscripción Activa:</b> {st.session_state.plan_suscripcion}</li>
                <li><b>Etapa Evaluada:</b> {etapa_eng} ({num_animales:,} cerdos)</li>
                <li><b>GDP Operativa:</b> {gdp_ajustada:.2f} kg/día | <b>CA:</b> {ca_ajustada:.2f}</li>
                <li><b>Margen Neto / Cerdo:</b> ${margen_neto_cerdo:,.2f} MXN</li>
                <li><b>Utilidad Neta Lote:</b> ${utilidad_neta_lote:,.2f} MXN (ROI: {roi_porcentaje:.1f}%)</li>
                <li><b>Punto de Equilibrio:</b> ${punto_equilibrio_kg:.2f} MXN/kg</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col_nutri:
        st.markdown(
            f"""
        <div class="report-card">
            <h3 style="color: #2e7d32; margin-top:0;">🧬 Confort Ambiental y PLF</h3>
            <ul>
                <li><b>Índice THI:</b> {thi_calculado:.1f}</li>
                <li><b>Ventilación:</b> {vel_aire} m/s</li>
                <li><b>Espacio Vital:</b> {espacio_vital.split('(')[0]}</li>
                <li><b>Estatus Sanitario:</b> {estatus_inmunologico.split('/')[0]}</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    pdf_bytes = generar_pdf_reporte(etapa_eng, raza_eng, num_animales, peso_inicial, peso_objetivo, gdp_ajustada, ca_ajustada, dias_estudio, consumo_total_cerdo, consumo_total_lote, costo_total_cerdo, ingreso_bruto_cerdo, margen_neto_cerdo, utilidad_neta_lote, roi_porcentaje, punto_equilibrio_kg)
    st.download_button("📄 Descargar Reporte Completo en PDF", data=pdf_bytes, file_name=f"Reporte_Porcidex_{etapa_eng}.pdf", mime="application/pdf")

st.markdown("---")
st.caption("Porcidex v3.0 Enterprise | S/N: PRX-2026-MX-9842 | Dr. Alejandro Castañeda Correa")
