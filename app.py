import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from pathlib import Path

# ─── CONFIGURACIÓN ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PMO Brescia 19 — Planning Master",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

ARCHIVO_CSV   = "BASE DE DATOS PLANNIG.csv"
FECHA_APERTURA = datetime(2026, 8, 3)
FECHA_INICIO   = datetime(2026, 5, 18)

FASES = [
    "DEMOLICIÓN", "TRABAJOS PREVIOS", "ALBAÑILERÍA",
    "IMPERMEABILIZACIÓN", "FONTANERÍA", "ELECTRICIDAD",
    "CLIMATIZACIÓN", "CARPINTERÍA EXT.", "PCI - INCENDIOS",
    "RECEPCIÓN", "FALSOS TECHOS", "REVESTIMIENTOS",
    "ACABADOS", "EQUIPAMIENTO", "ACCESIBILIDAD PMR",
    "INSPECCIONES", "HITOS",
]
ESTADOS = ["PENDIENTE", "EN PROCESO", "AMARILLO", "ROJO", "COMPLETADO"]

COLOR_ESTADO = {
    "COMPLETADO":  "#2ecc71",
    "EN PROCESO":  "#3498db",
    "PENDIENTE":   "#95a5a6",
    "AMARILLO":    "#f1c40f",
    "ROJO":        "#e74c3c",
}

