#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
actas_app.py — Sistema PMO Multi-Proyecto
The Nine Group · Darío A. López
streamlit run actas_app.py
"""

import streamlit as st
import json
from datetime import datetime, date, timedelta
from pathlib import Path
import pandas as pd

st.set_page_config(
    page_title="PMO — The Nine",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CONFIG PROYECTOS ─────────────────────────────────────────────
PROYECTOS = {
    "chamartin": {
        "nombre":     "The Nine Chamartín",
        "ref":        "WAK-13",
        "direccion":  "Profesor Waksman 13, Madrid",
        "data_file":  Path("actas_data/actas_chamartin.json"),
        "apertura":   "TBD",
        "inicio_ref": date(2026, 9, 1),
        "fase":       "LICITACIÓN",
        "color":      "#C9A96E",
        "gremio_kw": {
            "🧱 Munir — Civil":            ["munir","ziad","demolición","hormigón","zapata","forjado","losa","arqueta","escombro"],
            "🔧 Cador — Fontanería":        ["cador","nacho","gonzalo","saneamiento","fontanería","bajante","tubo","aguas","colector"],
            "⚡ Elecrea — Electricidad":    ["elecrea","electricidad","cuadro","cable","bandeja","iga","diferencial","carga"],
            "❄️ Clima — Carlos/Servitec":  ["carlos","clima","ahu","conducto","ventilación","servitec","fancoil","retorno"],
            "🏊 Álvaro Chuso — Piscina":   ["chuso","piscina","jacuzzi","vaso","zona húmeda","bomba agua","filtro","cloro"],
            "🧖 Thomas Wellness — Sauna":   ["enrique","thomas","wellness","sauna","vestuario","pilates","baño turco","hammam"],
            "🪵 Josevi — Cerrajería":       ["josevi","cerrajería","metálica","puerta","vidrio","barandilla","perfil"],
            "🌿 Constherba":                ["constherba","david const"],
            "💡 Dario Roblan — Ilum.":     ["roblan","iluminación","lux","luminaria","proyector"],
            "🏠 Robisipe":                  ["robisipe"],
            "🎨 Rafael Cifuentes":          ["cifuentes","rafael cif"],
            "🏡 Álvaro Medina":             ["álvaro medina","medina llave"],
        },
    },
    "brescia": {
        "nombre":     "Nine Fitness Brescia 19",
        "ref":        "BRE-19",
        "direccion":  "Calle Brescia 19, Madrid 28028",
        "data_file":  Path("actas_data/actas.json"),
        "apertura":   "3–5 AGO 2026 ✓",
        "inicio_ref": date(2026, 3, 23),
        "fase":       "CERRADO",
        "color":      "#e94560",
        "gremio_kw": {
            "⚡ Electricidad":   ["luis","elecrea","cuadro","bandeja","cableado","iga","diferencial","eléctric"],
            "❄️ Climatización": ["jose","nacho","servitec","conducto","daikin","clima","ahu","difusor","altillo"],
            "🧱 Albañilería":   ["munir","ziad","mohamed","solera","tabiq","escombro","nivelac","hormigón","pladur"],
            "🪵 Carpintería":   ["josevi","upn","espejo","carpintería","viga","estructura"],
            "🔥 PCI":           ["leo","troser","extinción","pci","rociador","boca incendio"],
            "♿ Accesibilidad": ["pedro","hersan","salvaescaleras","pmr","fortis","plataforma"],
            "🔧 Fontanería":    ["munir","agua","fontanería","sanitario","termo","bosch"],
        },
    },
}

# ─── DASHBOARD DATA (Chamartín · actualizar cada sesión) ──────────
CONTRATAS_CHAMARTIN = [
    {"empresa":"Munir (Ziad)",            "rol":"Demolición + Civil",       "visita":"✓", "mediciones":"Propias",   "presupuesto":"Parcial",     "importe":"60.476 € +pte", "estado":"aprobacion",   "notas":"Prep ✓ · Demol ✓ · Parte 3 sin recibir"},
    {"empresa":"Cador (Luis/Nacho)",      "rol":"Llave en mano (ex. clima)","visita":"✓", "mediciones":"Enviadas",  "presupuesto":"Pendiente",   "importe":"—",             "estado":"bloqueado",    "notas":"Falta: as-built · clima · sol. S-2"},
    {"empresa":"Elecrea (Luis)",          "rol":"Electricidad",              "visita":"~", "mediciones":"Enviadas",  "presupuesto":"Recibido",    "importe":"En revisión",   "estado":"revision",     "notas":"xlsx en carpeta ELECREA-LUIS"},
    {"empresa":"Josevi",                  "rol":"Cerrajería metálica",       "visita":"✗", "mediciones":"—",         "presupuesto":"Pendiente",   "importe":"—",             "estado":"sin_contacto", "notas":"Pendiente coordinar visita"},
    {"empresa":"Álvaro Medina",           "rol":"Llave en mano",             "visita":"✗", "mediciones":"Enviadas",  "presupuesto":"Pendiente",   "importe":"—",             "estado":"pendiente",    "notas":"Mediciones xlsx enviadas"},
    {"empresa":"Álvaro Chuso",            "rol":"Piscina + Zona húmeda",    "visita":"✓", "mediciones":"v02 ✓",     "presupuesto":"Pendiente",   "importe":"—",             "estado":"bloqueado",    "notas":"Bloqueado: renders piscina"},
    {"empresa":"Thomas Wellness (Enr.)",  "rol":"Sauna · Vestuarios · Pilates","visita":"✗","mediciones":"—",       "presupuesto":"Pendiente",   "importe":"—",             "estado":"sin_contacto", "notas":"Pendiente primer contacto"},
    {"empresa":"Constherba (David)",      "rol":"Llave en mano",             "visita":"✗", "mediciones":"Enviadas",  "presupuesto":"Pendiente",   "importe":"—",             "estado":"pendiente",    "notas":"Mediciones xlsx enviadas"},
    {"empresa":"Robisipe",                "rol":"Llave en mano",             "visita":"✓", "mediciones":"Enviadas",  "presupuesto":"Pendiente",   "importe":"—",             "estado":"pendiente",    "notas":"Visita realizada, esperando oferta"},
    {"empresa":"Rafael Cifuentes",        "rol":"Llave en mano",             "visita":"~", "mediciones":"Enviadas",  "presupuesto":"Recibido v02","importe":"En revisión",   "estado":"revision",     "notas":"Presupuesto v02 en carpeta"},
    {"empresa":"Dario Roblan",            "rol":"Iluminación",               "visita":"~", "mediciones":"Enviadas",  "presupuesto":"Recibido",    "importe":"En revisión",   "estado":"revision",     "notas":"xlsx iluminación v02"},
]

DECISIONES_CHAMARTIN = [
    {"nivel":"critico", "titulo":"Bajante fibrocemento/AMIANTO — notificar comunidad", "sub":"S-2 · Empresa RERA obligatoria · RD 396/2006 · URGENTE"},
    {"nivel":"critico", "titulo":"Saneamiento S-2: gravedad vs bombeo",                "sub":"Bloqueante para Cador · Requiere cata de cotas arqueta comunitaria"},
    {"nivel":"imp",     "titulo":"Proyecto climatización — pendiente de Ángel (TWAO)", "sub":"Sin proyecto no hay presupuesto de ninguna contrata de clima"},
    {"nivel":"imp",     "titulo":"Escalera: planos de sección → Cador",               "sub":"Hormigón visto propuesto · Ángel → Luis Cador"},
    {"nivel":"imp",     "titulo":"Renders zona piscina → Álvaro Chuso",               "sub":"Bloqueante para presupuesto definitivo de piscina"},
    {"nivel":"imp",     "titulo":"As-Built del local → Cador y Gonzalo",              "sub":"Sin as-built no pueden dimensionar la red de saneamiento"},
]

# ─── MANTENIMIENTO: CONSTANTES ────────────────────────────────────
CENTROS_OPERATIVOS = ["Acacias","Valdebebas","Cañaveral","Retiro","Guindalera","Chamberí","Pozuelo","Brescia 19"]
CATEGORIAS_MANT    = ["Climatización","Fontanería","Electricidad","Accesos/Seguridad","Piscina","PCI","General"]
PRIO_OPTS          = ["P1 · Crítica (<4h)","P2 · Urgente (<24h)","P3 · Normal (72h)"]
PRIO_SLA           = {"P1 · Crítica (<4h)":4,"P2 · Urgente (<24h)":24,"P3 · Normal (72h)":72}
TIPO_FAC_OPTS      = ["Mano de obra","Material","Desplazamiento","Preventivo"]
COSTE_DESPL_SLA    = 25.0   # € por visita según contrato marco
MARGEN_MAT_MAX     = 15.0   # % máximo sobre tarifa fabricante

PENDIENTES_CHAMARTIN = {
    "Darío — HOY": [
        ("u","Dar OK formal a Munir preparación — Presu 43 (20.546 €)"),
        ("u","Notificar comunidad: bajante fibrocemento/amianto deteriorada"),
        ("u","Enviar renders piscina a Álvaro Chuso"),
    ],
    "Darío — Esta semana": [
        ("n","Coordinar cata S-2 con Gonzalo: medir cota arqueta comunitaria"),
        ("n","Enviar as-built del local a Cador y Gonzalo"),
        ("n","Coordinar visitas: Josevi · Thomas Wellness · Constherba · Álvaro Medina"),
    ],
    "Ángel (TWAO Arquitectos)": [
        ("u","Entregar proyecto técnico climatización/ventilación"),
        ("n","Planos de sección escalera → enviar a Cador"),
    ],
    "Gonzalo (Fontanería)": [
        ("n","Informe diagnóstico saneamiento + propuesta gravedad"),
        ("n","Medir cota fondo arqueta S-2 (bajante comunitaria)"),
    ],
    "Álvaro Chuso (Piscina)": [
        ("n","Tabla de consumos eléctricos → a Luis Elecrea"),
        ("n","Verificar legalización cotas vaso: 1,00 m + 0,40 m (CTE-SUA)"),
    ],
}

# ─── CAPEX/OPEX TRACKER: CONSTANTES ──────────────────────────────
TODOS_CENTROS = ["Chamartín (WAK-13)","Brescia 19","Acacias","Valdebebas",
                 "Cañaveral","Retiro","Guindalera","Chamberí","Pozuelo"]
TODOS_PROVEEDORES = ["Munir (Ziad)","Cador (Luis/Nacho)","Elecrea (Luis)",
                     "Josevi","Álvaro Medina","Álvaro Chuso","Thomas Wellness",
                     "Constherba","Robisipe","Rafael Cifuentes","Dario Roblan",
                     "Climatec","Natalio (Fontanería)","Troser PCI","Otro"]
ESTADO_PET_OPTS  = ["Esperando precio","Recibido","Revisión técnica","Aprobado","Rechazado"]
ESTADO_EJEC_OPTS = ["No iniciado","En curso","Bloqueado","Terminado in situ"]
ESTADO_CIER_OPTS = ["Pendiente factura","Validado Darío","Traspasado Contabilidad"]
TIPO_OPTS        = ["CAPEX","OPEX"]

CAPEX_FILE = Path("actas_data/capex_opex.json")

def load_capex() -> list:
    if not CAPEX_FILE.exists():
        return []
    return json.loads(CAPEX_FILE.read_text(encoding="utf-8"))

def save_capex(data: list):
    CAPEX_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def nueva_peticion(ref: str) -> dict:
    return {
        "ref": ref, "centro": "Chamartín (WAK-13)", "tipo": "CAPEX",
        "concepto": "", "proveedor": "",
        "fecha_solicitud": str(date.today()),
        "estado_peticion": "Esperando precio", "importe_presupuestado": 0.0,
        "fecha_fin_estimada": "", "estado_ejecucion": "No iniciado", "notas": "",
        "importe_facturado": 0.0, "estado_cierre": "Pendiente factura",
        "fecha_recepcion": "", "garantia_meses": 12, "vencimiento_garantia": "",
    }

# ─── STORAGE ──────────────────────────────────────────────────────
DATA_DIR = Path("actas_data")
DATA_DIR.mkdir(exist_ok=True)

def load_actas(data_file: Path) -> list:
    if not data_file.exists():
        data_file.write_text("[]", encoding="utf-8")
    return json.loads(data_file.read_text(encoding="utf-8"))

def save_actas(actas: list, data_file: Path):
    data_file.write_text(json.dumps(actas, ensure_ascii=False, indent=2), encoding="utf-8")

# ─── DASHBOARD STORAGE ────────────────────────────────────────────
DASH_FILE = Path("actas_data/dashboard_chamartin.json")

def load_dashboard() -> dict:
    if not DASH_FILE.exists():
        data = {
            "actualizado": str(date.today()),
            "contratas":   CONTRATAS_CHAMARTIN,
            "decisiones":  DECISIONES_CHAMARTIN,
        }
        DASH_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return json.loads(DASH_FILE.read_text(encoding="utf-8"))

def save_dashboard(contratas: list, decisiones: list):
    data = {
        "actualizado": str(date.today()),
        "contratas":   contratas,
        "decisiones":  decisiones,
    }
    DASH_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# ─── MANTENIMIENTO STORAGE ─────────────────────────────────────────
def _mant_path(mes: str) -> Path:
    return DATA_DIR / f"mant_{mes.replace('/','_')}.json"

def load_mant(mes: str) -> dict:
    p = _mant_path(mes)
    if not p.exists():
        return {"ots": [], "factura": {"proveedor":"","numero":"","lineas":[]}}
    return json.loads(p.read_text(encoding="utf-8"))

def save_mant(mes: str, data: dict):
    _mant_path(mes).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def semana_proyecto(d: date, inicio_ref: date) -> int:
    return max(1, (d - inicio_ref).days // 7 + 1)

# ─── PARSER ───────────────────────────────────────────────────────
INCIDENCIA_KW = ["problem","retraso","falta","pendiente","alerta","urgente",
                 "no llega","sin material","avería","parado","bloqueado"]
AGENDA_KW = ["mañana","próximo","siguiente día","08:","09:","10:","11:"]

def parsear(texto: str, gremio_kw: dict) -> dict:
    lines = [l.strip() for l in texto.splitlines() if l.strip()]
    secciones = {g: [] for g in gremio_kw}
    incidencias, agenda = [], []
    for line in lines:
        ll = line.lower()
        for gremio, kws in gremio_kw.items():
            if any(k in ll for k in kws):
                secciones[gremio].append(line)
                break
        if any(k in ll for k in INCIDENCIA_KW):
            incidencias.append(line)
        if any(k in ll for k in AGENDA_KW):
            agenda.append(line)
    gremios_con_incidencia = [
        g for g in gremio_kw
        if secciones[g] and any(k in " ".join(secciones[g]).lower() for k in INCIDENCIA_KW)
    ]
    return {
        "secciones":          {g: "\n".join(v) for g, v in secciones.items() if v},
        "incidencias":        incidencias,
        "agenda_manana":      "\n".join(agenda),
        "gremios_incidencia": gremios_con_incidencia,
    }

# ─── HTML SEMANAL ─────────────────────────────────────────────────
def html_semanal(actas: list, semana: int, proyecto: dict) -> str:
    fechas = " · ".join(datetime.fromisoformat(a["fecha"]).strftime("%d/%m") for a in actas)
    bloques = ""
    for acta in actas:
        dia = datetime.fromisoformat(acta["fecha"]).strftime("%A %d/%m/%Y").capitalize()
        secs = ""
        for gremio, contenido in acta.get("secciones", {}).items():
            if contenido:
                emoji = gremio.split()[0]
                nombre = " ".join(gremio.split()[1:])
                secs += f"""
                <div style="margin-bottom:8px;">
                  <div style="font-size:11px;font-weight:700;text-transform:uppercase;color:#0f3460;margin-bottom:2px;">{emoji} {nombre}</div>
                  <div style="font-size:12px;color:#333;padding-left:8px;border-left:2px solid #e2e6f0;">{contenido.replace(chr(10),'<br>')}</div>
                </div>"""
        incs = "".join(f'<div style="color:#c0392b;font-size:11px;">⚠️ {i}</div>' for i in acta.get("incidencias", []))
        agenda = acta.get("agenda_manana", "")
        bloques += f"""
        <div style="border-left:4px solid {proyecto['color']};padding:12px 16px;margin-bottom:14px;background:#fff;border-radius:0 8px 8px 0;box-shadow:0 1px 4px rgba(0,0,0,.06);">
          <div style="font-weight:700;font-size:14px;color:#1a1a2e;margin-bottom:8px;">📋 {dia}</div>
          {secs}
          {f'<div style="margin-top:6px;">{incs}</div>' if incs else ''}
          {f'<div style="margin-top:8px;font-size:11px;color:#555;border-top:1px solid #f0f2f7;padding-top:6px;">📅 {agenda.replace(chr(10)," · ")}</div>' if agenda else ''}
        </div>"""
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<style>
  @page {{size:A4;margin:15mm 12mm}}
  body{{font-family:'Segoe UI',Arial,sans-serif;background:#fff;color:#1a1a2e;padding:0;margin:0}}
</style></head><body>
<div style="background:#0D0D0D;color:#fff;padding:20px 24px;border-radius:8px;margin-bottom:20px;border-bottom:3px solid {proyecto['color']};">
  <div style="font-size:12pt;color:{proyecto['color']};font-weight:700;letter-spacing:2px;">{proyecto['nombre'].upper()} · {proyecto['ref']}</div>
  <div style="font-size:15pt;font-weight:900;color:#fff;margin-top:4px;">ACTA SEMANAL — SEMANA {semana}</div>
  <div style="font-size:10pt;opacity:.65;margin-top:4px;">{proyecto['direccion']} · Días: {fechas} · D.O.: Darío A. López</div>
</div>
{bloques}
<div style="text-align:center;font-size:9pt;color:#aab;margin-top:20px;border-top:1px solid #e2e6f0;padding-top:8px;">
  {proyecto['nombre']} · {proyecto['ref']} · ACTA-SEM{semana}-{date.today().strftime('%d%m%Y')}
</div>
</body></html>"""

