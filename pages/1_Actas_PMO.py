#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pages/1_Actas_PMO.py — Actas diarias + semanales · Nine Fitness Brescia 19
"""

import json
import streamlit as st
from datetime import date, datetime, timedelta

_DIAS_ES  = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
_MESES_ES = ["enero","febrero","marzo","abril","mayo","junio","julio",
             "agosto","septiembre","octubre","noviembre","diciembre"]

def fecha_es(d, fmt="largo") -> str:
    if isinstance(d, str):
        try: d = datetime.fromisoformat(d)
        except: return d
    ds = _DIAS_ES[d.weekday()]
    ms = _MESES_ES[d.month - 1]
    if fmt == "largo":  return f"{ds} {d.day} de {ms} de {d.year}"
    if fmt == "corto":  return f"{ds[:3]} {d.strftime('%d/%m/%Y')}"
    if fmt == "mini":   return f"{ds[:3]} {d.strftime('%d/%m')}"
    return d.strftime('%d/%m/%Y')

def _parse_agenda(acta) -> list:
    raw = acta.get("agenda_proxima") or {}
    if isinstance(raw, str):
        try: raw = json.loads(raw)
        except: return [{"hora": "—", "evento": raw}]
    if isinstance(raw, dict):
        items = raw.get("items") or []
        if items:
            return [{"hora": str(i.get("hora","—")), "evento": str(i.get("evento",""))} for i in items]
        texto = raw.get("texto","")
        if texto:
            return [{"hora": "—", "evento": l.strip()} for l in texto.splitlines() if l.strip()]
    return []

def _texto_inc(i) -> str:
    """Normaliza incidencia a texto plano, sea string o dict."""
    if isinstance(i, dict):
        return i.get("descripcion") or i.get("detalle") or str(i)
    return str(i)

def _normalizar_incs(raw) -> list:
    """Devuelve lista de strings a partir de incidencias en cualquier formato."""
    if not raw:
        return []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            return [raw]
    if isinstance(raw, list):
        return [_texto_inc(i) for i in raw]
    return [str(raw)]

import db
from db import (
    init_db, backend_info, semana_obra,
    list_actas_diarias, get_acta_diaria, upsert_acta_diaria, delete_acta_diaria,
    list_actas_semanales, upsert_acta_semanal, delete_acta_semanal, consolidar_semana,
)

init_db()

modo_publico = st.query_params.get("view", "") == "public"

# ─── PARSER ───────────────────────────────────────────────────────
GREMIO_KW = {
    "⚡ Electricidad":  ["luis", "elecrea", "cuadro", "bandeja", "cableado", "iga", "diferencial"],
    "❄️ Climatización": ["jose", "nacho", "servitec", "conducto", "daikin", "clima", "difusor", "altillo"],
    "🧱 Albañilería":   ["munir", "ziad", "mohamed", "solera", "tabiq", "escombro", "nivelac", "pladur"],
    "🪵 Carpintería":   ["josevi", "upn", "espejo", "carpintería", "viga", "estructura"],
    "🔥 PCI":           ["leo", "troser", "extinción", "pci", "rociador"],
    "♿ Accesibilidad": ["pedro", "hersan", "salvaescaleras", "pmr", "fortis"],
}
INC_KW    = ["problema", "retraso", "falta", "pendiente urgente", "alerta", "sin material", "parado", "bloqueado", "ausencia", "no asistido"]
AGENDA_KW = ["mañana", "próximo día", "08:", "09:", "10:", "reunión"]

def parsear(texto: str) -> dict:
    lines   = [l.strip() for l in texto.splitlines() if l.strip()]
    secs: dict = {g: [] for g in GREMIO_KW}
    incs, agenda = [], []
    for line in lines:
        ll = line.lower()
        for g, kws in GREMIO_KW.items():
            if any(k in ll for k in kws):
                secs[g].append(line)
                break
        if any(k in ll for k in INC_KW):
            incs.append(line)
        if any(k in ll for k in AGENDA_KW):
            agenda.append(line)
    gremios_inc = [
        g for g in GREMIO_KW
        if secs[g] and any(k in " ".join(secs[g]).lower() for k in INC_KW)
    ]
    return {
        "intervenciones":       {g: "\n".join(v) for g, v in secs.items() if v},
        "incidencias":          incs,
        "agenda_proxima":       {"texto": "\n".join(agenda)},
        "gremios_incidencia":   gremios_inc,
    }

# ─── HELPERS INTERNOS HTML ────────────────────────────────────────
def _parse_json(raw, default=None):
    if default is None:
        default = []
    if not raw:
        return default
    if isinstance(raw, (list, dict)):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:
            return default
    return default

def _inc_to_dict(i) -> dict:
    if isinstance(i, dict):
        return i
    return {"gremio": "General", "descripcion": str(i), "prioridad": "normal"}

# ─── GENERADOR HTML SEMANAL ───────────────────────────────────────
def html_semanal(acta_sem: dict, diarias: list[dict]) -> str:
    sem      = acta_sem.get("semana_obra", "?")
    sem_ano  = acta_sem.get("semana_ano", f"S{sem}/2026")
    fi       = acta_sem.get("fecha_inicio", "")
    ff       = acta_sem.get("fecha_fin", "")
    fi_fmt   = fecha_es(fi, "corto") if fi else ""
    ff_fmt   = fecha_es(ff, "corto") if ff else ""
    act_id   = acta_sem.get("id", "")
    aprobado = acta_sem.get("aprobado_por", "Darío A. López")

    # ── Agregar datos de todas las diarias ──
    all_incs, all_logros, all_sols = [], [], []
    for a in diarias:
        for i in _parse_json(a.get("incidencias")):
            all_incs.append(_inc_to_dict(i))
        for l in _parse_json(a.get("logros_tecnicos")):
            if isinstance(l, dict) and l.get("descripcion"):
                all_logros.append(l)
        for s in _parse_json(a.get("solicitudes_direccion")):
            if isinstance(s, dict) and s.get("descripcion"):
                all_sols.append(s)

    # Deduplicar solicitudes por descripción
    seen, unique_sols = set(), []
    for s in all_sols:
        k = s.get("descripcion", "")
        if k not in seen:
            seen.add(k); unique_sols.append(s)

    # Agenda: del acta más reciente que tenga items
    agenda_items = []
    for a in diarias:
        items = _parse_agenda(a)
        if items:
            agenda_items = items; break

    # KPIs
    n_dias   = len(diarias)
    gremios  = set()
    for a in diarias:
        for g in _parse_json(a.get("gremios_incidencia")):
            gremios.add(g)
    n_logros = len(all_logros)
    n_incs   = len(all_incs)
    n_sols   = len(unique_sols)

    # ── CSS ──
    css = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Helvetica Neue',Arial,sans-serif;background:#f0f2f8;color:#1a1a2e;font-size:13px;line-height:1.5}
.doc{max-width:960px;margin:16px auto;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.12)}
.hdr{background:linear-gradient(135deg,#1a1a2e 0%,#0f3460 100%);padding:24px 34px 20px;color:#fff;position:relative}
.hdr-ey{font-size:9px;text-transform:uppercase;letter-spacing:3px;opacity:.5;margin-bottom:5px}
.hdr-t{font-size:26px;font-weight:900;letter-spacing:-.5px;line-height:1.1}
.hdr-s{font-size:11px;opacity:.6;margin-top:5px}
.hdr-badge{position:absolute;top:24px;right:34px;background:#e94560;color:#fff;font-size:10px;font-weight:800;padding:5px 16px;border-radius:20px;letter-spacing:1px;text-transform:uppercase}
.accent{position:absolute;bottom:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#e94560,#0f3460,#e94560)}
.meta{display:grid;grid-template-columns:repeat(5,1fr);border-bottom:1px solid #e2e8f0}
.mc{padding:12px 14px;border-right:1px solid #e2e8f0}
.mc:last-child{border-right:none}
.ml{font-size:9px;text-transform:uppercase;letter-spacing:1.5px;color:#94a3b8;font-weight:600;margin-bottom:3px}
.mv{font-size:13px;font-weight:700;color:#1a1a2e}
.kpi{display:grid;grid-template-columns:repeat(5,1fr);background:#f8f9ff;border-bottom:1px solid #e2e8f0}
.kc{padding:13px 14px;text-align:center;border-right:1px solid #e2e8f0}
.kc:last-child{border-right:none}
.kn{font-size:26px;font-weight:900;line-height:1}
.kd{font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#94a3b8;margin-top:3px}
.body{padding:26px 34px}
.sec{margin-bottom:24px}
.sh{display:flex;align-items:center;gap:10px;margin-bottom:11px;padding-bottom:7px;border-bottom:2px solid #e94560}
.st{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:1px;color:#1a1a2e}
.resumen{background:#f8f9ff;border-left:4px solid #0f3460;padding:13px 16px;border-radius:0 8px 8px 0;font-size:12px;color:#2c3e50;line-height:1.7}
.dia-wrap{display:grid;grid-template-columns:64px 1fr;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin-bottom:8px}
.dia-l{background:#1a1a2e;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:8px 6px;text-align:center}
.dia-n{font-size:24px;font-weight:900;color:#e94560;line-height:1}
.dia-nm{font-size:8px;text-transform:uppercase;letter-spacing:1px;color:rgba(255,255,255,.45);margin-top:2px}
.dia-b{padding:10px 13px;background:#fff}
.dia-title{font-size:12px;font-weight:700;color:#1a1a2e;margin-bottom:4px}
.dia-txt{font-size:11px;color:#475569;line-height:1.55}
.gremio-bl{margin-bottom:6px}
.gremio-nm{font-size:10px;font-weight:700;color:#0f3460;margin-bottom:2px}
.gremio-cnt{font-size:11px;padding-left:8px;border-left:2px solid #e2e6f0;color:#374151;line-height:1.5}
.inc-item{background:#fdf2f2;border-left:3px solid #e94560;padding:8px 12px;margin-bottom:6px;border-radius:0 5px 5px 0}
.inc-hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:3px}
.inc-g{font-size:10px;font-weight:700;color:#c0392b}
.inc-d{font-size:11px;color:#374151;line-height:1.5}
.badge{display:inline-block;padding:2px 7px;border-radius:10px;font-size:9px;font-weight:700;text-transform:uppercase}
.b-r{background:#fdf2f2;color:#c0392b;border:1px solid #f5c6c6}
.b-y{background:#fff8e1;color:#e65100;border:1px solid #ffe0b2}
.b-g{background:#e8f5e9;color:#1b5e20;border:1px solid #a5d6a7}
.logro-row{display:flex;gap:10px;padding:9px 0;border-bottom:1px solid #f0f2f8;align-items:flex-start}
.logro-row:last-child{border-bottom:none}
.logro-ico{font-size:18px;flex-shrink:0;margin-top:1px}
.logro-t{font-size:11px;font-weight:700;color:#1b5e20;margin-bottom:2px}
.logro-d{font-size:11px;color:#475569}
.chips{display:flex;gap:5px;margin-top:3px;font-size:10px;align-items:center}
.ch-b{background:#fdf2f2;color:#c0392b;padding:1px 6px;border-radius:5px}
.ch-a{background:#e8f5e9;color:#1b5e20;padding:1px 6px;border-radius:5px}
.ch-ar{color:#94a3b8}
.sol-item{background:#fdf2f2;border:1px solid #f5c6c6;border-left:4px solid #e94560;border-radius:0 5px 5px 0;padding:9px 12px;margin-bottom:6px}
.sol-t{font-size:11px;font-weight:700;color:#1a1a2e;margin-bottom:2px}
.sol-m{font-size:10px;color:#94a3b8}
.tbl{width:100%;border-collapse:collapse;font-size:11px}
.tbl thead tr{background:#1a1a2e;color:#fff}
.tbl th{padding:8px 11px;text-align:left;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:600}
.tbl td{padding:8px 11px;border-bottom:1px solid #e8ecf4;vertical-align:top;color:#374151;line-height:1.5}
.tbl tr:nth-child(odd) td{background:#f8f9ff}
.tbl tr:nth-child(even) td{background:#fff}
.ag-row{display:flex;gap:12px;padding:8px 0;border-bottom:1px solid #f0f2f8;align-items:flex-start}
.ag-row:last-child{border-bottom:none}
.ag-hora{min-width:90px;font-size:12px;font-weight:800;color:#e94560;flex-shrink:0;text-align:right;padding-right:12px;border-right:2px solid #e2e8f0}
.ag-ev{font-size:11px;color:#1a1a2e;flex:1;line-height:1.5}
.ftr{background:#1a1a2e;padding:11px 34px;display:flex;justify-content:space-between;align-items:center;color:rgba(255,255,255,.4);font-size:9px;flex-wrap:wrap;gap:4px}
.ftr b{color:rgba(255,255,255,.65)}
.no-print{max-width:960px;margin:10px auto 0;text-align:right}
@media print{body{background:#fff}.doc{box-shadow:none;margin:0;border-radius:0}.no-print{display:none!important}.dia-wrap{break-inside:avoid}}
@page{size:A4;margin:8mm}"""

    # ── RESUMEN EJECUTIVO ──
    resumen_raw = acta_sem.get("resumen_ejecutivo", "")
    resumen_html = resumen_raw.replace("\n", "<br>") if resumen_raw else "Sin resumen registrado."

    # ── DÍAS ──
    ICONOS_DIA = {0:"Lun",1:"Mar",2:"Mié",3:"Jue",4:"Vie",5:"Sáb",6:"Dom"}
    bloques_dias = ""
    for a in diarias:
        try:
            _d = datetime.fromisoformat(a["fecha"])
            num   = _d.day
            nomb  = ICONOS_DIA.get(_d.weekday(), "")
        except Exception:
            num, nomb = "?", ""
        secs = _parse_json(a.get("intervenciones"), {})
        if not isinstance(secs, dict):
            secs = {}
        sec_html = ""
        for g, c in secs.items():
            if c:
                ct = str(c).replace("\n", "<br>")
                sec_html += (f'<div class="gremio-bl"><div class="gremio-nm">{g}</div>'
                             f'<div class="gremio-cnt">{ct}</div></div>')
        incs_dia = [_inc_to_dict(i) for i in _parse_json(a.get("incidencias"))]
        inc_html = ""
        for inc in incs_dia:
            pr   = inc.get("prioridad","normal")
            bcls = "b-r" if pr == "alta" else ("b-r" if pr == "urgente" else "b-y")
            grem = inc.get("gremio","")
            desc = inc.get("descripcion","")
            if desc:
                inc_html += (f'<div class="inc-item"><div class="inc-hdr">'
                             f'<span class="inc-g">{grem}</span>'
                             f'<span class="badge {bcls}">{pr}</span></div>'
                             f'<div class="inc-d">{desc}</div></div>')
        ag_items = _parse_agenda(a)
        ag_line  = " · ".join(
            it["hora"] + " " + it["evento"] for it in ag_items[:2]
        )[:200] if ag_items else ""
        bloques_dias += f"""
<div class="dia-wrap">
  <div class="dia-l"><div class="dia-n">{num}</div><div class="dia-nm">{nomb}</div></div>
  <div class="dia-b">
    <div class="dia-title">{fecha_es(a['fecha'],'largo') if a.get('fecha') else ''}</div>
    <div class="dia-txt" style="margin-bottom:8px;">{a.get('resumen','')}</div>
    {sec_html}{inc_html}
    {f'<div style="font-size:10px;color:#888;border-top:1px solid #f0f2f7;padding-top:5px;margin-top:5px;">&#128197; {ag_line}</div>' if ag_line else ''}
  </div>
</div>"""

    # ── LOGROS ──
    ICONOS_LOGRO = ["&#127942;","&#9989;","&#128274;","&#10024;","&#9889;","&#128203;","&#128200;"]
    logros_html = ""
    for idx, l in enumerate(all_logros):
        ico = ICONOS_LOGRO[idx % len(ICONOS_LOGRO)]
        ant = l.get("mejora_de","")
        des = l.get("mejora_a","")
        chips = (f'<div class="chips"><span class="ch-b">{ant}</span>'
                 f'<span class="ch-ar">&#8594;</span>'
                 f'<span class="ch-a">{des}</span></div>') if ant or des else ""
        logros_html += (f'<div class="logro-row"><div class="logro-ico">{ico}</div><div>'
                        f'<div class="logro-t">{l.get("descripcion","")}</div>'
                        f'<div class="logro-d">{l.get("impacto","")}</div>'
                        f'{chips}</div></div>')
    if not logros_html:
        logros_html = '<div style="color:#94a3b8;font-size:12px;">Sin logros técnicos registrados.</div>'

    # ── INCIDENCIAS GLOBALES ──
    incs_global_html = ""
    for inc in all_incs:
        pr   = inc.get("prioridad","normal")
        bcls = "b-r" if pr in ("alta","urgente") else "b-y"
        color_borde = "#7b0000" if pr == "urgente" else "#e94560"
        grem = inc.get("gremio","")
        desc = inc.get("descripcion","")
        if desc:
            incs_global_html += (f'<div style="background:#fdf2f2;border:1px solid #f5c6c6;'
                                 f'border-left:4px solid {color_borde};border-radius:0 5px 5px 0;'
                                 f'padding:9px 12px;margin-bottom:6px;">'
                                 f'<div style="display:flex;justify-content:space-between;margin-bottom:3px;">'
                                 f'<span style="font-size:10px;font-weight:700;color:#c0392b;">{grem}</span>'
                                 f'<span class="badge {bcls}">{pr}</span></div>'
                                 f'<div style="font-size:11px;color:#374151;">{desc}</div></div>')
    if not incs_global_html:
        incs_global_html = '<div style="color:#27ae60;font-size:12px;">Sin incidencias registradas.</div>'

    # ── SOLICITUDES DIRECCIÓN ──
    sols_html = ""
    for s in unique_sols:
        urg = s.get("urgencia","normal")
        color_urg = "#7b0000" if urg == "crítica" else ("#c0392b" if urg == "alta" else "#475569")
        resp = s.get("responsable","")
        sols_html += (f'<div class="sol-item">'
                      f'<div class="sol-t">{s.get("descripcion","")}</div>'
                      f'<div class="sol-m">Responsable: <b>{resp}</b>'
                      f'&nbsp;&middot;&nbsp; Urgencia: <b style="color:{color_urg};">{urg.upper()}</b></div>'
                      f'</div>')
    if not sols_html:
        sols_html = '<div style="color:#94a3b8;font-size:12px;">Sin solicitudes pendientes.</div>'

    # ── HITOS ──
    hitos = _parse_json(acta_sem.get("hitos_cumplidos"))
    hitos_html = "".join(
        f'<div style="font-size:12px;color:#1b5e20;padding:4px 0;border-bottom:1px solid #f0f2f8;">&#9989; {h}</div>'
        for h in hitos
    ) or '<div style="color:#94a3b8;font-size:12px;">Sin hitos registrados.</div>'

    desv = _parse_json(acta_sem.get("desviaciones_criticas"))
    desv_html = "".join(f"<li style='margin-bottom:3px;'>{d}</li>" for d in desv) if desv else "<li>Sin desviaciones.</li>"

    # ── AGENDA ──
    agenda_html = ""
    for it in agenda_items:
        agenda_html += (f'<div class="ag-row">'
                        f'<div class="ag-hora">{it["hora"]}</div>'
                        f'<div class="ag-ev">{it["evento"]}</div></div>')
    if not agenda_html:
        agenda_html = '<div style="color:#94a3b8;font-size:12px;">Sin agenda registrada para la próxima semana.</div>'

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Acta Semanal {sem_ano} &mdash; Nine Fitness Brescia 19</title>
<style>{css}</style>
</head>
<body>
<div class="no-print">
  <button onclick="window.print()" style="background:#e94560;color:#fff;border:none;padding:8px 20px;border-radius:6px;font-size:13px;font-weight:700;cursor:pointer;">&#128438; Imprimir / Guardar PDF</button>
