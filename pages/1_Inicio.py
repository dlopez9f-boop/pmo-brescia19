#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pages/1_Inicio.py
Dashboard ejecutivo — KPIs globales de la red de centros Nine Fitness.
Fuente de datos: Google Sheets (PMO Tracker) + SQLite (Actas).
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from _auth import require_auth

st.set_page_config(page_title="Inicio · PMO", page_icon="📊", layout="wide")
require_auth()

NAVY = "#0B1F3A"
GOLD = "#C9A96E"
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden !important; }
  [data-testid="stSidebar"] { border-right: 1px solid #E8E0CE !important; }
</style>
""", unsafe_allow_html=True)

st.markdown(
    f"<div style='background:{NAVY};padding:12px 20px;border-bottom:2px solid {GOLD};"
    f"margin:-1rem -1rem 1rem -1rem'>"
    f"<span style='color:{GOLD};font-weight:700;font-size:15px;letter-spacing:.08em'>"
    f"📊 INICIO · RESUMEN EJECUTIVO</span>"
    f"<span style='color:#6a8aaa;font-size:11px;margin-left:14px'>Estado operativo de la red — {pd.Timestamp.now().strftime('%d/%m/%Y')}</span>"
    f"</div>",
    unsafe_allow_html=True,
)


# ── CONEXIÓN GOOGLE SHEETS ────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def _gs_client():
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPES
        )
        return gspread.authorize(creds)
    except Exception:
        return None

@st.cache_data(ttl=60, show_spinner=False)
def _load(tab: str) -> pd.DataFrame:
    client = _gs_client()
    if client is None:
        return pd.DataFrame()
    try:
        sh = client.open(st.secrets.get("sheet_name", "PMO_Nine_Tracker"))
        rows = sh.worksheet(tab).get_all_records()
        return pd.DataFrame(rows) if rows else pd.DataFrame()
    except Exception as e:
        st.warning(f"No se pudo cargar '{tab}' desde Google Sheets: {e}")
        return pd.DataFrame()


# ── CARGA DE DATOS ────────────────────────────────────────────────────────────
col_ref, _ = st.columns([1, 4])
if col_ref.button("🔄 Actualizar datos", use_container_width=True):
    _load.clear()
    st.rerun()

df_pres  = _load("Presupuestos")
df_obras = _load("Obras")


# ── KPIs PRESUPUESTOS ─────────────────────────────────────────────────────────
st.subheader("📋 Presupuestos")
if df_pres.empty:
    st.info("Sin datos de presupuestos. Verifica la conexión con Google Sheets.")
else:
    total_p   = len(df_pres)
    pte_ap    = (df_pres.get("Estado", pd.Series()) == "Recibido · pte. aprobación").sum()
    criticos  = (df_pres.get("Urgencia", pd.Series()) == "CRÍTICO").sum()
    importe   = pd.to_numeric(df_pres.get("Importe", pd.Series()), errors="coerce").sum()
    aprobados = (df_pres.get("Estado", pd.Series()) == "Aprobado").sum()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total presupuestos", total_p)
    k2.metric("Pte. aprobación", pte_ap, delta="⚠️" if pte_ap > 3 else None, delta_color="inverse")
    k3.metric("Aprobados", aprobados)
    k4.metric("🔴 Críticos", criticos, delta="urgente" if criticos else None, delta_color="inverse")
    k5.metric("Comprometido", f"{importe:,.0f} €".replace(",", "."))

    # Distribución por estado
    if "Estado" in df_pres.columns:
        fig_p = px.bar(
            df_pres["Estado"].value_counts().reset_index(),
            x="count", y="Estado", orientation="h",
            color="Estado", color_discrete_sequence=px.colors.qualitative.Set3,
            title="Presupuestos por estado",
        )
        fig_p.update_layout(
            height=240, showlegend=False, margin=dict(l=0, r=0, t=36, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e0e3ed", xaxis=dict(gridcolor="#2a2f3e"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_p, use_container_width=True)

st.divider()

# ── KPIs OBRAS ────────────────────────────────────────────────────────────────
st.subheader("🏗 Obras Abiertas")
if df_obras.empty:
    st.info("Sin datos de obras.")
else:
    tot_o  = len(df_obras)
    ejec_o = (df_obras.get("Estado", pd.Series()) == "En ejecución").sum()
    bloq_o = (df_obras.get("Estado", pd.Series()) == "Bloqueado").sum()
    term_o = (df_obras.get("Estado", pd.Series()) == "Terminado · pte. certificación").sum()

    o1, o2, o3, o4 = st.columns(4)
    o1.metric("Total obras", tot_o)
    o2.metric("En ejecución", ejec_o)
    o3.metric("🔴 Bloqueadas", bloq_o, delta="bloqueada" if bloq_o else None, delta_color="inverse")
    o4.metric("Pte. certificar", term_o)

    c1, c2 = st.columns(2)

    if "Centro" in df_obras.columns:
        with c1:
            fig_o = px.bar(
                df_obras["Centro"].value_counts().reset_index(),
                x="count", y="Centro", orientation="h",
                title="Obras por centro",
                color_discrete_sequence=[GOLD],
            )
            fig_o.update_layout(
                height=280, showlegend=False, margin=dict(l=0, r=0, t=36, b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e0e3ed", xaxis=dict(gridcolor="#2a2f3e"),
                yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            )
            st.plotly_chart(fig_o, use_container_width=True)

    if "Estado" in df_obras.columns:
        with c2:
            fig_e = px.pie(
                df_obras, names="Estado",
                title="Distribución por estado",
                color_discrete_sequence=px.colors.qualitative.Set2,
                hole=0.4,
            )
            fig_e.update_layout(
                height=280, margin=dict(l=0, r=0, t=36, b=0),
                paper_bgcolor="rgba(0,0,0,0)", font_color="#e0e3ed",
            )
            st.plotly_chart(fig_e, use_container_width=True)

st.divider()

# ── TABLA RÁPIDA BLOQUEADOS ───────────────────────────────────────────────────
if not df_obras.empty and "Estado" in df_obras.columns:
    bloqueados = df_obras[df_obras["Estado"] == "Bloqueado"]
    if not bloqueados.empty:
        st.subheader("🔴 Obras Bloqueadas — Acción Urgente")
        cols_show = [c for c in ["Centro", "Descripcion", "Gremio", "Responsable", "Notas"] if c in bloqueados.columns]
        st.dataframe(bloqueados[cols_show], use_container_width=True, hide_index=True)
