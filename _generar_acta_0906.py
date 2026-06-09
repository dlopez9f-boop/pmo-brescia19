#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera PDF del Acta Reunión Semanal S12 · 09/06/2026"""
import json, subprocess, tempfile, ctypes, ctypes.wintypes
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
_buf   = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
ctypes.windll.shell32.SHGetFolderPathW(0, 0, 0, 0, _buf)
ESCRITORIO = Path(_buf.value)

diarias = json.loads((Path("actas_data")/"actas_diarias.json").read_text(encoding="utf-8"))
REC = next(r for r in diarias if r["id"] == "ACT-20260609-1300")

def pj(raw, default=None):
    if default is None: default = []
    if not raw: return default
    if isinstance(raw, (list, dict)): return raw
    try: return json.loads(raw)
    except: return default

asistencia = pj(REC.get("asistencia"))
secs       = pj(REC.get("intervenciones"), {})
riesgos    = pj(REC.get("riesgos"))
defs       = pj(REC.get("definiciones_tecnicas"))
logros     = pj(REC.get("logros_tecnicos"))
sols       = pj(REC.get("solicitudes_direccion"))
ag_raw     = pj(REC.get("agenda_proxima"), {})
ag_items   = ag_raw.get("items", []) if isinstance(ag_raw, dict) else []
incs       = pj(REC.get("incidencias"))
alertas    = pj(REC.get("alertas_dashboard"))

