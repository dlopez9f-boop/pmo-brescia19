#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agentes_pmo.py — Panel privado de Agentes IA · PMO Brescia 19
Uso exclusivo: Darío A. López
Arrancar: streamlit run agentes_pmo.py --server.port 8505
"""

import streamlit as st
from datetime import date, datetime

st.set_page_config(
    page_title="Agentes PMO | Brescia 19",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Acceso privado ─────────────────────────────────────────────────
def _check():
    def _submit():
        st.session_state["_ok"] = (
            st.session_state.get("_pwd", "") == st.secrets.get("password_pmo", "brescia19")
        )
    if st.session_state.get("_ok"):
        return True
    st.markdown("""
    <style>
      [data-testid="stAppViewContainer"]{background:#0e1117;}
      [data-testid="stSidebar"]{display:none;}
    </style>
    """, unsafe_allow_html=True)
    col = st.columns([1,2,1])[1]
    with col:
        st.markdown("## 🤖 Agentes PMO — Acceso Privado")
        st.text_input("Contraseña", type="password", key="_pwd", on_change=_submit)
        if st.button("Entrar", use_container_width=True, type="primary"):
            _submit()
        if "_ok" in st.session_state and not st.session_state["_ok"]:
            st.error("Contraseña incorrecta.")
    return False

if not _check():
    st.stop()

# ── Conexión Supabase ──────────────────────────────────────────────
_sb_url = st.secrets.get("SUPABASE_URL", "")
_sb_key = st.secrets.get("SUPABASE_KEY", "")

if not _sb_url or _sb_url.startswith("https://TU"):
    st.error("Credenciales Supabase no configuradas en secrets.toml.")
    st.stop()

try:
    from supabase import create_client
    sb = create_client(_sb_url, _sb_key)
except Exception as e:
    st.error(f"Error conectando Supabase: {e}")
    st.stop()

# ── UI ─────────────────────────────────────────────────────────────
st.title("🤖 Reportes Automatizados de Agentes PMO")
st.caption("Panel privado · Brescia 19 · Solo director de obra")

TIPO_COLORS = {
    "incidencia": ("🔴", "⚠️"),
    "avance":     ("🟢", "📈"),
    "material":   ("🟡", "📦"),
    "calidad":    ("🔵", "🔍"),
    "seguridad":  ("🔴", "🦺"),
}
ESTADOS_REV = ["pendiente", "validado", "rechazado"]

# Filtros
fc1, fc2, fc3 = st.columns(3)
with fc1:
    f_agente = st.text_input("Buscar agente", placeholder="Ej: Agente Calidad")
with fc2:
    f_estado = st.selectbox("Estado", ["todos"] + ESTADOS_REV)
with fc3:
    f_tipo = st.selectbox("Tipo", ["todos", "incidencia", "avance", "material", "calidad", "seguridad"])

# Cargar reportes
try:
    q = sb.table("reportes_agentes").select("*").order("created_at", desc=True).limit(100)
    if f_estado != "todos":
        q = q.eq("estado_revision", f_estado)
    if f_tipo != "todos":
        q = q.eq("tipo_reporte", f_tipo)
    resp = q.execute()
    reportes = resp.data or []
    if f_agente.strip():
        reportes = [r for r in reportes if f_agente.lower() in (r.get("agente_emisor") or "").lower()]
except Exception as e:
    st.error(f"Error leyendo reportes: {e}")
    reportes = []

# KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total", len(reportes))
k2.metric("Pendientes",  sum(1 for r in reportes if r.get("estado_revision") == "pendiente"))
k3.metric("Validados",   sum(1 for r in reportes if r.get("estado_revision") == "validado"))
k4.metric("Rechazados",  sum(1 for r in reportes if r.get("estado_revision") == "rechazado"))

st.divider()

if not reportes:
    st.info("No hay reportes todavía. Los agentes envían datos vía POST a Supabase.")
    st.markdown("#### 📡 Endpoint para agentes")
    st.code(f"""import requests
requests.post(
    "{_sb_url}/rest/v1/reportes_agentes",
    headers={{"apikey": "{_sb_key[:20]}...", "Content-Type": "application/json"}},
    json={{
        "obra": "Brescia 19",
        "fecha": "{date.today().isoformat()}",
        "agente_emisor": "Agente Control Calidad",
        "tipo_reporte": "incidencia",
        "incidencias_detectadas": "Texto del reporte...",
        "estado_revision": "pendiente"
    }}
)""", language="python")
else:
    for r in reportes:
        tipo  = r.get("tipo_reporte", "") or "sin tipo"
        icono = TIPO_COLORS.get(tipo, ("⚪", "🤖"))[1]
        est   = r.get("estado_revision", "pendiente")
        fecha = r.get("fecha", "") or (r.get("created_at", "") or "")[:10]

        with st.expander(f"{icono} **{r.get('agente_emisor','Agente')}** · {fecha} · {tipo.upper()} · _{est}_"):
            col_info, col_acc = st.columns([2, 1])

            with col_info:
                st.markdown("**Incidencias / Hallazgos:**")
                inc_txt = r.get("incidencias_detectadas") or "_Sin texto._"
                st.warning(inc_txt) if est == "pendiente" else st.info(inc_txt)
                if r.get("datos_json"):
                    with st.expander("📎 JSON completo"):
                        st.json(r["datos_json"])

            with col_acc:
                st.markdown(f"**Obra:** {r.get('obra','')}")
                st.markdown(f"**ID:** `{str(r.get('id',''))[:8]}…`")
                st.divider()
                nuevo_estado = st.selectbox(
                    "Cambiar estado", ESTADOS_REV,
                    index=ESTADOS_REV.index(est) if est in ESTADOS_REV else 0,
                    key=f"est_{r['id']}",
                )
                if st.button("💾 Guardar", key=f"upd_{r['id']}", use_container_width=True, type="primary"):
                    try:
                        sb.table("reportes_agentes").update(
                            {"estado_revision": nuevo_estado}
                        ).eq("id", r["id"]).execute()
                        st.success(f"→ **{nuevo_estado}**")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

                if nuevo_estado == "validado":
                    if st.button("📋 Incorporar a Acta", key=f"inc_{r['id']}", use_container_width=True):
                        from db import upsert_acta_diaria, semana_obra as sw
                        try:
                            f_d = date.fromisoformat(str(fecha))
                        except Exception:
                            f_d = date.today()
                        _id_new = f"ACT-AGENTE-{r['id'][:8].upper()}"
                        upsert_acta_diaria({
                            "id":                    _id_new,
                            "fecha":                 f_d.isoformat(),
                            "semana_obra":           sw(f_d),
                            "obra":                  r.get("obra", "Brescia 19"),
                            "texto_original":        r.get("incidencias_detectadas", ""),
                            "resumen":               f"[Agente {r.get('agente_emisor','')}] {(r.get('incidencias_detectadas') or '')[:80]}",
                            "intervenciones":        "{}",
                            "definiciones_tecnicas": "{}",
                            "agenda_proxima":        "{}",
                            "incidencias":           f'["{r.get("incidencias_detectadas","")}"]',
                            "gremios_incidencia":    "[]",
                            "prioridad":             "alta",
                            "estado":                "borrador",
                            "creado_por":            r.get("agente_emisor", "Agente IA"),
                        })
                        st.success(f"✅ Incorporado como **{_id_new}**")

st.divider()
st.caption(f"PMO Brescia 19 · {date.today().isoformat()} · Darío A. López")
