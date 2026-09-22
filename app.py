#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app.py — PMO Master · Nine Fitness Group
Punto de entrada: autenticación + bienvenida con tarjetas navegables.
"""
import streamlit as st
from _auth import require_auth

st.set_page_config(
    page_title="PMO · Nine Fitness Group",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded",
)

require_auth()

# ── ESTILOS GLOBALES ──────────────────────────────────────────────────────────
st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden; }
  [data-testid="stAppViewContainer"] { background: #F2F3F5; }
  [data-testid="stSidebar"] { background: #fff; border-right: 1px solid #E5E8EF; }
  .mod-card {
    background: #fff;
    border: 1px solid #E5E8EF;
    border-radius: 12px;
    padding: 24px 20px 16px;
    text-align: center;
    min-height: 160px;
    box-shadow: 0 2px 12px rgba(11,31,58,.06);
    transition: box-shadow .2s, border-color .2s;
  }
  .mod-card:hover { border-color: #D31224; box-shadow: 0 6px 24px rgba(211,18,36,.10); }
  /* Botones de tarjeta en rojo */
  div[data-testid="column"] .stButton > button {
    background: #D31224 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 8px 0 !important;
    width: 100% !important;
    margin-top: 6px !important;
    box-shadow: 0 2px 8px rgba(211,18,36,.15) !important;
    transition: background .15s !important;
  }
  div[data-testid="column"] .stButton > button:hover {
    background: #B00E1D !important;
  }
</style>
""", unsafe_allow_html=True)

NAVY = "#0B1F3A"
GOLD = "#C9A96E"

st.markdown(
    f"<div style='background:{NAVY};padding:14px 22px;border-bottom:2px solid {GOLD};"
    f"margin:-1rem -1rem 1.5rem -1rem;display:flex;align-items:center;gap:14px'>"
    f"<span style='color:{GOLD};font-weight:800;font-size:16px;letter-spacing:.08em'>"
    f"🏋️&nbsp; PMO MASTER · NINE FITNESS GROUP</span>"
    f"<span style='color:#4a6a8a;font-size:11px'>Panel de control de operaciones · Red de centros</span>"
    f"</div>",
    unsafe_allow_html=True,
)

st.markdown("#### Selecciona un módulo")
st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

MODULOS = [
    ("📊", "Inicio",                  "KPIs globales, alertas activas y resumen ejecutivo de la red.", "pages/1_Inicio.py"),
    ("🏗",  "Obra Principal",          "Nine Club Chamartín — Gantt, licitaciones y control CAPEX.",   "pages/2_Obra_Principal.py"),
    ("📋", "PMO Live Tracker",        "Presupuestos y obras en centros operativos. Editable.",         "pages/3_PMO_Live_Tracker.py"),
    ("📝", "Actas y Certificaciones", "Actas diarias, semanales, generador y certificaciones.",        "pages/4_Actas_y_Certificaciones.py"),
]

cols = st.columns(4, gap="medium")
for col, (icon, nombre, desc, page) in zip(cols, MODULOS):
    with col:
        st.markdown(
            f"<div class='mod-card'>"
            f"<div style='font-size:32px;margin-bottom:10px'>{icon}</div>"
            f"<div style='font-size:13px;font-weight:700;color:#0B1F3A;margin-bottom:8px'>{nombre}</div>"
            f"<div style='font-size:11px;color:#6B7280;line-height:1.5'>{desc}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if st.button("Abrir →", key=f"nav_{nombre}", use_container_width=True):
            st.switch_page(page)