</div>
<div class="doc">
  <div class="hdr">
    <div class="hdr-badge">{sem_ano}</div>
    <div class="hdr-ey">Nine Fitness Group S.L. &middot; PMO Brescia 19 &middot; Informe Semanal Oficial</div>
    <div class="hdr-t">INFORME SEMANAL DE OBRA</div>
    <div class="hdr-s">{fi_fmt} &ndash; {ff_fmt} &nbsp;&middot;&nbsp; Calle Brescia 19, 28028 Madrid</div>
    <div class="accent"></div>
  </div>
  <div class="meta">
    <div class="mc"><div class="ml">Referencia</div><div class="mv" style="font-size:11px;">{act_id}</div></div>
    <div class="mc"><div class="ml">Per&iacute;odo</div><div class="mv" style="font-size:11px;">{fi} &rarr; {ff}</div></div>
    <div class="mc"><div class="ml">Director de Obra</div><div class="mv" style="font-size:11px;">{aprobado}</div></div>
    <div class="mc"><div class="ml">Estado</div><div class="mv"><span class="badge b-y">{acta_sem.get("estado_aprobacion","borrador").replace("_"," ").title()}</span></div></div>
    <div class="mc"><div class="ml">Apertura prevista</div><div class="mv" style="color:#e94560;">3&ndash;5 AGO 2026</div></div>
  </div>
  <div class="kpi">
    <div class="kc"><div class="kn" style="color:#e94560;">{n_dias}</div><div class="kd">D&iacute;as de obra</div></div>
    <div class="kc"><div class="kn" style="color:#2471a3;">{len(gremios)}</div><div class="kd">Gremios activos</div></div>
    <div class="kc"><div class="kn" style="color:#27ae60;">{n_logros}</div><div class="kd">Logros t&eacute;cnicos</div></div>
    <div class="kc"><div class="kn" style="color:#c0392b;">{n_incs}</div><div class="kd">Incidencias</div></div>
    <div class="kc"><div class="kn" style="color:#7b1fa2;">{n_sols}</div><div class="kd">Pendientes Direcci&oacute;n</div></div>
  </div>
  <div class="body">

    <div class="sec">
      <div class="sh"><span>&#128203;</span><span class="st">Resumen Ejecutivo</span></div>
      <div class="resumen">{resumen_html}</div>
    </div>

    <div class="sec">
      <div class="sh"><span>&#128197;</span><span class="st">Actividad Diaria</span></div>
      {bloques_dias}
    </div>

    <div class="sec">
      <div class="sh"><span>&#127942;</span><span class="st">Logros T&eacute;cnicos y Optimizaciones</span></div>
      {logros_html}
    </div>

    <div class="sec">
      <div class="sh"><span>&#9888;&#65039;</span><span class="st">Incidencias Semana</span></div>
      {incs_global_html}
    </div>

    <div class="sec">
      <div class="sh"><span>&#128204;</span><span class="st">Solicitudes a Direcci&oacute;n &mdash; Pendientes</span></div>
      {sols_html}
    </div>

    <div class="sec">
      <div class="sh"><span>&#9989;</span><span class="st">Hitos Cumplidos</span></div>
      {hitos_html}
    </div>

    <div class="sec">
      <div class="sh"><span>&#9888;&#65039;</span><span class="st">Gremios con Desviaciones</span></div>
      <div style="background:#fdf2f2;border-left:4px solid #e74c3c;padding:10px 14px;border-radius:0 6px 6px 0;font-size:12px;">
        <ul style="margin:0 0 0 14px;padding:0;">{desv_html}</ul>
      </div>
    </div>

    <div class="sec">
      <div class="sh"><span>&#128197;</span><span class="st">Agenda Pr&oacute;xima Semana</span></div>
      {agenda_html}
    </div>

  </div>
  <div class="ftr">
    <div>NINE FITNESS GROUP S.L. &middot; Calle Brescia 19, 28028 Madrid</div>
    <div>Dir. Obra: <b>{aprobado}</b> &nbsp;&middot;&nbsp; Arquitecto: <b>&Aacute;ngel Rodr&iacute;guez Mart&iacute;nez-Conde (COAM 12399)</b></div>
    <div>Ref: <b>{act_id}</b> &nbsp;&middot;&nbsp; Emitido: <b>{ff}</b> &nbsp;&middot;&nbsp; Confidencial</div>
  </div>
