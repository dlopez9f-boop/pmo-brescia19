#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generador_pmo_core.py — Generador Privado de Actas PMO · Nine Fitness Brescia 19
App LOCAL: streamlit run generador_pmo_core.py
Flujo: Dictar/Pegar → Parsear → Editar formulario → Exportar JSON + HTML
"""

import json
import uuid
import streamlit as st
from datetime import date, datetime, timedelta
from pathlib import Path

# ══════════════════════════════════════════════════════════════════
#  CONSTANTES
# ══════════════════════════════════════════════════════════════════
_DIAS_ES  = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
_MESES_ES = ["enero","febrero","marzo","abril","mayo","junio","julio",
             "agosto","septiembre","octubre","noviembre","diciembre"]

GREMIOS = [
    "⚡ Electricidad",
    "❄️ Climatización",
    "🧱 Albañilería / Civil",
    "🪵 Carpintería / Estructura",
    "🔥 PCI",
    "♿ Accesibilidad / Hersan",
    "🔧 General",
]

GREMIO_KW = {
    "⚡ Electricidad":          ["luis", "elecrea", "cuadro", "bandeja", "cableado", "iga", "diferencial", "potencia", "cgmp"],
    "❄️ Climatización":         ["jose", "nacho", "servitec", "conducto", "daikin", "clima", "difusor", "altillo", "fan-coil", "recuperadora"],
    "🧱 Albañilería / Civil":   ["munir", "ziad", "mohamed", "solera", "tabiq", "escombro", "nivelac", "pladur", "forjado", "mortero"],
    "🪵 Carpintería / Estructura":["josevi", "upn", "espejo", "carpintería", "viga", "estructura", "fachada"],
    "🔥 PCI":                   ["leo", "troser", "extinción", "pci", "rociador", "bies", "ei120", "perimetral"],
    "♿ Accesibilidad / Hersan": ["pedro", "hersan", "salvaescaleras", "pmr", "fortis", "rampa", "desnivel"],
}

INC_KW    = ["problema", "retraso", "falta", "pendiente urgente", "alerta", "sin material",
             "parado", "bloqueado", "ausencia", "no asistido", "incidencia", "error", "avería",
             "conflicto", "rechazo", "no llega"]
LOGRO_KW  = ["completado", "finalizado", "ejecutado", "terminado", "listo", "aprobado",
             "colocado", "instalado", "sellado", "revisado", "confirmado", "entregado",
             "medido", "conseguido", "alcanzado", "mejorado", "optimizado", "reducido",
             "ampliado", "subido"]
SOL_KW    = ["necesito", "solicito", "pendiente firma", "falta decisión", "requiere aprobación",
             "espera validación", "presupuesto pendiente", "hay que contratar", "llamar a",
             "confirmar con", "validar con", "revisar con", "informar a dirección",
             "autorización", "hay que decidir"]
AGENDA_KW = ["mañana", "próximo día", "semana que viene", "08:", "09:", "10:", "11:", "16:", "17:",
             "reunión", "visita", "entrega", "cita", "revisión"]

OBRA_INICIO = date(2026, 3, 23)

# ══════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════

def semana_obra(d: date) -> int:
    return max(1, (d - OBRA_INICIO).days // 7 + 1)

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

def _detectar_gremio(texto: str) -> str:
    tl = texto.lower()
    for g, kws in GREMIO_KW.items():
        if any(k in tl for k in kws):
            return g
    return "🔧 General"

# ══════════════════════════════════════════════════════════════════
#  PARSER
# ══════════════════════════════════════════════════════════════════

def parsear(texto: str, fecha: date) -> dict:
    lines = [l.strip() for l in texto.splitlines() if l.strip()]

    secs: dict = {g: [] for g in GREMIOS}
    incidencias, logros, solicitudes, agenda = [], [], [], []

    for line in lines:
        ll = line.lower()
        asignado = False
        for g, kws in GREMIO_KW.items():
            if any(k in ll for k in kws):
                secs[g].append(line)
                asignado = True
                break
        if not asignado:
            secs["🔧 General"].append(line)

        if any(k in ll for k in INC_KW):
            gremio_det = _detectar_gremio(line)
            incidencias.append({
                "gremio":      gremio_det,
                "descripcion": line,
                "prioridad":   "alta" if any(k in ll for k in ["urgente","parado","bloqueado","avería"]) else "normal",
            })

        if any(k in ll for k in LOGRO_KW):
            logros.append({
                "descripcion": line,
                "impacto":     "",
                "mejora_de":   "",
                "mejora_a":    "",
            })

        if any(k in ll for k in SOL_KW):
            solicitudes.append({
                "descripcion": line,
                "responsable": "Darío A. López",
                "urgencia":    "alta" if any(k in ll for k in ["urgente","crítico","hoy","firma"]) else "normal",
            })

        if any(k in ll for k in AGENDA_KW):
            hora = "—"
            for part in line.split():
                if ":" in part and part[:2].isdigit():
                    hora = part; break
            agenda.append({"hora": hora, "evento": line})

    gremios_incidencia = sorted({i["gremio"] for i in incidencias})
    sem = semana_obra(fecha)

    return {
        "intervenciones":       {g: "\n".join(v) for g, v in secs.items() if v},
        "incidencias":          incidencias,
        "logros_tecnicos":      logros,
        "solicitudes_direccion":solicitudes,
        "agenda_proxima":       {"items": [{"hora": a["hora"], "evento": a["evento"]} for a in agenda]},
        "gremios_incidencia":   gremios_incidencia,
        "semana_obra":          sem,
    }

# ══════════════════════════════════════════════════════════════════
#  GENERADOR HTML DIARIA
# ══════════════════════════════════════════════════════════════════

def html_diaria(rec: dict) -> str:
    fecha_str = rec.get("fecha","")
    fecha_fmt = fecha_es(fecha_str, "largo") if fecha_str else "—"
    sem       = rec.get("semana_obra","?")
    act_id    = rec.get("id","")
    resumen   = rec.get("resumen","")
    prioridad = rec.get("prioridad","normal")
    estado    = rec.get("estado","borrador")
    creado_por= rec.get("creado_por","Darío A. López")

    def _pjson(raw, default=None):
        if default is None: default = []
        if not raw: return default
        if isinstance(raw, (list, dict)): return raw
        try: return json.loads(raw)
        except: return default

    incidencias  = _pjson(rec.get("incidencias"))
    logros       = _pjson(rec.get("logros_tecnicos"))
    solicitudes  = _pjson(rec.get("solicitudes_direccion"))
    intervenciones = _pjson(rec.get("intervenciones"), {})
    agenda_raw   = _pjson(rec.get("agenda_proxima"), {})
    agenda_items = agenda_raw.get("items",[]) if isinstance(agenda_raw, dict) else []

    pr_color = {"urgente":"#c0392b","alta":"#e67e22","normal":"#27ae60"}.get(prioridad,"#27ae60")
    pr_label = {"urgente":"🔴 Urgente","alta":"🟡 Alta","normal":"🟢 Normal"}.get(prioridad,"Normal")
    est_color= {"borrador":"#2471a3","revisado":"#e65100","firmado":"#27ae60"}.get(estado,"#2471a3")

    css = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Helvetica Neue',Arial,sans-serif;background:#f0f2f8;color:#1a1a2e;font-size:13px;line-height:1.5}
.doc{max-width:800px;margin:16px auto;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.12)}
.hdr{background:linear-gradient(135deg,#1a1a2e 0%,#0f3460 100%);padding:20px 30px 16px;color:#fff;position:relative}
.hdr-ey{font-size:9px;text-transform:uppercase;letter-spacing:3px;opacity:.5;margin-bottom:4px}
.hdr-t{font-size:22px;font-weight:900;letter-spacing:-.5px;line-height:1.1}
.hdr-s{font-size:11px;opacity:.6;margin-top:4px}
.hdr-badge{position:absolute;top:20px;right:30px;background:#e94560;color:#fff;font-size:10px;font-weight:800;padding:4px 14px;border-radius:20px;letter-spacing:1px;text-transform:uppercase}
.accent{position:absolute;bottom:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#e94560,#0f3460,#e94560)}
.meta{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid #e2e8f0}
.mc{padding:10px 14px;border-right:1px solid #e2e8f0}
.mc:last-child{border-right:none}
.ml{font-size:9px;text-transform:uppercase;letter-spacing:1.5px;color:#94a3b8;font-weight:600;margin-bottom:3px}
.mv{font-size:13px;font-weight:700;color:#1a1a2e}
.body{padding:22px 30px}
.sec{margin-bottom:22px}
.sh{display:flex;align-items:center;gap:10px;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #e94560}
.st{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:1px;color:#1a1a2e}
.resumen{background:#f8f9ff;border-left:4px solid #0f3460;padding:12px 15px;border-radius:0 8px 8px 0;font-size:13px;color:#2c3e50;line-height:1.6}
.gremio-bl{margin-bottom:8px}
.gremio-nm{font-size:10px;font-weight:700;color:#0f3460;margin-bottom:3px}
.gremio-cnt{font-size:11px;padding-left:8px;border-left:2px solid #e2e6f0;color:#374151;line-height:1.5}
.inc-item{background:#fdf2f2;border-left:3px solid #e94560;padding:8px 12px;margin-bottom:6px;border-radius:0 5px 5px 0}
.badge{display:inline-block;padding:2px 7px;border-radius:10px;font-size:9px;font-weight:700;text-transform:uppercase}
.b-r{background:#fdf2f2;color:#c0392b;border:1px solid #f5c6c6}
.b-y{background:#fff8e1;color:#e65100;border:1px solid #ffe0b2}
.b-g{background:#e8f5e9;color:#1b5e20;border:1px solid #a5d6a7}
.logro-row{display:flex;gap:10px;padding:8px 0;border-bottom:1px solid #f0f2f8;align-items:flex-start}
.logro-row:last-child{border-bottom:none}
.logro-t{font-size:11px;font-weight:700;color:#1b5e20;margin-bottom:2px}
.logro-d{font-size:11px;color:#475569}
.sol-item{background:#fff8e1;border:1px solid #ffe0b2;border-left:4px solid #e67e22;border-radius:0 5px 5px 0;padding:8px 12px;margin-bottom:6px}
.ag-row{display:flex;gap:12px;padding:7px 0;border-bottom:1px solid #f0f2f8;align-items:flex-start}
.ag-row:last-child{border-bottom:none}
.ag-hora{min-width:80px;font-size:12px;font-weight:800;color:#e94560;flex-shrink:0;text-align:right;padding-right:12px;border-right:2px solid #e2e8f0}
.ag-ev{font-size:11px;color:#1a1a2e;flex:1;line-height:1.5}
.ftr{background:#1a1a2e;padding:10px 30px;display:flex;justify-content:space-between;align-items:center;color:rgba(255,255,255,.4);font-size:9px;flex-wrap:wrap;gap:4px}
.ftr b{color:rgba(255,255,255,.65)}
.no-print{max-width:800px;margin:10px auto 0;text-align:right}
@media print{body{background:#fff}.doc{box-shadow:none;margin:0;border-radius:0}.no-print{display:none!important}}
@page{size:A4;margin:8mm}"""

    # Intervenciones
    secs_html = ""
    if isinstance(intervenciones, dict):
        for g, c in intervenciones.items():
            if c:
                ct = str(c).replace("\n","<br>")
                secs_html += (f'<div class="gremio-bl"><div class="gremio-nm">{g}</div>'
                              f'<div class="gremio-cnt">{ct}</div></div>')
    if not secs_html:
        secs_html = '<div style="color:#94a3b8;font-size:12px;">Sin intervenciones registradas.</div>'

    # Incidencias
    incs_html = ""
    for inc in incidencias:
        if isinstance(inc, dict):
            pr   = inc.get("prioridad","normal")
            bcls = "b-r" if pr in ("alta","urgente") else "b-y"
            incs_html += (f'<div class="inc-item"><div style="display:flex;justify-content:space-between;margin-bottom:3px;">'
                          f'<span style="font-size:10px;font-weight:700;color:#c0392b;">{inc.get("gremio","")}</span>'
                          f'<span class="badge {bcls}">{pr}</span></div>'
                          f'<div style="font-size:11px;color:#374151;">{inc.get("descripcion","")}</div></div>')
    if not incs_html:
        incs_html = '<div style="color:#27ae60;font-size:12px;">Sin incidencias.</div>'

    # Logros
    logros_html = ""
    ICONOS = ["&#127942;","&#9989;","&#10024;","&#9889;","&#128274;","&#128203;"]
    for idx, l in enumerate(logros):
        if isinstance(l, dict):
            ico  = ICONOS[idx % len(ICONOS)]
            ant  = l.get("mejora_de","")
            nue  = l.get("mejora_a","")
            chips = ""
            if ant or nue:
                chips = (f'<div style="display:flex;gap:5px;margin-top:3px;font-size:10px;">'
                         f'<span style="background:#fdf2f2;color:#c0392b;padding:1px 6px;border-radius:5px;">{ant}</span>'
                         f'<span style="color:#94a3b8;">→</span>'
                         f'<span style="background:#e8f5e9;color:#1b5e20;padding:1px 6px;border-radius:5px;">{nue}</span></div>')
            logros_html += (f'<div class="logro-row"><div style="font-size:18px;flex-shrink:0;">{ico}</div><div>'
                            f'<div class="logro-t">{l.get("descripcion","")}</div>'
                            f'<div class="logro-d">{l.get("impacto","")}</div>'
                            f'{chips}</div></div>')
    if not logros_html:
        logros_html = '<div style="color:#94a3b8;font-size:12px;">Sin logros técnicos registrados.</div>'

    # Solicitudes
    sols_html = ""
    for s in solicitudes:
        if isinstance(s, dict):
            urg = s.get("urgencia","normal")
            uc  = "#7b0000" if urg=="crítica" else ("#c0392b" if urg=="alta" else "#475569")
            sols_html += (f'<div class="sol-item">'
                          f'<div style="font-size:11px;font-weight:700;color:#1a1a2e;margin-bottom:2px;">{s.get("descripcion","")}</div>'
                          f'<div style="font-size:10px;color:#94a3b8;">Resp.: <b>{s.get("responsable","")}</b> &middot; '
                          f'<b style="color:{uc};">{urg.upper()}</b></div></div>')
    if not sols_html:
        sols_html = '<div style="color:#94a3b8;font-size:12px;">Sin solicitudes a dirección.</div>'

    # Agenda
    agenda_html = ""
    for it in agenda_items:
        if isinstance(it, dict):
            agenda_html += (f'<div class="ag-row"><div class="ag-hora">{it.get("hora","—")}</div>'
                            f'<div class="ag-ev">{it.get("evento","")}</div></div>')
    if not agenda_html:
        agenda_html = '<div style="color:#94a3b8;font-size:12px;">Sin agenda para el próximo día.</div>'

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Acta Diaria {fecha_fmt} &mdash; Nine Fitness Brescia 19</title>
<style>{css}</style>
</head>
<body>
<div class="no-print">
  <button onclick="window.print()" style="background:#e94560;color:#fff;border:none;padding:8px 20px;border-radius:6px;font-size:13px;font-weight:700;cursor:pointer;">&#128438; Imprimir / Guardar PDF</button>
