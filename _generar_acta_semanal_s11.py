#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, subprocess, tempfile, ctypes, ctypes.wintypes
from pathlib import Path
from datetime import date

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
_buf   = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
ctypes.windll.shell32.SHGetFolderPathW(0, 0, 0, 0, _buf)
ESCRITORIO = Path(_buf.value)

data    = json.loads((Path("actas_data") / "actas_semanales.json").read_text(encoding="utf-8"))
REC     = next(r for r in data if r["id"] == "ACT-SEM-S11-2026")
hitos   = REC.get("hitos_cumplidos", [])
desvs   = REC.get("desviaciones_criticas", [])
alertas = REC.get("alertas_criticas", [])
incs    = REC.get("incidencias", [])
contratas = REC.get("avance_contratas", {})
eco     = REC.get("control_economico", {})
plan    = REC.get("planificacion_s12", {})

CSS = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Helvetica Neue',Arial,sans-serif;background:#fff;color:#1a1a2e;font-size:12px;line-height:1.55}
.doc{max-width:920px;margin:0 auto}
.hdr{background:linear-gradient(135deg,#1a1a2e 0%,#0f3460 60%,#1a4a7a 100%);padding:24px 36px 20px;color:#fff;position:relative}
.hdr-tag{font-size:9px;text-transform:uppercase;letter-spacing:3px;opacity:.5;margin-bottom:5px}
.hdr-t{font-size:26px;font-weight:900;letter-spacing:-.5px;line-height:1.1}
.hdr-s{font-size:11.5px;opacity:.7;margin-top:5px}
.hdr-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:16px}
.hdr-kpi{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);border-radius:7px;padding:9px 12px}
.hdr-kpi-l{font-size:8.5px;text-transform:uppercase;letter-spacing:1.5px;opacity:.5;margin-bottom:3px}
.hdr-kpi-v{font-size:13px;font-weight:800}
.accent{position:absolute;bottom:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#e94560,#0f3460,#e94560)}
.body{padding:20px 32px 28px}
.sec{margin-bottom:22px;break-inside:avoid}
.sh{display:flex;align-items:center;gap:9px;margin-bottom:11px;padding-bottom:7px;border-bottom:2px solid #e94560}
.st{font-size:10.5px;font-weight:800;text-transform:uppercase;letter-spacing:1.2px}
.resumen{background:#f8f9ff;border-left:4px solid #0f3460;padding:13px 16px;border-radius:0 8px 8px 0;font-size:12px;color:#2c3e50;line-height:1.7}
.alerta-card{border-radius:7px;overflow:hidden;margin-bottom:8px;border:1px solid}
.alerta-hdr{padding:8px 14px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.alerta-body{padding:8px 14px;font-size:11.5px;color:#374151;line-height:1.55}
.alerta-footer{padding:5px 14px 8px;font-size:10.5px;font-style:italic;opacity:.7}
.tbl{width:100%;border-collapse:collapse;font-size:11px}
.tbl thead tr{background:#1a1a2e;color:#fff}
.tbl th{padding:7px 10px;text-align:left;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:600}
.tbl td{padding:8px 10px;border-bottom:1px solid #f0f2f8;vertical-align:top;line-height:1.5}
.tbl tr:nth-child(even) td{background:#f8f9ff}
.contrata-card{border:1px solid #e2e8f0;border-radius:8px;margin-bottom:10px;overflow:hidden}
.contrata-hdr{padding:9px 14px;display:flex;align-items:center;gap:10px;background:#f8f9ff;border-bottom:1px solid #e2e8f0}
.contrata-body{padding:10px 14px}
.contrata-row{display:flex;gap:8px;margin-bottom:5px;font-size:11.5px}
.contrata-label{min-width:100px;font-size:9.5px;font-weight:800;text-transform:uppercase;color:#94a3b8;flex-shrink:0;padding-top:1px}
.eco-card{border-radius:7px;padding:10px 14px;margin-bottom:8px;border:1px solid}
.plan-item{display:flex;gap:10px;padding:7px 0;border-bottom:1px solid #f0f2f8;align-items:flex-start}
.plan-item:last-child{border-bottom:none}
.plan-hora{min-width:120px;font-size:11px;font-weight:800;color:#e94560;flex-shrink:0;text-align:right;padding-right:12px;border-right:2px solid #e2e8f0}
.plan-ev{font-size:11.5px;color:#1a1a2e;line-height:1.5}
.hito-item{display:flex;align-items:flex-start;gap:8px;padding:5px 0;border-bottom:1px solid #f0f2f8;font-size:11.5px}
.hito-item:last-child{border-bottom:none}
.desv-item{display:flex;align-items:flex-start;gap:8px;padding:5px 0;border-bottom:1px solid #f0f2f8;font-size:11.5px;color:#c0392b}
.desv-item:last-child{border-bottom:none}
.ftr{background:#1a1a2e;padding:10px 32px;display:flex;justify-content:space-between;align-items:center;color:rgba(255,255,255,.4);font-size:9px;flex-wrap:wrap;gap:4px}
.ftr b{color:rgba(255,255,255,.65)}
@media print{body{background:#fff}.doc{margin:0}.sec{break-inside:avoid}}
@page{size:A4;margin:8mm}"""


def badge(text, color, bg=None, size="9px"):
    bg = bg or color + "22"
    return (f'<span style="background:{color};color:#fff;font-size:{size};font-weight:800;'
            f'padding:2px 9px;border-radius:10px;text-transform:uppercase;">{text}</span>')


def build():
    # 1. ALERTAS CRÍTICAS
    tipo_col = {
        "RIESGO CRÍTICO LICENCIA": "#c0392b",
        "PENDIENTE CONFIRMACIÓN": "#e67e22",
        "CONTROL CONTABILIDAD": "#7b1fa2",
    }
    alertas_html = ""
    for a in alertas:
        bc = tipo_col.get(a.get("tipo", ""), "#e67e22")
        alertas_html += f"""<div class="alerta-card" style="border-color:{bc}44;border-left:5px solid {bc};">
  <div class="alerta-hdr" style="background:{bc}10;">
    {badge(a.get('tipo',''), bc)}
    <span style="font-size:11px;font-weight:800;color:#1a1a2e;">{a.get('codigo','')}</span>
    <span style="margin-left:auto;font-size:10px;font-weight:700;color:{bc};">Resp.: {a.get('responsable','')}</span>
  </div>
  <div class="alerta-body">{a.get('descripcion','')}</div>
  <div class="alerta-footer">&#9654; Acción: {a.get('accion_requerida','')} &nbsp;|&nbsp; Deadline: <b>{a.get('deadline','—')}</b></div>
</div>"""

    # 2. AVANCE CONTRATAS
    est_col = {"EN PLAZO": "#27ae60", "HITOS ALCANZADOS — pausa fin de semana": "#2471a3",
               "EN EJECUCIÓN — en plazo": "#27ae60", "ATENCIÓN — múltiples ausencias": "#e67e22",
               "PREPARACIÓN — entra S12": "#7b1fa2", "PAUSADO — cambio color": "#e67e22"}
    contratas_html = ""
    for key, c in contratas.items():
        est = c.get("estado", "")
        ec = est_col.get(est, "#94a3b8")
        contratas_html += f"""<div class="contrata-card">
  <div class="contrata-hdr">
    <span style="background:{ec};color:#fff;font-size:9px;font-weight:800;padding:2px 8px;border-radius:8px;">{est}</span>
    <span style="font-size:11px;font-weight:700;color:#1a1a2e;">{key.replace('_',' ').title()}</span>
  </div>
  <div class="contrata-body">
    <div class="contrata-row"><span class="contrata-label">Semana S11</span><span>{c.get('avance_semana','')}</span></div>
    <div class="contrata-row"><span class="contrata-label">S12 Próximo</span><span style="color:#0f3460;font-weight:600;">{c.get('proximo_s12','')}</span></div>
    <div class="contrata-row"><span class="contrata-label">Gantt</span><span style="color:#475569;font-size:11px;">{c.get('estado_gantt','')}</span></div>
  </div>
</div>"""

    # 3. CONTROL ECONÓMICO
    eco_html = ""
    for ap in eco.get("aprobados_semana", []):
        eco_html += f"""<div class="eco-card" style="border-color:#27ae6044;background:#f0faf5;border-left:5px solid #27ae60;">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
    {badge('APROBADO Y CERRADO', '#27ae60')}
    <span style="font-size:12px;font-weight:800;">{ap.get('contrata','')}</span>
  </div>
  <div style="font-size:11.5px;color:#374151;margin-bottom:5px;">{ap.get('detalle','')}</div>
  <div style="background:#e8f5e9;border:1px solid #27ae6033;border-radius:4px;padding:5px 9px;font-size:11px;color:#1b5e20;font-weight:700;">
    &#9888; Valentina: {ap.get('nota_valentina','')}
  </div>
</div>"""
    for pf in eco.get("pendientes_firma", []):
        eco_html += f"""<div class="eco-card" style="border-color:#e67e2244;background:#fff8e1;border-left:5px solid #e67e22;">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
    {badge('PENDIENTE FIRMA', '#e67e22')}
    <span style="font-size:12px;font-weight:800;">{pf.get('contrata','')}</span>
  </div>
  <div style="font-size:11.5px;color:#374151;margin-bottom:4px;">{pf.get('detalle','')}</div>
  <div style="font-size:11px;color:#e67e22;font-weight:700;">&#9654; {pf.get('accion','')}</div>
</div>"""

    eco_mod_rows = ""
    for m in eco.get("modificaciones_proyecto_semana", []):
        est_m = m.get("estado", "")
        c_m = "#27ae60" if "EJECUTADO" in est_m or "CERRADO" in est_m else "#e67e22"
        eco_mod_rows += f"""<tr>
  <td style="font-weight:700;color:#0f3460;">{m.get('codigo','')}</td>
  <td>{m.get('elemento','')}</td>
  <td style="color:#475569;">{m.get('impacto','')}</td>
  <td><span style="background:{c_m};color:#fff;font-size:9px;font-weight:700;padding:2px 7px;border-radius:8px;">{est_m}</span></td>
</tr>"""

    # 4. INCIDENCIAS
    inc_rows = ""
    estado_col = {"ACTIVO CRÍTICO": "#c0392b", "ACTIVO TÉCNICO": "#e67e22",
                  "PAUSADO": "#7b1fa2", "RESUELTO": "#27ae60", "CERRADA": "#27ae60"}
    for i in incs:
        est_i = i.get("estado", "")
        c_i = estado_col.get(est_i, "#94a3b8")
        inc_rows += f"""<tr>
  <td style="font-weight:700;color:#0f3460;">{i.get('codigo','')}</td>
  <td>{i.get('descripcion','')}</td>
  <td><span style="background:{c_i};color:#fff;font-size:9px;font-weight:700;padding:2px 7px;border-radius:8px;">{est_i}</span></td>
  <td style="color:#475569;">{i.get('responsable','—')}</td>
  <td style="color:#c0392b;font-weight:700;">{i.get('deadline_nuevo') or '—'}</td>
</tr>"""

    # 5. PLANIFICACIÓN S12
    obj_html = "".join(
        f'<div style="display:flex;gap:8px;padding:5px 0;border-bottom:1px solid #f0f2f8;font-size:11.5px;">'
        f'<span style="color:#e94560;font-weight:800;flex-shrink:0;">{i+1}.</span>'
        f'<span>{o}</span></div>'
        for i, o in enumerate(plan.get("objetivos_criticos", []))
    )
    entradas_rows = "".join(
        f'<tr><td style="font-weight:700;">{e.get("gremio","")}</td>'
        f'<td style="color:#0f3460;font-weight:600;">{e.get("dia","")}</td>'
        f'<td>{e.get("objetivo","")}</td></tr>'
        for e in plan.get("entradas_obra", [])
    )
    coord_html = "".join(
        f'<div style="padding:5px 0;border-bottom:1px solid #f0f2f8;font-size:11.5px;">'
        f'<span style="color:#e94560;margin-right:6px;">&#9654;</span>{c}</div>'
        for c in plan.get("coordinacion_gremios", [])
    )

    # 6. HITOS Y DESVIACIONES
    hitos_html = "".join(
        f'<div class="hito-item"><span style="color:#27ae60;font-size:14px;flex-shrink:0;">&#10003;</span><span>{h}</span></div>'
        for h in hitos
    )
    desv_html = "".join(
        f'<div class="desv-item"><span style="color:#c0392b;font-size:14px;flex-shrink:0;">&#9888;</span><span>{d}</span></div>'
        for d in desvs
    )
    today = date.today().strftime("%d/%m/%Y")
    estado_gantt = REC.get("estado_gantt", "EN PLAZO")
    eg_col = "#c0392b" if "ALERTA" in estado_gantt else ("#27ae60" if "PLAZO" in estado_gantt else "#e67e22")

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<title>Acta Semanal S11/2026 — Nine Fitness Brescia 19</title>
<style>{CSS}</style></head><body><div class="doc">

<div class="hdr">
  <div class="hdr-tag">Nine Fitness Group S.L. &middot; PMO Brescia 19 &middot; Acta Semanal de Obra</div>
  <div class="hdr-t">ACTA SEMANAL S11 &nbsp;&middot;&nbsp; 01–05 JUNIO 2026</div>
  <div class="hdr-s">Calle Brescia 19, 28028 Madrid &nbsp;|&nbsp; Redactor: Darío A. López (Director de Obra) &nbsp;|&nbsp; Para distribución a Contratas y Dirección</div>
  <div class="hdr-grid">
    <div class="hdr-kpi"><div class="hdr-kpi-l">Referencia</div><div class="hdr-kpi-v">ACT-SEM-S11-2026</div></div>
    <div class="hdr-kpi"><div class="hdr-kpi-l">Semana / Año</div><div class="hdr-kpi-v">S11 / 2026</div></div>
    <div class="hdr-kpi"><div class="hdr-kpi-l">Estado Gantt</div><div class="hdr-kpi-v" style="color:{eg_col};">{estado_gantt}</div></div>
    <div class="hdr-kpi"><div class="hdr-kpi-l">Apertura objetivo</div><div class="hdr-kpi-v">3–5 Agosto 2026</div></div>
  </div>
  <div class="accent"></div>
</div>

<div class="body">

  <div class="sec">
    <div class="sh"><span>&#128203;</span><span class="st">1. Resumen Ejecutivo y Estado Global</span></div>
    <div class="resumen">{REC.get('resumen_ejecutivo','')}</div>
  </div>

  <div class="sec">
    <div class="sh"><span>&#128680;</span><span class="st">Alertas Críticas de la Semana</span></div>
    {alertas_html}
  </div>

  <div class="sec">
    <div class="sh"><span>&#128296;</span><span class="st">2. Avance por Contratas y Estado de Tareas (Gantt S11)</span></div>
    {contratas_html}
  </div>

  <div class="sec">
    <div class="sh"><span>&#128176;</span><span class="st">3. Control Económico y Administrativo</span></div>
    {eco_html}
    <div style="margin-top:10px;">
      <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#1a1a2e;margin-bottom:6px;">Modificaciones de Proyecto con Impacto Económico</div>
      <table class="tbl">
        <thead><tr><th width="120">Código</th><th width="200">Elemento</th><th>Impacto</th><th width="100">Estado</th></tr></thead>
        <tbody>{eco_mod_rows}</tbody>
      </table>
    </div>
  </div>

  <div class="sec">
    <div class="sh"><span>&#9888;&#65039;</span><span class="st">4. Incidencias, Requerimientos y Bloqueos</span></div>
    <table class="tbl">
      <thead><tr><th width="100">Código</th><th>Descripción</th><th width="110">Estado</th><th width="120">Responsable</th><th width="85">Deadline</th></tr></thead>
      <tbody>{inc_rows}</tbody>
    </table>
  </div>

  <div class="sec">
    <div class="sh"><span>&#128197;</span><span class="st">5. Planificación Semana S12 (09–13 Junio) — Actualización Gantt</span></div>
    <div style="margin-bottom:12px;">
      <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#1a1a2e;margin-bottom:6px;">Objetivos Críticos S12</div>
      {obj_html}
    </div>
    <div style="margin-bottom:12px;">
      <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#1a1a2e;margin-bottom:6px;">Entradas en Obra</div>
      <table class="tbl">
        <thead><tr><th>Gremio / Empresa</th><th width="120">Día de Entrada</th><th>Objetivo Semana</th></tr></thead>
        <tbody>{entradas_rows}</tbody>
      </table>
    </div>
    <div style="margin-bottom:12px;">
      <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#1a1a2e;margin-bottom:6px;">Coordinación de Gremios</div>
      {coord_html}
    </div>
    <div style="background:#fdf2f2;border:1px solid #e9454044;border-radius:7px;padding:10px 14px;">
      <span style="font-size:11px;font-weight:800;color:#c0392b;">&#128197; CONVOCATORIA REUNIÓN DE OBRA S12:</span>
      <span style="font-size:12px;color:#1a1a2e;font-weight:700;margin-left:8px;">{plan.get('reunion_semanal','—')}</span>
      <div style="font-size:10.5px;color:#7f8c8d;margin-top:3px;">Asistencia OBLIGATORIA para todas las contratas activas.</div>
    </div>
  </div>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;" class="sec">
    <div>
      <div class="sh"><span>&#127942;</span><span class="st">Hitos Cumplidos S11</span></div>
      <div style="background:#f0faf5;border:1px solid #27ae6033;border-radius:8px;padding:10px 14px;">{hitos_html}</div>
    </div>
    <div>
      <div class="sh"><span>&#9888;</span><span class="st">Desviaciones y Alertas Activas</span></div>
      <div style="background:#fdf2f2;border:1px solid #c0392b33;border-radius:8px;padding:10px 14px;">{desv_html}</div>
    </div>
  </div>

</div>
<div class="ftr">
  <div>NINE FITNESS GROUP S.L. &middot; Calle Brescia 19, 28028 Madrid &middot; Distribución: Contratas + Dirección Interna &middot; Confidencial</div>
  <div>Director de Obra: <b>Darío A. López</b> &nbsp;&middot;&nbsp; Arquitecto: <b>Ángel Rodríguez Martínez-Conde (COAM 12399)</b></div>
  <div>Ref: <b>ACT-SEM-S11-2026</b> &nbsp;&middot;&nbsp; <b>{today}</b></div>
</div>
</div></body></html>"""


if __name__ == "__main__":
    html = build()
    with tempfile.TemporaryDirectory() as tmp:
        tmp  = Path(tmp)
        hp   = tmp / "acta_semanal.html"
        hp.write_text(html, encoding="utf-8")
        pdf  = ESCRITORIO / "ACTA_SEMANAL_S11_2026.pdf"
        r    = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
             "--disable-extensions", "--print-to-pdf-no-header",
             f"--print-to-pdf={pdf}", hp.as_uri()],
            capture_output=True, text=True, timeout=45)
        if pdf.exists() and pdf.stat().st_size > 8000:
            print(f"OK  {pdf.name}  ({pdf.stat().st_size // 1024} KB)")
        else:
            print("ERROR:", r.stderr[:400])
