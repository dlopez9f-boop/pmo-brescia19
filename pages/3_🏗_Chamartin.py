"""
pages/3_🏗_Chamartin.py
Mega-Proyecto Chamartín (WAK-13) — Seguimiento obra nueva, licitaciones y CAPEX.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, datetime

st.set_page_config(page_title="Chamartín · Nine", layout="wide", page_icon="🏗")

NAVY = "#0B1F3A"
GOLD = "#C9A96E"

st.markdown(
    f"<div style='background:{NAVY};padding:12px 20px;border-bottom:2px solid {GOLD};"
    f"margin:-1rem -1rem 1rem -1rem;display:flex;align-items:center;gap:12px'>"
    f"<span style='color:{GOLD};font-weight:700;font-size:15px;letter-spacing:.1em'>"
    f"🏗 MEGA-PROYECTO CHAMARTÍN (WAK-13)</span>"
    f"<span style='color:#3a5a80;font-size:11px'>C/ Waksman · Módulo de obra nueva</span>"
    f"</div>",
    unsafe_allow_html=True,
)

# ── EQUIPO ────────────────────────────────────────────────────────────────────
with st.expander("👥 Equipo de proyecto", expanded=False):
    cols = st.columns(5)
    equipo = [
        ("Darío L.", "Project Manager"),
        ("Ángel R.", "Proyectista / Arquitecto"),
        ("Óscar", "Obra civil"),
        ("Javi", "Obra civil"),
        ("Laura P.", "Equipamiento"),
    ]
    for col, (nombre, rol) in zip(cols, equipo):
        col.metric(rol, nombre)

st.divider()

# ── ALERTAS NORMATIVAS ────────────────────────────────────────────────────────
st.error(
    "⚠️ **ALERTA CRÍTICA** — Bajante comunitaria S-2: posible fibrocemento/amianto (Uralita). "
    "Empresa RERA obligatoria antes de cualquier demolición. "
    "Plan de Trabajo art.11 RD 396/2006 + notificación Inspección Trabajo (30 días previos)."
)

# ── KPIs FINANCIEROS ─────────────────────────────────────────────────────────
st.subheader("📊 Control CAPEX")

# Datos de licitaciones — actualizar conforme lleguen presupuestos
LICITACIONES = [
    {"Gremio": "Demoliciones",               "Empresa": "Anka Demoliciones",  "Estado": "En licitación",     "Presupuesto": 0,       "Adjudicado": 0},
    {"Gremio": "Climatización / Ventilación","Empresa": "Carlos (ejecuta)",    "Estado": "Contratado",        "Presupuesto": 0,       "Adjudicado": 0},
    {"Gremio": "Civil / Fontanería",         "Empresa": "Por definir",         "Estado": "En licitación",     "Presupuesto": 0,       "Adjudicado": 0},
    {"Gremio": "Electricidad",               "Empresa": "Por definir",         "Estado": "En licitación",     "Presupuesto": 0,       "Adjudicado": 0},
    {"Gremio": "Carpintería / Cerrajería",   "Empresa": "Por definir",         "Estado": "En licitación",     "Presupuesto": 0,       "Adjudicado": 0},
    {"Gremio": "PCI",                        "Empresa": "Por definir",         "Estado": "En licitación",     "Presupuesto": 0,       "Adjudicado": 0},
    {"Gremio": "Acabados / Pintura",         "Empresa": "Por definir",         "Estado": "En licitación",     "Presupuesto": 0,       "Adjudicado": 0},
    {"Gremio": "Equipamiento fitness",       "Empresa": "Thomas Wellness",     "Estado": "Por confirmar",     "Presupuesto": 0,       "Adjudicado": 0},
]
df_lit = pd.DataFrame(LICITACIONES)
total_ppto    = df_lit["Presupuesto"].sum()
total_adjud   = df_lit["Adjudicado"].sum()
contratados   = (df_lit["Estado"] == "Contratado").sum()
en_licitacion = (df_lit["Estado"] == "En licitación").sum()

m1, m2, m3, m4 = st.columns(4)
m1.metric("CAPEX presupuestado", f"{total_ppto:,.0f} €".replace(",",".") if total_ppto else "Pte.")
m2.metric("CAPEX adjudicado",    f"{total_adjud:,.0f} €".replace(",",".") if total_adjud else "Pte.")
m3.metric("Gremios contratados", contratados)
m4.metric("Pendientes precio",   en_licitacion)

st.divider()

# ── TABLA DE LICITACIONES ─────────────────────────────────────────────────────
st.subheader("📋 Licitaciones por gremio")

COLOR_ESTADO = {
    "Contratado":    "🟢",
    "En licitación": "🟡",
    "Por confirmar": "🔵",
    "Bloqueado":     "🔴",
}
df_display = df_lit.copy()
df_display[""] = df_display["Estado"].map(COLOR_ESTADO).fillna("⚪")
df_display = df_display[["","Gremio","Empresa","Estado","Presupuesto","Adjudicado"]]

st.dataframe(
    df_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Presupuesto": st.column_config.NumberColumn("Presupuesto (€)", format="%.0f"),
        "Adjudicado":  st.column_config.NumberColumn("Adjudicado (€)",  format="%.0f"),
        "":            st.column_config.TextColumn("", width="small"),
    },
)

st.divider()

# ── GANTT DE FASES ────────────────────────────────────────────────────────────
st.subheader("📅 Planificación de fases (provisional)")

FASES = [
    ("Proyecto técnico / Permisos", "2026-09-01", "2026-10-15"),
    ("Demoliciones",                "2026-10-16", "2026-11-15"),
    ("Civil / Fontanería",          "2026-11-01", "2026-12-15"),
    ("Electricidad",                "2026-11-15", "2027-01-10"),
    ("Climatización",               "2026-12-01", "2027-01-20"),
    ("Carpintería / Acabados",      "2027-01-10", "2027-02-10"),
    ("Equipamiento fitness",        "2027-01-20", "2027-02-20"),
    ("Entrega / Apertura",          "2027-02-21", "2027-03-01"),
]

hoy = date.today().isoformat()
fig = go.Figure()
for i, (fase, inicio, fin) in enumerate(FASES):
    color = GOLD if fin < hoy else ("#3a7bd5" if inicio <= hoy <= fin else "#4a90b8")
    fig.add_trace(go.Bar(
        x=[(datetime.fromisoformat(fin) - datetime.fromisoformat(inicio)).days],
        y=[fase],
        base=[datetime.fromisoformat(inicio).timestamp() * 1000],
        orientation="h",
        marker_color=color,
        showlegend=False,
        hovertemplate=f"<b>{fase}</b><br>{inicio} → {fin}<extra></extra>",
    ))

fig.update_layout(
    barmode="overlay",
    height=320,
    plot_bgcolor="#F0EDE8",
    paper_bgcolor="white",
    xaxis=dict(
        type="date",
        tickformat="%b %Y",
        gridcolor="#DEDAD4",
        title="",
    ),
    yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
    margin=dict(l=180, r=20, t=20, b=30),
)
fig.add_vline(x=datetime.now().timestamp() * 1000, line_color="red",
              line_dash="dash", line_width=1, annotation_text="Hoy")
st.plotly_chart(fig, use_container_width=True)

st.caption(
    "⚙️ *Fechas provisionales — actualizar conforme avance la licitación. "
    "El Gantt se actualizará automáticamente al editar la lista FASES en el código.*"
)

# ── NOTA ÁNGEL ────────────────────────────────────────────────────────────────
st.info(
    "📐 **Proyectos técnicos:** Ángel Rodríguez hace TODOS los proyectos técnicos "
    "(incluido clima). Carlos ejecuta clima pero NO proyecta. "
    "**Pendiente de Ángel:** proyecto climatización/ventilación."
)