CSS = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Helvetica Neue',Arial,sans-serif;background:#fff;color:#1a1a2e;font-size:12.5px;line-height:1.55}
.doc{max-width:900px;margin:0 auto}
.hdr{background:linear-gradient(135deg,#0d3b0d,#1b5e20);padding:22px 32px 18px;color:#fff;position:relative}
.hdr-ey{font-size:9px;text-transform:uppercase;letter-spacing:3px;opacity:.5;margin-bottom:4px}
.hdr-t{font-size:23px;font-weight:900;letter-spacing:-.5px}
.hdr-s{font-size:11px;opacity:.65;margin-top:4px}
.hdr-badge{position:absolute;top:22px;right:32px;background:#e94560;color:#fff;font-size:10px;font-weight:800;padding:4px 14px;border-radius:20px;letter-spacing:1px;text-transform:uppercase}
.sec{padding:14px 32px;border-bottom:1px solid #f0f0f0}
.sec-t{font-size:10px;text-transform:uppercase;letter-spacing:2px;color:#1b5e20;font-weight:700;margin-bottom:10px}
.resumen{background:#f1f8e9;border-left:4px solid #1b5e20;padding:12px 16px;border-radius:0 6px 6px 0;font-size:12px;line-height:1.6}
.card{background:#f8fdf8;border-radius:6px;padding:10px 12px;border:1px solid #c8e6c9;margin-bottom:8px}
.card-h{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;color:#1b5e20}
.card-b{font-size:11.5px;color:#444}
.int-block{background:#f8fdf8;border-radius:6px;padding:10px 14px;margin-bottom:8px;border-left:3px solid #1b5e20}
.int-t{font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:1px;color:#1b5e20;margin-bottom:3px}
.int-b{font-size:11.5px;color:#333;line-height:1.55}
.bloqueo{border-left-color:#e94560!important;background:#fff5f5!important}
.bloqueo .int-t{color:#c62828!important}
.tag{display:inline-block;font-size:9px;font-weight:700;padding:2px 8px;border-radius:10px;text-transform:uppercase;letter-spacing:.5px;margin-right:4px}
.tag-ok{background:#e8f5e9;color:#2e7d32}
.tag-pres{background:#e3f2fd;color:#1565c0}
.tag-aus{background:#fafafa;color:#999}
.tag-act{background:#fff3e0;color:#e65100}
.tag-crit{background:#ffebee;color:#c62828}
.row{display:flex;align-items:baseline;gap:8px;padding:5px 0;border-bottom:1px solid #f5f5f5}
.row-k{font-size:10px;color:#888;min-width:120px}
.row-v{font-size:12px;color:#1a1a2e}
.agen-row{padding:6px 0;border-bottom:1px solid #f5f5f5;display:flex;gap:14px}
.agen-h{font-size:10px;font-weight:700;color:#1b5e20;min-width:180px}
.agen-d{font-size:11.5px;color:#333}
.def-row{padding:6px 0;border-bottom:1px solid #f5f5f5;display:grid;grid-template-columns:160px 200px 1fr;gap:8px}
.def-cat{font-size:10px;color:#888}
.def-el{font-size:11px;font-weight:700;color:#1a1a2e}
.def-det{font-size:11px;color:#444}
.footer{background:#1a1a2e;color:#aaa;font-size:9px;padding:10px 32px;text-align:center}
.alerta{padding:7px 12px;border-radius:4px;margin-bottom:6px;display:flex;gap:10px;align-items:baseline}
.alerta-crit{background:#ffebee;border-left:3px solid #c62828}
.alerta-alta{background:#fff3e0;border-left:3px solid #e65100}
.alerta-norm{background:#e8f5e9;border-left:3px solid #2e7d32}
.alerta-tipo{font-size:9px;font-weight:800;text-transform:uppercase;min-width:120px}
.alerta-desc{font-size:11px;color:#333}
@media print{@page{size:A4;margin:8mm}.doc{max-width:100%}}"""

def estado_tag(e):
    e = str(e).upper()
    if "PRESENT" in e:  return f'<span class="tag tag-pres">{e}</span>'
    if "COMPLET" in e:  return f'<span class="tag tag-ok">{e}</span>'
    if "AUSENT" in e:   return f'<span class="tag tag-aus">{e}</span>'
    return f'<span class="tag tag-act">{e}</span>'

# ── Asistencia ──
rows_asis = ""
for a in asistencia:
    rows_asis += f"""
    <div class="row">
      <span class="row-k">{a.get('gremio','')}</span>
      <span>{estado_tag(a.get('estado',''))}</span>
      <span class="row-v" style="font-size:11px;color:#555">{a.get('avance','')}</span>
    </div>"""

# ── Intervenciones ──
secs_html = ""
for k, v in secs.items():
    is_blq = any(x in k.upper() for x in ["BLOQ","RIESGO","FUGA","🔴"])
    cls = "int-block bloqueo" if is_blq else "int-block"
    secs_html += f'<div class="{cls}"><div class="int-t">{k}</div><div class="int-b">{v}</div></div>'

# ── Riesgos ──
riesgos_html = ""
for r in riesgos:
    pri = r.get("prioridad","")
    tag_cls = "tag-crit" if pri == "critica" else "tag-act" if pri == "alta" else "tag-ok"
    riesgos_html += f"""
    <div class="int-block bloqueo" style="margin-bottom:8px">
      <div class="int-t">{r.get('codigo','')} — {r.get('tipo','')}
        <span class="tag {tag_cls}" style="margin-left:8px">{pri.upper()}</span>
      </div>
      <div class="int-b" style="margin-bottom:4px">{r.get('descripcion','')}</div>
      <div style="font-size:10.5px;color:#e94560"><strong>Acción:</strong> {r.get('accion','')}</div>
      <div style="font-size:10px;color:#888;margin-top:2px">Responsable: {r.get('responsable','')}</div>
    </div>"""

# ── Alertas dashboard ──
alertas_html = ""
for a in alertas:
    pri = a.get("prioridad","normal")
    cls = "alerta alerta-crit" if pri == "critica" else "alerta alerta-alta" if pri == "alta" else "alerta alerta-norm"
    alertas_html += f"""
    <div class="{cls}">
      <span class="alerta-tipo">{a.get('tipo','')}</span>
      <span class="alerta-desc">{a.get('descripcion','')}</span>
    </div>"""

# ── Definiciones técnicas ──
defs_html = ""
for d in defs:
    defs_html += f"""
    <div class="def-row">
      <span class="def-cat">{d.get('categoria','')}</span>
      <span class="def-el">{d.get('elemento','')}</span>
      <span class="def-det">{d.get('detalle','')}</span>
    </div>"""

# ── Logros ──
logros_html = ""
for l in logros:
    logros_html += f"""
    <div class="row">
      <span class="tag tag-ok">✓</span>
      <span class="row-v">{l.get('descripcion','')}</span>
    </div>"""

# ── Solicitudes ──
sols_html = ""
for s in sols:
    urg = s.get("urgencia","")
    urg_cls = "tag-crit" if urg in ("crítica","urgente") else "tag-act" if urg == "alta" else "tag-ok"
    sols_html += f"""
    <div class="row">
      <span class="tag {urg_cls}">{urg.upper()}</span>
      <span class="row-v">{s.get('descripcion','')}</span>
      <span style="font-size:10px;color:#888;margin-left:auto">{s.get('responsable','')}</span>
    </div>"""

# ── Agenda ──
ag_html = ""
for item in ag_items:
    ag_html += f"""
    <div class="agen-row">
      <span class="agen-h">{item.get('hora','')}</span>
      <span class="agen-d">{item.get('evento','')}</span>
    </div>"""

HTML = f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width">
<title>Acta Reunión Semanal S12 · 09/06/2026</title>
<style>{CSS}</style></head><body>
<div class="doc">
  <div class="hdr">
    <div class="hdr-ey">PMO · Brescia 19 · Reunión Semanal S12</div>
    <div class="hdr-t">Acta de Reunión Semanal — Martes 09 de Junio de 2026</div>
    <div class="hdr-s">Nine Fitness Brescia 19 · Calle Brescia 19, 28028 Madrid · Ref: ACT-20260609-1300</div>
    <div class="hdr-badge">S12 · 09 JUN · REUNIÓN</div>
  </div>

  <div class="sec">
    <div class="sec-t">Resumen Ejecutivo</div>
    <div class="resumen">{REC.get('resumen','')}</div>
  </div>

  <div class="sec">
    <div class="sec-t">Asistentes a la Reunión</div>
    {rows_asis}
  </div>

  <div class="sec">
    <div class="sec-t">Acuerdos y Estado por Gremio</div>
    {secs_html}
  </div>

  <div class="sec">
    <div class="sec-t">Riesgos y Bloqueos Activos</div>
    {riesgos_html}
  </div>

  <div class="sec">
    <div class="sec-t">Definiciones Técnicas — Acuerdos del 09/06</div>
    {defs_html}
  </div>

  <div class="sec">
    <div class="sec-t">Alertas Dashboard — Semana S12</div>
    {alertas_html}
  </div>

  <div class="sec">
    <div class="sec-t">Logros y Avances de la Semana</div>
    {logros_html}
  </div>

  <div class="sec">
    <div class="sec-t">Solicitudes a Dirección — Acción Inmediata</div>
    {sols_html}
  </div>

  <div class="sec">
    <div class="sec-t">Agenda Próximas Jornadas</div>
    {ag_html}
  </div>

  <div class="footer">
    Acta generada automáticamente · PMO Brescia 19 · Darío Alejandro López · {REC.get('created_at','')[:10]}
  </div>
</div></body></html>"""

with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
    f.write(HTML)
    tmp = f.name

out = ESCRITORIO / "ACTA_REUNION_S12_09062026.pdf"
subprocess.run([CHROME,"--headless","--disable-gpu",
    f"--print-to-pdf={out}",
    "--print-to-pdf-no-header",
    "--no-margins",
    tmp], check=True)

print(f"PDF OK: {out}  ({out.stat().st_size//1024} KB)")
