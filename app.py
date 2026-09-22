#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app.py — PMO Master · Nine Fitness Group
Punto de entrada: autenticación + bienvenida.
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
  [data-testid="stAppViewContainer"]{background:#0e1117}
  [data-testid="stSidebar"]{background:#161b27}
  [data-testid="stSidebar"] *{color:#e0e3ed!important}
  .mod-card{
    background:#161b27;border:1px solid #2a2f3e;border-radius:10px;
    padding:22px;text-align:center;height:170px;transition:border-color .2s
  }
  .mod-card:hover{border-color:#C9A96E}
</style>
""", unsafe_allow_html=True)

NAVY = "#0B1F3A"
GOLD = "#C9A96E"

st.markdown(
    f"<div style='background:{NAVY};padding:14px 22px;border-bottom:2px solid {GOLD};"
    f"margin:-1rem -1rem 1.5rem -1rem;display:flex;align-items:center;gap:14px'>"
    f"<span style='color:{GOLD};font-weight:800;font-size:16px;letter-spacing:.08em'>"
    f"🏋️&nbsp; PMO MASTER · NINE FITNESS GROUP</span>"
    f"<span style='color:#3a5a80;font-size:11px'>Panel de control de operaciones · Red de centros</span>"
    f"</div>",
    unsafe_allow_html=True,
)

st.markdown("#### Selecciona un módulo en el panel lateral")
st.caption("O haz clic en las tarjetas de acceso rápido.")

cols = st.columns(4)
MODULOS = [
    ("📊", "Inicio", "KPIs globales, alertas activas y resumen ejecutivo de la red de centros."),
    ("🏗", "Obra Principal", "Nine Club Chamartín — Gantt de fases, licitaciones y control CAPEX."),
    ("📋", "PMO Live Tracker", "Presupuestos y obras abiertas en centros operativos. Editable en tiempo real."),
    ("📝", "Actas y Certificaciones", "Registro de actas diarias, semanales, generador y certificaciones de avance."),
]
for col, (icon, nombre, desc) in zip(cols, MODULOS):
    col.markdown(
        f"<div class='mod-card'>"
        f"<div style='font-size:30px'>{icon}</div>"
        f"<div style='font-size:13px;font-weight:700;color:#fff;margin:8px 0 6px'>{nombre}</div>"
        f"<div style='font-size:11px;color:#64748b;line-height:1.45'>{desc}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