</div>
</body>
</html>"""

# ─── CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #f0f2f8; }
  [data-testid="stMain"] { padding-top: 0.4rem; }

  .pmo-header {
    background: linear-gradient(135deg, #1a1a2e, #0f3460);
    color: #fff; padding: 16px 24px; border-radius: 10px;
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 4px;
  }
  .acta-card {
    border-left: 4px solid #e94560; padding: 14px 16px;
    background: #fff; border-radius: 0 8px 8px 0;
    box-shadow: 0 2px 6px rgba(0,0,0,.07); margin-bottom: 12px;
  }
  .acta-card.urgente { border-left-color: #c0392b; }
  .acta-card.alta    { border-left-color: #f39c12; }
  .sem-card {
    border: 1px solid #e2e6f0; border-radius: 8px;
    padding: 14px 18px; background: #fff; margin-bottom: 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,.05);
  }
  .badge { display:inline-block; padding:3px 9px; border-radius:4px;
           font-size:11px; font-weight:700; }
  .b-red    { background:#fdf2f2; color:#c0392b; }
  .b-amber  { background:#fff8e1; color:#e65100; }
  .b-green  { background:#f0faf4; color:#27ae60; }
  .b-blue   { background:#eaf4ff; color:#2471a3; }
  .b-purple { background:#f5eeff; color:#6a1b9a; }
  .gtag { display:inline-block; padding:2px 8px; border-radius:3px;
          font-size:10px; font-weight:600; margin:2px;
          background:#eef1f8; color:#0f3460; }
  .scroll-box { max-height: 74vh; overflow-y: auto; padding-right: 2px; }
  .pub-banner {
    background: #fff8e1; border: 1px solid #ffd54f; border-radius: 8px;
    padding: 10px 16px; font-size: 12px; color: #e65100; margin-bottom: 12px;
  }
  .backend-pill {
    font-size: 11px; background: rgba(255,255,255,.15);
    padding: 3px 10px; border-radius: 4px; color: #dde;
  }
  div[data-testid="stForm"] {
    background: #fff; border-radius: 10px; padding: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,.07);
  }
  textarea { font-family: 'Courier New', monospace !important; font-size: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ───────────────────────────────────────────────────────
hoy   = date.today()
sem   = semana_obra(hoy)
lunes = hoy - timedelta(days=hoy.weekday())
be    = backend_info()

st.markdown(f"""
<div class="pmo-header">
  <div>
    <div style="font-size:18px;font-weight:900;">📋 PMO · NINE FITNESS BRESCIA 19</div>
    <div style="font-size:11px;opacity:.65;margin-top:3px;">
      {fecha_es(hoy, "corto")} · Semana {sem} de obra
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:12px;">
    <span class="backend-pill">{be}</span>
    <div style="background:#e94560;padding:7px 16px;border-radius:6px;text-align:center;font-weight:700;">
      <div style="font-size:9px;text-transform:uppercase;opacity:.9;">Apertura</div>
      <div style="font-size:15px;">3–5 AGO 2026</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

