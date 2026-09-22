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
  #MainMenu, footer, header { visibility: hidden !important; }
  html, body,
  [data-testid="stAppViewContainer"],
  [data-testid="stAppViewBlockContainer"],
  .main, .block-container,
  section[data-testid="stMain"] {
    background-color: #FDFCF9 !important;
  }
  [data-testid="stSidebar"] { background: #fff !important; border-right: 1px solid #E8E0CE !important; }
  .mod-card {
    background: #fff;
    border: 1px solid #E8E0CE;
    border-radius: 12px;
    padding: 24px 20px 16px;
    text-align: center;
    min-height: 160px;
    box-shadow: 0 2px 12px rgba(11,31,58,.06);
    transition: box-shadow .2s, border-color .2s;
  }
  .mod-card:hover { border-color: #C9A96E; box-shadow: 0 6px 24px rgba(201,169,110,.18); }
  div[data-testid="column"] .stButton > button {
    background: #C9A96E !important;
    color: #0B1F3A !important;
    border: none !important;
    border-radius: 7px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    letter-spacing: .04em !important;
    padding: 9px 0 !important;
    width: 100% !important;
    margin-top: 6px !important;
    box-shadow: 0 2px 8px rgba(201,169,110,.25) !important;
    transition: background .15s !important;
  }
  div[data-testid="column"] .stButton > button:hover {
    background: #B8935A !important;
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