# ─── 1. BASE DE DATOS ─────────────────────────────────────────────────────────
def datos_iniciales() -> pd.DataFrame:
    filas = [
        # DEMOLICIÓN
        (1,  "DEMOLICIÓN",       "Local diáfano 760m2 - forjado limpio",                  "Munir/Ziad",      "2026-05-04", "2026-05-13", 100, "COMPLETADO",  "No"),
        # TRABAJOS PREVIOS
        (2,  "TRABAJOS PREVIOS", "Recibir presupuestos contratas",                         "Darío/Valentina", "2026-05-04", "2026-05-14", 100, "COMPLETADO",  "No"),
        (3,  "TRABAJOS PREVIOS", "Adjudicar contratas",                                    "Dirección",       "2026-05-04", "2026-05-15",  95, "COMPLETADO",  "No"),
        (4,  "TRABAJOS PREVIOS", "Cerrar planning de obra",                                "Darío",           "2026-05-04", "2026-05-16",  95, "COMPLETADO",  "No"),
        (5,  "TRABAJOS PREVIOS", "Pedir fabricación equipos clima",                        "Darío/Jose",      "2026-05-15", "2026-05-17", 100, "COMPLETADO",  "No"),
        (6,  "TRABAJOS PREVIOS", "Luis Electricidad — pedido cuadros",                     "Luis/Elecrea",    "2026-05-16", "2026-05-20",  80, "COMPLETADO",  "No"),
        (7,  "TRABAJOS PREVIOS", "Arrancar fabricación mueble recepción",                  "Munir",           "2026-05-25", "2026-06-12",   0, "EN PROCESO",  "No"),
        (8,  "TRABAJOS PREVIOS", "Arrancar fabricación plataforma acceso Hersan",          "Darío",           "2026-05-25", "2026-06-15",   0, "EN PROCESO",  "Sí"),
        # ALBAÑILERÍA
        (9,  "ALBAÑILERÍA",      "Replanteo general + trazado tabiquería",                 "Munir",           "2026-05-25", "2026-05-27",   0, "EN PROCESO",  "No"),
        (10, "ALBAÑILERÍA",      "Hueco técnico para clima — conductos",                   "Munir",           "2026-05-25", "2026-05-28",   0, "EN PROCESO",  "No"),
        (11, "ALBAÑILERÍA",      "Pletinas aluminio soporte ventanas x2",                  "Munir",           "2026-05-27", "2026-05-30",   0, "PENDIENTE",   "No"),
        (12, "ALBAÑILERÍA",      "Tabique humedad PLACO Glasroc X vestuarios",             "Munir",           "2026-05-27", "2026-06-10",   0, "PENDIENTE",   "No"),
        (13, "ALBAÑILERÍA",      "Tabique grandes alturas",                                "Munir",           "2026-05-27", "2026-06-07",   0, "PENDIENTE",   "No"),
        (14, "ALBAÑILERÍA",      "Tabique sala colectiva + CT + limpieza",                 "Munir",           "2026-05-27", "2026-06-07",   0, "PENDIENTE",   "No"),
        (15, "ALBAÑILERÍA",      "Tabiques staff",                                         "Munir",           "2026-05-27", "2026-06-02",   0, "PENDIENTE",   "No"),
        (16, "ALBAÑILERÍA",      "Trasdosado acústico Silentboard — muro colindante",      "Munir",           "2026-06-01", "2026-06-13",   0, "PENDIENTE",   "No"),
        (17, "ALBAÑILERÍA",      "Trasdosado acústico Silentboard 181m2 — fachada",        "Munir",           "2026-06-01", "2026-06-13",   0, "PENDIENTE",   "No"),
        (18, "ALBAÑILERÍA",      "Falsas vigas cajón técnico 54m",                         "Munir",           "2026-06-04", "2026-06-13",   0, "PENDIENTE",   "No"),
        # IMPERMEABILIZACIÓN
        (19, "IMPERMEABILIZACIÓN","Kerdi/Dry80 suelo vestuarios",                          "Fontanería",      "2026-06-05", "2026-06-13",   0, "PENDIENTE",   "No"),
        (20, "IMPERMEABILIZACIÓN","Subida paredes duchas hasta 2.10m",                     "Fontanería",      "2026-06-05", "2026-06-13",   0, "PENDIENTE",   "No"),
        (21, "IMPERMEABILIZACIÓN","Zócalo perimetral 20cm vestuarios",                     "Fontanería",      "2026-06-06", "2026-06-13",   0, "PENDIENTE",   "No"),
        (22, "IMPERMEABILIZACIÓN","Prueba de estanqueidad",                                "Fontanería",      "2026-06-11", "2026-06-15",   0, "PENDIENTE",   "No"),
        # FONTANERÍA
        (23, "FONTANERÍA",       "Colectores suspendidos PVC 110-125mm",                  "Fontanería",      "2026-06-08", "2026-06-16",   0, "PENDIENTE",   "No"),
        (24, "FONTANERÍA",       "Red pequeña evacuación PVC 32-110mm",                   "Fontanería",      "2026-06-08", "2026-06-16",   0, "PENDIENTE",   "No"),
        (25, "FONTANERÍA",       "Botes sifónicos PVC x5",                                "Fontanería",      "2026-06-10", "2026-06-14",   0, "PENDIENTE",   "No"),
        (26, "FONTANERÍA",       "Bajante interior PVC 110mm + aireador x3",              "Fontanería",      "2026-06-08", "2026-06-16",   0, "PENDIENTE",   "No"),
        (27, "FONTANERÍA",       "Acometida PE100 32mm + alimentación acero",             "Fontanería",      "2026-06-12", "2026-06-16",   0, "PENDIENTE",   "No"),
        (28, "FONTANERÍA",       "Tuberías PE-Xa 16/20/25mm distribución",               "Fontanería",      "2026-06-10", "2026-06-22",   0, "PENDIENTE",   "No"),
        (29, "FONTANERÍA",       "Válvulas + llaves de paso",                             "Fontanería",      "2026-06-15", "2026-06-19",   0, "PENDIENTE",   "No"),
        (30, "FONTANERÍA",       "Termos eléctricos Bosch 250L x2",                       "Fontanería",      "2026-06-20", "2026-06-28",   0, "PENDIENTE",   "No"),
        # ELECTRICIDAD
        (31, "ELECTRICIDAD",     "Canalización principal bandejas + cuadro IGA 63A",      "Luis/Elecrea",    "2026-05-25", "2026-05-30",   0, "EN PROCESO",  "No"),
        (32, "ELECTRICIDAD",     "Cableado circuitos fuerza máquinas cardio",             "Luis/Elecrea",    "2026-05-28", "2026-06-10",   0, "PENDIENTE",   "No"),
        (33, "ELECTRICIDAD",     "Cableado iluminación LED general",                      "Luis/Elecrea",    "2026-06-01", "2026-06-15",   0, "PENDIENTE",   "No"),
        (34, "ELECTRICIDAD",     "Foseados tiras LED perimetrales",                       "Luis/Elecrea",    "2026-06-15", "2026-07-01",   0, "PENDIENTE",   "No"),
        (35, "ELECTRICIDAD",     "Cuadros secundarios + protecciones",                    "Luis/Elecrea",    "2026-06-05", "2026-06-20",   0, "PENDIENTE",   "No"),
        (36, "ELECTRICIDAD",     "Alumbrado emergencia + señalización evacuación",         "Luis/Elecrea",    "2026-06-20", "2026-07-05",   0, "PENDIENTE",   "No"),
        # CLIMATIZACIÓN
        (37, "CLIMATIZACIÓN",    "Conductos distribución aire Daikin 5MXM90A",            "Servitec/Jose",   "2026-05-29", "2026-06-20",  15, "EN PROCESO",  "No"),
        (38, "CLIMATIZACIÓN",    "Unidades interiores x4 + difusores",                    "Servitec/Jose",   "2026-06-10", "2026-06-25",   0, "PENDIENTE",   "No"),
        (39, "CLIMATIZACIÓN",    "Recuperador calor Daikin DAHU + extractores Silent",    "Servitec/Jose",   "2026-06-15", "2026-06-30",   0, "PENDIENTE",   "No"),
        (40, "CLIMATIZACIÓN",    "Bancadas antivibratorias unidad exterior",               "Servitec/Jose",   "2026-06-20", "2026-06-25",   0, "PENDIENTE",   "No"),
        # CARPINTERÍA EXT.
        (41, "CARPINTERÍA EXT.", "⚠ Viga UPN — estructura soporte (HITO)",               "Josevi",          "2026-05-27", "2026-05-28", 100, "COMPLETADO",  "Sí"),
        (42, "CARPINTERÍA EXT.", "Sistema cierre ventanas exterior",                       "Josevi",          "2026-06-01", "2026-07-07",   0, "PENDIENTE",   "No"),
        (43, "CARPINTERÍA EXT.", "Carpintería a medida recepción y vestuarios",            "Josevi",          "2026-07-08", "2026-07-24",   0, "PENDIENTE",   "No"),
        # PCI
        (44, "PCI - INCENDIOS",  "Trazados red extinción + BIEs",                         "Troser/Leo",      "2026-05-18", "2026-06-20",  10, "EN PROCESO",  "No"),
        (45, "PCI - INCENDIOS",  "Rociadores + detección automática",                     "Troser/Leo",      "2026-06-01", "2026-06-30",   0, "PENDIENTE",   "No"),
        (46, "PCI - INCENDIOS",  "Legalización PCI + boletín técnico",                    "Troser/Leo",      "2026-06-20", "2026-06-30",   0, "PENDIENTE",   "Sí"),
        # RECEPCIÓN
        (47, "RECEPCIÓN",        "Mostrador recepción 2.80x2.00m terracota",              "Munir",           "2026-06-20", "2026-07-01",   0, "PENDIENTE",   "No"),
        (48, "RECEPCIÓN",        "Tornos QR/RFID x2 + puerta PMR 900mm",                 "Proveedor",       "2026-06-20", "2026-07-01",   0, "PENDIENTE",   "No"),
        (49, "RECEPCIÓN",        "Rack IT 12U-15U ventilado + fuente agua inox",          "Proveedor",       "2026-06-25", "2026-07-01",   0, "PENDIENTE",   "No"),
        # FALSOS TECHOS
        (50, "FALSOS TECHOS",    "Techo Box-in-Box 81dB vest+staff+rack",                 "Munir",           "2026-07-15", "2026-07-26",   0, "PENDIENTE",   "No"),
        (51, "FALSOS TECHOS",    "Techo metálico aluminio baños/vestuarios",              "Munir",           "2026-07-15", "2026-07-26",   0, "PENDIENTE",   "No"),
        (52, "FALSOS TECHOS",    "Techo High-Sound viruta madera sala colectiva",         "Munir",           "2026-07-15", "2026-07-27",   0, "PENDIENTE",   "No"),
        (53, "FALSOS TECHOS",    "Falsa viga cajón técnico 3 tramos 54m",                "Munir",           "2026-07-18", "2026-07-26",   0, "PENDIENTE",   "No"),
        # REVESTIMIENTOS
        (54, "REVESTIMIENTOS",   "Alicatado 200x200mm blanco baños/vestuarios",           "Fontanería",      "2026-07-10", "2026-07-26",   0, "PENDIENTE",   "No"),
        (55, "REVESTIMIENTOS",   "Solado gres porcelánico 600x600mm",                     "Fontanería",      "2026-07-15", "2026-07-26",   0, "PENDIENTE",   "No"),
        # ACABADOS
        (56, "ACABADOS",         "Pintura plástica vertical paramentos",                   "Munir",           "2026-07-18", "2026-08-01",   0, "PENDIENTE",   "No"),
        (57, "ACABADOS",         "Pintura techos y horizontales >3m",                     "Munir",           "2026-07-18", "2026-08-01",   0, "PENDIENTE",   "No"),
        (58, "ACABADOS",         "Rodapié MDF 90x18mm — 159m",                            "Munir",           "2026-07-22", "2026-07-31",   0, "PENDIENTE",   "No"),
        (59, "ACABADOS",         "Pavimento vinílico lamas hall+sala activ. 143m2",        "Munir",           "2026-07-22", "2026-07-31",   0, "PENDIENTE",   "No"),
        (60, "ACABADOS",         "Pavimento caucho SBR 40mm sala gym 522m2",              "Munir",           "2026-07-22", "2026-07-28",   0, "PENDIENTE",   "No"),
        # EQUIPAMIENTO
        (61, "EQUIPAMIENTO",     "Lavabos x5 + griferías monomando",                      "Fontanería",      "2026-07-15", "2026-07-24",   0, "PENDIENTE",   "No"),
        (62, "EQUIPAMIENTO",     "Inodoros x4 + inodoro PMR",                             "Fontanería",      "2026-07-15", "2026-07-24",   0, "PENDIENTE",   "No"),
        (63, "EQUIPAMIENTO",     "Duchas x8 + plato PMR + griferías x8",                 "Fontanería",      "2026-07-15", "2026-07-24",   0, "PENDIENTE",   "No"),
        (64, "EQUIPAMIENTO",     "Accesorios PMR — barras x2 + espejo PMR",              "Fontanería",      "2026-07-15", "2026-07-24",   0, "PENDIENTE",   "No"),
        (65, "EQUIPAMIENTO",     "Cabinas fenólico HPL 900x1400mm x4",                   "Proveedor",       "2026-07-18", "2026-07-26",   0, "PENDIENTE",   "No"),
        (66, "EQUIPAMIENTO",     "Taquillas HPL 400x500x1800mm x89",                     "Proveedor",       "2026-07-18", "2026-07-26",   0, "PENDIENTE",   "No"),
        (67, "EQUIPAMIENTO",     "Bancos HPL 1000mm x30",                                 "Fontanería",      "2026-07-20", "2026-07-26",   0, "PENDIENTE",   "No"),
        # ACCESIBILIDAD PMR
        (68, "ACCESIBILIDAD PMR","🔴 Plataforma FORTIS 300kg Hersan — CUELLO BOTELLA",   "Hersan",          "2026-07-07", "2026-07-15",   0, "PENDIENTE",   "Sí"),
        (69, "ACCESIBILIDAD PMR","Señalización PMR + evacuación",                         "Proveedor",       "2026-07-15", "2026-07-18",   0, "PENDIENTE",   "No"),
        # INSPECCIONES
        (70, "INSPECCIONES",     "Prueba instalación eléctrica con equipamientos",         "Luis/Elecrea",    "2026-07-25", "2026-07-28",   0, "PENDIENTE",   "No"),
        (71, "INSPECCIONES",     "Puesta en marcha clima 4 unidades",                     "Servitec/Jose",   "2026-07-25", "2026-07-29",   0, "PENDIENTE",   "No"),
        (72, "INSPECCIONES",     "Prueba ACS + fontanería + estanqueidad",                "Fontanería",      "2026-07-25", "2026-07-29",   0, "PENDIENTE",   "No"),
        (73, "INSPECCIONES",     "Inspección PCI final",                                  "Troser/Leo",      "2026-07-25", "2026-07-29",   0, "PENDIENTE",   "Sí"),
        (74, "INSPECCIONES",     "Limpieza final de obra",                                "PMO Darío",       "2026-07-30", "2026-08-02",   0, "PENDIENTE",   "No"),
        (75, "INSPECCIONES",     "Inspección licencia apertura municipal",                 "PMO Darío",       "2026-07-30", "2026-08-03",   0, "PENDIENTE",   "Sí"),
        # HITOS
        (76, "HITOS",            "🚀 APERTURA NINE FITNESS BRESCIA 19",                   "Todo el equipo",  "2026-08-03", "2026-08-05",   0, "PENDIENTE",   "Sí"),
    ]
    cols = ["ID","FASE","TAREA","RESPONSABLE","FECHA_INICIO","FECHA_FIN",
            "PROGRESO","ESTADO","HITO_CRITICO"]
    df = pd.DataFrame(filas, columns=cols)
    df["FECHA_INICIO"] = pd.to_datetime(df["FECHA_INICIO"])
    df["FECHA_FIN"]    = pd.to_datetime(df["FECHA_FIN"])
    return df