if modo_publico:
    st.markdown("""
    <div class="pub-banner">
      👁️ <strong>Vista pública de solo lectura</strong> — No se pueden crear, editar ni eliminar registros en este modo.
    </div>""", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────
if modo_publico:
    tab1, tab3 = st.tabs(["📊 Dashboard", "📅 Actas Semanales"])
    tab2 = None
    tab2b = None
else:
    tab1, tab2, tab2b, tab3 = st.tabs(["📊 Dashboard", "✍️ Registrar", "📅 Consolidación Semanal", "🔗 Vista Pública"])


# ══════════════════════════════════════════════════════════════════
#  TAB 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════
with tab1:
    fc1, fc2, fc3, fc4, fc5 = st.columns([1.2, 1.2, 1, 1, 1])
    with fc1: f_desde = st.date_input("Desde", value=date(2026, 5, 1), key="d1")
    with fc2: f_hasta = st.date_input("Hasta", value=date(2026, 8, 31), key="d2")
    with fc3: f_prio  = st.selectbox("Prioridad", ["todas","urgente","alta","normal"], key="p1")
    with fc4: f_est   = st.selectbox("Estado",    ["todos","borrador","revisado","firmado"], key="e1")
    with fc5:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("🔄 Actualizar", use_container_width=True, key="ref1")

    actas = list_actas_diarias(f_desde.isoformat(), f_hasta.isoformat(), f_prio, f_est)

    k1, k2, k3, k4 = st.columns(4)
    total_inc = sum(len(a.get("incidencias") or []) for a in actas)
    urgentes  = sum(1 for a in actas if a.get("prioridad") == "urgente")
    firmadas  = sum(1 for a in actas if a.get("estado") == "firmado")
    with k1: st.metric("Actas registradas", len(actas))
    with k2: st.metric("Incidencias totales", total_inc)
    with k3: st.metric("Urgentes", urgentes)
    with k4: st.metric("Firmadas", firmadas)

    st.divider()
    st.caption(f"**{len(actas)}** acta(s) · filtro activo")

    st.markdown('<div class="scroll-box">', unsafe_allow_html=True)
    if not actas:
        st.info("Sin actas en el rango seleccionado.")
    for acta in actas:
        _fstr  = fecha_es(acta["fecha"], "corto")
        _prio  = acta.get("prioridad", "normal")
        _est   = acta.get("estado", "borrador")
        _sem   = acta.get("semana_obra", "?")
        _pb    = {"urgente":("b-red","🔴 Urgente"),"alta":("b-amber","🟡 Alta"),"normal":("b-green","🟢 Normal")}.get(_prio,("b-green","Normal"))
        _eb    = {"borrador":("b-blue","Borrador"),"revisado":("b-amber","Revisado"),"firmado":("b-green","✓ Firmado")}.get(_est,("b-blue","Borrador"))
        _incs  = _normalizar_incs(acta.get("incidencias"))
        _inc_h = "".join(f'<div style="font-size:11px;color:#c0392b;">⚠️ {i[:100]}</div>' for i in _incs[:3])
        _gi    = acta.get("gremios_incidencia") or []
        if isinstance(_gi, str):
            try: _gi = json.loads(_gi)
            except: _gi = [_gi]
        _gi_h  = "".join(f'<span class="gtag">{g}</span>' for g in _gi)
        _ag_items = _parse_agenda(acta)
        _ag_t     = " · ".join(it["hora"] + " " + it["evento"] for it in _ag_items[:2]) if _ag_items else ""
        _cls   = {"urgente":"acta-card urgente","alta":"acta-card alta"}.get(_prio,"acta-card")

        st.markdown(f"""
        <div class="{_cls}">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <div>
              <span style="font-size:15px;font-weight:700;">📋 {_fstr}</span>
              <span style="font-size:11px;color:#999;margin-left:8px;">S{_sem}</span>
            </div>
            <div style="display:flex;gap:6px;">
              <span class="badge {_pb[0]}">{_pb[1]}</span>
              <span class="badge {_eb[0]}">{_eb[1]}</span>
            </div>
          </div>
          <div style="font-size:13px;color:#444;margin-bottom:6px;">{acta.get('resumen','')}</div>
          {f'<div style="margin-bottom:4px;">{_inc_h}</div>' if _inc_h else ''}
          {f'<div style="margin-bottom:4px;">{_gi_h}</div>' if _gi_h else ''}
          {f'<div style="font-size:11px;color:#777;border-top:1px solid #f0f2f7;padding-top:6px;margin-top:4px;">📅 {_ag_t[:180]}</div>' if _ag_t else ''}
        </div>""", unsafe_allow_html=True)

        with st.expander(f"Detalle — {acta['id']}"):
            t_orig, t_gremio, t_inc = st.tabs(["📝 Texto original", "🔧 Por gremio", "⚠️ Incidencias"])
            with t_orig:
                st.text_area("", value=acta.get("texto_original",""), height=160, disabled=True, key=f"to_{acta['id']}")
            with t_gremio:
                secs = acta.get("intervenciones") or {}
                if isinstance(secs, str):
                    try: secs = json.loads(secs)
                    except: secs = {}
                if secs:
                    for g, c in secs.items():
                        st.markdown(f"**{g}**"); st.markdown(str(c).replace("\n","  \n")); st.divider()
                else:
                    st.info("Sin secciones parseadas.")
            with t_inc:
                incs = _normalizar_incs(acta.get("incidencias"))
                for i in incs:
                    st.error(f"⚠️ {i}")
                if not incs:
                    st.success("Sin incidencias.")

            if not modo_publico:
                col_est, col_del = st.columns([2, 1])
                with col_est:
                    nuevo_est = st.selectbox(
                        "Cambiar estado", ["borrador","revisado","firmado"],
                        index=["borrador","revisado","firmado"].index(acta.get("estado","borrador")),
                        key=f"es_{acta['id']}"
                    )
                    if st.button("Actualizar estado", key=f"upd_{acta['id']}"):
                        acta["estado"] = nuevo_est
                        upsert_acta_diaria(acta)
                        st.rerun()
                with col_del:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️ Eliminar", key=f"del_{acta['id']}", type="secondary"):
                        st.session_state[f"_cdel_{acta['id']}"] = True
                    if st.session_state.get(f"_cdel_{acta['id']}"):
                        st.warning("⚠️ ¿Confirmar borrado? Escribe en GitHub y **no se puede deshacer**.")
                        _cy2, _cn2 = st.columns(2)
                        with _cy2:
                            if st.button("✅ Sí, borrar", key=f"ydel_{acta['id']}", type="primary"):
                                delete_acta_diaria(acta["id"])
                                st.session_state.pop(f"_cdel_{acta['id']}", None)
                                st.rerun()
                        with _cn2:
                            if st.button("❌ Cancelar", key=f"ndel_{acta['id']}"):
                                st.session_state.pop(f"_cdel_{acta['id']}", None)
                                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  TAB 2 — REGISTRAR
# ══════════════════════════════════════════════════════════════════
if not modo_publico and tab2 is not None:
    with tab2:
        col_form, col_prev = st.columns([1, 1.2], gap="large")

        with col_form:
            st.markdown("### ✍️ Nueva Acta Diaria")
            with st.form("form_nueva", clear_on_submit=True):
                fecha_acta = st.date_input("Fecha", value=hoy)
                texto_raw  = st.text_area(
                    "Notas de campo (texto libre)", height=280,
                    placeholder=(
                        "Escribe o pega tus notas del día...\n\n"
                        "Ej:\n"
                        "- Luis (Elecrea): cuadro CGMP pendiente, falta IGA.\n"
                        "- Jose (Servitec): inicio conductos altillo.\n"
                        "- Mohamed (Munir): replanteo tabiquería.\n"
                        "- Mañana 08:30 reunión contratas."
                    )
                )
                resumen_m = st.text_input("Resumen ejecutivo (opcional)")
                c1, c2 = st.columns(2)
                with c1: prioridad = st.selectbox("Prioridad", ["normal","alta","urgente"])
                with c2: estado    = st.selectbox("Estado",    ["borrador","revisado","firmado"])
                guardar = st.form_submit_button("💾 Guardar", use_container_width=True, type="primary")

            if guardar:
                if not texto_raw.strip():
                    st.warning("Escribe las notas antes de guardar.")
                else:
                    from datetime import datetime as _dt
                    p   = parsear(texto_raw)
                    _id = f"ACT-{fecha_acta.strftime('%Y%m%d')}-{_dt.now().strftime('%H%M%S')}"
                    nueva = {
                        "id":                    _id,
                        "fecha":                 fecha_acta.isoformat(),
                        "semana_obra":           semana_obra(fecha_acta),
                        "obra":                  "Brescia 19",
                        "texto_original":        texto_raw,
                        "resumen":               resumen_m.strip() or f"Acta S{semana_obra(fecha_acta)} · {fecha_acta.strftime('%d/%m/%Y')}",
                        "intervenciones":        json.dumps(p["intervenciones"],     ensure_ascii=False),
                        "definiciones_tecnicas": json.dumps({},                      ensure_ascii=False),
                        "agenda_proxima":        json.dumps(p["agenda_proxima"],     ensure_ascii=False),
                        "incidencias":           json.dumps(p["incidencias"],        ensure_ascii=False),
                        "gremios_incidencia":    json.dumps(p["gremios_incidencia"], ensure_ascii=False),
                        "prioridad":             prioridad,
                        "estado":                estado,
                        "creado_por":            "Dario A. Lopez",
                    }
                    upsert_acta_diaria(nueva)
                    st.success(f"✅ Acta {_id} guardada · backend: {backend_info()}")
                    st.rerun()

        with col_prev:
            st.markdown("### 🔍 Previsualizar parser")
            pv_txt = st.text_area("Texto a analizar", height=200, key="pv",
                                   placeholder="Pega aquí para ver cómo lo parsea el sistema...")
            if st.button("Analizar", key="btn_pv"):
                if pv_txt.strip():
                    res = parsear(pv_txt)
                    st.markdown("**Secciones detectadas:**")
                    for g, c in res["intervenciones"].items():
                        st.markdown(f"- **{g}**: {str(c)[:90]}…")
                    if res["incidencias"]:
                        st.markdown("**⚠️ Incidencias:** " + " · ".join(_texto_inc(i) for i in res["incidencias"][:3]))
                    if res["agenda_proxima"].get("texto"):
                        st.markdown("**📅 Agenda:** " + res["agenda_proxima"]["texto"][:120])
                    st.markdown(f"**Gremios con incidencia:** {', '.join(res['gremios_incidencia']) or 'ninguno'}")


# ══════════════════════════════════════════════════════════════════
#  TAB 2b — CONSOLIDACIÓN SEMANAL
# ══════════════════════════════════════════════════════════════════
if not modo_publico and tab2b is not None:
    with tab2b:
        st.markdown("### 📅 Generar Acta Semanal")

        cs1, cs2, cs3 = st.columns([1, 1, 2])
        with cs1: sem_sel = st.number_input("Semana de obra", min_value=1, max_value=52, value=sem)
        with cs2:
            st.markdown("<br>", unsafe_allow_html=True)
            gen_btn = st.button("⚙️ Consolidar semana", use_container_width=True, type="primary")

        if gen_btn:
            borrador = consolidar_semana(sem_sel)
            if borrador:
                st.session_state["borrador_semanal"] = borrador
                n = len([i for i in borrador['actas_diarias_ids'].split(',') if i])
                st.success(f"Borrador S{sem_sel} generado con {n} actas.")
            else:
                st.warning(f"Sin actas diarias registradas para la semana {sem_sel}.")

        if "borrador_semanal" in st.session_state:
            b = st.session_state["borrador_semanal"]
            st.divider()
            st.markdown(f"#### Borrador: {b['semana_ano']}  ({b['fecha_inicio']} → {b['fecha_fin']})")

            resumen_edit = st.text_area("Resumen ejecutivo (editable)", value=b.get("resumen_ejecutivo",""), height=180)
            estado_ap    = st.selectbox("Estado de aprobación", ["borrador","pendiente_firma","aprobado"])
            aprobado_por = st.text_input("Aprobado por", value="Dario A. Lopez")

            col_g, col_d = st.columns(2)
            with col_g:
                if st.button("💾 Guardar acta semanal", use_container_width=True, type="primary"):
                    b["resumen_ejecutivo"]  = resumen_edit
                    b["estado_aprobacion"]  = estado_ap
                    b["aprobado_por"]       = aprobado_por
                    upsert_acta_semanal(b)
                    st.success(f"✅ Acta semanal {b['id']} guardada.")
                    del st.session_state["borrador_semanal"]
                    st.rerun()

            ids_list    = [i for i in b["actas_diarias_ids"].split(",") if i]
            diarias_sem = [a for a in list_actas_diarias(b["fecha_inicio"], b["fecha_fin"]) if a["id"] in ids_list]
            html_rep    = html_semanal(b, diarias_sem)
            with col_d:
                st.download_button(
                    "⬇️ Descargar HTML",
                    data=html_rep.encode("utf-8"),
                    file_name=f"ACTA_{b['id']}_{hoy.strftime('%d%m%Y')}.html",
                    mime="text/html",
                    use_container_width=True,
                )

        st.divider()
        st.markdown("#### Actas semanales guardadas")
        sem_list = list_actas_semanales()
        if not sem_list:
            st.info("No hay actas semanales. Usa el botón de consolidación.")
        for s in sem_list:
            _ea = {"borrador":"b-blue","pendiente_firma":"b-amber","aprobado":"b-green"}.get(s.get("estado_aprobacion","borrador"),"b-blue")
            st.markdown(f"""
            <div class="sem-card">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <b style="font-size:14px;">📅 {s.get('semana_ano','')} · {s.get('fecha_inicio','')} → {s.get('fecha_fin','')}</b>
                <span class="badge {_ea}">{s.get('estado_aprobacion','borrador').replace('_',' ').title()}</span>
              </div>
              <div style="font-size:12px;color:#555;margin-top:6px;">{str(s.get('resumen_ejecutivo',''))[:200]}…</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"🗑️ Eliminar {s['id']}", key=f"dsem_{s['id']}", type="secondary"):
                st.session_state[f"_cdsem_{s['id']}"] = True
            if st.session_state.get(f"_cdsem_{s['id']}"):
                st.warning(f"⚠️ ¿Confirmar eliminación de **{s['id']}**? Escribe en GitHub y **no se puede deshacer**.")
                _csy, _csn = st.columns(2)
                with _csy:
                    if st.button("✅ Sí, eliminar definitivamente", key=f"ydsem_{s['id']}", type="primary"):
                        delete_acta_semanal(s["id"])
                        st.session_state.pop(f"_cdsem_{s['id']}", None)
                        st.rerun()
                with _csn:
                    if st.button("❌ Cancelar", key=f"ndsem_{s['id']}"):
                        st.session_state.pop(f"_cdsem_{s['id']}", None)
                        st.rerun()


# ══════════════════════════════════════════════════════════════════
#  TAB 3 — VISTA PÚBLICA / COMPARTIR
# ══════════════════════════════════════════════════════════════════
with tab3:
    if not modo_publico:
        st.markdown("### 🔗 Compartir con el equipo")

        cloud_url = "https://kntwcg5w7wfjqnqqvh8izv.streamlit.app"
        pub_url   = f"{cloud_url}/Actas_PMO?view=public"

        st.markdown(f"""
        <div style="background:#fff;border:1px solid #e2e6f0;border-radius:10px;padding:20px 24px;margin-bottom:16px;">
          <div style="font-size:15px;font-weight:700;margin-bottom:12px;">🔗 URLs de acceso</div>
          <div style="margin-bottom:10px;">
            <div style="font-size:11px;text-transform:uppercase;color:#888;margin-bottom:3px;">App completa (equipo interno)</div>
            <code style="background:#f0f2f8;padding:6px 12px;border-radius:4px;font-size:12px;">{cloud_url}/Actas_PMO</code>
          </div>
          <div>
            <div style="font-size:11px;text-transform:uppercase;color:#888;margin-bottom:3px;">Vista pública solo lectura (Laura, Valentina, dirección)</div>
            <code style="background:#f0faf4;padding:6px 12px;border-radius:4px;font-size:12px;color:#27ae60;">{pub_url}</code>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 👁️ Preview de la vista pública")
        st.caption("Así verá el equipo de dirección el histórico de actas sin poder editar nada.")

    sem_list_pub = list_actas_semanales()
    if not sem_list_pub:
        st.info("No hay actas semanales aprobadas aún.")
    else:
        for s in sem_list_pub:
            ea  = s.get("estado_aprobacion","borrador")
            _ec = {"borrador":"b-blue","pendiente_firma":"b-amber","aprobado":"b-green"}.get(ea,"b-blue")
            ids_list = [i for i in (s.get("actas_diarias_ids") or "").split(",") if i]
            with st.expander(f"📅 {s.get('semana_ano','')} · {s.get('fecha_inicio','')} → {s.get('fecha_fin','')}"):
                st.markdown(f'<span class="badge {_ec}">{ea.replace("_"," ").title()}</span>', unsafe_allow_html=True)
                st.markdown(f"**Aprobado por:** {s.get('aprobado_por','—')}")
                st.markdown("**Resumen ejecutivo:**")
                st.markdown(s.get("resumen_ejecutivo",""))
                if ids_list:
                    diarias_p = [a for a in list_actas_diarias(s["fecha_inicio"], s["fecha_fin"]) if a["id"] in ids_list]
                    if diarias_p:
                        st.markdown("**Actas diarias incluidas:**")
                        for a in diarias_p:
                            d_str = fecha_es(a["fecha"], "mini")
                            st.markdown(f"— **{d_str}**: {a.get('resumen','')}")
                        html_dl = html_semanal(s, diarias_p)
                        st.download_button(
                            "⬇️ Descargar acta semanal (HTML/PDF)",
                            data=html_dl.encode("utf-8"),
                            file_name=f"ACTA_{s.get('id','SEM')}_{s.get('fecha_inicio','')}.html",
                            mime="text/html",
                            use_container_width=True,
                            key=f"dl_pub_{s['id']}",
                        )


# ─── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Sistema")
    st.markdown(f"**Backend:** `{be}`")
    st.markdown(f"**Semana actual:** S{sem}")
    st.markdown(f"**Modo:** {'🔒 Solo lectura' if modo_publico else '✏️ Edición completa'}")
    st.divider()
    st.markdown("**URL pública:**")
    st.code(f"?view=public  ← modo lectura", language=None)