</div>
<div class="doc">
  <div class="hdr">
    <div class="hdr-badge">S{sem}</div>
    <div class="hdr-ey">Nine Fitness Group S.L. &middot; PMO Brescia 19 &middot; Acta Diaria</div>
    <div class="hdr-t">ACTA DIARIA DE OBRA</div>
    <div class="hdr-s">{fecha_fmt} &nbsp;&middot;&nbsp; Calle Brescia 19, 28028 Madrid</div>
    <div class="accent"></div>
  </div>
  <div class="meta">
    <div class="mc"><div class="ml">Referencia</div><div class="mv" style="font-size:11px;">{act_id}</div></div>
    <div class="mc"><div class="ml">Semana de obra</div><div class="mv">S{sem}</div></div>
    <div class="mc"><div class="ml">Prioridad</div>
      <div class="mv"><span style="color:{pr_color};font-weight:700;">{pr_label}</span></div></div>
    <div class="mc"><div class="ml">Estado</div>
      <div class="mv"><span style="color:{est_color};font-weight:700;">{estado.upper()}</span></div></div>
  </div>
  <div class="body">
    <div class="sec">
      <div class="sh"><span>&#128203;</span><span class="st">Resumen Ejecutivo</span></div>
      <div class="resumen">{resumen}</div>
    </div>
    <div class="sec">
      <div class="sh"><span>&#128295;</span><span class="st">Intervenciones por Gremio</span></div>
      {secs_html}
    </div>
    <div class="sec">
      <div class="sh"><span>&#9888;&#65039;</span><span class="st">Incidencias</span></div>
      {incs_html}
    </div>
    <div class="sec">
      <div class="sh"><span>&#127942;</span><span class="st">Logros Técnicos</span></div>
      {logros_html}
    </div>
    <div class="sec">
      <div class="sh"><span>&#128204;</span><span class="st">Solicitudes a Dirección</span></div>
      {sols_html}
    </div>
    <div class="sec">
      <div class="sh"><span>&#128197;</span><span class="st">Agenda Próximo Día</span></div>
      {agenda_html}
    </div>
  </div>
  <div class="ftr">
    <div>NINE FITNESS GROUP S.L. &middot; Calle Brescia 19, 28028 Madrid</div>
    <div>Dir. Obra: <b>{creado_por}</b> &nbsp;&middot;&nbsp; Arq.: <b>&Aacute;ngel Rodr&iacute;guez Mart&iacute;nez-Conde (COAM 12399)</b></div>
    <div>Ref: <b>{act_id}</b> &nbsp;&middot;&nbsp; Generado: <b>{date.today().isoformat()}</b> &nbsp;&middot;&nbsp; Confidencial</div>
  </div>