@st.cache_data
def cargar_datos() -> pd.DataFrame:
    if Path(ARCHIVO_CSV).exists():
        df = pd.read_csv(ARCHIVO_CSV)
        df["FECHA_INICIO"] = pd.to_datetime(df["FECHA_INICIO"])
        df["FECHA_FIN"]    = pd.to_datetime(df["FECHA_FIN"])
    else:
        df = datos_iniciales()
        df.to_csv(ARCHIVO_CSV, index=False)
    return df


def guardar_datos(df: pd.DataFrame):
    df.to_csv(ARCHIVO_CSV, index=False)
    st.cache_data.clear()


def ts(fecha_str: str) -> float:
    return pd.Timestamp(fecha_str).timestamp() * 1000


# ─── 2. CARGA DE DATOS ────────────────────────────────────────────────────────
df = cargar_datos()

hoy        = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
dias_rest  = (FECHA_APERTURA - hoy).days
avance_gl  = int(df["PROGRESO"].mean())
alertas    = len(df[df["ESTADO"].isin(["ROJO", "AMARILLO"])])
completadas = len(df[df["ESTADO"] == "COMPLETADO"])
en_proceso  = len(df[df["ESTADO"] == "EN PROCESO"])

# ─── 3. SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/building.png", width=60)
    st.title("PMO Brescia 19")
    st.caption("Nine Fitness Group S.L.")
    st.divider()

    st.subheader("🗂️ Filtros")
    fases_sel = st.multiselect(
        "Fase", options=FASES, default=FASES,
        help="Filtra las tareas por fase de obra"
    )
    responsables = sorted(df["RESPONSABLE"].unique().tolist())
    resp_sel = st.multiselect(
        "Responsable", options=responsables, default=responsables
    )
    estados_sel = st.multiselect(
        "Estado", options=ESTADOS, default=ESTADOS
    )
    solo_criticos = st.checkbox("Solo hitos críticos", value=False)

    st.divider()
    st.caption(f"📅 Hoy: {hoy.strftime('%d/%m/%Y')}")
    st.caption(f"🚀 Apertura: 03/08/2026")

