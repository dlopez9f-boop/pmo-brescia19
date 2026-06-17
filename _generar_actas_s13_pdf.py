#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera PDFs actas S13: 15/06 (diaria), 16/06 (semanal), 17/06 (diaria)"""
import json, subprocess, tempfile, ctypes, ctypes.wintypes
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
_buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
ctypes.windll.shell32.SHGetFolderPathW(0, 0, 0, 0, _buf)
ESCRITORIO = Path(_buf.value)

diarias = json.loads((Path("actas_data") / "actas_diarias.json").read_text(encoding="utf-8"))

def pj(raw, default=None):
    if default is None: default = []
    if not raw: return default
    if isinstance(raw, (list, dict)): return raw
    try: return json.loads(raw)
    except: return default

def get_acta(acta_id):
    return next(r for r in diarias if r["id"] == acta_id)

CSS_DIARIA = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Helvetica Neue',Arial,sans-serif;background:#fff;color:#1a1a2e;font-size:12.5px;line-height:1.55}
.doc{max-width:900px;margin:0 auto}
.hdr{background:linear-gradient(135deg,#1a1a2e,#0f3460);padding:22px 32px 18px;color:#fff;position:relative}
.hdr-ey{font-size:9px;text-transform:uppercase;letter-spacing:3px;opacity:.5;margin-bottom:4px}
.hdr-t{font-size:23px;font-weight:900;letter-spacing:-.5px}
.hdr-s{font-size:11px;opacity:.65;margin-top:4px}
.hdr-badge{position:absolute;top:22px;right:32px;background:#1565c0;color:#fff;font-size:10px;font-weight:800;padding:4px 14px;border-radius:20px;letter-spacing:1px;text-transform:uppercase}
.hdr-badge-crit{background:#c62828!important}
.sec{padding:14px 32px;border-bottom:1px solid #f0f0f0}
.sec-t{font-size:10px;text-transform:uppercase;letter-spacing:2px;color:#e94560;font-weight:700;margin-bottom:10px}
.resumen{background:#f8f9ff;border-left:4px solid #0f3460;padding:12px 16px;border-radius:0 6px 6px 0;font-size:12px;line-height:1.6}
.int-block{background:#f8f9ff;border-radius:6px;padding:10px 14px;margin-bottom:8px;border-left:3px solid #0f3460}
.int-t{font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:1px;color:#0f3460;margin-bottom:3px}
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
.agen-h{font-size:10px;font-weight:700;color:#0f3460;min-width:160px}
.agen-d{font-size:11.5px;color:#333}
.alerta{padding:7px 12px;border-radius:4px;margin-bottom:6px;display:flex;gap:10px;align-items:baseline}
.alerta-crit{background:#ffebee;border-left:3px solid #c62828}
.alerta-alta{background:#fff3e0;border-left:3px solid #e65100}
.alerta-norm{background:#e8f5e9;border-left:3px solid #2e7d32}
.alerta-tipo{font-size:9px;font-weight:800;text-transform:uppercase;min-width:140px;color:#333}
.alerta-desc{font-size:11px;color:#444}
.footer{background:#1a1a2e;color:#aaa;font-size:9px;padding:10px 32px;text-align:center}
@media print{@page{size:A4;margin:8mm}.doc{max-width:100%}}"""

CSS_SEMANAL = CSS_DIARIA.replace(
    "background:linear-gradient(135deg,#1a1a2e,#0f3460)",
    "background:linear-gradient(135deg,#0d3b0d,#1b5e20)"
).replace(
    "color:#0f3460;font-weight:700;margin-bottom:10px",
    "color:#1b5e20;font-weight:700;margin-bottom:10px"
).replace(
    "border-left:4px solid #0f3460",
    "border-left:4px solid #1b5e20"
).replace(
    "border-left:3px solid #0f3460",
    "border-left:3px solid #1b5e20"
).replace(
    "color:#0f3460;margin-bottom:3px",
    "color:#1b5e20;margin-bottom:3px"
).replace(
    "font-weight:700;color:#0f3460;min-width:160px",
    "font-weight:700;color:#1b5e20;min-width:160px"
)

def estado_tag(e):
    e = str(e).upper()
    if "PRESENT" in e:  return f'<span class="tag tag-pres">{e}</span>'
    if "COMPLET" in e:  return f'<span class="tag tag-ok">{e}</span>'
    if "AUSENT" in e:   return f'<span class="tag tag-aus">{e}</span>'
    if "2DO" in e or "CRITICO" in e or "BLOQ" in e: return f'<span class="tag tag-crit">{e}</span>'
    return f'<span class="tag tag-act">{e}</span>'

def build_html(rec, css, hdr_color="#1565c0", tipo_badge="DIARIA", fecha_larga=""):
    asistencia = pj(rec.get("asistencia"))
    secs       = pj(rec.get("intervenciones"), {})
    riesgos    = pj(rec.get("riesgos"))
    alertas    = pj(rec.get("alertas_dashboard"))
    logros     = pj(rec.get("logros_tecnicos"))
    sols       = pj(rec.get("solicitudes_direccion"))
    ag_raw     = pj(rec.get("agenda_proxima"), {})
    ag_items   = ag_raw.get("items", []) if isinstance(ag_raw, dict) else []

    rows_asis = ""
    for a in asistencia:
        rows_asis += f"""<div class="row">
          <span class="row-k">{a.get('gremio','')}</span>
          <span>{estado_tag(a.get('estado',''))}</span>
          <span class="row-v" style="font-size:11px;color:#666">{a.get('avance','')}</span>
        </div>"""

    secs_html = ""
    for k, v in secs.items():
        is_blq = any(x in k.upper() for x in ["BLOQ","RIESGO","FUGA","CRITICO","AUSENCIA"])
        cls = "int-block bloqueo" if is_blq else "int-block"
        secs_html += f'<div class="{cls}"><div class="int-t">{k}</div><div class="int-b">{v}</div></div>'

    riesgos_html = ""
    for r in riesgos:
        pri = r.get("prioridad","")
        tag_cls = "tag-crit" if pri == "critica" else "tag-act" if pri == "alta" else "tag-ok"
        riesgos_html += f"""<div class="int-block bloqueo" style="margin-bottom:8px">
          <div class="int-t">{r.get('codigo','')} — {r.get('tipo','')}
            <span class="tag {tag_cls}" style="margin-left:8px">{pri.upper()}</span>
          </div>
          <div class="int-b" style="margin-bottom:4px">{r.get('descripcion','')}</div>
          <div style="font-size:10.5px;color:#e94560"><strong>Accion:</strong> {r.get('accion','')}</div>
          <div style="font-size:10px;color:#888;margin-top:2px">Responsable: {r.get('responsable','')}</div>
        </div>"""

    alertas_html = ""
    for a in alertas:
        pri = a.get("prioridad","normal")
        cls = "alerta alerta-crit" if pri=="critica" else "alerta alerta-alta" if pri=="alta" else "alerta alerta-norm"
        alertas_html += f"""<div class="{cls}">
          <span class="alerta-tipo">{a.get('tipo','')}</span>
          <span class="alerta-desc">{a.get('descripcion','')}</span>
        </div>"""

    logros_html = ""
    for l in logros:
        logros_html += f"""<div class="row">
          <span class="tag tag-ok">OK</span>
          <span class="row-v">{l.get('descripcion','')}</span>
        </div>"""

    sols_html = ""
    for s in sols:
        urg = s.get("urgencia","")
        urg_cls = "tag-crit" if urg in ("critica","critica","urgente") else "tag-act" if urg=="alta" else "tag-ok"
        sols_html += f"""<div class="row">
          <span class="tag {urg_cls}">{urg.upper()}</span>
          <span class="row-v">{s.get('descripcion','')}</span>
          <span style="font-size:10px;color:#888;margin-left:auto">{s.get('responsable','')}</span>
        </div>"""

    ag_html = ""
    for item in ag_items:
        ag_html += f"""<div class="agen-row">
          <span class="agen-h">{item.get('hora','')}</span>
          <span class="agen-d">{item.get('evento','')}</span>
        </div>"""

    badge_cls = "hdr-badge hdr-badge-crit" if rec.get("prioridad") == "critica" else "hdr-badge"
    badge_color = f'style="background:{hdr_color}"'

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<title>Acta {fecha_larga}</title>
<style>{css}</style></head><body>
<div class="doc">
  <div class="hdr">
    <div class="hdr-ey">PMO · Brescia 19 · {tipo_badge}</div>
    <div class="hdr-t">Acta de Obra — {fecha_larga}</div>
    <div class="hdr-s">Nine Fitness Brescia 19 · Calle Brescia 19, 28028 Madrid · Ref: {rec['id']}</div>
    <div class="{badge_cls}" {badge_color}>S13 · {rec['fecha'][8:10]}/{rec['fecha'][5:7]}</div>
  </div>
  <div class="sec">
    <div class="sec-t">Resumen Ejecutivo</div>
    <div class="resumen">{rec.get('resumen','')}</div>
  </div>
  <div class="sec">
    <div class="sec-t">Asistencia y Estado por Gremio</div>
    {rows_asis}
  </div>
  <div class="sec">
    <div class="sec-t">Intervenciones y Estado de Obra</div>
    {secs_html}
  </div>
  <div class="sec">
    <div class="sec-t">Riesgos y Bloqueos Activos</div>
    {riesgos_html if riesgos_html else '<div style="color:#888;font-size:11px">Sin riesgos nuevos.</div>'}
  </div>
  <div class="sec">
    <div class="sec-t">Alertas Dashboard</div>
    {alertas_html}
  </div>
  <div class="sec">
    <div class="sec-t">Logros y Avances</div>
    {logros_html}
  </div>
  <div class="sec">
    <div class="sec-t">Solicitudes a Direccion — Accion Inmediata</div>
    {sols_html}
  </div>
  <div class="sec">
    <div class="sec-t">Agenda Proximas Jornadas</div>
    {ag_html}
  </div>
  <div class="footer">
    Acta generada automaticamente · PMO Brescia 19 · Dario Alejandro Lopez · {rec.get('created_at','')[:10]}
  </div>
</div></body></html>"""

def render_pdf(html_str, out_path):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html_str)
        tmp = f.name
    subprocess.run([CHROME, "--headless", "--disable-gpu",
        f"--print-to-pdf={out_path}",
        "--print-to-pdf-no-header", "--no-margins", tmp], check=True)
    print(f"PDF OK: {out_path.name}  ({out_path.stat().st_size//1024} KB)")

# ── 15/06 — Diaria S13 ────────────────────────────────────────────────────
rec15 = get_acta("ACT-20260615-1800")
html15 = build_html(rec15, CSS_DIARIA, "#1565c0", "Acta Diaria S13",
                    "Lunes 15 de Junio de 2026")
render_pdf(html15, ESCRITORIO / "ACTA_DIARIA_S13_15062026.pdf")

# ── 16/06 — Reunion Semanal S13 ───────────────────────────────────────────
rec16 = get_acta("ACT-20260616-1300")
html16 = build_html(rec16, CSS_SEMANAL, "#1b5e20", "Reunion Semanal S13",
                    "Martes 16 de Junio de 2026 — Reunion Semanal")
render_pdf(html16, ESCRITORIO / "ACTA_REUNION_S13_16062026.pdf")

# ── 17/06 — Diaria S13 ────────────────────────────────────────────────────
rec17 = get_acta("ACT-20260617-1800")
html17 = build_html(rec17, CSS_DIARIA, "#c62828", "Acta Diaria S13 — ALERTA ELECTRICA",
                    "Miercoles 17 de Junio de 2026")
render_pdf(html17, ESCRITORIO / "ACTA_DIARIA_S13_17062026.pdf")

print("\nTodos los PDFs generados en el Escritorio.")
