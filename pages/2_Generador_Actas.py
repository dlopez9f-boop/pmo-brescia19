#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pages/2_Generador_Actas.py
Motor de generación de actas oficiales · Nine Fitness Brescia 19

Bloques:
  1. Capa de datos   — CRUD via db.py (GitHub JSON / SQLite)
  2. Motor HTML      — generar_html(datos) → plantilla corporativa
  3. UI Streamlit    — form editor + preview en tiempo real + descarga
"""

import json
import uuid
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date, datetime

from db import (
    init_db, backend_info, semana_obra,
    list_registro_actas, get_registro_acta,
    upsert_registro_acta, delete_registro_acta,
)

init_db()

# ══════════════════════════════════════════════════════════════════
#  BLOQUE 1 — HELPERS DE DATOS
# ══════════════════════════════════════════════════════════════════

ESTADOS_GENERAL = ["en_curso", "alerta", "critico", "completado", "borrador"]
ESTADOS_CONTRATA = ["en_curso", "completado", "incidencia", "pendiente", "no_iniciado"]
PRIORIDADES = ["alta", "media", "baja", "critica"]

CATEGORIAS_DEF = [
    "Distribución y accesos",
    "Protección contra incendios",
    "Tabiquería y estructuras",
    "Acabados y estética",
    "Instalaciones",
    "Equipamiento",
    "Normativa PMR",
    "Otro",
]

def _df_intervenciones(data: list) -> pd.DataFrame:
    cols = ["contrata", "responsable", "estado", "descripcion"]
    if not data:
        return pd.DataFrame([{c: "" for c in cols}])
    rows = [{c: r.get(c, "") for c in cols} for r in data]
    return pd.DataFrame(rows)

def _df_definiciones(data: list) -> pd.DataFrame:
    cols = ["categoria", "elemento", "detalle"]
    if not data:
        return pd.DataFrame([{c: "" for c in cols}])
    rows = [{c: r.get(c, "") for c in cols} for r in data]
    return pd.DataFrame(rows)

def _df_acuerdos(data: list) -> pd.DataFrame:
    cols = ["acuerdo", "responsable", "plazo"]
    if not data:
        return pd.DataFrame([{c: "" for c in cols}])
    rows = [{c: r.get(c, "") for c in cols} for r in data]
    return pd.DataFrame(rows)

def _df_agenda(data: list) -> pd.DataFrame:
    cols = ["hora", "evento", "obligatorio"]
    if not data:
        return pd.DataFrame([{"hora": "", "evento": "", "obligatorio": False}])
    rows = [{"hora": r.get("hora",""), "evento": r.get("evento",""), "obligatorio": bool(r.get("obligatorio", False))} for r in data]
    return pd.DataFrame(rows)

def _df_incidencias(data: list) -> pd.DataFrame:
    cols = ["gremio", "descripcion", "prioridad"]
    if not data:
        return pd.DataFrame([{c: "" for c in cols}])
    rows = [{c: r.get(c, "") for c in cols} for r in data]
    return pd.DataFrame(rows)

def _df_to_list(df: pd.DataFrame) -> list:
    return [r for r in df.to_dict("records") if any(str(v).strip() for v in r.values())]


# ══════════════════════════════════════════════════════════════════
#  BLOQUE 2 — MOTOR HTML / CSS
# ══════════════════════════════════════════════════════════════════

_BADGE_CSS = {
    "en_curso":    "background:#fff8e1;color:#e65100;border:1px solid #ffe0b2;",
    "completado":  "background:#f0faf4;color:#27ae60;border:1px solid #a8d8b9;",
    "incidencia":  "background:#fdf2f2;color:#c0392b;border:1px solid #f5c6c6;",
    "pendiente":   "background:#f1f5f9;color:#64748b;border:1px solid #cbd5e1;",
    "no_iniciado": "background:#f8f9ff;color:#94a3b8;border:1px solid #e2e8f0;",
    "alerta":      "background:#fff3e0;color:#e65100;border:1px solid #ffe0b2;",
    "critico":     "background:#c0392b;color:#fff;border:1px solid #c0392b;",
    "borrador":    "background:#eef2ff;color:#3730a3;border:1px solid #c7d2fe;",
    "alta":        "background:#fdf2f2;color:#c0392b;border:1px solid #f5c6c6;",
    "media":       "background:#fff8e1;color:#e65100;border:1px solid #ffe0b2;",
    "baja":        "background:#f0faf4;color:#27ae60;border:1px solid #a8d8b9;",
    "critica":     "background:#c0392b;color:#fff;border:1px solid #c0392b;",
}

_ESTADO_LABEL = {
    "en_curso": "En curso", "completado": "Completado", "incidencia": "Incidencia",
    "pendiente": "Pendiente", "no_iniciado": "No iniciado", "alerta": "Alerta",
    "critico": "Crítico", "borrador": "Borrador", "alta": "Alta", "media": "Media",
    "baja": "Baja", "critica": "Crítica",
}

def _badge(estado: str) -> str:
    css = _BADGE_CSS.get(estado, "background:#eee;color:#333;")
    label = _ESTADO_LABEL.get(estado, estado.replace("_", " ").title())
    return (
        f'<span style="display:inline-block;padding:3px 10px;border-radius:20px;'
        f'font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;{css}">'
        f'{label}</span>'
    )

def _rows_intervenciones(items: list) -> str:
    if not items:
        return '<tr><td colspan="4" style="color:#94a3b8;font-style:italic;padding:12px 14px;">Sin intervenciones registradas.</td></tr>'
    rows = ""
    for i, r in enumerate(items):
        bg = "#f8f9ff" if i % 2 == 0 else "#fff"
        rows += f"""
        <tr style="background:{bg};">
          <td style="padding:10px 14px;font-weight:600;color:#1a1a2e;border-bottom:1px solid #e2e8f0;">{r.get('contrata','')}</td>
          <td style="padding:10px 14px;color:#475569;border-bottom:1px solid #e2e8f0;">{r.get('responsable','')}</td>
          <td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;">{_badge(r.get('estado','pendiente'))}</td>
          <td style="padding:10px 14px;color:#374151;border-bottom:1px solid #e2e8f0;line-height:1.5;">{r.get('descripcion','')}</td>
        </tr>"""
    return rows

def _rows_definiciones(items: list) -> str:
    if not items:
        return '<div style="color:#94a3b8;font-style:italic;padding:12px 0;">Sin definiciones técnicas.</div>'
    html = ""
    for r in items:
        html += f"""
        <div style="display:grid;grid-template-columns:170px 200px 1fr;margin-bottom:6px;
                    border:1px solid #e2e8f0;border-radius:6px;overflow:hidden;">
          <div style="background:#0f3460;color:#fff;padding:10px 12px;font-size:10px;
                      font-weight:700;text-transform:uppercase;letter-spacing:.5px;
                      display:flex;align-items:center;">{r.get('categoria','')}</div>
          <div style="background:#e8ecf4;padding:10px 12px;font-size:11px;font-weight:600;
                      color:#1a1a2e;display:flex;align-items:center;">{r.get('elemento','')}</div>
          <div style="background:#fff;padding:10px 14px;font-size:12px;color:#374151;
                      display:flex;align-items:center;line-height:1.5;">{r.get('detalle','')}</div>
        </div>"""
    return html

def _items_acuerdos(items: list) -> str:
    if not items:
        return '<div style="color:#94a3b8;font-style:italic;padding:12px 0;">Sin acuerdos técnicos.</div>'
    html = ""
    for i, r in enumerate(items, 1):
        html += f"""
        <div style="display:flex;gap:12px;padding:10px 14px;border:1px solid #e2e8f0;
                    border-radius:6px;margin-bottom:6px;background:#fff;">
          <div style="min-width:24px;height:24px;background:#e94560;color:#fff;border-radius:50%;
                      display:flex;align-items:center;justify-content:center;font-size:11px;
                      font-weight:700;flex-shrink:0;">{i}</div>
          <div style="flex:1;">
            <div style="font-size:12px;color:#1a1a2e;margin-bottom:4px;">{r.get('acuerdo','')}</div>
            <div style="font-size:10px;color:#94a3b8;">
              Responsable: <b style="color:#475569;">{r.get('responsable','—')}</b>
              &nbsp;·&nbsp; Plazo: <b style="color:#475569;">{r.get('plazo','—')}</b>
            </div>
          </div>
        </div>"""
    return html

def _items_agenda(items: list) -> str:
    if not items:
        return '<div style="color:#94a3b8;font-style:italic;padding:12px 0;">Sin agenda registrada.</div>'
    html = ""
    for r in items:
        oblig = '<span style="font-size:9px;background:#e94560;color:#fff;padding:2px 6px;border-radius:3px;font-weight:700;margin-left:8px;">OBLIGATORIO</span>' if r.get("obligatorio") else ""
        html += f"""
        <div style="display:flex;gap:14px;padding:9px 0;border-bottom:1px solid #f0f2f8;
                    align-items:flex-start;">
          <div style="min-width:52px;font-size:13px;font-weight:800;color:#e94560;">{r.get('hora','')}</div>
          <div style="font-size:12px;color:#1a1a2e;flex:1;">{r.get('evento','')}{oblig}</div>
        </div>"""
    return html

def _items_incidencias(items: list) -> str:
    if not items:
        return '<div style="color:#94a3b8;font-style:italic;padding:12px 0;">Sin incidencias.</div>'
    html = ""
    for r in items:
        html += f"""
        <div style="background:#fdf2f2;border:1px solid #f5c6c6;border-left:4px solid #e94560;
                    border-radius:0 6px 6px 0;padding:10px 14px;margin-bottom:8px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
            <span style="font-size:11px;font-weight:700;color:#c0392b;">⚠ {r.get('gremio','')}</span>
            {_badge(r.get('prioridad','media'))}
          </div>
          <div style="font-size:12px;color:#2c3e50;">{r.get('descripcion','')}</div>
        </div>"""
    return html


def generar_html(datos: dict) -> str:
    """Toma un registro_actas y devuelve HTML corporativo listo para imprimir."""
    fecha_str = ""
    try:
        fecha_str = datetime.fromisoformat(datos.get("fecha", "")).strftime("%A %d de %B de %Y").capitalize()
    except Exception:
        fecha_str = datos.get("fecha", "")

    sem   = datos.get("semana_obra", "—")
    fase  = datos.get("fase", "—")
    redac = datos.get("redactor", "Darío A. López")
    est   = datos.get("estado_general", "en_curso")
    resum = (datos.get("resumen_ejecutivo") or "").replace("\n", "<br>")
    rec_id = datos.get("id", "—")
    created = datos.get("created_at", "")[:10]

    def _safe_list(key):
        v = datos.get(key) or []
        if isinstance(v, str):
            try: v = json.loads(v)
            except: v = []
        return v

    intervenciones     = _safe_list("intervenciones")
    definiciones       = _safe_list("definiciones_tecnicas")
    acuerdos           = _safe_list("acuerdos_tecnicos")
    agenda             = _safe_list("agenda_proxima")
    incidencias        = _safe_list("incidencias")

    n_inc  = len(incidencias)
    n_int  = len(intervenciones)
    n_ac   = len(acuerdos)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Acta {rec_id}</title>
<style>
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Helvetica Neue',Arial,sans-serif;background:#f0f2f8;
        color:#1a1a2e;font-size:13px;line-height:1.5}}
  .doc{{max-width:960px;margin:20px auto;background:#fff;border-radius:12px;
        overflow:hidden;box-shadow:0 4px 32px rgba(0,0,0,.13)}}

  /* HEADER */
  .hdr{{background:linear-gradient(135deg,#1a1a2e 0%,#0f3460 100%);
        padding:28px 36px 24px;color:#fff;position:relative}}
  .hdr-eyebrow{{font-size:9px;text-transform:uppercase;letter-spacing:3px;
                opacity:.55;margin-bottom:6px}}
  .hdr-title{{font-size:26px;font-weight:900;letter-spacing:-.5px;line-height:1.1}}
  .hdr-sub{{font-size:11px;opacity:.65;margin-top:5px}}
  .hdr-accent{{position:absolute;bottom:0;left:0;right:0;height:4px;background:#e94560}}

  /* META GRID */
  .meta{{display:grid;grid-template-columns:repeat(5,1fr);
         border-bottom:1px solid #e2e8f0}}
  .meta-cell{{padding:14px 18px;border-right:1px solid #e2e8f0}}
  .meta-cell:last-child{{border-right:none}}
  .meta-label{{font-size:9px;text-transform:uppercase;letter-spacing:1.5px;
               color:#94a3b8;font-weight:600;margin-bottom:4px}}
  .meta-value{{font-size:14px;font-weight:700;color:#1a1a2e}}

  /* KPI ROW */
  .kpi{{display:grid;grid-template-columns:repeat(3,1fr);
        background:#f8f9ff;border-bottom:1px solid #e2e8f0}}
  .kpi-cell{{padding:12px 20px;text-align:center;border-right:1px solid #e2e8f0}}
  .kpi-cell:last-child{{border-right:none}}
  .kpi-num{{font-size:24px;font-weight:900;color:#e94560}}
  .kpi-desc{{font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#94a3b8;margin-top:2px}}

  /* BODY */
  .body{{padding:28px 36px}}

  /* SECTIONS */
  .sec{{margin-bottom:28px}}
  .sec-hdr{{display:flex;align-items:center;gap:10px;margin-bottom:14px;
            padding-bottom:8px;border-bottom:2px solid #e94560}}
  .sec-icon{{font-size:16px}}
  .sec-title{{font-size:12px;font-weight:800;text-transform:uppercase;
              letter-spacing:1px;color:#1a1a2e}}

  /* RESUMEN */
  .resumen{{background:#f8f9ff;border-left:4px solid #0f3460;padding:14px 18px;
            border-radius:0 8px 8px 0;font-size:13px;color:#2c3e50;line-height:1.7}}

  /* TABLE */
  .tbl{{width:100%;border-collapse:collapse;font-size:12px}}
  .tbl thead tr{{background:#1a1a2e;color:#fff}}
  .tbl th{{padding:10px 14px;text-align:left;font-size:10px;text-transform:uppercase;
           letter-spacing:1px;font-weight:600}}
  .tbl tbody tr:hover{{background:#eef2ff!important}}

  /* FOOTER */
  .ftr{{background:#1a1a2e;padding:14px 36px;display:flex;
        justify-content:space-between;align-items:center;
        color:rgba(255,255,255,.45);font-size:10px}}
  .ftr b{{color:rgba(255,255,255,.7)}}

  @media print{{
    body{{background:#fff}}
    .doc{{box-shadow:none;margin:0;border-radius:0;max-width:100%}}
  }}
  @page{{size:A4;margin:10mm}}
</style>
</head>
<body>
<div class="doc">

  <!-- CABECERA -->
  <div class="hdr">
    <div class="hdr-eyebrow">Nine Fitness Group S.L. · Dirección de Obra</div>
    <div class="hdr-title">ACTA DE OBRA OFICIAL</div>
    <div class="hdr-sub">{fecha_str} &nbsp;·&nbsp; {datos.get('obra','Brescia 19')} &nbsp;·&nbsp; {fase}</div>
    <div class="hdr-accent"></div>
  </div>

  <!-- META DATOS -->
  <div class="meta">
    <div class="meta-cell">
      <div class="meta-label">Referencia</div>
      <div class="meta-value" style="font-size:12px;">{rec_id}</div>
    </div>
    <div class="meta-cell">
      <div class="meta-label">Semana de obra</div>
      <div class="meta-value">S{sem}</div>
    </div>
    <div class="meta-cell">
      <div class="meta-label">Redactor</div>
      <div class="meta-value" style="font-size:12px;">{redac}</div>
    </div>
    <div class="meta-cell">
      <div class="meta-label">Estado general</div>
      <div class="meta-value">{_badge(est)}</div>
    </div>
    <div class="meta-cell">
      <div class="meta-label">Apertura prevista</div>
      <div class="meta-value" style="color:#e94560;">3–5 AGO 2026</div>
    </div>
  </div>

  <!-- KPI ROW -->
  <div class="kpi">
    <div class="kpi-cell">
      <div class="kpi-num">{n_int}</div>
      <div class="kpi-desc">Contratas activas</div>
    </div>
    <div class="kpi-cell">
      <div class="kpi-num" style="color:#c0392b;">{n_inc}</div>
      <div class="kpi-desc">Incidencias</div>
    </div>
    <div class="kpi-cell">
      <div class="kpi-num" style="color:#27ae60;">{n_ac}</div>
      <div class="kpi-desc">Acuerdos técnicos</div>
    </div>
  </div>

  <!-- CUERPO -->
  <div class="body">

    <!-- RESUMEN EJECUTIVO -->
    {'<div class="sec"><div class="sec-hdr"><span class="sec-icon">📋</span><span class="sec-title">Resumen Ejecutivo</span></div><div class="resumen">' + (resum or '<span style="color:#94a3b8;font-style:italic;">Sin resumen registrado.</span>') + '</div></div>' if True else ''}

    <!-- INCIDENCIAS -->
    <div class="sec">
      <div class="sec-hdr">
        <span class="sec-icon">⚠️</span>
        <span class="sec-title">Incidencias de Jornada</span>
      </div>
      {_items_incidencias(incidencias)}
    </div>

    <!-- INTERVENCIONES -->
    <div class="sec">
      <div class="sec-hdr">
        <span class="sec-icon">🔧</span>
        <span class="sec-title">Intervenciones por Contrata</span>
      </div>
      <table class="tbl">
        <thead>
          <tr>
            <th style="width:160px;">Contrata</th>
            <th style="width:130px;">Responsable</th>
            <th style="width:110px;">Estado</th>
            <th>Descripción</th>
          </tr>
        </thead>
        <tbody>
          {_rows_intervenciones(intervenciones)}
        </tbody>
      </table>
    </div>

    <!-- DEFINICIONES TÉCNICAS -->
    <div class="sec">
      <div class="sec-hdr">
        <span class="sec-icon">📐</span>
        <span class="sec-title">Definiciones Técnicas · Replanteos y Cotas</span>
      </div>
      {_rows_definiciones(definiciones)}
    </div>

    <!-- ACUERDOS TÉCNICOS -->
    <div class="sec">
      <div class="sec-hdr">
        <span class="sec-icon">✅</span>
        <span class="sec-title">Acuerdos Técnicos</span>
      </div>
      {_items_acuerdos(acuerdos)}
    </div>

    <!-- AGENDA PRÓXIMA JORNADA -->
    <div class="sec">
      <div class="sec-hdr">
        <span class="sec-icon">📅</span>
        <span class="sec-title">Agenda — Próxima Jornada</span>
      </div>
      {_items_agenda(agenda)}
    </div>

  </div><!-- /body -->

  <!-- PIE -->
  <div class="ftr">
    <div>NINE FITNESS GROUP S.L. · Calle Brescia 19, 28028 Madrid</div>
    <div>Dir. Obra: <b>Darío A. López</b> · Arquitecto: <b>Ángel Rodríguez (COAM 12399)</b></div>
    <div>Ref: <b>{rec_id}</b> · Emitido: <b>{created}</b> · Confidencial</div>
  </div>

</div><!-- /doc -->
</body>
</html>"""