# ─── 4. CABECERA ──────────────────────────────────────────────────────────────
st.title("🏗️ Planning Master — Nine Fitness Brescia 19")
st.caption("C/ Brescia 19, 28028 Madrid · Promotor: Nine Fitness Group S.L. · DO: Darío A. López")

# ─── 5. KPIs ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("⏳ Días para Apertura",  f"{dias_rest}d",
          delta="🟢 En plazo" if dias_rest > 45 else "🔴 Urgente",
          delta_color="off")
k2.metric("📈 Avance Global",       f"{avance_gl}%",
          delta=f"{completadas} completadas")
k3.metric("🔵 En Proceso",          f"{en_proceso} tareas")
k4.metric("⚠️ Alertas Activas",    f"{alertas} tareas",
          delta_color="inverse",
          delta="Rojo/Amarillo")
k5.metric("📋 Total Partidas",      f"{len(df)} tareas",
          delta=f"{len(df[df['HITO_CRITICO']=='Sí'])} hitos críticos")

st.divider()

# ─── 6. FILTRADO ──────────────────────────────────────────────────────────────
mask = (
    df["FASE"].isin(fases_sel) &
    df["RESPONSABLE"].isin(resp_sel) &
    df["ESTADO"].isin(estados_sel)
)
if solo_criticos:
    mask &= df["HITO_CRITICO"] == "Sí"

