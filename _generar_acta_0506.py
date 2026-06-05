#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, subprocess, tempfile, ctypes, ctypes.wintypes
from pathlib import Path
from datetime import date

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
_buf   = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
ctypes.windll.shell32.SHGetFolderPathW(0, 0, 0, 0, _buf)
ESCRITORIO = Path(_buf.value)

diarias = json.loads((Path("actas_data") / "actas_diarias.json").read_text(encoding="utf-8"))
REC     = next(r for r in diarias if r["id"] == "ACT-20260605-1800")

def pj(raw, default=None):
    if default is None: default = []
    if not raw: return default
    if isinstance(raw, (list, dict)): return raw
    try: return json.loads(raw)
    except: return default

incs       = pj(REC.get("incidencias"))
logros     = pj(REC.get("logros_tecnicos"))
sols       = pj(REC.get("solicitudes_direccion"))
secs       = pj(REC.get("intervenciones"), {})
ag_raw     = pj(REC.get("agenda_proxima"), {})
ag_items   = ag_raw.get("items", []) if isinstance(ag_raw, dict) else []
alertas_d  = pj(REC.get("alertas_dashboard"))
asistencia = pj(REC.get("asistencia"))
riesgos    = pj(REC.get("riesgos"))
defs       = pj(REC.get("definiciones_tecnicas"))