# ══════════════════════════════════════════════════════════════════
#  BLOQUE 3 — UI STREAMLIT
# ══════════════════════════════════════════════════════════════════

# ─── CSS APP ──────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #f0f2f8; }
  [data-testid="stMain"] { padding-top: 0.3rem; }
  div[data-testid="stForm"] {
    background: #fff; border-radius: 10px; padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,.07); margin-bottom: 12px;
  }
  .gen-header {
    background: linear-gradient(135deg, #1a1a2e, #0f3460);
    color: #fff; padding: 14px 22px; border-radius: 10px;
    margin-bottom: 12px; display: flex;
    justify-content: space-between; align-items: center;
  }
  .section-tag {
    display: inline-block; background: #e94560; color: #fff;
    padding: 2px 10px; border-radius: 4px; font-size: 11px;
    font-weight: 700; margin-bottom: 8px; text-transform: uppercase;
    letter-spacing: .5px;
  }
  iframe { border-radius: 8px; border: 1px solid #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ───────────────────────────────────────────────────────
hoy = date.today()
st.markdown(f"""
<div class="gen-header">
  <div>
    <div style="font-size:17px;font-weight:900;">📄 GENERADOR DE ACTAS OFICIALES</div>
    <div style="font-size:10px;opacity:.6;margin-top:2px;">
      Nine Fitness · Brescia 19 · {hoy.strftime('%A %d/%m/%Y').capitalize()}
    </div>
  </div>
  <div style="text-align:right;">
    <div style="font-size:10px;opacity:.5;">Backend</div>
    <div style="font-size:12px;font-weight:700;">{backend_info()}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── SELECTOR DE MODO ─────────────────────────────────────────────
modo = st.radio(
    "Modo", ["✨ Nueva acta", "✏️ Editar acta existente"],
    horizontal=True, label_visibility="collapsed",
)

acta_base: dict = {}

if modo == "✏️ Editar acta existente":
    actas = list_registro_actas()
    if not actas:
        st.info("No hay actas oficiales guardadas aún. Crea la primera.")
        st.stop()
    opciones = {f"{a['id']} — {a['fecha']} · {a.get('fase','')}": a["id"] for a in actas}
    sel = st.selectbox("Selecciona acta a editar", list(opciones.keys()))
    acta_base = get_registro_acta(opciones[sel]) or {}

# ─── LAYOUT PRINCIPAL: FORM | PREVIEW ─────────────────────────────
col_form, col_prev = st.columns([1, 1.3], gap="medium")

# ══════════════════════════════════════════════════════════════════
#  COLUMNA IZQUIERDA — FORMULARIO DE EDICIÓN
# ══════════════════════════════════════════════════════════════════
with col_form:
    st.markdown('<div class="section-tag">01 · Metadatos</div>', unsafe_allow_html=True)
    with st.form("form_acta_oficial", clear_on_submit=False):

        # — Metadatos —
        c1, c2 = st.columns(2)
        with c1:
            fecha_val = date.fromisoformat(acta_base["fecha"]) if acta_base.get("fecha") else hoy
            f_fecha = st.date_input("Fecha del acta", value=fecha_val)
        with c2:
            f_fase = st.text_input("Fase / Capítulo de obra",
                                   value=acta_base.get("fase", ""),
                                   placeholder="Ej: Instalaciones y Tabiquería Técnica")

        c3, c4 = st.columns(2)
        with c3:
            f_redactor = st.text_input("Redactor", value=acta_base.get("redactor", "Darío A. López"))
        with c4:
            idx_est = ESTADOS_GENERAL.index(acta_base["estado_general"]) if acta_base.get("estado_general") in ESTADOS_GENERAL else 0
            f_estado = st.selectbox("Estado general", ESTADOS_GENERAL,
                                    index=idx_est,
                                    format_func=lambda x: x.replace("_"," ").title())

        f_resumen = st.text_area("Resumen ejecutivo",
                                  value=acta_base.get("resumen_ejecutivo", ""),
                                  height=100,
                                  placeholder="Describe el avance general de la jornada...")

        st.divider()
        st.markdown('<div class="section-tag">02 · Incidencias</div>', unsafe_allow_html=True)
        df_inc = st.data_editor(
            _df_incidencias(acta_base.get("incidencias") or []),
            num_rows="dynamic", use_container_width=True, key="ed_inc",
            column_config={
                "gremio":      st.column_config.TextColumn("Gremio", width="medium"),
                "descripcion": st.column_config.TextColumn("Descripción", width="large"),
                "prioridad":   st.column_config.SelectboxColumn("Prioridad", options=PRIORIDADES, width="small"),
            },
        )

        st.divider()
        st.markdown('<div class="section-tag">03 · Intervenciones por contrata</div>', unsafe_allow_html=True)
        df_int = st.data_editor(
            _df_intervenciones(acta_base.get("intervenciones") or []),
            num_rows="dynamic", use_container_width=True, key="ed_int",
            column_config={
                "contrata":    st.column_config.TextColumn("Contrata", width="medium"),
                "responsable": st.column_config.TextColumn("Responsable", width="medium"),
                "estado":      st.column_config.SelectboxColumn("Estado", options=ESTADOS_CONTRATA, width="small"),
                "descripcion": st.column_config.TextColumn("Descripción", width="large"),
            },
        )

        st.divider()
        st.markdown('<div class="section-tag">04 · Definiciones técnicas</div>', unsafe_allow_html=True)
        df_def = st.data_editor(
            _df_definiciones(acta_base.get("definiciones_tecnicas") or []),
            num_rows="dynamic", use_container_width=True, key="ed_def",
            column_config={
                "categoria": st.column_config.SelectboxColumn("Categoría", options=CATEGORIAS_DEF, width="medium"),
                "elemento":  st.column_config.TextColumn("Elemento", width="medium"),
                "detalle":   st.column_config.TextColumn("Detalle / Cota", width="large"),
            },
        )

        st.divider()
        st.markdown('<div class="section-tag">05 · Acuerdos técnicos</div>', unsafe_allow_html=True)
        df_ac = st.data_editor(
            _df_acuerdos(acta_base.get("acuerdos_tecnicos") or []),
            num_rows="dynamic", use_container_width=True, key="ed_ac",
            column_config={
                "acuerdo":     st.column_config.TextColumn("Acuerdo", width="large"),
                "responsable": st.column_config.TextColumn("Responsable", width="medium"),
                "plazo":       st.column_config.TextColumn("Plazo", width="small"),
            },
        )

        st.divider()
        st.markdown('<div class="section-tag">06 · Agenda próxima jornada</div>', unsafe_allow_html=True)
        df_ag = st.data_editor(
            _df_agenda(acta_base.get("agenda_proxima") or []),
            num_rows="dynamic", use_container_width=True, key="ed_ag",
            column_config={
                "hora":        st.column_config.TextColumn("Hora", width="small"),
                "evento":      st.column_config.TextColumn("Evento", width="large"),
                "obligatorio": st.column_config.CheckboxColumn("Oblig.", width="small"),
            },
        )

        st.divider()
        btn_guardar = st.form_submit_button(
            "💾 Guardar / Actualizar Acta", use_container_width=True, type="primary"
        )

    # ── Procesar guardado ──────────────────────────────────────────
    if btn_guardar:
        _id = acta_base.get("id") or f"ACTA-{f_fecha.strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
        registro = {
            "id":                    _id,
            "fecha":                 f_fecha.isoformat(),
            "obra":                  "Brescia 19",
            "semana_obra":           semana_obra(f_fecha),
            "fase":                  f_fase.strip(),
            "redactor":              f_redactor.strip(),
            "estado_general":        f_estado,
            "resumen_ejecutivo":     f_resumen.strip(),
            "incidencias":           _df_to_list(df_inc),
            "intervenciones":        _df_to_list(df_int),
            "definiciones_tecnicas": _df_to_list(df_def),
            "acuerdos_tecnicos":     _df_to_list(df_ac),
            "agenda_proxima":        _df_to_list(df_ag),
            "galeria_imagenes":      acta_base.get("galeria_imagenes", []),
            "created_at":            acta_base.get("created_at", datetime.now().isoformat()),
        }
        upsert_registro_acta(registro)
        st.session_state["acta_preview"] = registro
        st.success(f"✅ Acta **{_id}** guardada · {backend_info()}")
        st.rerun()

# ══════════════════════════════════════════════════════════════════
#  COLUMNA DERECHA — PREVIEW + DESCARGA
# ══════════════════════════════════════════════════════════════════
with col_prev:
    st.markdown('<div class="section-tag">PREVISUALIZACIÓN EN TIEMPO REAL</div>', unsafe_allow_html=True)

    # Construir datos de preview desde el estado actual del formulario
    # (antes de guardar, usando los valores de session_state si existen)
    preview_datos = st.session_state.get("acta_preview") or acta_base or {}

    if not preview_datos:
        # Preview vacío con mensaje de instrucción
        st.info("Rellena el formulario de la izquierda y haz clic en **Guardar** para ver la previsualización del acta.")
    else:
        html_doc = generar_html(preview_datos)

        # Preview embebido (iframe)
        components.html(html_doc, height=860, scrolling=True)

        st.divider()

        # ── Botones de descarga ────────────────────────────────────
        dl1, dl2 = st.columns(2)
        _fname = f"ACTA_{preview_datos.get('id','')}_BRESCIA19.html"

        with dl1:
            st.download_button(
                label="⬇️ Descargar HTML",
                data=html_doc.encode("utf-8"),
                file_name=_fname,
                mime="text/html",
                use_container_width=True,
                type="primary",
                help="HTML autocontenido · imprime desde el navegador como PDF (Ctrl+P)",
            )
        with dl2:
            st.download_button(
                label="📋 Descargar JSON",
                data=json.dumps(preview_datos, ensure_ascii=False, indent=2).encode("utf-8"),
                file_name=_fname.replace(".html", ".json"),
                mime="application/json",
                use_container_width=True,
                help="Datos estructurados para reimportación o auditoría",
            )

        st.caption(
            "💡 Para PDF: abre el HTML descargado → **Ctrl+P** → "
            "«Guardar como PDF» → márgenes mínimos, sin cabecera/pie de página."
        )


# ── LISTADO HISTÓRICO (expandible) ────────────────────────────────
with st.expander("📚 Histórico de actas oficiales guardadas", expanded=False):
    actas_hist = list_registro_actas()
    if not actas_hist:
        st.info("Sin actas guardadas aún.")
    else:
        for a in actas_hist:
            c_info, c_prev, c_del = st.columns([4, 1, 1])
            with c_info:
                est_badge = _badge(a.get("estado_general","borrador"))
                st.markdown(
                    f"**{a['id']}** &nbsp; {a.get('fecha','')} · S{a.get('semana_obra','?')} · "
                    f"{a.get('fase','')} &nbsp; {est_badge}",
                    unsafe_allow_html=True,
                )
            with c_prev:
                if st.button("👁 Ver", key=f"v_{a['id']}", use_container_width=True):
                    st.session_state["acta_preview"] = a
                    st.rerun()
            with c_del:
                if st.button("🗑", key=f"d_{a['id']}", use_container_width=True, type="secondary"):
                    delete_registro_acta(a["id"])
                    if st.session_state.get("acta_preview", {}).get("id") == a["id"]:
                        del st.session_state["acta_preview"]
                    st.rerun()