df_vis = df[mask].copy()

# ─── 7. GANTT ─────────────────────────────────────────────────────────────────
st.subheader("📊 Diagrama de Gantt Interactivo")

df_gantt = df_vis.copy()
# Hitos de 1 día: ampliar para visibilidad
mismo_dia = df_gantt["FECHA_INICIO"] == df_gantt["FECHA_FIN"]
df_gantt.loc[mismo_dia, "FECHA_FIN"] = df_gantt.loc[mismo_dia, "FECHA_FIN"] + pd.Timedelta(days=1)

fig = px.timeline(
    df_gantt,
    x_start="FECHA_INICIO",
    x_end="FECHA_FIN",
    y="TAREA",
    color="ESTADO",
    color_discrete_map=COLOR_ESTADO,
    hover_data={
        "FASE": True, "RESPONSABLE": True,
        "PROGRESO": True, "HITO_CRITICO": True,
        "FECHA_INICIO": "|%d-%b-%Y", "FECHA_FIN": "|%d-%b-%Y",
    },
    title=f"Cronograma Maestro Brescia 19 · {len(df_vis)} partidas · Apertura 03-Ago-2026",
)

fig.add_vline(x=ts(hoy.strftime("%Y-%m-%d")),
              line_width=2, line_dash="dash", line_color="#FFFFFF",
              annotation_text=f"HOY {hoy.strftime('%d %b')}",
              annotation_font=dict(color="#FFFFFF", size=11))
