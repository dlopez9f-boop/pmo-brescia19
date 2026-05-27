#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pages/1_Actas_PMO.py — Actas diarias + semanales · Nine Fitness Brescia 19
"""

import json
import streamlit as st
from datetime import date, datetime, timedelta

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

# ─── GENERADOR HTML SEMANAL ───────────────────────────────────────
def html_semanal(acta_sem: dict, diarias: list[dict]) -> str:
    sem    = acta_sem.get("semana_obra", "?")
    fechas = " · ".join(
        datetime.fromisoformat(a["fecha"]).strftime("%d/%m") for a in diarias
    )
    bloques = ""
    for a in diarias:
        dia  = datetime.fromisoformat(a["fecha"]).strftime("%A %d/%m/%Y").capitalize()
        secs = a.get("intervenciones") or {}
        if isinstance(secs, str):
            try: secs = json.loads(secs)
            except: secs = {}
        sec_html = ""
        for g, c in secs.items():
            if c:
                sec_html += (f'<div style="margin-bottom:7px;">'
                             f'<b style="font-size:11px;color:#0f3460;">{g}</b>'
                             f'<div style="font-size:12px;padding-left:8px;border-left:2px solid #e2e6f0;'
                             f'color:#333;">{str(c).replace(chr(10),"<br>")}</div></div>')
        incs = _normalizar_incs(a.get("incidencias"))
        inc_html = "".join(
            f'<div style="color:#c0392b;font-size:11px;">⚠️ {i}</div>' for i in incs
        )
        _ag_items = _parse_agenda(a)
        _ag_line  = " · ".join(it["hora"] + " " + it["evento"] for it in _ag_items[:2]) if _ag_items else ""
        bloques += f"""
        <div style="border-left:4px solid #e94560;padding:12px 16px;margin-bottom:14px;
                    background:#fff;border-radius:0 8px 8px 0;box-shadow:0 1px 4px rgba(0,0,0,.06);">
          <b style="font-size:14px;color:#1a1a2e;">📋 {dia}</b>
          <div style="font-size:13px;color:#555;margin:6px 0 8px 0;">{a.get('resumen','')}</div>
          {sec_html}{inc_html}
          {f'<div style="font-size:11px;color:#888;border-top:1px solid #f0f2f7;padding-top:6px;margin-top:6px;">📅 {_ag_line[:220]}</div>' if _ag_line else ''}
        </div>"""

    desv = acta_sem.get("desviaciones_criticas") or []
    if isinstance(desv, str):
        try: desv = json.loads(desv)
        except: desv = [desv]
    desv_html = "".join(f"<li>{d}</li>" for d in desv) if desv else "<li>Sin desviaciones críticas registradas.</li>"

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<style>
  @page {{size:A4;margin:14mm 12mm}}
  body{{font-family:'Segoe UI',Arial,sans-serif;background:#fff;color:#1a1a2e;margin:0;padding:0}}
</style></head><body>
<div style="background:linear-gradient(135deg,#1a1a2e,#0f3460);color:#fff;
            padding:18px 22px;border-radius:8px;margin-bottom:18px;">
  <div style="font-size:15pt;font-weight:900;">ACTA SEMANAL EJECUTIVA — SEMANA {sem}</div>
  <div style="font-size:9pt;opacity:.75;margin-top:3px;">
    Nine Fitness · Brescia 19 · Días: {fechas} · Dir. Obra: Darío A. López
  </div>
</div>
<div style="background:#fdf2f2;border-left:4px solid #e74c3c;padding:10px 14px;
            border-radius:0 6px 6px 0;margin-bottom:16px;font-size:12px;">
  <b>⚠️ Gremios con desviaciones:</b> <ul style="margin:4px 0 0 0;">{desv_html}</ul>
</div>
{bloques}
<div style="text-align:center;font-size:8pt;color:#bbb;margin-top:18px;
            border-top:1px solid #e2e6f0;padding-top:8px;">
  NINE FITNESS GROUP S.L. · Brescia 19, Madrid · Ref: {acta_sem.get('id','')} · Confidencial
</div></body></html>"""

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
      {hoy.strftime('%A %d/%m/%Y').capitalize()} · Semana {sem} de obra
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
        _fstr  = datetime.fromisoformat(acta["fecha"]).strftime("%A %d/%m/%Y").capitalize()
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
                        delete_acta_diaria(acta["id"])
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
                delete_acta_semanal(s["id"])
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
                            d_str = datetime.fromisoformat(a["fecha"]).strftime("%a %d/%m").capitalize()
                            st.markdown(f"— **{d_str}**: {a.get('resumen','')}")


# ─── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Sistema")
    st.markdown(f"**Backend:** `{be}`")
    st.markdown(f"**Semana actual:** S{sem}")
    st.markdown(f"**Modo:** {'🔒 Solo lectura' if modo_publico else '✏️ Edición completa'}")
    st.divider()
    st.markdown("**URL pública:**")
    st.code(f"?view=public  ← modo lectura", language=None)