</div>
</body>
</html>"""


# ══════════════════════════════════════════════════════════════════
#  STREAMLIT CONFIG
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Generador PMO · Brescia 19",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #f0f2f8; }
  [data-testid="stMain"] { padding-top: 0.3rem; }
  .gen-header {
    background: linear-gradient(135deg, #1a1a2e, #0f3460);
    color: #fff; padding: 16px 24px; border-radius: 10px;
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 16px;
  }
  .step-box {
    background: #fff; border-radius: 10px; padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,.07); margin-bottom: 12px;
  }
  .step-num {
    display:inline-block; width:24px; height:24px; border-radius:50%;
    background:#e94560; color:#fff; font-size:12px; font-weight:900;
    text-align:center; line-height:24px; margin-right:8px;
  }
  textarea { font-family: 'Courier New', monospace !important; font-size: 12px !important; }
  div[data-testid="stDataFrame"] { font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏗️ PMO Brescia 19")
    st.markdown("**Generador local de actas**")
    st.divider()

    modulo = st.radio(
        "Módulo activo",
        ["📋 Acta Diaria", "📅 Consolidación Semanal *(próx.)*", "📊 Certificaciones *(próx.)*"],
        index=0,
    )
    st.divider()
    st.markdown("**Obra:**")
    st.markdown("Nine Fitness · Brescia 19")
    st.markdown(f"**Hoy:** {fecha_es(date.today(), 'corto')}")
    st.markdown(f"**Semana:** S{semana_obra(date.today())}")
    st.markdown(f"**Apertura:** 3–5 Ago 2026")
    st.divider()
    st.caption("App local · Sin conexión a GitHub")
    st.caption("Exporta el JSON → súbelo a la app pública")

# ─── HEADER PRINCIPAL ─────────────────────────────────────────────
st.markdown(f"""
<div class="gen-header">
  <div>
    <div style="font-size:18px;font-weight:900;">🏗️ GENERADOR PMO · NINE FITNESS BRESCIA 19</div>
    <div style="font-size:11px;opacity:.6;margin-top:3px;">App local privada · {fecha_es(date.today(),'corto')}</div>
  </div>
  <div style="background:#e94560;padding:7px 16px;border-radius:6px;text-align:center;font-weight:700;">
    <div style="font-size:9px;text-transform:uppercase;opacity:.9;">Apertura</div>
    <div style="font-size:15px;">3–5 AGO 2026</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  MÓDULO: ACTA DIARIA