fig.add_vline(x=ts("2026-07-07"),
              line_width=2, line_dash="dot", line_color="#e74c3c",
              annotation_text="Hersan 07-Jul ♿",
              annotation_font=dict(color="#e74c3c", size=11))
fig.add_vline(x=ts("2026-08-03"),
              line_width=2, line_dash="dot", line_color="#FFD700",
              annotation_text="APERTURA 🚀",
              annotation_font=dict(color="#FFD700", size=11))
fig.add_vrect(x0=ts("2026-07-25"), x1=ts("2026-08-02"),
              fillcolor="#1ABC9C", opacity=0.07, layer="below", line_width=0,
              annotation_text="Limpieza/Licencias",
              annotation_font=dict(color="#1ABC9C", size=10))

fig.update_layout(
    paper_bgcolor="#0e1117", plot_bgcolor="#161b27", font_color="#F0F2F6",
    height=max(500, len(df_vis) * 22 + 80),
    xaxis=dict(showgrid=True, gridcolor="#2a2f3e",
               tickformat="%d %b", tickangle=-40,
               range=[FECHA_INICIO - pd.Timedelta(days=3),
                      FECHA_APERTURA + pd.Timedelta(days=5)]),
    yaxis=dict(autorange="reversed", showgrid=False, tickfont=dict(size=10)),
    legend=dict(orientation="h", yanchor="bottom", y=1.01,
                xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=10, r=10, t=60, b=40),
)
st.plotly_chart(fig, use_container_width=True)