# ─── CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #F0EDE8; }
  [data-testid="stMain"] { padding-top: 0.5rem; }

  section[data-testid="stSidebar"] { background: #0D0D0D !important; }
  section[data-testid="stSidebar"] p,
  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] span { color: #C8C3BA !important; }

  .pmo-header {
    background: #0D0D0D;
    color: #fff;
    padding: 15px 22px;
    border-radius: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
    border-bottom: 2px solid #C9A96E;
  }
  .pmo-header .brand { color: #C9A96E; font-size: 17px; font-weight: 900; letter-spacing: .3px; }
  .pmo-header .meta  { font-size: 11px; opacity: .6; margin-top: 3px; }
  .pmo-header .fase-badge { background: #C9A96E; color: #0D0D0D; padding: 6px 16px; border-radius: 3px; font-weight: 800; font-size: 12px; letter-spacing: 1px; }

  .acta-card {
    border-left: 4px solid #C9A96E;
    padding: 12px 14px;
    background: #fff;
    border-radius: 0 5px 5px 0;
    box-shadow: 0 1px 4px rgba(0,0,0,.07);
    margin-bottom: 10px;
  }
  .acta-card-urgente { border-left-color: #C0392B !important; }
  .acta-card-alta    { border-left-color: #B7610A !important; }

  .badge { display:inline-block; padding:2px 8px; border-radius:2px; font-size:10px; font-weight:700; }
  .b-red   { background:#fdf2f2; color:#c0392b; }
  .b-amber { background:#fff8e1; color:#B7610A; }
  .b-green { background:#f0faf4; color:#1E7A54; }
  .b-blue  { background:#eaf4ff; color:#1A5C8A; }

  .gtag { display:inline-block; padding:2px 7px; border-radius:2px; font-size:10px; font-weight:600; margin:2px; background:#F2EFE9; color:#776F63; }
  .scroll-wrap { max-height:66vh; overflow-y:auto; padding-right:2px; }
  div[data-testid="stForm"] { background:#fff; border-radius:6px; padding:14px; box-shadow:0 1px 5px rgba(0,0,0,.07); }
  textarea { font-family:'Courier New',monospace !important; font-size:12px !important; }

  /* dashboard components */
  .ct-wrap { background:#fff; border:1px solid #DDD8CE; border-radius:4px; overflow:hidden; }
  .ct-row  { display:flex; gap:0; border-bottom:1px solid #DDD8CE; align-items:center; }
  .ct-row:last-child { border-bottom:none; }
  .ct-row:not(.ct-head):hover { background:#F2EFE9; }
  .ct-head { background:#EDE9E1; font-size:9.5px; font-weight:700; text-transform:uppercase; color:#776F63; letter-spacing:.8px; }
  .ct-c    { padding:7px 10px; font-size:12px; flex:1; min-width:0; }
  .ct-c-sm { padding:7px 6px; flex:0 0 72px; text-align:center; font-size:12px; }
  .ct-c-st { padding:7px 8px; flex:0 0 130px; }

  .chip { display:inline-flex; align-items:center; font-size:8px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; padding:2px 6px; border-radius:2px; white-space:nowrap; }
  .chip-red { background:rgba(192,57,43,.10); color:#C0392B; border:1px solid rgba(192,57,43,.28); }
  .chip-grn { background:rgba(30,122,84,.10);  color:#1E7A54; border:1px solid rgba(30,122,84,.28); }
  .chip-amb { background:rgba(183,97,10,.10);  color:#B7610A; border:1px solid rgba(183,97,10,.28); }
  .chip-blu { background:rgba(26,92,138,.10);  color:#1A5C8A; border:1px solid rgba(26,92,138,.28); }
  .chip-gry { background:#EDE9E1; color:#776F63; border:1px solid #DDD8CE; }

  .dec-item  { display:flex; gap:10px; padding:8px 12px; background:#fff; border:1px solid #DDD8CE; border-radius:3px; margin-bottom:5px; }
  .dec-crit  { border-left:3px solid #C0392B !important; background:rgba(192,57,43,.04) !important; }
  .dec-imp   { border-left:3px solid #B7610A !important; }
  .dec-dot   { width:6px; height:6px; border-radius:50%; flex-shrink:0; margin-top:5px; }

  .kpi-box  { background:#fff; border:1px solid #DDD8CE; border-radius:4px; padding:12px 14px; }
  .kpi-val  { font-size:24px; font-weight:700; line-height:1.1; }
  .kpi-lbl  { font-size:9.5px; font-weight:700; text-transform:uppercase; letter-spacing:.8px; color:#776F63; margin-top:4px; }

  .presu-card { background:#fff; border:1px solid #DDD8CE; border-radius:3px; padding:12px 14px; height:100%; }
  .presu-card.ready { border-left:3px solid #1E7A54; }
  .presu-card.pte   { border-left:3px solid #B7610A; opacity:.85; }
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏗️ PMO · The Nine")
    st.markdown("---")
    pkey = st.radio(
        "Vista activa",
        options=["chamartin","mantenimiento","capex_opex","brescia"],
        format_func=lambda k: {
            "chamartin":    "🟢 Chamartín (obra)",
            "mantenimiento":"🔧 Red de Centros",
            "capex_opex":   "📊 Control CAPEX/OPEX",
            "brescia":      "⚪ Brescia 19 (archivo)",
        }[k],
    )
    if pkey in PROYECTOS:
        proyecto = PROYECTOS[pkey]
        st.markdown(f"**{proyecto['nombre']}**  \n`{proyecto['ref']}`")
        st.caption(proyecto["direccion"])
        st.markdown(f"**Fase:** `{proyecto['fase']}`")
        st.markdown(f"**Apertura:** {proyecto['apertura']}")
    elif pkey == "mantenimiento":
        proyecto = None
        st.markdown("**7 centros operativos**")
        st.caption("Acacias · Valdebebas · Cañaveral · Retiro · Guindalera · Chamberí · Pozuelo")
        st.markdown("**Modo:** `MANTENIMIENTO OPEX`")
    else:  # capex_opex
        proyecto = None
        reqs = load_capex()
        st.markdown(f"**{len(reqs)} peticiones registradas**")
        cap = len([r for r in reqs if r.get('tipo') == 'CAPEX'])
        op  = len([r for r in reqs if r.get('tipo') == 'OPEX'])
        st.caption(f"CAPEX: {cap} · OPEX: {op}")
        st.markdown("**Modo:** `CICLO DE VIDA`")
    st.markdown("---")
    st.caption("The Nine Group · PMO · Darío A. López")

# ─── HEADER ───────────────────────────────────────────────────────
hoy   = date.today()
if pkey in PROYECTOS:
    sem   = semana_proyecto(hoy, proyecto["inicio_ref"])
    lunes = hoy - timedelta(days=hoy.weekday())
    st.markdown(f"""
<div class="pmo-header">
  <div>
    <div class="brand">{proyecto['nombre'].upper()}</div>
    <div class="meta">{proyecto['ref']} · {proyecto['direccion']} · {hoy.strftime('%A %d/%m/%Y').capitalize()} · Semana {sem}</div>
  </div>
  <div class="fase-badge">{proyecto['fase']}</div>
</div>
""", unsafe_allow_html=True)
elif pkey == "mantenimiento":
    st.markdown(f"""
<div class="pmo-header">
  <div>
    <div class="brand">NINE GROUP · RED DE CENTROS</div>
    <div class="meta">7 centros operativos · OPEX Mantenimiento · {hoy.strftime('%d/%m/%Y')}</div>
  </div>
  <div class="fase-badge">MANTENIMIENTO</div>
</div>
""", unsafe_allow_html=True)
else:  # capex_opex
    st.markdown(f"""
<div class="pmo-header">
  <div>
    <div class="brand">NINE GROUP · CONTROL CAPEX / OPEX</div>
    <div class="meta">Ciclo de vida de presupuestos · Licitación → Ejecución → Facturación → Garantía · {hoy.strftime('%d/%m/%Y')}</div>
  </div>
  <div class="fase-badge">CICLO DE VIDA</div>
</div>
""", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────
if pkey == "chamartin":
    tab_actas, tab_dash, tab_semanal = st.tabs(["📋 Actas", "📊 Dashboard", "📄 Semanal"])
    tab_ots = tab_fac = tab_audit = tab_apr_v = None
elif pkey == "mantenimiento":
    tab_ots, tab_fac, tab_audit, tab_apr_v = st.tabs(["📋 OTs del mes", "🧾 Factura", "🔍 Auditoría", "✅ → Valentina"])
elif pkey == "capex_opex":
    tab_pipeline, tab_licita, tab_ejec, tab_factura_cv, tab_garantia = st.tabs([
        "🗂 Pipeline", "1️⃣ Licitación", "2️⃣ Ejecución", "3️⃣ Facturación", "4️⃣ Garantías"
    ])
else:
    tab_actas, tab_semanal = st.tabs(["📋 Actas", "📄 Semanal"])
    tab_dash = None

# ══════════════════════════════════════════════════════════════════
# MODO: MANTENIMIENTO (Red de Centros)
# ══════════════════════════════════════════════════════════════════
if pkey == "mantenimiento":
    mes_sel = hoy.strftime("%m/%Y")
    mant_data = load_mant(mes_sel)
    ots_saved = mant_data.get("ots", [])
    fac_saved = mant_data.get("factura", {"proveedor":"","numero":"","lineas":[]})

    # ── TAB OTs ──────────────────────────────────────────────────
    with tab_ots:
        st.markdown("### 📋 Órdenes de Trabajo — " + mes_sel)
        st.caption("Introduce los tickets cerrados de Partner este mes. Guarda al terminar.")

        col_sel, col_add = st.columns([3,1])
        with col_sel:
            proveedor_sel = st.selectbox("Proveedor del mes", ["Climatec Madrid","Natalio (Fontanería)","Elecrea","Control Accesos","Álvaro Chuso (Piscina)","Troser PCI","Otro"])
        with col_add:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Añadir fila OT"):
                ots_saved.append({
                    "Centro":"Valdebebas","Categoría":"Climatización","Prioridad":"P3 · Normal (72h)",
                    "Técnico":"","Descripción":"","Apertura":mes_sel[:2]+"/09/2026","Cierre":mes_sel[:2]+"/09/2026",
                    "Horas":1.0,"Material":"","€_Fab":0.0,"€_Fac":0.0,
                    "Garantía":False,"G_hasta":"","Albarán":True,"Fotos":True,"Firma":True
                })
                save_mant(mes_sel, {"ots": ots_saved, "factura": fac_saved})
                st.rerun()

        if ots_saved:
            df_ots = pd.DataFrame(ots_saved)
            edited_ots = st.data_editor(
                df_ots,
                column_config={
                    "Centro":     st.column_config.SelectboxColumn("Centro",     options=CENTROS_OPERATIVOS, width="small"),
                    "Categoría":  st.column_config.SelectboxColumn("Categoría",  options=CATEGORIAS_MANT,    width="small"),
                    "Prioridad":  st.column_config.SelectboxColumn("Prioridad",  options=PRIO_OPTS,          width="medium"),
                    "Técnico":    st.column_config.TextColumn("Técnico",   width="small"),
                    "Descripción":st.column_config.TextColumn("Descripción",width="large"),
                    "Apertura":   st.column_config.TextColumn("Apertura",  width="small"),
                    "Cierre":     st.column_config.TextColumn("Cierre",    width="small"),
                    "Horas":      st.column_config.NumberColumn("Horas",   format="%.1f", width="small"),
                    "Material":   st.column_config.TextColumn("Material",  width="medium"),
                    "€_Fab":      st.column_config.NumberColumn("€ Fabricante", format="%.2f €", width="small"),
                    "€_Fac":      st.column_config.NumberColumn("€ Facturado",  format="%.2f €", width="small"),
                    "Garantía":   st.column_config.CheckboxColumn("Garantía?",  width="small"),
                    "G_hasta":    st.column_config.TextColumn("Garantía hasta", width="small"),
                    "Albarán":    st.column_config.CheckboxColumn("Albarán ✓",  width="small"),
                    "Fotos":      st.column_config.CheckboxColumn("Fotos ✓",    width="small"),
                    "Firma":      st.column_config.CheckboxColumn("Firma ✓",    width="small"),
                },
                use_container_width=True, hide_index=True, num_rows="dynamic", key="ots_editor"
            )
            if st.button("💾 Guardar OTs", type="primary"):
                save_mant(mes_sel, {"ots": edited_ots.to_dict("records"), "factura": fac_saved})
                st.success(f"✅ {len(edited_ots)} OTs guardadas — {mes_sel}")
                st.rerun()
        else:
            st.info("Sin OTs este mes. Pulsa '➕ Añadir fila OT' para empezar.")

    # ── TAB FACTURA ───────────────────────────────────────────────
    with tab_fac:
        st.markdown("### 🧾 Factura del proveedor — " + mes_sel)
        st.caption("Introduce las líneas de la factura recibida para cruzarlas con las OTs.")

        c1, c2 = st.columns(2)
        with c1:
            prov_nombre = st.text_input("Proveedor", value=fac_saved.get("proveedor",""))
        with c2:
            prov_num = st.text_input("Nº Factura", value=fac_saved.get("numero",""))

        lineas = fac_saved.get("lineas", [])
        if st.button("➕ Añadir línea factura"):
            lineas.append({"Concepto":"","Unidades":1.0,"€_ud":0.0,"Total":0.0,"Tipo":"Mano de obra"})
            save_mant(mes_sel, {"ots": ots_saved, "factura": {"proveedor":prov_nombre,"numero":prov_num,"lineas":lineas}})
            st.rerun()

        if lineas:
            df_fac = pd.DataFrame(lineas)
            edited_fac = st.data_editor(
                df_fac,
                column_config={
                    "Concepto":  st.column_config.TextColumn("Concepto",   width="large"),
                    "Unidades":  st.column_config.NumberColumn("Uds",      format="%.2f", width="small"),
                    "€_ud":      st.column_config.NumberColumn("€/ud",     format="%.2f €", width="small"),
                    "Total":     st.column_config.NumberColumn("Total €",  format="%.2f €", width="small"),
                    "Tipo":      st.column_config.SelectboxColumn("Tipo",  options=TIPO_FAC_OPTS, width="medium"),
                },
                use_container_width=True, hide_index=True, num_rows="dynamic", key="fac_editor"
            )
            total_base = edited_fac["Total"].sum()
            st.markdown(f"**Base imponible: `{total_base:,.2f} €` · IVA 21%: `{total_base*0.21:,.2f} €` · Total: `{total_base*1.21:,.2f} €`**")
            if st.button("💾 Guardar factura", type="primary"):
                save_mant(mes_sel, {"ots": ots_saved, "factura": {"proveedor":prov_nombre,"numero":prov_num,"lineas":edited_fac.to_dict("records")}})
                st.success("✅ Factura guardada")
                st.rerun()
        else:
            st.info("Sin líneas de factura. Añade al menos una línea.")

    # ── TAB AUDITORÍA ─────────────────────────────────────────────
    with tab_audit:
        st.markdown("### 🔍 Auditoría — 3 Filtros automáticos")
        if not ots_saved:
            st.warning("Introduce y guarda las OTs en la pestaña anterior primero.")
        else:
            df = pd.DataFrame(ots_saved)

            # Filtro 1: Garantías
            st.markdown("#### Filtro 1 · Garantías")
            gdf = df[df["Garantía"] == True]
            if gdf.empty:
                st.success("✓ Ninguna OT en período de garantía — todo facturable.")
            else:
                st.error(f"⚠ {len(gdf)} OT(s) sobre equipo en garantía — NO cobrable(s):")
                st.dataframe(gdf[["Centro","Descripción","G_hasta","€_Fac"]], use_container_width=True, hide_index=True)

            # Filtro 2: SLA tiempos
            st.markdown("#### Filtro 2 · SLA Tiempos de respuesta")
            sla_rows = []
            for _, r in df.iterrows():
                p = r.get("Prioridad","")
                sla_max = PRIO_SLA.get(p, 72)
                sla_rows.append({**r, "SLA máx (h)": sla_max})
            st.caption("Comprueba manualmente que los tiempos de respuesta (Apertura→Cierre) cumplen el SLA según prioridad.")
            sla_df = pd.DataFrame(sla_rows)[["Centro","Prioridad","Apertura","Cierre","SLA máx (h)","Horas"]]
            st.dataframe(sla_df, use_container_width=True, hide_index=True)

            # Filtro 3: Márgenes materiales
            st.markdown("#### Filtro 3 · Margen de materiales (límite 15%)")
            mat_df = df[df["€_Fab"] > 0].copy()
            if mat_df.empty:
                st.info("Sin materiales con precio de fabricante registrado.")
            else:
                mat_df["Margen %"] = ((mat_df["€_Fac"] - mat_df["€_Fab"]) / mat_df["€_Fab"] * 100).round(1)
                alertas_mat = mat_df[mat_df["Margen %"] > MARGEN_MAT_MAX]
                if alertas_mat.empty:
                    st.success(f"✓ Todos los márgenes dentro del límite ({MARGEN_MAT_MAX}%)")
                else:
                    st.warning(f"⚠ {len(alertas_mat)} material(es) superan el margen del {MARGEN_MAT_MAX}%:")
                    st.dataframe(alertas_mat[["Centro","Material","€_Fab","€_Fac","Margen %"]], use_container_width=True, hide_index=True)

            # Desplazamientos
            lineas = fac_saved.get("lineas", [])
            despl = [l for l in lineas if l.get("Tipo") == "Desplazamiento"]
            if despl:
                st.markdown("#### Filtro 3b · Desplazamientos (contrato: 25 €/visita)")
                for d in despl:
                    n_vis = len(ots_saved)
                    max_despl = n_vis * COSTE_DESPL_SLA
                    fac_despl = d.get("Total", 0)
                    diff = fac_despl - max_despl
                    if diff > 0:
                        st.error(f"⚠ Desplazamientos facturados: **{fac_despl:.0f} €** · Máx. contractual ({n_vis} visitas × {COSTE_DESPL_SLA}€): **{max_despl:.0f} €** · Sobrecoste: **{diff:.0f} €**")
                    else:
                        st.success(f"✓ Desplazamientos OK: {fac_despl:.0f} € ≤ máx. {max_despl:.0f} €")

    # ── TAB APROBACIÓN ────────────────────────────────────────────
    with tab_apr_v:
        st.markdown("### ✅ Aprobación y envío a Valentina")
        if not ots_saved or not fac_saved.get("lineas"):
            st.warning("Completa primero las OTs y la factura.")
        else:
            lineas_fac = fac_saved.get("lineas", [])
            total_base = sum(l.get("Total", 0) for l in lineas_fac)
            garantia_descuento = sum(r.get("€_Fac", 0) for r in ots_saved if r.get("Garantía"))

            st.markdown(f"**Proveedor:** {fac_saved.get('proveedor','—')} · **Factura:** {fac_saved.get('numero','—')} · **Mes:** {mes_sel}")
            st.divider()

            k1, k2, k3 = st.columns(3)
            k1.metric("Total facturado (base)", f"{total_base:,.2f} €")
            k2.metric("Descuento garantías", f"-{garantia_descuento:,.2f} €", delta=f"-{garantia_descuento:,.2f} €", delta_color="inverse")
            k3.metric("Total a pagar (base)", f"{(total_base - garantia_descuento):,.2f} €")

            st.markdown("#### Asignación de centros de coste")
            cc_data = []
            for l in lineas_fac:
                tipo = l.get("Tipo","MO")
                prefijo = "CAPEX" if tipo == "Inversión" else "OPEX"
                cat_code = {"Mano de obra":"MO","Material":"MAT","Desplazamiento":"DESPL","Preventivo":"PREV"}.get(tipo, "MO")
                cc_data.append({
                    "Concepto": l.get("Concepto",""),
                    "Total €":  l.get("Total", 0.0),
                    "Código coste": f"{prefijo}-XXX-{cat_code}",
                    "Notas validación": "",
                })
            cc_df = pd.DataFrame(cc_data)
            edited_cc = st.data_editor(
                cc_df,
                column_config={
                    "Concepto":         st.column_config.TextColumn(disabled=True, width="large"),
                    "Total €":          st.column_config.NumberColumn(disabled=True, format="%.2f €", width="small"),
                    "Código coste":     st.column_config.TextColumn("Código coste (edita)", width="medium"),
                    "Notas validación": st.column_config.TextColumn("Notas", width="large"),
                },
                use_container_width=True, hide_index=True, num_rows="fixed", key="cc_editor"
            )

            total_ajustado_iva = (total_base - garantia_descuento) * 1.21
            st.markdown(f"### Total a pagar con IVA: **{total_ajustado_iva:,.2f} €**")

            if st.button("📤 Marcar como enviado a Valentina", type="primary"):
                aprobacion = {
                    "fecha": str(hoy),
                    "proveedor": fac_saved.get("proveedor",""),
                    "factura": fac_saved.get("numero",""),
                    "total_base": total_base,
                    "descuento_garantias": garantia_descuento,
                    "total_pagar_iva": total_ajustado_iva,
                    "codigos_coste": edited_cc.to_dict("records"),
                    "aprobado_por": "Darío A. López",
                }
                mant_data_updated = load_mant(mes_sel)
                mant_data_updated["aprobacion"] = aprobacion
                save_mant(mes_sel, mant_data_updated)
                st.success(f"✅ Enviado a Valentina — {total_ajustado_iva:,.2f} € · {str(hoy)}")
                st.balloons()

    st.stop()  # mantenimiento: no renderizar secciones de obra

# ══════════════════════════════════════════════════════════════════
# MODO: CAPEX/OPEX — CICLO DE VIDA
# ══════════════════════════════════════════════════════════════════
if pkey == "capex_opex":
    reqs = load_capex()

    # ── BOTÓN NUEVA PETICIÓN ──────────────────────────────────────
    col_hdr, col_btn = st.columns([5,1])
    with col_btn:
        if st.button("➕ Nueva petición", type="primary"):
            ref_nueva = f"REQ-{hoy.strftime('%y%m%d')}-{len(reqs)+1:03d}"
            reqs.append(nueva_peticion(ref_nueva))
            save_capex(reqs)
            st.rerun()

    # ── KPIs ──────────────────────────────────────────────────────
    n_total   = len(reqs)
    n_esper   = len([r for r in reqs if r.get("estado_peticion") == "Esperando precio"])
    n_ejec    = len([r for r in reqs if r.get("estado_ejecucion") == "En curso"])
    n_bloq    = len([r for r in reqs if r.get("estado_ejecucion") == "Bloqueado"])
    n_contab  = len([r for r in reqs if r.get("estado_cierre") == "Traspasado Contabilidad"])
    tot_pres  = sum(r.get("importe_presupuestado", 0) for r in reqs)
    tot_fac   = sum(r.get("importe_facturado", 0) for r in reqs)
    # garantías próximas a vencer (< 90 días)
    from datetime import datetime as dt_
    n_garantia_alert = 0
    for r in reqs:
        vg = r.get("vencimiento_garantia","")
        if vg:
            try:
                dias = (dt_.strptime(vg, "%Y-%m-%d").date() - hoy).days
                if 0 <= dias <= 90:
                    n_garantia_alert += 1
            except ValueError:
                pass

    k1,k2,k3,k4,k5 = st.columns(5)
    k1.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:var(--blue,#1A5C8A)">{n_total}</div><div class="kpi-lbl">Total peticiones</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:var(--amber,#B7610A)">{n_esper}</div><div class="kpi-lbl">Esperando precio</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:var(--amber,#B7610A)">{n_ejec}</div><div class="kpi-lbl">En ejecución</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:#C0392B">{n_bloq}</div><div class="kpi-lbl">Bloqueadas</div></div>', unsafe_allow_html=True)
    k5.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:#C0392B">{n_garantia_alert}</div><div class="kpi-lbl">Garantías próx. vencer</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── TAB PIPELINE (vista global) ───────────────────────────────
    with tab_pipeline:
        st.markdown("#### Vista completa — todas las fases")
        if not reqs:
            st.info("Sin peticiones. Pulsa '➕ Nueva petición' para empezar.")
        else:
            # Filtros
            fc1, fc2, fc3, fc4 = st.columns(4)
            with fc1:
                f_centro = st.selectbox("Centro", ["Todos"] + TODOS_CENTROS, key="f_centro_pip")
            with fc2:
                f_tipo = st.selectbox("Tipo", ["Todos","CAPEX","OPEX"], key="f_tipo_pip")
            with fc3:
                f_pet = st.selectbox("Estado petición", ["Todos"] + ESTADO_PET_OPTS, key="f_pet_pip")
            with fc4:
                f_ejec = st.selectbox("Estado ejecución", ["Todos"] + ESTADO_EJEC_OPTS, key="f_ejec_pip")

            reqs_f = reqs
            if f_centro != "Todos": reqs_f = [r for r in reqs_f if r.get("centro") == f_centro]
            if f_tipo   != "Todos": reqs_f = [r for r in reqs_f if r.get("tipo")   == f_tipo]
            if f_pet    != "Todos": reqs_f = [r for r in reqs_f if r.get("estado_peticion") == f_pet]
            if f_ejec   != "Todos": reqs_f = [r for r in reqs_f if r.get("estado_ejecucion") == f_ejec]

            df_pip = pd.DataFrame(reqs_f)[[
                "ref","centro","tipo","concepto","proveedor",
                "estado_peticion","importe_presupuestado",
                "estado_ejecucion","notas",
                "importe_facturado","estado_cierre",
                "vencimiento_garantia"
            ]] if reqs_f else pd.DataFrame()

            if not df_pip.empty:
                st.dataframe(df_pip, use_container_width=True, hide_index=True,
                    column_config={
                        "ref":                  st.column_config.TextColumn("Ref", width="small"),
                        "centro":               st.column_config.TextColumn("Centro", width="small"),
                        "tipo":                 st.column_config.TextColumn("Tipo", width="small"),
                        "concepto":             st.column_config.TextColumn("Concepto", width="large"),
                        "proveedor":            st.column_config.TextColumn("Proveedor", width="medium"),
                        "estado_peticion":      st.column_config.TextColumn("F1 · Estado", width="medium"),
                        "importe_presupuestado":st.column_config.NumberColumn("Presup. €", format="%.0f €", width="small"),
                        "estado_ejecucion":     st.column_config.TextColumn("F2 · Ejecución", width="medium"),
                        "notas":                st.column_config.TextColumn("Notas", width="medium"),
                        "importe_facturado":    st.column_config.NumberColumn("Facturado €", format="%.0f €", width="small"),
                        "estado_cierre":        st.column_config.TextColumn("F3 · Cierre", width="medium"),
                        "vencimiento_garantia": st.column_config.TextColumn("F4 · Garantía hasta", width="small"),
                    })
                tot_p = sum(r.get("importe_presupuestado",0) for r in reqs_f)
                tot_f = sum(r.get("importe_facturado",0) for r in reqs_f)
                desv = tot_f - tot_p
                st.markdown(f"**Presupuestado: `{tot_p:,.0f} €` · Facturado: `{tot_f:,.0f} €` · Desviación: `{'+'if desv>=0 else ''}{desv:,.0f} €`**")
            else:
                st.info("Sin resultados para ese filtro.")

    # ── TAB F1 LICITACIÓN ─────────────────────────────────────────
    with tab_licita:
        st.markdown("#### Fase 1 · Licitación — Peticiones de presupuesto")
        st.caption("Edita directamente. Guarda al terminar.")
        if reqs:
            df_f1 = pd.DataFrame(reqs)
            edited_f1 = st.data_editor(
                df_f1[["ref","centro","tipo","concepto","proveedor","fecha_solicitud","estado_peticion","importe_presupuestado"]],
                column_config={
                    "ref":                   st.column_config.TextColumn("Ref", disabled=True, width="small"),
                    "centro":                st.column_config.SelectboxColumn("Centro",    options=TODOS_CENTROS, width="small"),
                    "tipo":                  st.column_config.SelectboxColumn("Tipo",      options=TIPO_OPTS, width="small"),
                    "concepto":              st.column_config.TextColumn("Concepto",       width="large"),
                    "proveedor":             st.column_config.SelectboxColumn("Proveedor", options=TODOS_PROVEEDORES, width="medium"),
                    "fecha_solicitud":       st.column_config.TextColumn("Fecha solicitud",width="small"),
                    "estado_peticion":       st.column_config.SelectboxColumn("Estado",    options=ESTADO_PET_OPTS, width="medium"),
                    "importe_presupuestado": st.column_config.NumberColumn("Importe €",    format="%.2f €", width="small"),
                },
                use_container_width=True, hide_index=True, num_rows="fixed", key="f1_editor"
            )
            if st.button("💾 Guardar Fase 1", type="primary", key="save_f1"):
                for i, row in edited_f1.iterrows():
                    reqs[i].update({k: row[k] for k in edited_f1.columns})
                save_capex(reqs)
                st.success("✅ Fase 1 guardada")
                st.rerun()
        else:
            st.info("Añade peticiones con el botón '➕ Nueva petición'.")

    # ── TAB F2 EJECUCIÓN ──────────────────────────────────────────
    with tab_ejec:
        st.markdown("#### Fase 2 · Ejecución — Trabajos activos")
        if reqs:
            df_f2 = pd.DataFrame(reqs)
            edited_f2 = st.data_editor(
                df_f2[["ref","centro","concepto","proveedor","fecha_fin_estimada","estado_ejecucion","notas"]],
                column_config={
                    "ref":               st.column_config.TextColumn("Ref", disabled=True, width="small"),
                    "centro":            st.column_config.TextColumn("Centro", disabled=True, width="small"),
                    "concepto":          st.column_config.TextColumn("Concepto", disabled=True, width="large"),
                    "proveedor":         st.column_config.TextColumn("Proveedor", disabled=True, width="medium"),
                    "fecha_fin_estimada":st.column_config.TextColumn("Fin estimado", width="small"),
                    "estado_ejecucion":  st.column_config.SelectboxColumn("Estado", options=ESTADO_EJEC_OPTS, width="medium"),
                    "notas":             st.column_config.TextColumn("Notas / restricciones", width="large"),
                },
                use_container_width=True, hide_index=True, num_rows="fixed", key="f2_editor"
            )
            if st.button("💾 Guardar Fase 2", type="primary", key="save_f2"):
                for i, row in edited_f2.iterrows():
                    reqs[i].update({k: row[k] for k in edited_f2.columns if k not in ["ref","centro","concepto","proveedor"]})
                save_capex(reqs)
                st.success("✅ Fase 2 guardada")
                st.rerun()

    # ── TAB F3 FACTURACIÓN ────────────────────────────────────────
    with tab_factura_cv:
        st.markdown("#### Fase 3 · Facturación — Control económico")
        if reqs:
            df_f3 = pd.DataFrame(reqs)
            edited_f3 = st.data_editor(
                df_f3[["ref","centro","concepto","importe_presupuestado","importe_facturado","estado_cierre"]],
                column_config={
                    "ref":                   st.column_config.TextColumn("Ref", disabled=True, width="small"),
                    "centro":                st.column_config.TextColumn("Centro", disabled=True, width="small"),
                    "concepto":              st.column_config.TextColumn("Concepto", disabled=True, width="large"),
                    "importe_presupuestado": st.column_config.NumberColumn("Presup. €", format="%.2f €", width="small"),
                    "importe_facturado":     st.column_config.NumberColumn("Facturado €", format="%.2f €", width="small"),
                    "estado_cierre":         st.column_config.SelectboxColumn("Estado cierre", options=ESTADO_CIER_OPTS, width="medium"),
                },
                use_container_width=True, hide_index=True, num_rows="fixed", key="f3_editor"
            )
            # Desviaciones
            df_tmp = edited_f3.copy()
            df_tmp["Desv. €"] = df_tmp["importe_facturado"] - df_tmp["importe_presupuestado"]
            alertas_desv = df_tmp[df_tmp["Desv. €"] > 0]
            if not alertas_desv.empty:
                st.warning(f"⚠ {len(alertas_desv)} partida(s) con sobrecoste:")
                st.dataframe(alertas_desv[["ref","concepto","importe_presupuestado","importe_facturado","Desv. €"]], use_container_width=True, hide_index=True)
            if st.button("💾 Guardar Fase 3", type="primary", key="save_f3"):
                for i, row in edited_f3.iterrows():
                    reqs[i].update({k: row[k] for k in ["importe_presupuestado","importe_facturado","estado_cierre"]})
                save_capex(reqs)
                st.success("✅ Fase 3 guardada")
                st.rerun()

    # ── TAB F4 GARANTÍAS ──────────────────────────────────────────
    with tab_garantia:
        st.markdown("#### Fase 4 · Garantías — Asset Management")
        st.caption("Registra fecha de recepción y vencimiento. El sistema alertará cuando queden < 90 días.")
        if reqs:
            df_f4 = pd.DataFrame(reqs)
            edited_f4 = st.data_editor(
                df_f4[["ref","centro","concepto","proveedor","fecha_recepcion","garantia_meses","vencimiento_garantia"]],
                column_config={
                    "ref":                  st.column_config.TextColumn("Ref", disabled=True, width="small"),
                    "centro":               st.column_config.TextColumn("Centro", disabled=True, width="small"),
                    "concepto":             st.column_config.TextColumn("Concepto", disabled=True, width="large"),
                    "proveedor":            st.column_config.TextColumn("Proveedor", disabled=True, width="medium"),
                    "fecha_recepcion":      st.column_config.TextColumn("Recepción real", width="small"),
                    "garantia_meses":       st.column_config.NumberColumn("Garantía (meses)", format="%d m", width="small"),
                    "vencimiento_garantia": st.column_config.TextColumn("Vence (YYYY-MM-DD)", width="small"),
                },
                use_container_width=True, hide_index=True, num_rows="fixed", key="f4_editor"
            )
            # Alertas garantías próximas
            alertas_g = []
            for _, row in edited_f4.iterrows():
                vg = row.get("vencimiento_garantia","")
                if vg:
                    try:
                        dias = (dt_.strptime(vg, "%Y-%m-%d").date() - hoy).days
                        if 0 <= dias <= 90:
                            alertas_g.append({"Ref": row["ref"], "Concepto": row["concepto"], "Días restantes": dias, "Vence": vg})
                    except ValueError:
                        pass
            if alertas_g:
                st.warning(f"⚠ {len(alertas_g)} garantía(s) vencen en menos de 90 días:")
                st.dataframe(pd.DataFrame(alertas_g), use_container_width=True, hide_index=True)
            if st.button("💾 Guardar Fase 4", type="primary", key="save_f4"):
                for i, row in edited_f4.iterrows():
                    reqs[i].update({k: row[k] for k in ["fecha_recepcion","garantia_meses","vencimiento_garantia"]})
                save_capex(reqs)
                st.success("✅ Fase 4 guardada")
                st.rerun()
    st.stop()  # capex_opex: no renderizar secciones de obra

# ══════════════════════════════════════════════════════════════════
# TAB: ACTAS
# ══════════════════════════════════════════════════════════════════
with tab_actas:
    col_new, col_list = st.columns([1, 1.55], gap="large")

    with col_new:
        st.markdown("### ✍️ Nueva Acta")
        with st.form("form_acta", clear_on_submit=True):
            fecha_acta = st.date_input("Fecha del acta", value=hoy)
            texto_raw = st.text_area(
                "Notas de campo — texto libre",
                height=280,
                placeholder=(
                    "Pega o escribe tus notas aquí.\n\n"
                    "Ejemplos (Chamartín):\n"
                    "- Munir: inicio demolición PB zona cardio. Huecos S-2 cerrados.\n"
                    "- Gonzalo Cador: medición bajante S-2. Pendiente cata cotas.\n"
                    "- Álvaro Chuso: confirma recepción renders piscina.\n"
                    "- Mañana 09:00 reunión Ángel + contratas."
                ),
            )
            resumen_manual = st.text_input("Resumen ejecutivo (opcional)", placeholder="Deja vacío para auto-generar")
            c1, c2 = st.columns(2)
            with c1:
                prioridad = st.selectbox("Prioridad", ["normal", "alta", "urgente"])
            with c2:
                estado = st.selectbox("Estado", ["borrador", "revisado", "firmado"])
            guardar = st.form_submit_button("💾 Guardar Acta", use_container_width=True, type="primary")

        if guardar:
            if not texto_raw.strip():
                st.warning("Escribe las notas del día antes de guardar.")
            else:
                parsed = parsear(texto_raw, proyecto["gremio_kw"])
                s_num  = semana_proyecto(fecha_acta, proyecto["inicio_ref"])
                acta_id = f"ACT-{pkey[:3].upper()}-{fecha_acta.strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
                nueva = {
                    "id":                 acta_id,
                    "proyecto":           pkey,
                    "fecha":              fecha_acta.isoformat(),
                    "semana":             s_num,
                    "texto_original":     texto_raw,
                    "resumen":            resumen_manual.strip() or f"Acta S{s_num} — {fecha_acta.strftime('%d/%m/%Y')}",
                    "secciones":          parsed["secciones"],
                    "incidencias":        parsed["incidencias"],
                    "agenda_manana":      parsed["agenda_manana"],
                    "gremios_incidencia": parsed["gremios_incidencia"],
                    "prioridad":          prioridad,
                    "estado":             estado,
                    "created_at":         datetime.now().isoformat(),
                }
                actas_all = load_actas(proyecto["data_file"])
                actas_all = [a for a in actas_all if a["fecha"] != fecha_acta.isoformat()]
                actas_all.append(nueva)
                actas_all.sort(key=lambda x: x["fecha"], reverse=True)
                save_actas(actas_all, proyecto["data_file"])
                st.success(f"✅ Acta guardada — {acta_id}")
                st.rerun()

        st.markdown("---")
        st.markdown("#### 🔍 Previsualizar parser")
        preview_txt = st.text_area("Texto a analizar", height=110, key="preview_input",
                                   placeholder="Pega aquí para ver cómo clasifica el parser...")
        if st.button("Analizar texto", key="btn_preview"):
            if preview_txt.strip():
                res = parsear(preview_txt, proyecto["gremio_kw"])
                for g, c in res["secciones"].items():
                    st.markdown(f"- **{g}**: {c[:80]}{'…' if len(c) > 80 else ''}")
                if res["incidencias"]:
                    st.markdown("**Incidencias:** " + " · ".join(res["incidencias"][:3]))
                if res["agenda_manana"]:
                    st.markdown("**Agenda mañana:** " + res["agenda_manana"][:120])

    with col_list:
        st.markdown("### 📂 Registro de Actas")
        fc1, fc2, fc3, fc4 = st.columns([1.1, 1.1, 1, 1])
        with fc1: f_desde = st.date_input("Desde", value=date(2026, 1, 1), key="fd")
        with fc2: f_hasta = st.date_input("Hasta", value=date(2027, 12, 31), key="fh")
        with fc3: f_prio  = st.selectbox("Prioridad", ["todas", "urgente", "alta", "normal"], key="fp")
        with fc4: f_est   = st.selectbox("Estado", ["todos", "borrador", "revisado", "firmado"], key="fe")

        actas_all = load_actas(proyecto["data_file"])
        actas_vis = [
            a for a in actas_all
            if f_desde.isoformat() <= a["fecha"] <= f_hasta.isoformat()
            and (f_prio == "todas" or a.get("prioridad") == f_prio)
            and (f_est  == "todos" or a.get("estado")    == f_est)
        ]

        ba1, ba2 = st.columns([2, 1])
        with ba1:
            st.caption(f"**{len(actas_vis)}** acta(s) · Semana {sem} · {hoy.strftime('%d/%m/%Y')}")
        with ba2:
            gen_btn = st.button(f"📄 Acta Semanal S{sem}", use_container_width=True)

        if gen_btn:
            actas_semana = [
                a for a in actas_all
                if lunes.isoformat() <= a["fecha"] <= (lunes + timedelta(days=6)).isoformat()
            ]
            if actas_semana:
                st.session_state["reporte_semanal"] = (actas_semana, sem)
            else:
                st.info("No hay actas esta semana.")

        if "reporte_semanal" in st.session_state:
            acs, s = st.session_state["reporte_semanal"]
            with st.expander(f"📋 BORRADOR — ACTA SEMANAL S{s}", expanded=True):
                html_rep = html_semanal(acs, s, proyecto)
                st.download_button(
                    label="⬇️ Descargar HTML",
                    data=html_rep.encode("utf-8"),
                    file_name=f"ACTA_SEMANAL_{proyecto['ref']}_S{s}_{hoy.strftime('%d%m%Y')}.html",
                    mime="text/html",
                    use_container_width=True,
                )
                for a in acs:
                    st.markdown(f"- {datetime.fromisoformat(a['fecha']).strftime('%A %d/%m').capitalize()} — {a.get('resumen','')}")

        st.markdown('<div class="scroll-wrap">', unsafe_allow_html=True)

        if not actas_vis:
            st.markdown("""
            <div style="text-align:center;padding:40px 20px;color:#aab;background:#fff;border-radius:8px;">
              <div style="font-size:28px;margin-bottom:8px;">📋</div>
              <div style="font-size:13px;">Sin actas en el rango seleccionado.</div>
            </div>""", unsafe_allow_html=True)

        for acta in actas_vis:
            fecha_fmt = datetime.fromisoformat(acta["fecha"]).strftime("%A %d/%m/%Y").capitalize()
            prio  = acta.get("prioridad", "normal")
            est   = acta.get("estado", "borrador")
            s_num = acta.get("semana", "?")

            prio_badge = {"urgente": ("b-red","🔴 Urgente"), "alta": ("b-amber","🟡 Alta"), "normal": ("b-green","🟢 Normal")}.get(prio, ("b-green","Normal"))
            est_badge  = {"borrador": ("b-blue","Borrador"), "revisado": ("b-amber","Revisado"), "firmado": ("b-green","✓ Firmado")}.get(est, ("b-blue","Borrador"))

            inc_html  = "".join(f'<div style="font-size:11px;color:#c0392b;">⚠️ {i[:90]}{"…" if len(i)>90 else ""}</div>' for i in acta.get("incidencias",[])[:3])
            gremios_h = "".join(f'<span class="gtag">{g}</span>' for g in acta.get("gremios_incidencia",[]))
            agenda_h  = ""
            if acta.get("agenda_manana"):
                agt = acta["agenda_manana"].replace("\n"," · ")[:120]
                agenda_h = f'<div style="font-size:11px;color:#555;border-top:1px solid #f0f2f7;padding-top:5px;margin-top:5px;">📅 {agt}</div>'

            card_cls = {"urgente": "acta-card acta-card-urgente", "alta": "acta-card acta-card-alta"}.get(prio, "acta-card")

            st.markdown(f"""
            <div class="{card_cls}">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:7px;">
                <span style="font-size:14px;font-weight:700;">📋 {fecha_fmt}
                  <span style="font-size:11px;color:#999;margin-left:8px;">S{s_num}</span>
                </span>
                <div style="display:flex;gap:5px;">
                  <span class="badge {prio_badge[0]}">{prio_badge[1]}</span>
                  <span class="badge {est_badge[0]}">{est_badge[1]}</span>
                </div>
              </div>
              <div style="font-size:12px;color:#444;margin-bottom:5px;">{acta.get('resumen','')}</div>
              {f'<div style="margin-bottom:3px;">{inc_html}</div>' if inc_html else ''}
              {f'<div style="margin-bottom:3px;">{gremios_h}</div>' if gremios_h else ''}
              {agenda_h}
            </div>""", unsafe_allow_html=True)

            with st.expander(f"Ver / editar — {acta['id']}"):
                t1, t2, t3, t4 = st.tabs(["📝 Original", "🔧 Por Gremio", "⚠️ Incidencias", "🗑️ Eliminar"])
                with t1:
                    st.text_area("Texto original", value=acta.get("texto_original",""), height=160,
                                 key=f"txt_{acta['id']}", disabled=True)
                with t2:
                    secs = acta.get("secciones", {})
                    if secs:
                        for gremio, contenido in secs.items():
                            st.markdown(f"**{gremio}**")
                            st.markdown(contenido.replace("\n","  \n"))
                            st.divider()
                    else:
                        st.info("No se detectaron secciones por gremio.")
                with t3:
                    incs = acta.get("incidencias", [])
                    for inc in incs: st.error(f"⚠️ {inc}")
                    if not incs: st.success("Sin incidencias.")
                with t4:
                    st.warning(f"¿Eliminar **{acta['id']}** ({fecha_fmt})? No se puede deshacer.")
                    if st.button("🗑️ Confirmar eliminación", key=f"del_{acta['id']}", type="secondary"):
                        updated = [a for a in load_actas(proyecto["data_file"]) if a["id"] != acta["id"]]
                        save_actas(updated, proyecto["data_file"])
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# TAB: DASHBOARD (solo Chamartín)
# ══════════════════════════════════════════════════════════════════
if tab_dash:
    with tab_dash:
        # Cargar datos desde JSON (persiste entre sesiones)
        dash = load_dashboard()
        contratas  = dash.get("contratas",  CONTRATAS_CHAMARTIN)
        decisiones = dash.get("decisiones", DECISIONES_CHAMARTIN)
        actualizado = dash.get("actualizado", str(date.today()))

        # ── KPIs calculados en vivo ──
        n_total   = len(contratas)
        n_pres    = len([c for c in contratas if c["estado"] in ("revision","aprobado","aprobacion")])
        n_bloq    = len([c for c in contratas if c["estado"] == "bloqueado"])
        n_dec_abi = len([d for d in decisiones if not d.get("resuelta", False)])
        # primer pago: importe de la primera contrata con aprobacion pendiente
        primer_pago = next((c["importe"] for c in contratas if c["estado"] == "aprobacion"), "—")

        st.markdown(f"**Estado · Actualizado {actualizado} · Semana {sem}**")
        st.divider()

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:#1A5C8A;">{n_total}</div><div class="kpi-lbl">Contratas activas</div></div>', unsafe_allow_html=True)
        with k2:
            st.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:#B7610A;">{n_pres}</div><div class="kpi-lbl">Presupuestos recibidos</div></div>', unsafe_allow_html=True)
        with k3:
            st.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:#C0392B;">{n_bloq}</div><div class="kpi-lbl">Contratas bloqueadas</div></div>', unsafe_allow_html=True)
        with k4:
            st.markdown(f'<div class="kpi-box"><div class="kpi-val" style="color:#C0392B;">{n_dec_abi}</div><div class="kpi-lbl">Decisiones abiertas</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Tabla contratas editable ──
        st.markdown("#### Contratas · Estado de Licitación")
        st.caption("Edita directamente en la tabla y pulsa **Guardar cambios**.")

        ESTADO_OPTS = ["bloqueado","aprobacion","revision","pendiente","sin_contacto","aprobado"]
        VISITA_OPTS = ["✓","✗","~"]

        df = pd.DataFrame([{
            "Empresa":      c["empresa"],
            "Especialidad": c["rol"],
            "Visita":       c["visita"],
            "Presupuesto":  c["presupuesto"],
            "Importe":      c["importe"],
            "Estado":       c["estado"],
            "Notas":        c["notas"],
        } for c in contratas])

        edited = st.data_editor(
            df,
            column_config={
                "Empresa":      st.column_config.TextColumn("Empresa",      disabled=True, width="medium"),
                "Especialidad": st.column_config.TextColumn("Especialidad", width="medium"),
                "Visita":       st.column_config.SelectboxColumn("Visita",  options=VISITA_OPTS, width="small"),
                "Presupuesto":  st.column_config.TextColumn("Presupuesto",  width="small"),
                "Importe":      st.column_config.TextColumn("Importe",      width="small"),
                "Estado":       st.column_config.SelectboxColumn("Estado",  options=ESTADO_OPTS, width="medium"),
                "Notas":        st.column_config.TextColumn("Notas",        width="large"),
            },
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            key="contratas_editor",
        )

        if st.button("💾 Guardar cambios en contratas", type="primary"):
            updated = []
            for i, row in edited.iterrows():
                c = contratas[i].copy()
                c.update({
                    "rol":        row["Especialidad"],
                    "visita":     row["Visita"],
                    "presupuesto": row["Presupuesto"],
                    "importe":    row["Importe"],
                    "estado":     row["Estado"],
                    "notas":      row["Notas"],
                })
                updated.append(c)
            save_dashboard(updated, decisiones)
            st.success(f"✅ Dashboard guardado — {date.today().strftime('%d/%m/%Y')}")
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Decisiones + Pendientes ──
        dc1, dc2 = st.columns(2, gap="large")

        with dc1:
            st.markdown("#### Decisiones abiertas")
            st.caption("Marca como resuelta cuando se desbloquee.")
            changed = False
            for i, d in enumerate(decisiones):
                cls = "dec-item dec-crit" if d["nivel"] == "critico" else "dec-item dec-imp"
                dot = "#C0392B" if d["nivel"] == "critico" else "#B7610A"
                resuelta = d.get("resuelta", False)

                col_txt, col_chk = st.columns([11, 1])
                with col_txt:
                    op = "~~" if resuelta else ""
                    st.markdown(
                        f'<div class="{cls}" style="{"opacity:.45;" if resuelta else ""}">'
                        f'<div class="dec-dot" style="background:{dot};"></div>'
                        f'<div>'
                        f'<div style="font-size:12px;font-weight:600;color:#111;">{op}{d["titulo"]}{op}</div>'
                        f'<div style="font-size:11px;color:#776F63;margin-top:2px;">{d["sub"]}</div>'
                        f'</div></div>',
                        unsafe_allow_html=True
                    )
                with col_chk:
                    nueva = st.checkbox("✓", value=resuelta, key=f"dec_{i}", label_visibility="collapsed")
                    if nueva != resuelta:
                        decisiones[i]["resuelta"] = nueva
                        changed = True

            if changed:
                save_dashboard(contratas, decisiones)
                st.rerun()

        with dc2:
            st.markdown("#### Pendientes por responsable")
            for owner, items in PENDIENTES_CHAMARTIN.items():
                st.markdown(f"**{owner}**")
                for urgencia, texto in items:
                    color  = "#C0392B" if urgencia == "u" else "#555"
                    border = "#C0392B" if urgencia == "u" else "#DDD8CE"
                    icon   = "🔴" if urgencia == "u" else "▸"
                    st.markdown(
                        f'<div style="font-size:12px;color:{color};padding:3px 8px;border-left:2px solid {border};margin-bottom:3px;">{icon} {texto}</div>',
                        unsafe_allow_html=True
                    )
                st.markdown("<br>", unsafe_allow_html=True)

        # ── Munir resumen ──
        st.divider()
        st.markdown("#### Munir · Presupuestos para aprobación")
        m1, m2, m3 = st.columns(3, gap="small")

        with m1:
            st.markdown("""<div class="presu-card ready">
              <div style="font-size:9px;font-weight:700;letter-spacing:1px;color:#776F63;text-transform:uppercase;margin-bottom:5px;">Presu 43 · Preparación</div>
              <div style="font-size:13px;font-weight:600;color:#111;margin-bottom:8px;">Zonas de trabajo</div>
              <div style="font-size:11px;color:#776F63;line-height:1.8;">
                Aseo + comedor trabajadores<br>Vallas · barreras · rampas<br>Trabajos extras ejecutados
              </div>
              <div style="border-top:1px solid #DDD8CE;margin-top:10px;padding-top:8px;display:flex;justify-content:space-between;align-items:baseline;">
                <span style="font-size:10px;color:#776F63;">Base 16.980 € + IVA</span>
                <span style="font-size:18px;font-weight:700;color:#1E7A54;">20.546 €</span>
              </div>
            </div>""", unsafe_allow_html=True)

        with m2:
            st.markdown("""<div class="presu-card ready">
              <div style="font-size:9px;font-weight:700;letter-spacing:1px;color:#776F63;text-transform:uppercase;margin-bottom:5px;">Presu 45 · Demolición</div>
              <div style="font-size:13px;font-weight:600;color:#111;margin-bottom:8px;">Demoliciones y cierres</div>
              <div style="font-size:11px;color:#776F63;line-height:1.8;">
                Demoliciones · abrir huecos<br>Cerrar huecos hormigón<br>Picar forjados ligeros
              </div>
              <div style="border-top:1px solid #DDD8CE;margin-top:10px;padding-top:8px;display:flex;justify-content:space-between;align-items:baseline;">
                <span style="font-size:10px;color:#776F63;">Base 33.000 € + IVA</span>
                <span style="font-size:18px;font-weight:700;color:#1E7A54;">39.930 €</span>
              </div>
            </div>""", unsafe_allow_html=True)

        with m3:
            st.markdown("""<div class="presu-card pte">
              <div style="font-size:9px;font-weight:700;letter-spacing:1px;color:#B7610A;text-transform:uppercase;margin-bottom:5px;">3ª Parte · PENDIENTE</div>
              <div style="font-size:13px;font-weight:600;color:#111;margin-bottom:8px;">Actualización estructural</div>
              <div style="font-size:11px;color:#776F63;line-height:1.8;">
                Forjado S-1 · Zapatas pilares<br>Huecos saneamiento<br>Arquetas
              </div>
              <div style="border-top:1px solid #DDD8CE;margin-top:10px;padding-top:8px;display:flex;justify-content:space-between;align-items:baseline;">
                <span style="font-size:10px;color:#B7610A;">Sin recibir de Munir</span>
                <span style="font-size:18px;font-weight:700;color:#B7610A;">— €</span>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#EDE9E1;border:1px solid #DDD8CE;border-radius:3px;padding:10px 16px;
                    display:flex;justify-content:space-between;align-items:center;margin-top:8px;">
          <div>
            <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:#776F63;">Total conocido (Presu 43 + 45)</div>
            <div style="font-size:11px;color:#776F63;margin-top:2px;">IVA incluido · Falta 3ª parte · Total final estimado: 80.000–100.000 €</div>
          </div>
          <span style="font-size:22px;font-weight:700;color:#B7610A;">60.476 €</span>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# TAB: SEMANAL
# ══════════════════════════════════════════════════════════════════
with tab_semanal:
    st.markdown("### 📄 Generador de Acta Semanal")
    s_sel = st.number_input("Número de semana de proyecto", min_value=1, max_value=100, value=sem)

    lunes_sel   = proyecto["inicio_ref"] + timedelta(weeks=int(s_sel) - 1)
    viernes_sel = lunes_sel + timedelta(days=4)

    actas_all = load_actas(proyecto["data_file"])
    actas_s   = [a for a in actas_all if lunes_sel.isoformat() <= a["fecha"] <= viernes_sel.isoformat()]

    st.caption(f"Semana {s_sel}: {lunes_sel.strftime('%d/%m')} – {viernes_sel.strftime('%d/%m/%Y')} · **{len(actas_s)} acta(s)**")

    if actas_s:
        html_rep = html_semanal(actas_s, s_sel, proyecto)
        st.download_button(
            label=f"⬇️ Descargar Acta Semanal S{s_sel} — {proyecto['ref']}",
            data=html_rep.encode("utf-8"),
            file_name=f"ACTA_SEMANAL_{proyecto['ref']}_S{s_sel}_{hoy.strftime('%d%m%Y')}.html",
            mime="text/html",
            use_container_width=True,
        )
        st.markdown("**Días incluidos:**")
        for a in actas_s:
            st.markdown(f"- {datetime.fromisoformat(a['fecha']).strftime('%A %d/%m').capitalize()} — {a.get('resumen','')}")
    else:
        st.info(f"No hay actas para la semana {s_sel}. Crea actas en la pestaña 📋 Actas.")