# ══════════════════════════════════════════════════════════════════
if "📋 Acta Diaria" in modulo:

    # ── PASO 1: ENTRADA ───────────────────────────────────────────
    st.markdown('<div class="step-box"><span class="step-num">1</span><strong>Entrada: transcripción de voz o notas de campo</strong></div>', unsafe_allow_html=True)

    c_meta1, c_meta2, c_meta3 = st.columns([1, 1, 2])
    with c_meta1:
        fecha_acta = st.date_input("Fecha del acta", value=date.today())
    with c_meta2:
        sem_acta = st.number_input("Semana de obra", min_value=1, max_value=52,
                                   value=semana_obra(date.today()))
    with c_meta3:
        resumen_directo = st.text_input("Resumen ejecutivo (una línea)",
                                        placeholder="Ej: PCI perimetral completada. Munir ausente. Reunión gremios.")

    texto_raw = st.text_area(
        "Notas de campo / transcripción de voz",
        height=240,
        placeholder=(
            "Dicta o pega aquí las notas del día...\n\n"
            "Ejemplo:\n"
            "Luis (Elecrea): ejecuta sala colectiva. Bandeja en altillo instalada.\n"
            "Jose (Servitec): clima al 90%, falta difusor zona pesas.\n"
            "Munir ausente sin justificación. Problema: solera zona vestuarios parada.\n"
            "Hersan detecta tramo curvo en salvaescaleras, desnivel 1.58m.\n"
            "Necesito presupuesto actualizado de Josevi urgente.\n"
            "Mañana 09:00 reunión con Ángel para revisar forjado recuperadora.\n"
            "Logro: paso libre baños mejorado de 2.50 a 2.77m."
        ),
        key="txt_entrada",
    )

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        btn_parsear = st.button("⚙️ Parsear y estructurar", type="primary", use_container_width=True)
    with col_btn2:
        if st.button("🗑️ Limpiar todo", use_container_width=False):
            for k in list(st.session_state.keys()):
                if k.startswith("acta_") or k in ("txt_entrada", "parsed_data"):
                    del st.session_state[k]
            st.rerun()

    if btn_parsear:
        if not texto_raw.strip():
            st.warning("Escribe o pega las notas antes de parsear.")
        else:
            parsed = parsear(texto_raw, fecha_acta)
            parsed["resumen"] = resumen_directo.strip() or f"Acta S{sem_acta} · {fecha_es(fecha_acta,'corto')}"
            parsed["fecha"]   = fecha_acta.isoformat()
            _ts = datetime.now().strftime("%H%M%S")
            parsed["id"]      = f"ACT-{fecha_acta.strftime('%Y%m%d')}-{_ts}"
            parsed["texto_original"] = texto_raw
            st.session_state["parsed_data"] = parsed
            st.success(f"✅ Parseado: {len(parsed['incidencias'])} incidencias · {len(parsed['logros_tecnicos'])} logros · {len(parsed['solicitudes_direccion'])} solicitudes a dirección")
            st.rerun()

    # ── PASO 2: EDITAR ────────────────────────────────────────────
    if "parsed_data" in st.session_state:
        p = st.session_state["parsed_data"]
        st.divider()
        st.markdown('<div class="step-box"><span class="step-num">2</span><strong>Revisar y editar antes de exportar</strong></div>', unsafe_allow_html=True)

        ec1, ec2, ec3 = st.columns([3, 1, 1])
        with ec1:
            p["resumen"] = st.text_input("Resumen ejecutivo", value=p.get("resumen",""), key="ed_resumen")
        with ec2:
            p["prioridad"] = st.selectbox("Prioridad", ["normal","alta","urgente"],
                                          index=["normal","alta","urgente"].index(p.get("prioridad","normal")),
                                          key="ed_prio")
        with ec3:
            p["estado"] = st.selectbox("Estado", ["borrador","revisado","firmado"],
                                       index=["borrador","revisado","firmado"].index(p.get("estado","borrador")),
                                       key="ed_estado")

        p["creado_por"] = st.text_input("Director de obra", value=p.get("creado_por","Darío A. López"), key="ed_autor")

        ed_tab1, ed_tab2, ed_tab3, ed_tab4, ed_tab5 = st.tabs([
            "🔧 Por Gremio", "⚠️ Incidencias", "🏆 Logros", "📌 Solicitudes Dir.", "📅 Agenda"
        ])

        with ed_tab1:
            st.caption("Edita el texto de cada gremio. Deja vacío para excluir.")
            secs = p.get("intervenciones", {})
            for g in GREMIOS:
                secs[g] = st.text_area(g, value=secs.get(g,""), height=80, key=f"gr_{g}")
            p["intervenciones"] = {g: v for g, v in secs.items() if v.strip()}

        with ed_tab2:
            st.caption("Edita la lista de incidencias detectadas.")
            incs = p.get("incidencias", [])
            incs_df = [
                {"gremio": i.get("gremio","🔧 General") if isinstance(i, dict) else "🔧 General",
                 "descripcion": i.get("descripcion","") if isinstance(i, dict) else str(i),
                 "prioridad": i.get("prioridad","normal") if isinstance(i, dict) else "normal"}
                for i in incs
            ]
            import pandas as pd
            df_incs = pd.DataFrame(incs_df or [{"gremio":"","descripcion":"","prioridad":"normal"}])
            edited_incs = st.data_editor(
                df_incs,
                column_config={
                    "gremio":     st.column_config.SelectboxColumn("Gremio", options=GREMIOS, width="medium"),
                    "descripcion":st.column_config.TextColumn("Descripción", width="large"),
                    "prioridad":  st.column_config.SelectboxColumn("Prioridad", options=["normal","alta","urgente","crítica"]),
                },
                num_rows="dynamic", key="ed_incs", use_container_width=True,
            )
            p["incidencias"] = edited_incs.to_dict("records")
            p["gremios_incidencia"] = sorted({r["gremio"] for r in p["incidencias"] if r.get("gremio")})

        with ed_tab3:
            st.caption("Logros técnicos y optimizaciones del día.")
            logros = p.get("logros_tecnicos", [])
            log_df = [
                {"descripcion": l.get("descripcion","") if isinstance(l, dict) else str(l),
                 "impacto":     l.get("impacto","") if isinstance(l, dict) else "",
                 "mejora_de":   l.get("mejora_de","") if isinstance(l, dict) else "",
                 "mejora_a":    l.get("mejora_a","") if isinstance(l, dict) else ""}
                for l in logros
            ]
            df_log = pd.DataFrame(log_df or [{"descripcion":"","impacto":"","mejora_de":"","mejora_a":""}])
            edited_log = st.data_editor(
                df_log,
                column_config={
                    "descripcion":st.column_config.TextColumn("Logro / hito", width="large"),
                    "impacto":    st.column_config.TextColumn("Impacto operativo"),
                    "mejora_de":  st.column_config.TextColumn("Antes"),
                    "mejora_a":   st.column_config.TextColumn("Después"),
                },
                num_rows="dynamic", key="ed_log", use_container_width=True,
            )
            p["logros_tecnicos"] = edited_log.to_dict("records")

        with ed_tab4:
            st.caption("Decisiones o firmas que requieren al Director de Obra.")
            sols = p.get("solicitudes_direccion", [])
            sol_df = [
                {"descripcion": s.get("descripcion","") if isinstance(s, dict) else str(s),
                 "responsable": s.get("responsable","Darío A. López") if isinstance(s, dict) else "Darío A. López",
                 "urgencia":    s.get("urgencia","normal") if isinstance(s, dict) else "normal"}
                for s in sols
            ]
            df_sol = pd.DataFrame(sol_df or [{"descripcion":"","responsable":"Darío A. López","urgencia":"normal"}])
            edited_sol = st.data_editor(
                df_sol,
                column_config={
                    "descripcion": st.column_config.TextColumn("Solicitud", width="large"),
                    "responsable": st.column_config.TextColumn("Responsable"),
                    "urgencia":    st.column_config.SelectboxColumn("Urgencia", options=["normal","alta","crítica"]),
                },
                num_rows="dynamic", key="ed_sol", use_container_width=True,
            )
            p["solicitudes_direccion"] = edited_sol.to_dict("records")

        with ed_tab5:
            st.caption("Agenda del próximo día de obra.")
            ag_raw   = p.get("agenda_proxima", {})
            ag_items = ag_raw.get("items",[]) if isinstance(ag_raw, dict) else []
            ag_df = pd.DataFrame(
                [{"hora": a.get("hora","—"), "evento": a.get("evento","")} for a in ag_items]
                or [{"hora":"08:00","evento":""}]
            )
            edited_ag = st.data_editor(
                ag_df,
                column_config={
                    "hora":   st.column_config.TextColumn("Hora", width="small"),
                    "evento": st.column_config.TextColumn("Evento / tarea", width="large"),
                },
                num_rows="dynamic", key="ed_ag", use_container_width=True,
            )
            p["agenda_proxima"] = {"items": edited_ag.to_dict("records")}

        st.session_state["parsed_data"] = p

        # ── PASO 3: EXPORTAR ──────────────────────────────────────
        st.divider()
        st.markdown('<div class="step-box"><span class="step-num">3</span><strong>Exportar acta</strong></div>', unsafe_allow_html=True)

        # Construir el record final limpio
        record_final = {
            "id":                    p["id"],
            "fecha":                 p["fecha"],
            "semana_obra":           int(sem_acta),
            "obra":                  "Brescia 19",
            "resumen":               p.get("resumen",""),
            "texto_original":        p.get("texto_original",""),
            "intervenciones":        json.dumps(p.get("intervenciones",{}),  ensure_ascii=False),
            "definiciones_tecnicas": json.dumps({},                           ensure_ascii=False),
            "logros_tecnicos":       json.dumps(p.get("logros_tecnicos",[]),  ensure_ascii=False),
            "solicitudes_direccion": json.dumps(p.get("solicitudes_direccion",[]), ensure_ascii=False),
            "agenda_proxima":        json.dumps(p.get("agenda_proxima",{}),   ensure_ascii=False),
            "incidencias":           json.dumps(p.get("incidencias",[]),       ensure_ascii=False),
            "gremios_incidencia":    json.dumps(p.get("gremios_incidencia",[]),ensure_ascii=False),
            "prioridad":             p.get("prioridad","normal"),
            "estado":                p.get("estado","borrador"),
            "creado_por":            p.get("creado_por","Darío A. López"),
            "created_at":            datetime.now().isoformat(),
        }

        exp_col1, exp_col2, exp_col3 = st.columns(3)

        # JSON — para subir a la app pública
        json_bytes = json.dumps(record_final, ensure_ascii=False, indent=2).encode("utf-8")
        with exp_col1:
            st.download_button(
                "⬇️ Descargar JSON",
                data=json_bytes,
                file_name=f"{record_final['id']}.json",
                mime="application/json",
                use_container_width=True,
                type="primary",
            )

        # HTML/PDF diaria
        record_para_html = dict(record_final)
        record_para_html["intervenciones"]         = p.get("intervenciones",{})
        record_para_html["incidencias"]             = p.get("incidencias",[])
        record_para_html["logros_tecnicos"]         = p.get("logros_tecnicos",[])
        record_para_html["solicitudes_direccion"]   = p.get("solicitudes_direccion",[])
        record_para_html["agenda_proxima"]          = p.get("agenda_proxima",{})
        html_bytes = html_diaria(record_para_html).encode("utf-8")
        with exp_col2:
            st.download_button(
                "⬇️ Descargar HTML/PDF",
                data=html_bytes,
                file_name=f"{record_final['id']}.html",
                mime="text/html; charset=utf-8",
                use_container_width=True,
            )

        # Guardar JSON localmente en actas_data/
        with exp_col3:
            if st.button("💾 Guardar en actas_data/", use_container_width=True):
                out_dir = Path("actas_data")
                out_dir.mkdir(exist_ok=True)

                # Leer / actualizar actas_diarias.json
                jf = out_dir / "actas_diarias.json"
                existing = json.loads(jf.read_text(encoding="utf-8")) if jf.exists() else []
                existing = [r for r in existing if r.get("id") != record_final["id"]]
                existing.append(record_final)
                existing.sort(key=lambda x: x.get("fecha",""), reverse=True)
                jf.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
                st.success(f"✅ Guardado en actas_data/actas_diarias.json — {record_final['id']}")

        # Preview
        with st.expander("👁️ Preview HTML del acta"):
            st.components.v1.html(html_diaria(record_para_html), height=600, scrolling=True)

elif "📅 Consolidación" in modulo:
    st.info("Módulo de consolidación semanal — próximamente.")

elif "📊 Certificaciones" in modulo:
    st.info("Módulo de certificaciones — próximamente.")