CSS = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Helvetica Neue',Arial,sans-serif;background:#fff;color:#1a1a2e;font-size:12.5px;line-height:1.55}
.doc{max-width:900px;margin:0 auto}
.hdr{background:linear-gradient(135deg,#1a1a2e,#0f3460);padding:22px 32px 18px;color:#fff;position:relative}
.hdr-ey{font-size:9px;text-transform:uppercase;letter-spacing:3px;opacity:.5;margin-bottom:4px}
.hdr-t{font-size:23px;font-weight:900;letter-spacing:-.5px}
.hdr-s{font-size:11px;opacity:.65;margin-top:4px}
.hdr-badge{position:absolute;top:22px;right:32px;background:#7b1fa2;color:#fff;font-size:10px;font-weight:800;padding:4px 14px;border-radius:20px;letter-spacing:1px;text-transform:uppercase}
.accent{position:absolute;bottom:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#e94560,#0f3460,#e94560)}
.meta{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid #e2e8f0;background:#f8f9ff}
.mc{padding:10px 14px;border-right:1px solid #e2e8f0}.mc:last-child{border-right:none}
.ml{font-size:9px;text-transform:uppercase;letter-spacing:1.5px;color:#94a3b8;font-weight:600;margin-bottom:3px}
.mv{font-size:12px;font-weight:700}
.body{padding:20px 32px 26px}
.sec{margin-bottom:20px;break-inside:avoid}
.sh{display:flex;align-items:center;gap:9px;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #e94560}
.st{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:1px}
.resumen{background:#f8f9ff;border-left:4px solid #0f3460;padding:12px 15px;border-radius:0 8px 8px 0;font-size:12px;color:#2c3e50;line-height:1.65}
.gbl{margin-bottom:8px;padding-bottom:8px;border-bottom:1px solid #f0f4f8}.gbl:last-child{border-bottom:none;margin-bottom:0;padding-bottom:0}
.gnm{font-size:10px;font-weight:800;color:#0f3460;margin-bottom:3px;text-transform:uppercase;letter-spacing:.5px}
.gcnt{font-size:11px;padding-left:10px;border-left:3px solid #e2e6f0;color:#374151;line-height:1.55}
.tbl{width:100%;border-collapse:collapse;font-size:11px}
.tbl thead tr{background:#1a1a2e;color:#fff}
.tbl th{padding:7px 10px;text-align:left;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:600}
.tbl td{padding:8px 10px;border-bottom:1px solid #f0f2f8;vertical-align:middle;line-height:1.5}
.tbl tr:nth-child(even) td{background:#f8f9ff}
.rcard{border-radius:8px;overflow:hidden;margin-bottom:8px}
.logrow{display:flex;gap:10px;padding:8px 0;border-bottom:1px solid #f0f2f8;align-items:flex-start}
.logrow:last-child{border-bottom:none}
.sol-item{border:1px solid;border-radius:0 6px 6px 0;padding:8px 12px;margin-bottom:6px}
.ag-row{display:flex;gap:12px;padding:7px 0;border-bottom:1px solid #f0f2f8;align-items:flex-start}
.ag-row:last-child{border-bottom:none}
.ag-hora{min-width:130px;font-size:11px;font-weight:800;color:#e94560;flex-shrink:0;text-align:right;padding-right:12px;border-right:2px solid #e2e8f0}
.ag-ev{font-size:11px;color:#1a1a2e;line-height:1.5}
.alert-card{border-radius:7px;overflow:hidden;margin-bottom:7px;display:flex;gap:0}
.eco-card{border-radius:7px;padding:10px 14px;margin-bottom:8px;border:1px solid}
.ftr{background:#1a1a2e;padding:10px 32px;display:flex;justify-content:space-between;align-items:center;color:rgba(255,255,255,.4);font-size:9px;flex-wrap:wrap;gap:4px}
.ftr b{color:rgba(255,255,255,.65)}
@media print{body{background:#fff}.doc{margin:0}.sec{break-inside:avoid}}
@page{size:A4;margin:8mm}"""


def build():
    # Asistencia
    asist_rows = ""
    for a in asistencia:
        est = a.get("estado", "")
        col = {"PRESENTE": "#27ae60", "AUSENTE": "#c0392b", "PAUSADO": "#7b1fa2"}.get(est, "#94a3b8")
        bg  = {"PRESENTE": "#e8f5e9", "AUSENTE": "#fdf2f2", "PAUSADO": "#f3e5f5"}.get(est, "#f8f9ff")
        asist_rows += f"""<tr style="background:{bg};">
  <td style="font-weight:700;">{a.get('gremio','')}</td>
  <td><span style="background:{col};color:#fff;font-size:9px;font-weight:800;padding:2px 9px;border-radius:10px;">{est}</span></td>
  <td style="color:#475569;">{a.get('horas','')}</td>
  <td style="color:#374151;">{a.get('avance','')}</td>
</tr>"""

    # Riesgos
    riesgos_html = ""
    for r in riesgos:
        pr  = r.get("prioridad", "normal")
        bc  = "#c0392b" if pr in ("critica","urgente") else ("#e67e22" if pr == "alta" else "#2471a3")
        est = r.get("estado", "ACTIVO")
        ec  = {"ACTIVO": "#c0392b", "EN GESTIÓN": "#e67e22", "RESUELTO": "#27ae60"}.get(est, "#c0392b")
        riesgos_html += f"""<div class="rcard" style="border:1px solid {bc}33;border-left:5px solid {bc};">
  <div style="background:{bc}0d;padding:8px 14px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
    <span style="background:{bc};color:#fff;font-size:9px;font-weight:800;padding:2px 9px;border-radius:10px;text-transform:uppercase;">{r.get('tipo','')}</span>
    <span style="font-size:11px;font-weight:800;color:#1a1a2e;">{r.get('codigo','')}</span>
    <span style="margin-left:auto;background:{ec}22;color:{ec};font-size:9px;font-weight:800;padding:2px 8px;border-radius:8px;border:1px solid {ec}44;">{est}</span>
    <span style="font-size:10px;color:#94a3b8;">Resp.: {r.get('responsable','')}</span>
  </div>
  <div style="padding:9px 14px;font-size:11px;color:#374151;line-height:1.6;">
    {r.get('descripcion','')}
    <div style="margin-top:6px;padding:5px 9px;background:{bc}12;color:{bc};font-size:11px;font-weight:700;border-radius:4px;">
      &#9654; {r.get('accion','')}
    </div>
  </div>
</div>"""

    # Control económico (extraído de intervenciones)
    eco_html = ""
    eco_keys = [k for k in secs if "Control Económico" in k or "💰" in k]
    for key in eco_keys:
        contenido = secs[key]
        if "CERRADO" in contenido or "APROBADO" in contenido:
            border = "#27ae60"; bg_eco = "#f0faf5"
            badge_txt = "APROBADO Y CERRADO"; badge_col = "#27ae60"
        elif "PENDIENTE" in contenido:
            border = "#e67e22"; bg_eco = "#fff8e1"
            badge_txt = "PENDIENTE FIRMA"; badge_col = "#e67e22"
        else:
            border = "#2471a3"; bg_eco = "#eaf4ff"
            badge_txt = "EN REVISIÓN"; badge_col = "#2471a3"
        eco_html += f"""<div class="eco-card" style="border-color:{border}44;background:{bg_eco};border-left:5px solid {border};">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
    <span style="background:{badge_col};color:#fff;font-size:9px;font-weight:800;padding:2px 8px;border-radius:10px;">{badge_txt}</span>
    <span style="font-size:11px;font-weight:700;color:#1a1a2e;">{key}</span>
  </div>
  <div style="font-size:11.5px;color:#374151;line-height:1.6;">{contenido}</div>
</div>"""

    # Alertas dashboard
    alertas_html = ""
    tipo_colores = {
        "PENDIENTE CONFIRMACIÓN": "#e67e22", "PENDIENTE FIRMA": "#e67e22",
        "CONTROL CONTABILIDAD": "#7b1fa2", "REVISIÓN TÉCNICA CRÍTICA": "#c0392b",
        "ESCALADO URGENTE": "#c0392b",
    }
    for a in alertas_d:
        bc  = tipo_colores.get(a.get("tipo", ""), "#e67e22")
        pr  = a.get("prioridad", "normal")
        pr_label = {"critica": "🔴 CRÍTICA", "alta": "🟡 ALTA", "normal": "⚪ NORMAL"}.get(pr, "⚪")
        alertas_html += f"""<div class="alert-card" style="border:1px solid {bc}33;border-left:4px solid {bc};border-radius:7px;overflow:hidden;margin-bottom:7px;">
  <div style="padding:7px 13px;background:{bc}0a;display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
    <span style="background:{bc};color:#fff;font-size:9px;font-weight:800;padding:2px 8px;border-radius:10px;white-space:nowrap;text-transform:uppercase;">{a.get('tipo','')}</span>
    <span style="font-size:10px;font-weight:700;color:#1a1a2e;">{a.get('codigo','')}</span>
    <span style="margin-left:auto;font-size:10px;font-weight:700;color:{bc};">{pr_label}</span>
  </div>
  <div style="padding:7px 13px;font-size:11px;color:#374151;line-height:1.55;">{a.get('descripcion','')}</div>
</div>"""

    # Intervenciones (excluir las de control económico ya mostradas arriba)
    secs_html = ""
    if isinstance(secs, dict):
        for g, c in secs.items():
            if c and "💰" not in g:
                secs_html += (f'<div class="gbl"><div class="gnm">{g}</div>'
                              f'<div class="gcnt">{str(c).replace(chr(10),"<br>")}</div></div>')

    # Definiciones técnicas
    def_rows = "".join(f"""<tr>
  <td style="color:#0f3460;font-weight:700;font-size:10px;">{d.get('categoria','')}</td>
  <td style="font-weight:600;">{d.get('elemento','')}</td>
  <td style="color:#374151;">{d.get('detalle','')}</td>
</tr>""" for d in defs)

    # Logros
    ICONOS = ["&#127942;", "&#9989;", "&#10024;", "&#9889;", "&#128274;", "&#128203;"]
    logros_html = "".join(
        f'<div class="logrow"><div style="font-size:18px;flex-shrink:0;">{ICONOS[i%len(ICONOS)]}</div><div>'
        f'<div style="font-size:11px;font-weight:700;color:#1b5e20;margin-bottom:1px;">{l.get("descripcion","")}</div>'
        f'<div style="font-size:11px;color:#475569;">{l.get("impacto","")}</div>'
        + (f'<div style="display:flex;gap:5px;margin-top:2px;font-size:10px;">'
           f'<span style="background:#fdf2f2;color:#c0392b;padding:1px 6px;border-radius:5px;">{l.get("mejora_de","")}</span>'
           f'<span style="color:#94a3b8;">&#8594;</span>'
           f'<span style="background:#e8f5e9;color:#1b5e20;padding:1px 6px;border-radius:5px;">{l.get("mejora_a","")}</span></div>'
           if l.get("mejora_de") or l.get("mejora_a") else "")
        + '</div></div>'
        for i, l in enumerate(logros) if isinstance(l, dict)
    )

    # Solicitudes
    sols_html = ""
    for s in sols:
        if isinstance(s, dict):
            urg = s.get("urgencia", "normal")
            bc  = "#c0392b" if urg in ("crítica","urgente") else ("#e67e22" if urg == "alta" else "#475569")
            bg  = "#fdf2f2" if urg in ("crítica","urgente") else ("#fff8e1" if urg == "alta" else "#f8f9ff")
            sols_html += (f'<div class="sol-item" style="background:{bg};border-color:{bc}55;border-left-color:{bc};">'
                          f'<div style="font-size:11px;font-weight:700;color:#1a1a2e;margin-bottom:3px;">{s.get("descripcion","")}</div>'
                          f'<div style="font-size:10px;color:#94a3b8;">Resp.: <b>{s.get("responsable","")}</b>'
                          f' &nbsp;&middot;&nbsp; <b style="color:{bc};">{urg.upper()}</b></div></div>')

    # Agenda
    agenda_html = "".join(
        f'<div class="ag-row"><div class="ag-hora">{it.get("hora","—")}</div><div class="ag-ev">{it.get("evento","")}</div></div>'
        for it in ag_items if isinstance(it, dict)
    )

    today = date.today().strftime("%d/%m/%Y")

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<title>Acta Diaria 05/06/2026 — Nine Fitness Brescia 19</title>
<style>{CSS}</style></head><body><div class="doc">

<div class="hdr">
  <div class="hdr-badge">S11 · 05 JUN · CIERRE</div>
  <div class="hdr-ey">Nine Fitness Group S.L. &middot; PMO Brescia 19 &middot; Acta Diaria de Obra</div>
  <div class="hdr-t">ACTA DIARIA DE OBRA</div>
  <div class="hdr-s">Viernes 5 de junio de 2026 &nbsp;&middot;&nbsp; Calle Brescia 19, 28028 Madrid &nbsp;&middot;&nbsp; Cierre Semana S11</div>
  <div class="accent"></div>
</div>
<div class="meta">
  <div class="mc"><div class="ml">Referencia</div><div class="mv">ACT-20260605-1800</div></div>
  <div class="mc"><div class="ml">Semana de obra</div><div class="mv">S11 / 2026 — Cierre</div></div>
  <div class="mc"><div class="ml">Prioridad</div><div class="mv" style="color:#e67e22;">&#128993; Alta</div></div>
  <div class="mc"><div class="ml">Director de Obra</div><div class="mv">Dar&iacute;o A. L&oacute;pez</div></div>
</div>

<div class="body">

  <div class="sec">
    <div class="sh"><span>&#128203;</span><span class="st">Resumen Ejecutivo</span></div>
    <div class="resumen">{REC.get('resumen','')}</div>
  </div>

  <div class="sec">
    <div class="sh"><span>&#128101;</span><span class="st">Control de Asistencia &mdash; 05/06/2026</span></div>
    <table class="tbl">
      <thead><tr><th width="220">Gremio / Empresa</th><th width="90">Estado</th><th width="130">Horas</th><th>Avance del d&iacute;a</th></tr></thead>
      <tbody>{asist_rows}</tbody>
    </table>
  </div>

  <div class="sec">
    <div class="sh"><span>&#128680;</span><span class="st">Dashboard de Riesgos</span></div>
    {riesgos_html}
  </div>

  <div class="sec">
    <div class="sh"><span>&#128176;</span><span class="st">Control Econ&oacute;mico y Presupuestos</span></div>
    {eco_html}
  </div>

  <div class="sec">
    <div class="sh"><span>&#128276;</span><span class="st">Alertas de Seguimiento &mdash; To-Do Dashboard</span></div>
    {alertas_html}
  </div>

  <div class="sec">
    <div class="sh"><span>&#128295;</span><span class="st">Intervenciones por Gremio</span></div>
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:13px 15px;">{secs_html}</div>
  </div>

  <div class="sec">
    <div class="sh"><span>&#128218;</span><span class="st">Definiciones T&eacute;cnicas y Planificaci&oacute;n S12</span></div>
    <table class="tbl">
      <thead><tr><th width="160">Categor&iacute;a</th><th width="200">Elemento</th><th>Detalle t&eacute;cnico</th></tr></thead>
      <tbody>{def_rows}</tbody>
    </table>
  </div>

  <div class="sec">
    <div class="sh"><span>&#127942;</span><span class="st">Logros y Resoluciones del D&iacute;a</span></div>
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:12px 14px;">{logros_html}</div>
  </div>

  <div class="sec">
    <div class="sh"><span>&#128204;</span><span class="st">Acciones y Solicitudes a Direcci&oacute;n</span></div>
    {sols_html}
  </div>

  <div class="sec">
    <div class="sh"><span>&#128197;</span><span class="st">Agenda Semana S12 &mdash; L&uacute;nes 08/06 en adelante</span></div>
    {agenda_html}
  </div>

</div>
<div class="ftr">
  <div>NINE FITNESS GROUP S.L. &middot; Calle Brescia 19, 28028 Madrid &middot; Confidencial</div>
  <div>Dir. Obra: <b>Dar&iacute;o A. L&oacute;pez</b> &nbsp;&middot;&nbsp; Arq.: <b>&Aacute;ngel Rodr&iacute;guez Mart&iacute;nez-Conde (COAM 12399)</b></div>
  <div>Ref: <b>ACT-20260605-1800</b> &nbsp;&middot;&nbsp; <b>{today}</b></div>
</div>
</div></body></html>"""


if __name__ == "__main__":
    html = build()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        hp  = tmp / "acta.html"
        hp.write_text(html, encoding="utf-8")
        pdf = ESCRITORIO / "ACTA_DIARIA_S11_05062026.pdf"
        r   = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
             "--disable-extensions", "--print-to-pdf-no-header",
             f"--print-to-pdf={pdf}", hp.as_uri()],
            capture_output=True, text=True, timeout=35)
        if pdf.exists() and pdf.stat().st_size > 5000:
            print(f"OK  {pdf.name}  ({pdf.stat().st_size // 1024} KB)")
        else:
            print("ERROR:", r.stderr[:300])
