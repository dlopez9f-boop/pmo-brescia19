#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pages/2_Obra_Principal.py
Nine Club Chamartín (Waksman) — Seguimiento de obra nueva, licitaciones y CAPEX.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, datetime
from _auth import require_auth

st.set_page_config(page_title="Chamartín · PMO", page_icon="🏗", layout="wide")
require_auth()

NAVY = "#0B1F3A"
GOLD = "#C9A96E"

st.markdown(
    f"<div style='background:{NAVY};padding:12px 20px;border-bottom:2px solid {GOLD};"
    f"margin:-1rem -1rem 1rem -1rem;display:flex;align-items:center;gap:12px'>"
    f"<span style='color:{GOLD};font-weight:700;font-size:15px;letter-spacing:.08em'>"
    f"🏗 NINE CLUB CHAMARTÍN (WAKSMAN)</span>"
    f"<span style='color:#3a5a80;font-size:11px'>C/ Waksman · Obra nueva · Módulo de seguimiento</span>"
    f"</div>",
    unsafe_allow_html=True,
)

tab_res, tab_lit, tab_gantt, tab_capex = st.tabs(
    ["📋 Resumen", "💼 Licitaciones", "📅 Planificación", "💰 Control CAPEX"]
)

# ── TAB 1: RESUMEN ────────────────────────────────────────────────────────────
with tab_res:
    st.error(
        "⚠️ **ALERTA CRÍTICA** — Bajante comunitaria S-2: posible fibrocemento/amianto (Uralita). "
        "Empresa RERA obligatoria antes de cualquier demolición. "
        "Plan de Trabajo art.11 RD 396/2006 + notificación Inspección Trabajo (30 días previos). "
        "Coste: comunidad de propietarios."
    )
    st.info(
        "📐 **Proyectos técnicos:** Ángel Rodríguez hace TODOS los proyectos técnicos (incluido clima). "
        "Carlos ejecuta clima pero NO proyecta. **Pendiente de Ángel:** proyecto climatización/ventilación."
    )

    st.subheader("👥 Equipo de proyecto")
    cols = st.columns(5)
    equipo = [
        ("Darío L.",  "Project Manager"),
        ("Ángel R.",  "Proyectista / Arquitecto"),
        ("Óscar",     "Obra civil"),
        ("Javi",      "Obra civil"),
        ("Laura P.",  "Equipamiento"),
    ]
    for col, (nombre, rol) in zip(cols, equipo):
        col.metric(rol, nombre)

    st.divider()

    st.subheader("📌 Estado del proyecto")
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Fase actual", "Licitación")
    e2.metric("Inicio obras previsto", "Oct 2026")
    e3.metric("Apertura estimada", "Mar 2027")
    e4.metric("Gremios contratados", "1 / 8")


# ── TAB 2: LICITACIONES ───────────────────────────────────────────────────────
with tab_lit:
    LICITACIONES = [
        {"Gremio": "Demoliciones",               "Empresa": "Anka Demoliciones",  "Estado": "En licitación", "Ppto €": 0,  "Adjud €": 0},
        {"Gremio": "Climatización / Ventilación","Empresa": "Carlos (ejecuta)",    "Estado": "Contratado",    "Ppto €": 0,  "Adjud €": 0},
        {"Gremio": "Civil / Fontanería",         "Empresa": "Por definir",         "Estado": "En licitación", "Ppto €": 0,  "Adjud €": 0},
        {"Gremio": "Electricidad",               "Empresa": "Por definir",         "Estado": "En licitación", "Ppto €": 0,  "Adjud €": 0},
        {"Gremio": "Carpintería / Cerrajería",   "Empresa": "Por definir",         "Estado": "En licitación", "Ppto €": 0,  "Adjud €": 0},
        {"Gremio": "PCI",                        "Empresa": "Por definir",         "Estado": "En licitación", "Ppto €": 0,  "Adjud €": 0},
        {"Gremio": "Acabados / Pintura",         "Empresa": "Por definir",         "Estado": "En licitación", "Ppto €": 0,  "Adjud €": 0},
        {"Gremio": "Equipamiento fitness",       "Empresa": "Thomas Wellness",     "Estado": "Por confirmar", "Ppto €": 0,  "Adjud €": 0},
    ]
    df_lit = pd.DataFrame(LICITACIONES)

    total_ppto  = df_lit["Ppto €"].sum()
    total_adj   = df_lit["Adjud €"].sum()
    contratados = (df_lit["Estado"] == "Contratado").sum()
    en_lit      = (df_lit["Estado"] == "En licitación").sum()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("CAPEX presupuestado", f"{total_ppto:,.0f} €".replace(",",".") if total_ppto else "Pte.")
    m2.metric("CAPEX adjudicado",    f"{total_adj:,.0f} €".replace(",",".") if total_adj else "Pte.")
    m3.metric("Gremios contratados", contratados)
    m4.metric("Pendientes precio",   en_lit)

    st.divider()

    BADGE = {"Contratado": "🟢", "En licitación": "🟡", "Por confirmar": "🔵", "Bloqueado": "🔴"}
    df_show = df_lit.copy()
    df_show.insert(0, "", df_show["Estado"].map(BADGE).fillna("⚪"))
    st.dataframe(
        df_show[["","Gremio","Empresa","Estado","Ppto €","Adjud €"]],
        use_container_width=True, hide_index=True,
        column_config={
            "Ppto €":  st.column_config.NumberColumn("Presupuesto (€)", format="%.0f"),
            "Adjud €": st.column_config.NumberColumn("Adjudicado (€)",  format="%.0f"),
            "":        st.column_config.TextColumn("", width="small"),
        },
    )


