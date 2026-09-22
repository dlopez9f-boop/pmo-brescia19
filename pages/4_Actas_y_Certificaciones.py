#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pages/4_Actas_y_Certificaciones.py
Gestión de actas diarias, semanales, generador de actas y certificaciones de avance.
Backend: SQLite via db.py
"""
import json
import re
import base64
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date, datetime
from _auth import require_auth

st.set_page_config(page_title="Actas · PMO", page_icon="📝", layout="wide")
require_auth()

from db import (
    init_db, backend_info, semana_obra,
    list_actas_diarias, upsert_acta_diaria, delete_acta_diaria,
    list_actas_semanales, upsert_acta_semanal, delete_acta_semanal,
    consolidar_semana,
    list_registro_actas, upsert_registro_acta, delete_registro_acta,
)
init_db()

NAVY = "#0B1F3A"
GOLD = "#C9A96E"

st.markdown(
    f"<div style='background:{NAVY};padding:12px 20px;border-bottom:2px solid {GOLD};"
    f"margin:-1rem -1rem 1rem -1rem;display:flex;align-items:center;gap:12px'>"
    f"<span style='color:{GOLD};font-weight:700;font-size:15px;letter-spacing:.08em'>"
    f"📝 ACTAS Y CERTIFICACIONES</span>"
    f"<span style='color:#3a5a80;font-size:11px'>Backend: {backend_info()}</span>"
    f"</div>",
    unsafe_allow_html=True,
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .acta-card{border-left:4px solid #e94560;padding:10px 14px;background:#1a1f2e;
             border-radius:0 8px 8px 0;margin-bottom:8px}
  .acta-card.urgente{border-left-color:#c0392b}
  .badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700}
  .b-red{background:#3d1515;color:#e74c3c} .b-amber{background:#3d2e0a;color:#f39c12}
  .b-green{background:#0d2e1a;color:#27ae60} .b-blue{background:#0d1f3d;color:#3498db}
</style>
""", unsafe_allow_html=True)

# ── HELPERS ───────────────────────────────────────────────────────────────────
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
    return d.strftime('%d/%m/%Y')

GREMIO_KW = {
    "⚡ Electricidad":  ["luis","elecrea","cuadro","cableado","iga","diferencial"],
    "❄️ Climatización": ["jose","nacho","servitec","conducto","daikin","clima","difusor"],
    "🧱 Albañilería":   ["munir","ziad","mohamed","solera","tabiq","escombro","pladur"],
    "🪵 Carpintería":   ["josevi","upn","espejo","carpintería","viga","estructura"],
    "🔥 PCI":           ["leo","troser","extinción","pci","rociador"],
    "♿ Accesibilidad": ["pedro","hersan","salvaescaleras","pmr"],
}
INC_KW    = ["problema","retraso","falta","pendiente urgente","alerta","sin material","parado","bloqueado"]
AGENDA_KW = ["mañana","próximo día","08:","09:","10:","reunión"]
_RE_HORA  = re.compile(r'\b(\d{1,2}[:.h]\d{2})\b')

def parsear(texto: str) -> dict:
    lines  = [l.strip() for l in texto.splitlines() if l.strip()]
    secs   = {g: [] for g in GREMIO_KW}
    incs, avances, agenda = [], [], []
    for line in lines:
        ll = line.lower()
        gremio    = next((g for g, kws in GREMIO_KW.items() if any(k in ll for k in kws)), None)
        is_inc    = any(k in ll for k in INC_KW)
        hora_m    = _RE_HORA.search(ll)
        is_agenda = bool(hora_m) or any(k in ll for k in AGENDA_KW)
        if gremio:
            secs[gremio].append(line)
            if is_inc:
                incs.append({"gremio": gremio, "descripcion": line, "prioridad": "alta"})
            else:
                avances.append({"gremio": gremio, "descripcion": line})
        if is_agenda:
            agenda.append({"hora": hora_m.group(1) if hora_m else "—", "evento": line})
    return {
        "incidencias":        incs,
        "avances":            avances,
        "agenda":             agenda,
        "intervenciones":     {g: "\n".join(v) for g, v in secs.items() if v},
        "gremios_incidencia": list(dict.fromkeys(i["gremio"] for i in incs)),
        "agenda_proxima":     {"items": agenda, "texto": "\n".join(f"{a['hora']} — {a['evento']}" for a in agenda)},
    }