# ─── 8. EDITOR INTERACTIVO ────────────────────────────────────────────────────
st.divider()
st.subheader("✏️ Editor de Planning — Edición en Tiempo Real")
st.caption("Edita directamente en la tabla. Pulsa 💾 para guardar los cambios.")

df_edit = df_vis.copy()

edited = st.data_editor(
    df_edit,
    use_container_width=True,
    num_rows="fixed",
    hide_index=True,
    column_config={
        "ID": st.column_config.NumberColumn("ID", disabled=True, width="small"),
        "FASE": st.column_config.SelectboxColumn(
            "Fase", options=FASES, required=True, width="medium"
        ),
        "TAREA": st.column_config.TextColumn(
            "Tarea / Partida", width="large"
        ),
        "RESPONSABLE": st.column_config.TextColumn(
            "Responsable", width="medium"
        ),
        "FECHA_INICIO": st.column_config.DateColumn(
            "Inicio", format="DD/MM/YYYY", width="small"
        ),
        "FECHA_FIN": st.column_config.DateColumn(
            "Fin", format="DD/MM/YYYY", width="small"
        ),
        "PROGRESO": st.column_config.NumberColumn(
            "% Progreso", min_value=0, max_value=100,
            step=5, format="%d%%", width="small"
        ),
        "ESTADO": st.column_config.SelectboxColumn(
            "Estado", options=ESTADOS, required=True, width="medium"
        ),
        "HITO_CRITICO": st.column_config.SelectboxColumn(
            "Hito Crítico", options=["Sí", "No"], width="small"
        ),
    },
    key="editor_planning",
)

col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
with col_btn1:
    if st.button("💾 Guardar Cambios en la Obra", type="primary", use_container_width=True):
        # Actualizar el df principal con los cambios del editor filtrado
        df_updated = df.copy()
        df_updated.update(edited.set_index("ID"), overwrite=True)
        # Reconstruir desde edited para las filas filtradas
        for _, row in edited.iterrows():
            df_updated.loc[df_updated["ID"] == row["ID"], edited.columns] = row.values
        guardar_datos(df_updated)
        st.success(f"✅ Cambios guardados en `{ARCHIVO_CSV}` — {len(edited)} partidas actualizadas.")
        st.rerun()

with col_btn2:
    csv_export = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Exportar CSV", data=csv_export,
        file_name=ARCHIVO_CSV, mime="text/csv",
        use_container_width=True
    )

with col_btn3:
    if st.button("🔄 Recargar datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ─── 9. RESUMEN POR FASE ──────────────────────────────────────────────────────
st.divider()
st.subheader("📋 Resumen de Avance por Fase")

resumen = (
    df.groupby("FASE")
    .agg(
        Tareas=("ID", "count"),
        Completadas=("ESTADO", lambda x: (x == "COMPLETADO").sum()),
        En_Proceso=("ESTADO", lambda x: (x == "EN PROCESO").sum()),
        Alertas=("ESTADO", lambda x: x.isin(["ROJO", "AMARILLO"]).sum()),
        Avance_Medio=("PROGRESO", "mean"),
    )
    .reset_index()
)
resumen["Avance_Medio"] = resumen["Avance_Medio"].round(0).astype(int)
resumen.columns = ["Fase", "Tareas", "Completadas", "En Proceso", "Alertas", "% Avance"]

st.dataframe(
    resumen,
    use_container_width=True,
    hide_index=True,
    column_config={
        "% Avance": st.column_config.ProgressColumn(
            "% Avance", min_value=0, max_value=100, format="%d%%"
        )
    }
)

# ─── PIE ──────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    f"PMO Multi-Agente Brescia 19 · @pmo-planning + @pmo-dashboard · "
    f"Base de datos: `{ARCHIVO_CSV}` · "
    f"Actualizado: {hoy.strftime('%d/%m/%Y')} · "
    f"76 partidas · Apertura: 03-08-2026"
)