# ── TAB 3: GANTT ─────────────────────────────────────────────────────────────
with tab_gantt:
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
    for fase, inicio, fin in FASES:
        if fin < hoy:
            color = GOLD
        elif inicio <= hoy <= fin:
            color = "#3a7bd5"
        else:
            color = "#4a90b8"
        duracion = (datetime.fromisoformat(fin) - datetime.fromisoformat(inicio)).days
        fig.add_trace(go.Bar(
            x=[duracion],
            y=[fase],
            base=[datetime.fromisoformat(inicio).timestamp() * 1000],
            orientation="h",
            marker_color=color,
            showlegend=False,
            hovertemplate=f"<b>{fase}</b><br>{inicio} → {fin}<br>{duracion} días<extra></extra>",
        ))

    fig.add_vline(
        x=datetime.now().timestamp() * 1000,
        line_color="#e74c3c", line_dash="dash", line_width=1.5,
        annotation_text="Hoy", annotation_font_color="#e74c3c",
    )
    fig.update_layout(
        barmode="overlay", height=340,
        plot_bgcolor="#F0EDE8", paper_bgcolor="white",
        xaxis=dict(type="date", tickformat="%b %Y", gridcolor="#DEDAD4", title=""),
        yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
        margin=dict(l=190, r=20, t=20, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("⚙️ Fechas provisionales — actualizar conforme avance la licitación.")


# ── TAB 4: CONTROL CAPEX ─────────────────────────────────────────────────────
with tab_capex:
    st.info("💡 Control CAPEX en construcción. Los datos se actualizarán conforme se adjudiquen gremios.")

    CAPEX_REFERENCIA = [
        {"Partida": "Demoliciones",      "Estimado €": 45000, "Real €": 0, "Diferencia €": -45000},
        {"Partida": "Civil / Fontanería","Estimado €": 80000, "Real €": 0, "Diferencia €": -80000},
        {"Partida": "Electricidad",      "Estimado €": 60000, "Real €": 0, "Diferencia €": -60000},
        {"Partida": "Climatización",     "Estimado €": 70000, "Real €": 0, "Diferencia €": -70000},
        {"Partida": "Carpintería",       "Estimado €": 40000, "Real €": 0, "Diferencia €": -40000},
        {"Partida": "Acabados",          "Estimado €": 35000, "Real €": 0, "Diferencia €": -35000},
        {"Partida": "PCI",               "Estimado €": 25000, "Real €": 0, "Diferencia €": -25000},
        {"Partida": "Equipamiento",      "Estimado €": 180000,"Real €": 0, "Diferencia €": -180000},
    ]
    df_capex = pd.DataFrame(CAPEX_REFERENCIA)
    total_est  = df_capex["Estimado €"].sum()
    total_real = df_capex["Real €"].sum()

    cap1, cap2, cap3 = st.columns(3)
    cap1.metric("CAPEX estimado total",  f"{total_est:,.0f} €".replace(",","."))
    cap2.metric("CAPEX comprometido",    f"{total_real:,.0f} €".replace(",","."))
    cap3.metric("% Comprometido", f"{(total_real/total_est*100):.1f}%" if total_est else "—")

    st.dataframe(df_capex, use_container_width=True, hide_index=True,
        column_config={
            "Estimado €":   st.column_config.NumberColumn("Estimado (€)",   format="%.0f"),
            "Real €":       st.column_config.NumberColumn("Real (€)",        format="%.0f"),
            "Diferencia €": st.column_config.NumberColumn("Diferencia (€)", format="%.0f"),
        })