def _imgs_b64(files: list) -> list:
    result = []
    for f in (files or []):
        if f is None: continue
        b64  = base64.b64encode(f.read()).decode()
        result.append({"src": f"data:{f.type or 'image/jpeg'};base64,{b64}", "caption": f.name})
    return result

def _parse_json_field(acta, key):
    v = acta.get(key) or []
    if isinstance(v, str):
        try: v = json.loads(v)
        except: v = []
    return v if isinstance(v, list) else []

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

def html_acta_diaria(acta: dict, imagenes=None) -> str:
    try: fecha_str = fecha_es(acta["fecha"], "largo")
    except: fecha_str = acta.get("fecha", "")

    secs = acta.get("intervenciones") or {}
    if isinstance(secs, str):
        try: secs = json.loads(secs)
        except: secs = {}
    sec_html = "".join(
        f'<div style="margin-bottom:10px">'
        f'<div style="font-size:11px;font-weight:700;color:#0f3460;text-transform:uppercase;margin-bottom:4px">{g}</div>'
        f'<div style="font-size:12px;padding-left:10px;border-left:3px solid #e2e8f0;color:#374151;line-height:1.6">'
        f'{str(c).replace(chr(10),"<br>")}</div></div>'
        for g, c in secs.items() if c
    )
    incs = _parse_json_field(acta, "incidencias")
    inc_html = "".join(
        f'<div style="background:#fdf2f2;border-left:3px solid #e94560;padding:7px 10px;'
        f'margin-bottom:5px;border-radius:0 4px 4px 0;font-size:12px;color:#c0392b">⚠ '
        f'{i.get("descripcion",str(i)) if isinstance(i,dict) else str(i)}</div>'
        for i in incs
    )
    ag_items  = _parse_agenda(acta)
    ag_rows   = "".join(
        f'<div style="display:flex;gap:14px;padding:8px 0;border-bottom:1px solid #f0f2f8">'
        f'<span style="font-size:11px;font-weight:800;color:#e94560;min-width:52px">{it["hora"]}</span>'
        f'<span style="font-size:12px;color:#374151">{it["evento"]}</span></div>'
        for it in ag_items
    )
    ag_html = (f'<div style="margin-top:10px">{ag_rows}</div>' if ag_rows else "")
    _est = {"borrador":"background:#eef2ff;color:#3730a3","revisado":"background:#fff8e1;color:#e65100",
            "firmado":"background:#f0faf4;color:#27ae60"}.get(acta.get("estado","borrador"),"background:#eee;color:#333")
    imgs_html = ""
    if imagenes:
        items_html = "".join(
            f'<div style="border-radius:8px;overflow:hidden;aspect-ratio:4/3;background:#f8f9ff">'
            f'<img src="{img["src"]}" style="width:100%;height:100%;object-fit:cover"></div>'
            for img in imagenes[:3]
        )
        imgs_html = f'<div style="margin-top:14px"><div style="font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.8px;color:#1a1a2e;margin-bottom:8px;padding-bottom:6px;border-bottom:2px solid #e94560">📸 Registro Fotográfico</div><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">{items_html}</div></div>'

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<style>*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:'Helvetica Neue',Arial,sans-serif;background:#f0f2f8;font-size:13px}}
.doc{{max-width:820px;margin:16px auto;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 3px 20px rgba(0,0,0,.1)}}
.hdr{{background:linear-gradient(135deg,#1a1a2e,#0f3460);color:#fff;padding:20px 28px;position:relative}}
.accent{{position:absolute;bottom:0;left:0;right:0;height:3px;background:#e94560}}
.meta{{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid #e2e8f0;background:#fafbff}}
.mc{{padding:11px 16px;border-right:1px solid #e2e8f0}}.mc:last-child{{border-right:none}}
.ml{{font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#94a3b8;font-weight:600;margin-bottom:3px}}
.mv{{font-size:13px;font-weight:700}}.body{{padding:22px 28px}}
.sh{{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.8px;color:#1a1a2e;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #e94560}}
.sec{{margin-bottom:20px}}.ftr{{background:#1a1a2e;padding:10px 28px;font-size:9px;color:rgba(255,255,255,.4);display:flex;justify-content:space-between}}</style>
</head><body><div class="doc">
<div class="hdr"><div style="font-size:20px;font-weight:900">📋 {fecha_str}</div>
<div style="font-size:11px;opacity:.65;margin-top:4px">{acta.get("resumen","")}</div><div class="accent"></div></div>
<div class="meta">
<div class="mc"><div class="ml">Referencia</div><div class="mv" style="font-size:11px">{acta.get("id","")}</div></div>
<div class="mc"><div class="ml">Semana</div><div class="mv">S{acta.get("semana_obra","")}</div></div>
<div class="mc"><div class="ml">Prioridad</div><div class="mv">{acta.get("prioridad","normal").title()}</div></div>
<div class="mc"><div class="ml">Estado</div><div class="mv"><span style="padding:2px 8px;border-radius:20px;font-size:10px;font-weight:700;{_est}">{acta.get("estado","borrador").title()}</span></div></div>
</div>
<div class="body">
{f'<div class="sec"><div class="sh">⚠ Incidencias</div>{inc_html}</div>' if inc_html else ""}
{f'<div class="sec"><div class="sh">🔧 Intervenciones</div>{sec_html}</div>' if sec_html else ""}
{f'<div class="sec"><div class="sh">📅 Agenda Próxima Jornada</div>{ag_html}</div>' if ag_html else ""}
{imgs_html}
</div>
<div class="ftr"><span>Nine Fitness Group S.L.</span><span>Dir. Obra: Darío A. López · Confidencial</span></div>
</div></body></html>"""

def html_semanal_completo(acta_sem: dict, diarias: list) -> str:
    sem    = acta_sem.get("semana_obra","?")
    fechas = " · ".join(datetime.fromisoformat(a["fecha"]).strftime("%d/%m") for a in diarias if "fecha" in a)
    bloques = ""
    for a in diarias:
        dia   = fecha_es(a["fecha"], "corto")
        secs  = a.get("intervenciones") or {}
        if isinstance(secs, str):
            try: secs = json.loads(secs)
            except: secs = {}
        sec_html = "".join(
            f'<div style="margin-bottom:6px"><b style="font-size:11px;color:#0f3460">{g}</b>'
            f'<div style="font-size:11px;padding-left:8px;border-left:2px solid #e2e6f0;color:#333">'
            f'{str(c).replace(chr(10),"<br>")}</div></div>'
            for g, c in secs.items() if c
        )
        bloques += (
            f'<div style="border-left:4px solid #e94560;padding:12px 16px;margin-bottom:12px;'
            f'background:#fff;border-radius:0 8px 8px 0;box-shadow:0 1px 4px rgba(0,0,0,.06)">'
            f'<b style="font-size:14px;color:#1a1a2e">📋 {dia}</b>'
            f'<div style="font-size:12px;color:#555;margin:5px 0 7px">{a.get("resumen","")}</div>'
            f'{sec_html}</div>'
        )
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<style>body{{font-family:'Helvetica Neue',Arial,sans-serif;background:#fff;color:#1a1a2e;font-size:12px;margin:16px}}</style>
</head><body>
<div style="background:linear-gradient(135deg,#1a1a2e,#0f3460);color:#fff;padding:18px 22px;border-radius:6px;margin-bottom:16px">
<div style="font-size:15pt;font-weight:900">ACTA SEMANAL EJECUTIVA — SEMANA {sem}</div>
<div style="font-size:9pt;opacity:.7;margin-top:3px">Nine Fitness Group · {fechas} · Dir. Obra: Darío A. López</div></div>
{bloques}
<div style="text-align:center;font-size:8pt;color:#bbb;margin-top:16px;border-top:1px solid #e2e6f0;padding-top:8px">
Nine Fitness Group S.L. · Ref: {acta_sem.get("id","")} · Confidencial</div></body></html>"""


# ════════════════════════════════════════════════════════════════════════════
# TABS PRINCIPALES
# ════════════════════════════════════════════════════════════════════════════
tab_dia, tab_sem, tab_gen, tab_cert = st.tabs([
    "📋 Actas Diarias",
    "📁 Actas Semanales",
    "✍️ Generador de Actas",
    "📊 Certificaciones",
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — ACTAS DIARIAS
# ─────────────────────────────────────────────────────────────────────────────
with tab_dia:
    sub_hist, sub_nueva, sub_rapida = st.tabs(["📚 Histórico", "✍️ Nueva", "⚡ Ingesta Rápida"])

    with sub_hist:
        fc1, fc2, fc3, fc4 = st.columns([1.2, 1.2, 1, 1])
        with fc1: f_desde = st.date_input("Desde", value=date(2026, 1, 1))
        with fc2: f_hasta = st.date_input("Hasta", value=date.today())
        with fc3: f_prio  = st.selectbox("Prioridad", ["todas","urgente","alta","normal"])
        with fc4: f_est   = st.selectbox("Estado", ["todos","borrador","revisado","firmado"])

        actas = list_actas_diarias(f_desde.isoformat(), f_hasta.isoformat(), f_prio, f_est)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Actas", len(actas))
        k2.metric("Incidencias", sum(len(_parse_json_field(a,"incidencias")) for a in actas))
        k3.metric("Urgentes", sum(1 for a in actas if a.get("prioridad") == "urgente"))
        k4.metric("Firmadas", sum(1 for a in actas if a.get("estado") == "firmado"))
        st.divider()

        col_lista, col_visor = st.columns([1, 1.6])
        with col_lista:
            if not actas:
                st.info("Sin actas en el rango.")
            for acta in actas:
                _fstr = datetime.fromisoformat(acta["fecha"]).strftime("%a %d/%m/%Y").capitalize()
                _incs = _parse_json_field(acta, "incidencias")
                if st.button(f"**{_fstr}** · S{acta.get('semana_obra','?')} {'⚠' if _incs else ''}",
                             key=f"sel_{acta['id']}", use_container_width=True):
                    st.session_state["acta_vista"] = acta

        with col_visor:
            acta_v = st.session_state.get("acta_vista")
            if not acta_v:
                st.info("Selecciona un acta de la lista.")
            else:
                components.html(html_acta_diaria(acta_v), height=560, scrolling=True)
                dl1, dl2, dl3 = st.columns(3)
                with dl1:
                    st.download_button("⬇️ HTML", data=html_acta_diaria(acta_v).encode("utf-8"),
                                       file_name=f"ACTA_{acta_v['id']}.html", mime="text/html",
                                       use_container_width=True, type="primary")
                with dl2:
                    nuevo_est = st.selectbox("Estado", ["borrador","revisado","firmado"],
                                             index=["borrador","revisado","firmado"].index(acta_v.get("estado","borrador")),
                                             key="chg_est")
                with dl3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("💾 Actualizar", use_container_width=True, key="btn_upd_est"):
                        acta_v["estado"] = nuevo_est
                        upsert_acta_diaria(acta_v)
                        st.session_state["acta_vista"] = acta_v
                        st.success("Estado actualizado.")
                        st.rerun()
                if st.button("🗑️ Eliminar acta", key="btn_del_acta", type="secondary"):
                    delete_acta_diaria(acta_v["id"])
                    del st.session_state["acta_vista"]
                    st.rerun()

    with sub_nueva:
        col_form, col_prev = st.columns([1, 1.2], gap="large")
        with col_form:
            with st.form("form_nueva_acta", clear_on_submit=True):
                f_fecha   = st.date_input("Fecha", value=date.today())
                texto_raw = st.text_area("Notas de campo", height=220,
                    placeholder="- Luis Elecrea: cuadro pendiente.\n- Munir: solera planta baja.\n- Reunión mañana 09:00.")
                resumen_m = st.text_input("Resumen ejecutivo (opcional)")
                fotos     = st.file_uploader("📸 Fotos (máx. 3)", type=["jpg","jpeg","png"],
                                             accept_multiple_files=True, key="fotos_nueva")
                c1, c2   = st.columns(2)
                with c1: prioridad = st.selectbox("Prioridad", ["normal","alta","urgente"])
                with c2: estado    = st.selectbox("Estado",    ["borrador","revisado","firmado"])
                guardar = st.form_submit_button("💾 Guardar", use_container_width=True, type="primary")

            if guardar:
                if not texto_raw.strip():
                    st.warning("Escribe las notas antes de guardar.")
                else:
                    p   = parsear(texto_raw)
                    imgs = _imgs_b64(fotos[:3] if fotos else [])
                    _id  = f"ACT-{f_fecha.strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
                    nueva = {
                        "id": _id, "fecha": f_fecha.isoformat(),
                        "semana_obra": semana_obra(f_fecha),
                        "resumen": resumen_m.strip() or f"Acta S{semana_obra(f_fecha)} · {f_fecha.strftime('%d/%m/%Y')}",
                        "intervenciones":     json.dumps(p["intervenciones"],     ensure_ascii=False),
                        "agenda_proxima":     json.dumps(p["agenda_proxima"],     ensure_ascii=False),
                        "incidencias":        json.dumps(p["incidencias"],        ensure_ascii=False),
                        "gremios_incidencia": json.dumps(p["gremios_incidencia"], ensure_ascii=False),
                        "prioridad": prioridad, "estado": estado,
                        "creado_por": "Darío A. López",
                    }
                    upsert_acta_diaria(nueva)
                    st.session_state["acta_preview_nueva"] = nueva
                    st.session_state["acta_preview_imgs"]  = imgs
                    st.success(f"✅ Acta **{_id}** guardada.")
                    st.rerun()

        with col_prev:
            st.markdown("### 🔍 Preview")
            prev = st.session_state.get("acta_preview_nueva")
            if prev:
                components.html(html_acta_diaria(prev, st.session_state.get("acta_preview_imgs")), height=500, scrolling=True)
            else:
                st.info("El preview aparecerá aquí tras guardar.")

    with sub_rapida:
        st.caption("Pega notas de voz o texto libre. El parser detecta gremios, incidencias y agenda.")
        col_in, col_out = st.columns([1, 1], gap="large")
        with col_in:
            ir_fecha  = st.date_input("Fecha", value=date.today(), key="ir_fecha")
            ir_texto  = st.text_area("Notas de campo", height=300, key="ir_texto",
                placeholder="- Luis Elecrea: baja operario, jornada improductiva.\n- Munir: replanteo tabique 5.50m.\n- Reunión mañana 08:30.")
            ir_fotos  = st.file_uploader("📸 Fotos", type=["jpg","jpeg","png"], accept_multiple_files=True, key="ir_fotos")
            ir_prio   = st.selectbox("Prioridad", ["normal","alta","urgente"], key="ir_prio")
            procesar  = st.button("🚀 Procesar y Publicar", use_container_width=True, type="primary", key="ir_btn")

        with col_out:
            if procesar:
                if not ir_texto.strip():
                    st.warning("Escribe las notas antes de procesar.")
                else:
                    p    = parsear(ir_texto)
                    imgs = _imgs_b64(ir_fotos[:3] if ir_fotos else [])
                    _id  = f"ACT-{ir_fecha.strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
                    acta = {
                        "id": _id, "fecha": ir_fecha.isoformat(),
                        "semana_obra": semana_obra(ir_fecha),
                        "resumen": f"Ingesta rápida · {ir_fecha.strftime('%d/%m/%Y')}",
                        "intervenciones":     json.dumps(p["intervenciones"],     ensure_ascii=False),
                        "agenda_proxima":     json.dumps(p["agenda_proxima"],     ensure_ascii=False),
                        "incidencias":        json.dumps([i["descripcion"] for i in p["incidencias"]], ensure_ascii=False),
                        "gremios_incidencia": json.dumps(p["gremios_incidencia"], ensure_ascii=False),
                        "prioridad": ir_prio, "estado": "borrador",
                        "creado_por": "Darío A. López",
                    }
                    upsert_acta_diaria(acta)
                    st.session_state["ir_resultado"] = p
                    st.session_state["ir_acta"]      = acta
                    st.session_state["ir_imgs"]       = imgs
                    st.success(f"✅ **{_id}** guardada.")

            res = st.session_state.get("ir_resultado")
            if res:
                if res["incidencias"]:
                    st.markdown("**⚠️ Incidencias**")
                    for inc in res["incidencias"]:
                        st.markdown(
                            f'<div style="border-left:3px solid #e74c3c;padding:6px 10px;'
                            f'background:#1a1a2e;border-radius:0 4px 4px 0;margin-bottom:4px;font-size:12px">'
                            f'<b>{inc["gremio"]}</b> · {inc["descripcion"]}</div>',
                            unsafe_allow_html=True)
                if res["avances"]:
                    st.markdown("**✅ Avances**")
                    for av in res["avances"]:
                        st.markdown(
                            f'<div style="border-left:3px solid #2ecc71;padding:6px 10px;'
                            f'background:#1a1a2e;border-radius:0 4px 4px 0;margin-bottom:4px;font-size:12px">'
                            f'<b>{av["gremio"]}</b> · {av["descripcion"]}</div>',
                            unsafe_allow_html=True)
                if res["agenda"]:
                    st.markdown("**📅 Agenda**")
                    for ag in res["agenda"]:
                        st.markdown(f'`{ag["hora"]}` — {ag["evento"]}')
                if st.session_state.get("ir_acta"):
                    st.divider()
                    components.html(
                        html_acta_diaria(st.session_state["ir_acta"], st.session_state.get("ir_imgs")),
                        height=400, scrolling=True)
            else:
                st.info("El análisis aparecerá aquí tras procesar.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — ACTAS SEMANALES
# ─────────────────────────────────────────────────────────────────────────────
with tab_sem:
    sub_gen, sub_hist_sem = st.tabs(["⚙️ Generar", "📚 Historial"])

    with sub_gen:
        cs1, cs2 = st.columns([1, 2])
        with cs1:
            sem_sel = st.number_input("Semana de obra", min_value=1, max_value=60,
                                      value=semana_obra(date.today()))
            gen_btn = st.button("⚙️ Consolidar semana", use_container_width=True, type="primary")

        if gen_btn:
            borrador = consolidar_semana(sem_sel)
            if borrador:
                st.session_state["borrador_semanal"] = borrador
                n = len([i for i in borrador.get("actas_diarias_ids","").split(",") if i])
                st.success(f"Borrador S{sem_sel} con {n} actas diarias generado.")
            else:
                st.warning(f"Sin actas diarias para la semana {sem_sel}.")

        if "borrador_semanal" in st.session_state:
            b = st.session_state["borrador_semanal"]
            st.divider()
            st.markdown(f"#### Borrador: {b.get('semana_ano','')} ({b.get('fecha_inicio','')} → {b.get('fecha_fin','')})")
            col_ed, col_pv = st.columns([1, 1.3])
            with col_ed:
                resumen_edit = st.text_area("Resumen ejecutivo", value=b.get("resumen_ejecutivo",""), height=150)
                estado_ap    = st.selectbox("Estado", ["borrador","pendiente_firma","aprobado"])
                aprobado_por = st.text_input("Aprobado por", value="Darío A. López")
                cg, cd = st.columns(2)
                ids_list    = [i for i in b.get("actas_diarias_ids","").split(",") if i]
                diarias_sem = [a for a in list_actas_diarias(b["fecha_inicio"], b["fecha_fin"]) if a["id"] in ids_list]
                html_rep    = html_semanal_completo(b, diarias_sem)
                with cg:
                    if st.button("💾 Guardar acta semanal", use_container_width=True, type="primary"):
                        b["resumen_ejecutivo"] = resumen_edit
                        b["estado_aprobacion"] = estado_ap
                        b["aprobado_por"]      = aprobado_por
                        upsert_acta_semanal(b)
                        st.success(f"✅ {b['id']} guardada.")
                        del st.session_state["borrador_semanal"]
                        st.rerun()
                with cd:
                    st.download_button("⬇️ HTML", data=html_rep.encode("utf-8"),
                                       file_name=f"ACTA_{b['id']}.html", mime="text/html",
                                       use_container_width=True)
            with col_pv:
                components.html(html_rep, height=500, scrolling=True)

    with sub_hist_sem:
        sem_list = list_actas_semanales()
        if not sem_list:
            st.info("No hay actas semanales guardadas.")
        for s in sem_list:
            ea  = s.get("estado_aprobacion","borrador")
            _ec = {"borrador":"b-blue","pendiente_firma":"b-amber","aprobado":"b-green"}.get(ea,"b-blue")
            ids_list = [i for i in (s.get("actas_diarias_ids") or "").split(",") if i]
            with st.expander(f"📅 {s.get('semana_ano','')} · {s.get('fecha_inicio','')} → {s.get('fecha_fin','')}"):
                st.markdown(f'<span class="badge {_ec}">{ea.replace("_"," ").title()}</span>'
                            f' &nbsp; Por: **{s.get("aprobado_por","—")}**', unsafe_allow_html=True)
                st.markdown(s.get("resumen_ejecutivo",""))
                c1, c2 = st.columns(2)
                with c1:
                    diarias_p = [a for a in list_actas_diarias(s["fecha_inicio"], s["fecha_fin"]) if a["id"] in ids_list]
                    html_dl   = html_semanal_completo(s, diarias_p)
                    st.download_button("⬇️ Descargar HTML", data=html_dl.encode("utf-8"),
                                       file_name=f"ACTA_{s['id']}.html", mime="text/html",
                                       use_container_width=True, key=f"dl_sem_{s['id']}")
                with c2:
                    if st.button("🗑️ Eliminar", key=f"del_sem_{s['id']}", use_container_width=True, type="secondary"):
                        delete_acta_semanal(s["id"]); st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — GENERADOR DE ACTAS (Reuniones / Visitas de obra)
# ─────────────────────────────────────────────────────────────────────────────
with tab_gen:
    st.caption("Genera actas formales de reunión o visita de obra con estructura fija.")

    OBRAS_GEN    = ["Nine Club Chamartín", "Red de Centros", "Otro"]
    TIPOS_ACTA   = ["Visita de obra", "Reunión de coordinación", "Reunión de proyecto", "Acta de decisión"]
    ESTADOS_GEN  = ["en_curso","alerta","critico","completado","borrador"]

    actas_reg = list_registro_actas() if callable(list_registro_actas) else []
    acta_ids  = [a.get("id","") for a in actas_reg]

    col_form_g, col_prev_g = st.columns([1, 1.2], gap="large")
    with col_form_g:
        sel_id = st.selectbox("Cargar acta existente (o 'Nueva')", ["Nueva"] + acta_ids, key="gen_sel")

        if sel_id != "Nueva" and callable(list_registro_actas):
            try:
                from db import get_registro_acta
                acta_cargada = get_registro_acta(sel_id) or {}
            except Exception:
                acta_cargada = {}
        else:
            acta_cargada = {}

        with st.form("form_gen_acta"):
            st.markdown("#### 📌 Metadatos")
            g1, g2 = st.columns(2)
            with g1:
                g_fecha   = st.date_input("Fecha", value=date.today())
                g_obra    = st.selectbox("Proyecto / Obra", OBRAS_GEN,
                    index=OBRAS_GEN.index(acta_cargada.get("obra","Nine Club Chamartín")) if acta_cargada.get("obra") in OBRAS_GEN else 0)
                g_tipo    = st.selectbox("Tipo de acta", TIPOS_ACTA)
            with g2:
                g_estado  = st.selectbox("Estado general", ESTADOS_GEN)
                g_asist   = st.text_area("Asistentes (uno por línea)", height=80,
                    value=acta_cargada.get("asistentes",""))
                g_lugar   = st.text_input("Lugar", value=acta_cargada.get("lugar",""))

            st.markdown("#### 📝 Incidencias / Alertas")
            df_incs_init = pd.DataFrame([{"gremio":"","descripcion":"","prioridad":"alta"}])
            df_incs_ed = st.data_editor(df_incs_init, num_rows="dynamic", use_container_width=True,
                key="gen_incs",
                column_config={
                    "prioridad": st.column_config.SelectboxColumn("Prioridad", options=["baja","media","alta","critica"]),
                })

            st.markdown("#### ✅ Acuerdos y Compromisos")
            df_ac_init = pd.DataFrame([{"acuerdo":"","responsable":"","plazo":""}])
            df_ac_ed = st.data_editor(df_ac_init, num_rows="dynamic", use_container_width=True, key="gen_ac")

            st.markdown("#### 📅 Agenda próxima")
            g_agenda = st.text_area("Puntos de agenda (texto libre)", height=80)

            guardar_g = st.form_submit_button("💾 Guardar Acta", use_container_width=True, type="primary")

        if guardar_g:
            _id_g = acta_cargada.get("id") or f"ACT-GEN-{g_fecha.strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
            registro = {
                "id":          _id_g,
                "fecha":       g_fecha.isoformat(),
                "semana_obra": semana_obra(g_fecha),
                "obra":        g_obra,
                "tipo":        g_tipo,
                "estado":      g_estado,
                "asistentes":  g_asist,
                "lugar":       g_lugar,
                "incidencias": json.dumps(df_incs_ed.to_dict("records"), ensure_ascii=False),
                "acuerdos":    json.dumps(df_ac_ed.to_dict("records"), ensure_ascii=False),
                "agenda":      g_agenda,
                "creado_por":  "Darío A. López",
            }
            upsert_registro_acta(registro)
            st.success(f"✅ Acta **{_id_g}** guardada.")
            st.rerun()

    with col_prev_g:
        st.markdown("### 🔍 Actas generadas")
        actas_reg = list_registro_actas() if callable(list_registro_actas) else []
        if not actas_reg:
            st.info("Sin actas generadas. Usa el formulario.")
        for a in actas_reg[:10]:
            with st.expander(f"📄 {a.get('id','')} · {a.get('fecha','')} · {a.get('obra','')}"):
                st.markdown(f"**Tipo:** {a.get('tipo','—')} | **Estado:** {a.get('estado','—')}")
                st.markdown(f"**Lugar:** {a.get('lugar','—')}")
                incs_a = json.loads(a.get("incidencias","[]")) if isinstance(a.get("incidencias"), str) else []
                if incs_a:
                    st.markdown(f"**Incidencias:** {len(incs_a)}")
                if st.button("🗑️ Eliminar", key=f"del_gen_{a['id']}", type="secondary"):
                    delete_registro_acta(a["id"]); st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — CERTIFICACIONES
# ─────────────────────────────────────────────────────────────────────────────
with tab_cert:
    st.caption("Cruza el % de avance real vs. coste ejecutado para justificar certificaciones ante la propiedad.")

    st.info("💡 Módulo en construcción. Conectar con la tabla de CAPEX de cada proyecto para automatizar el cálculo.")

    CERT_COLS = ["Partida / Gremio", "Presupuesto €", "Ejecutado €", "% Avance Real", "% Facturado", "Diferencia €", "Observaciones"]
    df_cert = pd.DataFrame([
        {"Partida / Gremio": "Demoliciones",      "Presupuesto €": 0, "Ejecutado €": 0, "% Avance Real": 0, "% Facturado": 0, "Diferencia €": 0, "Observaciones": ""},
        {"Partida / Gremio": "Civil / Fontanería","Presupuesto €": 0, "Ejecutado €": 0, "% Avance Real": 0, "% Facturado": 0, "Diferencia €": 0, "Observaciones": ""},
        {"Partida / Gremio": "Electricidad",      "Presupuesto €": 0, "Ejecutado €": 0, "% Avance Real": 0, "% Facturado": 0, "Diferencia €": 0, "Observaciones": ""},
        {"Partida / Gremio": "Climatización",     "Presupuesto €": 0, "Ejecutado €": 0, "% Avance Real": 0, "% Facturado": 0, "Diferencia €": 0, "Observaciones": ""},
        {"Partida / Gremio": "Carpintería",       "Presupuesto €": 0, "Ejecutado €": 0, "% Avance Real": 0, "% Facturado": 0, "Diferencia €": 0, "Observaciones": ""},
        {"Partida / Gremio": "Acabados / PCI",    "Presupuesto €": 0, "Ejecutado €": 0, "% Avance Real": 0, "% Facturado": 0, "Diferencia €": 0, "Observaciones": ""},
        {"Partida / Gremio": "Equipamiento",      "Presupuesto €": 0, "Ejecutado €": 0, "% Avance Real": 0, "% Facturado": 0, "Diferencia €": 0, "Observaciones": ""},
    ])

    cert_editado = st.data_editor(
        df_cert, num_rows="dynamic", use_container_width=True, key="editor_cert",
        column_config={
            "Presupuesto €":  st.column_config.NumberColumn("Presupuesto (€)",  format="%.0f"),
            "Ejecutado €":    st.column_config.NumberColumn("Ejecutado (€)",    format="%.0f"),
            "% Avance Real":  st.column_config.NumberColumn("% Avance Real",    min_value=0, max_value=100, format="%d%%"),
            "% Facturado":    st.column_config.NumberColumn("% Facturado",      min_value=0, max_value=100, format="%d%%"),
            "Diferencia €":   st.column_config.NumberColumn("Diferencia (€)",   format="%.0f"),
            "Observaciones":  st.column_config.TextColumn("Observaciones", width="large"),
        },
        hide_index=True,
    )

    # Totales automáticos
    if not cert_editado.empty:
        total_ppto = pd.to_numeric(cert_editado["Presupuesto €"], errors="coerce").sum()
        total_ejec = pd.to_numeric(cert_editado["Ejecutado €"],   errors="coerce").sum()
        avance_gl  = pd.to_numeric(cert_editado["% Avance Real"], errors="coerce").mean()

        ct1, ct2, ct3 = st.columns(3)
        ct1.metric("Total Presupuestado", f"{total_ppto:,.0f} €".replace(",","."))
        ct2.metric("Total Ejecutado",     f"{total_ejec:,.0f} €".replace(",","."))
        ct3.metric("Avance Global",       f"{avance_gl:.1f}%")

        if total_ppto > 0:
            cert_html = (
                f"<h3>CERTIFICACIÓN — {date.today().strftime('%d/%m/%Y')}</h3>"
                f"<p>CAPEX presupuestado: <b>{total_ppto:,.0f} €</b> | "
                f"Ejecutado: <b>{total_ejec:,.0f} €</b> | "
                f"Avance medio: <b>{avance_gl:.1f}%</b></p>"
            )
            st.download_button("⬇️ Exportar certificación HTML", data=cert_html.encode("utf-8"),
                               file_name=f"CERTIFICACION_{date.today().strftime('%Y%m%d')}.html",
                               mime="text/html", use_container_width=False)
