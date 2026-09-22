#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pages/2_Obra_Principal.py
Nine Club Chamartín (Waksman) — Seguimiento de obra nueva, licitaciones y CAPEX.
Planning source: 7425_Waksman_Notion_Tareas.csv (20260920)
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, datetime
from _auth import require_auth

st.set_page_config(page_title="Chamartín · PMO", page_icon="🏗", layout="wide")
require_auth()

st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden !important; }
  [data-testid="stSidebar"] { border-right: 1px solid #E8E0CE !important; }
</style>
""", unsafe_allow_html=True)

NAVY = "#0B1F3A"
GOLD = "#C9A96E"

st.markdown(
    f"<div style='background:{NAVY};padding:12px 20px;border-bottom:2px solid {GOLD};"
    f"margin:-1rem -1rem 1rem -1rem;display:flex;align-items:center;gap:12px'>"
    f"<span style='color:{GOLD};font-weight:700;font-size:15px;letter-spacing:.08em'>"
    f"🏗 NINE CLUB CHAMARTÍN (WAKSMAN)</span>"
    f"<span style='color:#6a8aaa;font-size:11px'>C/ Waksman · Obra nueva · Inicio: 22/09/2026</span>"
    f"</div>",
    unsafe_allow_html=True,
)

tab_res, tab_lit, tab_gantt, tab_capex = st.tabs(
    ["📋 Resumen", "💼 Licitaciones", "📅 Planning Gantt", "💰 Control CAPEX"]
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
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Project Manager", "Darío L.")
    col2.metric("CEO", "Óscar / Javi")
    col3.metric("Jefa de Producto", "Laura Plaza")
    col4.metric("Contabilidad", "Valentina")
    col5.metric("Proyectista / Arq.", "Ángel R.")

    st.divider()

    st.subheader("📌 Estado del proyecto")
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Fase actual", "Trabajos previos")
    e2.metric("Inicio obra", "22 Sep 2026")
    e3.metric("Apertura estimada", "Abr/May 2027")
    e4.metric("Gremios contratados", "2 / 9")

    st.divider()

    st.subheader("🔑 Hitos críticos")
    hitos = [
        ("22/09/2026", "Entrada Munir — Instalaciones de seguridad + replanteos", "🟢 En curso"),
        ("30/09/2026", "Inicio demoliciones — Excavación zapatas boxing (Munir)", "⏳ Próximo"),
        ("05/10/2026", "Inicio estructuras (Anca)", "⏳ Próximo"),
        ("02/11/2026", "Inicio instalaciones eléctricas (Por definir)", "⏳ Por contratar"),
        ("28/12/2026", "Inicio revestimientos y falsos techos", "⏳ Por contratar"),
        ("28/04/2027", "Apertura Nine Club Chamartín", "🎯 Objetivo"),
    ]
    df_hitos = pd.DataFrame(hitos, columns=["Fecha", "Hito", "Estado"])
    st.dataframe(df_hitos, use_container_width=True, hide_index=True)


# ── TAB 2: LICITACIONES ───────────────────────────────────────────────────────
with tab_lit:
    LICITACIONES = [
        {"Gremio": "Civil / Fontanería",          "Empresa": "Munir (Ziad)",     "Inicio":  "22/09/2026", "Estado": "Contratado",    "Ppto €": 0, "Adjud €": 0, "Notas": "Seguridad, replanteos, civil, albañilería, fontanería"},
        {"Gremio": "Demoliciones / Estructuras",   "Empresa": "Anca Demoliciones","Inicio":  "05/10/2026", "Estado": "Contratado",    "Ppto €": 0, "Adjud €": 0, "Notas": "Forjados boxing y entreplanta, estructuras"},
        {"Gremio": "Climatización / Ventilación",  "Empresa": "Carlos (ejecuta)", "Inicio":  "09/11/2026", "Estado": "Contratado",    "Ppto €": 0, "Adjud €": 0, "Notas": "Ejecución. Proyecto técnico: Ángel (pendiente)"},
        {"Gremio": "Electricidad",                 "Empresa": "Por definir",      "Inicio":  "02/11/2026", "Estado": "En licitación", "Ppto €": 0, "Adjud €": 0, "Notas": ""},
        {"Gremio": "PCI",                          "Empresa": "Por definir",      "Inicio":  "16/11/2026", "Estado": "En licitación", "Ppto €": 0, "Adjud €": 0, "Notas": ""},
        {"Gremio": "Carpintería / Cerrajería",     "Empresa": "Por definir",      "Inicio":  "11/01/2027", "Estado": "En licitación", "Ppto €": 0, "Adjud €": 0, "Notas": ""},
        {"Gremio": "Ascensor",                     "Empresa": "Por definir",      "Inicio":  "11/01/2027", "Estado": "En licitación", "Ppto €": 0, "Adjud €": 0, "Notas": ""},
        {"Gremio": "Acabados / Pintura / FT",      "Empresa": "Por definir",      "Inicio":  "28/12/2026", "Estado": "En licitación", "Ppto €": 0, "Adjud €": 0, "Notas": ""},
        {"Gremio": "Equipamiento fitness",         "Empresa": "Thomas Wellness",  "Inicio":  "14/04/2027", "Estado": "Por confirmar", "Ppto €": 0, "Adjud €": 0, "Notas": ""},
    ]
    df_lit = pd.DataFrame(LICITACIONES)

    total_ppto  = df_lit["Ppto €"].sum()
    total_adj   = df_lit["Adjud €"].sum()
    contratados = (df_lit["Estado"] == "Contratado").sum()
    en_lit      = (df_lit["Estado"] == "En licitación").sum()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("CAPEX presupuestado", "Pendiente")
    m2.metric("CAPEX adjudicado",    "Pendiente")
    m3.metric("Gremios contratados", f"{contratados} / {len(df_lit)}")
    m4.metric("🔴 Pendientes precio",   en_lit)

    st.divider()

    BADGE = {"Contratado": "🟢", "En licitación": "🟡", "Por confirmar": "🔵"}
    df_show = df_lit.copy()
    df_show.insert(0, "", df_show["Estado"].map(BADGE).fillna("⚪"))
    st.dataframe(
        df_show[["", "Gremio", "Empresa", "Inicio", "Estado", "Ppto €", "Adjud €", "Notas"]],
        use_container_width=True, hide_index=True,
        column_config={
            "Ppto €":  st.column_config.NumberColumn("Presupuesto (€)", format="%.0f"),
            "Adjud €": st.column_config.NumberColumn("Adjudicado (€)",  format="%.0f"),
            "":        st.column_config.TextColumn("", width="small"),
            "Notas":   st.column_config.TextColumn("Notas", width="large"),
        },
    )


# ── TAB 3: GANTT ─────────────────────────────────────────────────────────────
with tab_gantt:
    # Fases principales extraídas del CSV 7425_Waksman_Notion_Tareas.csv
    # Inicio ajustado a 22/09/2026 (entrada real Munir)
    FASES = [
        # (Tarea, Inicio, Fin, Recurso/Gremio, Color)
        ("Trabajos previos",            "2026-09-22", "2026-11-02", "Munir",          "#C9A96E"),
        ("Demoliciones (Munir)",        "2026-09-30", "2026-10-27", "Munir",          "#C9A96E"),
        ("Demolición forjados (Anca)",  "2026-10-05", "2026-11-05", "Anca",           "#4a90d9"),
        ("Estructuras (Anca)",          "2026-10-05", "2026-11-11", "Anca",           "#4a90d9"),
        ("Albañilería (Munir)",         "2026-10-05", "2026-12-24", "Munir",          "#C9A96E"),
        ("Saneamiento",                 "2026-10-19", "2026-11-08", "Munir",          "#C9A96E"),
        ("Electricidad",                "2026-11-02", "2027-03-15", "Por definir",    "#9B59B6"),
        ("Fontanería (Munir)",          "2026-11-09", "2027-02-08", "Munir",          "#C9A96E"),
        ("Climatización (Carlos)",      "2026-11-09", "2027-02-17", "Carlos",         "#27AE60"),
        ("Ventilación",                 "2026-11-09", "2027-04-02", "Por definir",    "#9B59B6"),
        ("PCI",                         "2026-11-16", "2027-03-15", "Por definir",    "#E74C3C"),
        ("Falsos techos / Revestim.",   "2026-12-28", "2027-04-14", "Por definir",    "#7F8C8D"),
        ("Carpintería / Cerrajería",    "2027-01-11", "2027-03-15", "Por definir",    "#7F8C8D"),
        ("Ascensor",                    "2027-01-11", "2027-02-15", "Por definir",    "#7F8C8D"),
        ("Equipamiento fitness",        "2027-04-14", "2027-04-28", "Thomas Wellness","#0B1F3A"),
    ]

    hoy = date.today().isoformat()
    fig = go.Figure()

    for fase, inicio, fin, recurso, color in FASES:
        duracion = (datetime.fromisoformat(fin) - datetime.fromisoformat(inicio)).days
        # Oscurecer si ya pasó
        if fin < hoy:
            bar_color = "#B0B0B0"
        elif inicio <= hoy:
            bar_color = color
        else:
            bar_color = color + "AA"  # semitransparente

        fig.add_trace(go.Bar(
            x=[duracion],
            y=[fase],
            base=[datetime.fromisoformat(inicio).timestamp() * 1000],
            orientation="h",
            marker_color=bar_color,
            marker_line_width=0,
            showlegend=False,
            hovertemplate=(
                f"<b>{fase}</b><br>"
                f"Gremio: {recurso}<br>"
                f"{inicio} → {fin}<br>"
                f"{duracion} días<extra></extra>"
            ),
        ))

    # Línea de hoy
    fig.add_vline(
        x=datetime.now().timestamp() * 1000,
        line_color="#D31224", line_dash="dash", line_width=2,
        annotation_text="Hoy", annotation_font_color="#D31224",
        annotation_position="top",
    )

    fig.update_layout(
        barmode="overlay",
        height=520,
        plot_bgcolor="#FDFCF9",
        paper_bgcolor="#FDFCF9",
        xaxis=dict(
            type="date",
            tickformat="%b %Y",
            gridcolor="#E8E0CE",
            title="",
            tickfont=dict(size=11, color="#0B1F3A"),
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=11, color="#0B1F3A"),
        ),
        margin=dict(l=210, r=20, t=20, b=30),
        font=dict(color="#0B1F3A"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Leyenda
    leg1, leg2, leg3, leg4 = st.columns(4)
    leg1.markdown(f"<span style='color:#C9A96E;font-weight:700'>■</span> Munir (Civil / Fontanería)", unsafe_allow_html=True)
    leg2.markdown(f"<span style='color:#4a90d9;font-weight:700'>■</span> Anca (Demolición / Estructura)", unsafe_allow_html=True)
    leg3.markdown(f"<span style='color:#27AE60;font-weight:700'>■</span> Carlos (Climatización)", unsafe_allow_html=True)
    leg4.markdown(f"<span style='color:#9B59B6;font-weight:700'>■</span> Por contratar", unsafe_allow_html=True)

    st.caption("⚙️ Planning base: 20260920 · Inicio obra ajustado a 22/09/2026 (entrada real Munir).")


# ── TAB 4: CONTROL CAPEX ─────────────────────────────────────────────────────
with tab_capex:
    st.info("💡 Control CAPEX en construcción. Los datos se actualizarán conforme se adjudiquen gremios.")

    CAPEX_REFERENCIA = [
        {"Partida": "Trabajos previos / Seguridad",  "Gremio": "Munir",          "Estimado €": 0, "Real €": 0},
        {"Partida": "Demoliciones / Estructuras",     "Gremio": "Anca",           "Estimado €": 0, "Real €": 0},
        {"Partida": "Civil / Albañilería / Font.",    "Gremio": "Munir",          "Estimado €": 0, "Real €": 0},
        {"Partida": "Electricidad",                   "Gremio": "Por definir",    "Estimado €": 0, "Real €": 0},
        {"Partida": "Climatización / Ventilación",    "Gremio": "Carlos",         "Estimado €": 0, "Real €": 0},
        {"Partida": "PCI",                            "Gremio": "Por definir",    "Estimado €": 0, "Real €": 0},
        {"Partida": "Falsos techos / Revestimientos", "Gremio": "Por definir",    "Estimado €": 0, "Real €": 0},
        {"Partida": "Carpintería / Cerrajería",       "Gremio": "Por definir",    "Estimado €": 0, "Real €": 0},
        {"Partida": "Ascensor",                       "Gremio": "Por definir",    "Estimado €": 0, "Real €": 0},
        {"Partida": "Equipamiento fitness",           "Gremio": "Thomas Wellness","Estimado €": 0, "Real €": 0},
    ]
    df_capex = pd.DataFrame(CAPEX_REFERENCIA)
    df_capex["Diferencia €"] = df_capex["Real €"] - df_capex["Estimado €"]

    cap1, cap2, cap3 = st.columns(3)
    cap1.metric("CAPEX estimado total",  "Pendiente licitaciones")
    cap2.metric("CAPEX comprometido",    "0 €")
    cap3.metric("Gremios contratados",   "2 / 10")

    st.dataframe(df_capex, use_container_width=True, hide_index=True,
        column_config={
            "Estimado €":   st.column_config.NumberColumn("Estimado (€)",   format="%.0f"),
            "Real €":       st.column_config.NumberColumn("Real (€)",        format="%.0f"),
            "Diferencia €": st.column_config.NumberColumn("Diferencia (€)", format="%.0f"),
        })
