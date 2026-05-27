#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app.py — PMO Master · Nine Fitness Brescia 19
Navegación lateral unificada: Gantt · Actas Diarias · Actas Semanales · Agentes IA
"""

import json
import re
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from pathlib import Path

from db import (
    init_db, backend_info, semana_obra,
    list_actas_diarias, upsert_acta_diaria, delete_acta_diaria,
    list_actas_semanales, upsert_acta_semanal, delete_acta_semanal,
    consolidar_semana,
)

# ─── CONFIGURACIÓN ────────────────────────────────────────────────
st.set_page_config(
    page_title="PMO Master | Brescia 19",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════
#  MURO DE ACCESO — debe ejecutarse antes que cualquier contenido
# ══════════════════════════════════════════════════════════════════

def _check_password() -> bool:
    """Devuelve True si la contraseña es correcta o ya estaba validada."""

    def _on_submit():
        pwd_ok = st.session_state.get("_pwd_input","") == st.secrets.get("password_pmo","brescia19")
        st.session_state["_pwd_ok"] = pwd_ok

    if st.session_state.get("_pwd_ok"):
        return True

    # Pantalla de login
    st.markdown("""
    <style>
      [data-testid="stAppViewContainer"] { background: #0e1117; }
      [data-testid="stSidebar"] { display: none; }
      .login-box {
        max-width: 420px; margin: 80px auto; padding: 40px 36px;
        background: #161b27; border-radius: 14px;
        border: 1px solid #2a2f3e;
        box-shadow: 0 8px 40px rgba(0,0,0,.5);
        text-align: center;
      }
    </style>
    <div class="login-box">
      <div style="font-size:36px;">🏗️</div>
      <div style="font-size:20px;font-weight:900;color:#fff;margin:10px 0 4px;">PMO BRESCIA 19</div>
      <div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:28px;">
        Nine Fitness Group S.L. · Acceso Restringido
      </div>
    </div>
    """, unsafe_allow_html=True)

    col = st.columns([1, 2, 1])[1]
    with col:
        st.text_input(
            "Contraseña PMO",
            type="password",
            key="_pwd_input",
            on_change=_on_submit,
            placeholder="Introduce la contraseña...",
        )
        if st.button("Acceder →", use_container_width=True, type="primary"):
            _on_submit()

        if "_pwd_ok" in st.session_state and not st.session_state["_pwd_ok"]:
            st.error("Contraseña incorrecta.")

        st.caption("Acceso exclusivo para el equipo de dirección de obra.")

    return False


if not _check_password():
    st.stop()

init_db()

ARCHIVO_CSV    = "BASE DE DATOS PLANNIG.csv"
FECHA_APERTURA = datetime(2026, 8, 3)
FECHA_INICIO   = datetime(2026, 5, 18)

FASES = [
    "DEMOLICIÓN", "TRABAJOS PREVIOS", "ALBAÑILERÍA",
    "IMPERMEABILIZACIÓN", "FONTANERÍA", "ELECTRICIDAD",
    "CLIMATIZACIÓN", "CARPINTERÍA EXT.", "PCI - INCENDIOS",
    "RECEPCIÓN", "FALSOS TECHOS", "REVESTIMIENTOS",
    "ACABADOS", "EQUIPAMIENTO", "ACCESIBILIDAD PMR",
    "INSPECCIONES", "HITOS",
]
ESTADOS = ["PENDIENTE", "EN PROCESO", "AMARILLO", "ROJO", "COMPLETADO"]
COLOR_ESTADO = {
    "COMPLETADO": "#2ecc71", "EN PROCESO": "#3498db",
    "PENDIENTE":  "#95a5a6", "AMARILLO":   "#f1c40f", "ROJO": "#e74c3c",
}

GREMIO_KW = {
    "⚡ Electricidad":  ["luis", "elecrea", "cuadro", "bandeja", "cableado", "iga", "diferencial"],
    "❄️ Climatización": ["jose", "nacho", "servitec", "conducto", "daikin", "clima", "difusor", "altillo"],
    "🧱 Albañilería":   ["munir", "ziad", "mohamed", "solera", "tabiq", "escombro", "nivelac", "pladur"],
    "🪵 Carpintería":   ["josevi", "upn", "espejo", "carpintería", "viga", "estructura"],
    "🔥 PCI":           ["leo", "troser", "extinción", "pci", "rociador"],
    "♿ Accesibilidad": ["pedro", "hersan", "salvaescaleras", "pmr", "fortis"],
}
INC_KW    = ["problema","retraso","falta","pendiente urgente","alerta","sin material","parado","bloqueado","ausencia","no asistido"]
AGENDA_KW = ["mañana","próximo día","08:","09:","10:","reunión"]


# ══════════════════════════════════════════════════════════════════
#  HELPERS GANTT
# ══════════════════════════════════════════════════════════════════

def datos_iniciales() -> pd.DataFrame:
    filas = [
        (1,  "DEMOLICIÓN",       "Local diáfano 760m2 - forjado limpio",                 "Munir/Ziad",      "2026-05-04","2026-05-13",100,"COMPLETADO","No"),
        (2,  "TRABAJOS PREVIOS", "Recibir presupuestos contratas",                        "Darío/Valentina", "2026-05-04","2026-05-14",100,"COMPLETADO","No"),
        (3,  "TRABAJOS PREVIOS", "Adjudicar contratas",                                   "Dirección",       "2026-05-04","2026-05-15", 95,"COMPLETADO","No"),
        (4,  "TRABAJOS PREVIOS", "Cerrar planning de obra",                               "Darío",           "2026-05-04","2026-05-16", 95,"COMPLETADO","No"),
        (5,  "TRABAJOS PREVIOS", "Pedir fabricación equipos clima",                       "Darío/Jose",      "2026-05-15","2026-05-17",100,"COMPLETADO","No"),
        (6,  "TRABAJOS PREVIOS", "Luis Electricidad — pedido cuadros",                    "Luis/Elecrea",    "2026-05-16","2026-05-20", 80,"COMPLETADO","No"),
        (7,  "TRABAJOS PREVIOS", "Arrancar fabricación mueble recepción",                 "Munir",           "2026-05-25","2026-06-12",  0,"EN PROCESO","No"),
        (8,  "TRABAJOS PREVIOS", "Arrancar fabricación plataforma acceso Hersan",         "Darío",           "2026-05-25","2026-06-15",  0,"EN PROCESO","Sí"),
        (9,  "ALBAÑILERÍA",      "Replanteo general + trazado tabiquería",                "Munir",           "2026-05-25","2026-05-27",  0,"EN PROCESO","No"),
        (10, "ALBAÑILERÍA",      "Hueco técnico para clima — conductos",                  "Munir",           "2026-05-25","2026-05-28",  0,"EN PROCESO","No"),
        (11, "ALBAÑILERÍA",      "Pletinas aluminio soporte ventanas x2",                 "Munir",           "2026-05-27","2026-05-30",  0,"PENDIENTE", "No"),
        (12, "ALBAÑILERÍA",      "Tabique humedad PLACO Glasroc X vestuarios",            "Munir",           "2026-05-27","2026-06-10",  0,"PENDIENTE", "No"),
        (13, "ALBAÑILERÍA",      "Tabique grandes alturas",                               "Munir",           "2026-05-27","2026-06-07",  0,"PENDIENTE", "No"),
        (14, "ALBAÑILERÍA",      "Tabique sala colectiva + CT + limpieza",                "Munir",           "2026-05-27","2026-06-07",  0,"PENDIENTE", "No"),
        (15, "ALBAÑILERÍA",      "Tabiques staff",                                        "Munir",           "2026-05-27","2026-06-02",  0,"PENDIENTE", "No"),
        (16, "ALBAÑILERÍA",      "Trasdosado acústico Silentboard — muro colindante",     "Munir",           "2026-06-01","2026-06-13",  0,"PENDIENTE", "No"),
        (17, "ALBAÑILERÍA",      "Trasdosado acústico Silentboard 181m2 — fachada",       "Munir",           "2026-06-01","2026-06-13",  0,"PENDIENTE", "No"),
        (18, "ALBAÑILERÍA",      "Falsas vigas cajón técnico 54m",                        "Munir",           "2026-06-04","2026-06-13",  0,"PENDIENTE", "No"),
        (19, "IMPERMEABILIZACIÓN","Kerdi/Dry80 suelo vestuarios",                         "Fontanería",      "2026-06-05","2026-06-13",  0,"PENDIENTE", "No"),
        (20, "IMPERMEABILIZACIÓN","Subida paredes duchas hasta 2.10m",                    "Fontanería",      "2026-06-05","2026-06-13",  0,"PENDIENTE", "No"),
        (21, "IMPERMEABILIZACIÓN","Zócalo perimetral 20cm vestuarios",                    "Fontanería",      "2026-06-06","2026-06-13",  0,"PENDIENTE", "No"),
        (22, "IMPERMEABILIZACIÓN","Prueba de estanqueidad",                               "Fontanería",      "2026-06-11","2026-06-15",  0,"PENDIENTE", "No"),
        (23, "FONTANERÍA",       "Colectores suspendidos PVC 110-125mm",                 "Fontanería",      "2026-06-08","2026-06-16",  0,"PENDIENTE", "No"),
        (24, "FONTANERÍA",       "Red pequeña evacuación PVC 32-110mm",                  "Fontanería",      "2026-06-08","2026-06-16",  0,"PENDIENTE", "No"),
        (25, "FONTANERÍA",       "Botes sifónicos PVC x5",                               "Fontanería",      "2026-06-10","2026-06-14",  0,"PENDIENTE", "No"),
        (26, "FONTANERÍA",       "Bajante interior PVC 110mm + aireador x3",             "Fontanería",      "2026-06-08","2026-06-16",  0,"PENDIENTE", "No"),
        (27, "FONTANERÍA",       "Acometida PE100 32mm + alimentación acero",            "Fontanería",      "2026-06-12","2026-06-16",  0,"PENDIENTE", "No"),
        (28, "FONTANERÍA",       "Tuberías PE-Xa 16/20/25mm distribución",              "Fontanería",      "2026-06-10","2026-06-22",  0,"PENDIENTE", "No"),
        (29, "FONTANERÍA",       "Válvulas + llaves de paso",                            "Fontanería",      "2026-06-15","2026-06-19",  0,"PENDIENTE", "No"),
        (30, "FONTANERÍA",       "Termos eléctricos Bosch 250L x2",                      "Fontanería",      "2026-06-20","2026-06-28",  0,"PENDIENTE", "No"),
        (31, "ELECTRICIDAD",     "Canalización principal bandejas + cuadro IGA 63A",     "Luis/Elecrea",    "2026-05-25","2026-05-30",  0,"EN PROCESO","No"),
        (32, "ELECTRICIDAD",     "Cableado circuitos fuerza máquinas cardio",            "Luis/Elecrea",    "2026-05-28","2026-06-10",  0,"PENDIENTE", "No"),
        (33, "ELECTRICIDAD",     "Cableado iluminación LED general",                     "Luis/Elecrea",    "2026-06-01","2026-06-15",  0,"PENDIENTE", "No"),
        (34, "ELECTRICIDAD",     "Foseados tiras LED perimetrales",                      "Luis/Elecrea",    "2026-06-15","2026-07-01",  0,"PENDIENTE", "No"),
        (35, "ELECTRICIDAD",     "Cuadros secundarios + protecciones",                   "Luis/Elecrea",    "2026-06-05","2026-06-20",  0,"PENDIENTE", "No"),
        (36, "ELECTRICIDAD",     "Alumbrado emergencia + señalización evacuación",        "Luis/Elecrea",    "2026-06-20","2026-07-05",  0,"PENDIENTE", "No"),
        (37, "CLIMATIZACIÓN",    "Conductos distribución aire Daikin 5MXM90A",           "Servitec/Jose",   "2026-05-29","2026-06-20", 15,"EN PROCESO","No"),
        (38, "CLIMATIZACIÓN",    "Unidades interiores x4 + difusores",                   "Servitec/Jose",   "2026-06-10","2026-06-25",  0,"PENDIENTE", "No"),
        (39, "CLIMATIZACIÓN",    "Recuperador calor Daikin DAHU + extractores Silent",   "Servitec/Jose",   "2026-06-15","2026-06-30",  0,"PENDIENTE", "No"),
        (40, "CLIMATIZACIÓN",    "Bancadas antivibratorias unidad exterior",              "Servitec/Jose",   "2026-06-20","2026-06-25",  0,"PENDIENTE", "No"),
        (41, "CARPINTERÍA EXT.", "Viga UPN — estructura soporte (HITO)",                 "Josevi",          "2026-05-27","2026-05-28",100,"COMPLETADO","Sí"),
        (42, "CARPINTERÍA EXT.", "Sistema cierre ventanas exterior",                      "Josevi",          "2026-06-01","2026-07-07",  0,"PENDIENTE", "No"),
        (43, "CARPINTERÍA EXT.", "Carpintería a medida recepción y vestuarios",           "Josevi",          "2026-07-08","2026-07-24",  0,"PENDIENTE", "No"),
        (44, "PCI - INCENDIOS",  "Trazados red extinción + BIEs",                        "Troser/Leo",      "2026-05-18","2026-06-20", 10,"EN PROCESO","No"),
        (45, "PCI - INCENDIOS",  "Rociadores + detección automática",                    "Troser/Leo",      "2026-06-01","2026-06-30",  0,"PENDIENTE", "No"),
        (46, "PCI - INCENDIOS",  "Legalización PCI + boletín técnico",                   "Troser/Leo",      "2026-06-20","2026-06-30",  0,"PENDIENTE", "Sí"),
        (47, "RECEPCIÓN",        "Mostrador recepción 2.80x2.00m terracota",             "Munir",           "2026-06-20","2026-07-01",  0,"PENDIENTE", "No"),
        (48, "RECEPCIÓN",        "Tornos QR/RFID x2 + puerta PMR 900mm",                "Proveedor",       "2026-06-20","2026-07-01",  0,"PENDIENTE", "No"),
        (49, "RECEPCIÓN",        "Rack IT 12U-15U ventilado + fuente agua inox",         "Proveedor",       "2026-06-25","2026-07-01",  0,"PENDIENTE", "No"),
        (50, "FALSOS TECHOS",    "Techo Box-in-Box 81dB vest+staff+rack",                "Munir",           "2026-07-15","2026-07-26",  0,"PENDIENTE", "No"),
        (51, "FALSOS TECHOS",    "Techo metálico aluminio baños/vestuarios",             "Munir",           "2026-07-15","2026-07-26",  0,"PENDIENTE", "No"),
        (52, "FALSOS TECHOS",    "Techo High-Sound viruta madera sala colectiva",        "Munir",           "2026-07-15","2026-07-27",  0,"PENDIENTE", "No"),
        (53, "FALSOS TECHOS",    "Falsa viga cajón técnico 3 tramos 54m",               "Munir",           "2026-07-18","2026-07-26",  0,"PENDIENTE", "No"),
        (54, "REVESTIMIENTOS",   "Alicatado 200x200mm blanco baños/vestuarios",          "Fontanería",      "2026-07-10","2026-07-26",  0,"PENDIENTE", "No"),
        (55, "REVESTIMIENTOS",   "Solado gres porcelánico 600x600mm",                    "Fontanería",      "2026-07-15","2026-07-26",  0,"PENDIENTE", "No"),
        (56, "ACABADOS",         "Pintura plástica vertical paramentos",                  "Munir",           "2026-07-18","2026-08-01",  0,"PENDIENTE", "No"),
        (57, "ACABADOS",         "Pintura techos y horizontales >3m",                    "Munir",           "2026-07-18","2026-08-01",  0,"PENDIENTE", "No"),
        (58, "ACABADOS",         "Rodapié MDF 90x18mm — 159m",                           "Munir",           "2026-07-22","2026-07-31",  0,"PENDIENTE", "No"),
        (59, "ACABADOS",         "Pavimento vinílico lamas hall+sala activ. 143m2",       "Munir",           "2026-07-22","2026-07-31",  0,"PENDIENTE", "No"),
        (60, "ACABADOS",         "Pavimento caucho SBR 40mm sala gym 522m2",             "Munir",           "2026-07-22","2026-07-28",  0,"PENDIENTE", "No"),
        (61, "EQUIPAMIENTO",     "Lavabos x5 + griferías monomando",                     "Fontanería",      "2026-07-15","2026-07-24",  0,"PENDIENTE", "No"),
        (62, "EQUIPAMIENTO",     "Inodoros x4 + inodoro PMR",                            "Fontanería",      "2026-07-15","2026-07-24",  0,"PENDIENTE", "No"),
        (63, "EQUIPAMIENTO",     "Duchas x8 + plato PMR + griferías x8",                "Fontanería",      "2026-07-15","2026-07-24",  0,"PENDIENTE", "No"),
        (64, "EQUIPAMIENTO",     "Accesorios PMR — barras x2 + espejo PMR",             "Fontanería",      "2026-07-15","2026-07-24",  0,"PENDIENTE", "No"),
        (65, "EQUIPAMIENTO",     "Cabinas fenólico HPL 900x1400mm x4",                  "Proveedor",       "2026-07-18","2026-07-26",  0,"PENDIENTE", "No"),
        (66, "EQUIPAMIENTO",     "Taquillas HPL 400x500x1800mm x89",                    "Proveedor",       "2026-07-18","2026-07-26",  0,"PENDIENTE", "No"),
        (67, "EQUIPAMIENTO",     "Bancos HPL 1000mm x30",                                "Fontanería",      "2026-07-20","2026-07-26",  0,"PENDIENTE", "No"),
        (68, "ACCESIBILIDAD PMR","Plataforma FORTIS 300kg Hersan — CUELLO BOTELLA",      "Hersan",          "2026-07-07","2026-07-15",  0,"PENDIENTE", "Sí"),
        (69, "ACCESIBILIDAD PMR","Señalización PMR + evacuación",                        "Proveedor",       "2026-07-15","2026-07-18",  0,"PENDIENTE", "No"),
        (70, "INSPECCIONES",     "Prueba instalación eléctrica con equipamientos",        "Luis/Elecrea",    "2026-07-25","2026-07-28",  0,"PENDIENTE", "No"),
        (71, "INSPECCIONES",     "Puesta en marcha clima 4 unidades",                    "Servitec/Jose",   "2026-07-25","2026-07-29",  0,"PENDIENTE", "No"),
        (72, "INSPECCIONES",     "Prueba ACS + fontanería + estanqueidad",               "Fontanería",      "2026-07-25","2026-07-29",  0,"PENDIENTE", "No"),
        (73, "INSPECCIONES",     "Inspección PCI final",                                 "Troser/Leo",      "2026-07-25","2026-07-29",  0,"PENDIENTE", "Sí"),
        (74, "INSPECCIONES",     "Limpieza final de obra",                               "PMO Darío",       "2026-07-30","2026-08-02",  0,"PENDIENTE", "No"),
        (75, "INSPECCIONES",     "Inspección licencia apertura municipal",                "PMO Darío",       "2026-07-30","2026-08-03",  0,"PENDIENTE", "Sí"),
        (76, "HITOS",            "APERTURA NINE FITNESS BRESCIA 19",                     "Todo el equipo",  "2026-08-03","2026-08-05",  0,"PENDIENTE", "Sí"),
    ]
    cols = ["ID","FASE","TAREA","RESPONSABLE","FECHA_INICIO","FECHA_FIN","PROGRESO","ESTADO","HITO_CRITICO"]
    df = pd.DataFrame(filas, columns=cols)
    df["FECHA_INICIO"] = pd.to_datetime(df["FECHA_INICIO"])
    df["FECHA_FIN"]    = pd.to_datetime(df["FECHA_FIN"])
    return df

@st.cache_data
def cargar_datos() -> pd.DataFrame:
    if Path(ARCHIVO_CSV).exists():
        df = pd.read_csv(ARCHIVO_CSV)
        df["FECHA_INICIO"] = pd.to_datetime(df["FECHA_INICIO"])
        df["FECHA_FIN"]    = pd.to_datetime(df["FECHA_FIN"])
    else:
        df = datos_iniciales()
        df.to_csv(ARCHIVO_CSV, index=False)
    return df

def guardar_datos(df: pd.DataFrame):
    df.to_csv(ARCHIVO_CSV, index=False)
    st.cache_data.clear()

def ts(fecha_str: str) -> float:
    return pd.Timestamp(fecha_str).timestamp() * 1000


# ══════════════════════════════════════════════════════════════════
#  HELPERS ACTAS
# ══════════════════════════════════════════════════════════════════

_RE_HORA     = re.compile(r'\b(\d{1,2}[:.h]\d{2})\b')
_RE_MEDIDA   = re.compile(r'\d+[\.,]?\d*\s*(?:m[²2]?|cm|ml)\b|\d+\s*[×x]\s*\d+|'
                          r'\bdimensi|\breplanteo\b|\btabiq|\bmontante|\bmedid|\bhueco\b')
_INC_ALTA_KW = ["no asist", "baja", "sin personal", "parado", "bloqueado",
                "sin material", "improductiv", "ausencia", "no puede"]

def procesar_texto_bruto_a_json(texto: str) -> dict:
    lines       = [l.strip() for l in texto.splitlines() if l.strip()]
    secs        = {g: [] for g in GREMIO_KW}
    incidencias = []
    avances     = []
    replanteos  = []
    agenda      = []

    for line in lines:
        ll = line.lower()

        gremio = next((g for g, kws in GREMIO_KW.items() if any(k in ll for k in kws)), None)
        is_inc = any(k in ll for k in INC_KW)
        hora_m = _RE_HORA.search(ll)
        is_agenda    = bool(hora_m) or any(k in ll for k in AGENDA_KW)
        is_replanteo = bool(_RE_MEDIDA.search(ll))

        if gremio:
            secs[gremio].append(line)
            if is_inc:
                prioridad = "alta" if any(k in ll for k in _INC_ALTA_KW) else "normal"
                incidencias.append({"gremio": gremio, "descripcion": line, "prioridad": prioridad})
            else:
                avances.append({"gremio": gremio, "descripcion": line})

        if is_replanteo:
            if ":" in line:
                el, det = line.split(":", 1)
                replanteos.append({"elemento": el.strip(), "detalle": det.strip()})
            else:
                replanteos.append({"elemento": "Replanteo", "detalle": line})

        if is_agenda:
            hora = hora_m.group(1) if hora_m else "—"
            agenda.append({"hora": hora, "evento": line})

    gremios_inc = list(dict.fromkeys(i["gremio"] for i in incidencias))
    ag_texto    = "\n".join(f"{a['hora']} — {a['evento']}" for a in agenda)

    return {
        "incidencias":        incidencias,
        "avances":            avances,
        "replanteos":         replanteos,
        "agenda":             agenda,
        "intervenciones":     {g: "\n".join(v) for g, v in secs.items() if v},
        "gremios_incidencia": gremios_inc,
        "agenda_proxima":     {"items": agenda, "texto": ag_texto},
    }

# Alias para compatibilidad con código existente
def parsear(texto: str) -> dict:
    return procesar_texto_bruto_a_json(texto)

def _gallery_html(imagenes: list) -> str:
    if not imagenes:
        return ""
    items = ""
    for i, img in enumerate(imagenes[:3]):
        cls = "gallery-item highlight" if i == 0 else "gallery-item"
        items += (
            f'<div class="{cls}">'
            f'<img src="{img["src"]}" alt="{img["caption"]}">'
            f'<div class="gallery-caption">{img["caption"]}</div>'
            f'</div>'
        )
    return f'<div class="sec"><div class="sh">📸 Registro Fotográfico</div><div class="gallery">{items}</div></div>'


def _imgs_b64(files: list) -> list:
    """Convierte lista de UploadedFile a lista de {src, caption}."""
    import base64
    result = []
    for f in (files or []):
        if f is None:
            continue
        b64 = base64.b64encode(f.read()).decode()
        mime = f.type or "image/jpeg"
        result.append({"src": f"data:{mime};base64,{b64}", "caption": f.name})
    return result


def _parse_agenda(acta) -> list:
    """Devuelve lista de {hora, evento} siempre, sin importar el formato almacenado."""
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

def _agenda_html(acta: dict) -> str:
    items = _parse_agenda(acta)
    if not items:
        return ""
    rows = "".join(
        '<div style="display:flex;gap:14px;align-items:flex-start;padding:8px 0;'
        'border-bottom:1px solid #f0f2f8;">'
        '<span style="font-size:11px;font-weight:800;color:#e94560;white-space:nowrap;'
        'min-width:52px;padding-top:1px;">' + it["hora"] + '</span>'
        '<span style="font-size:12px;color:#374151;line-height:1.5;">' + it["evento"] + '</span>'
        '</div>'
        for it in items
    )
    return (
        '<div class="sec"><div class="sh">📅 Agenda Próxima Jornada</div>'
        '<div style="margin-top:6px;">' + rows + '</div></div>'
    )

def _parse_json_field(acta, key):
    v = acta.get(key) or []
    if isinstance(v, str):
        try: v = json.loads(v)
        except: v = []
    return v if isinstance(v, list) else []

def _solicitudes_html(acta: dict) -> str:
    items = _parse_json_field(acta, "solicitudes_direccion")
    if not items:
        return ""
    rows = "".join(
        f'<div style="display:flex;align-items:flex-start;gap:10px;padding:8px 10px;'
        f'background:#fff0f0;border-radius:6px;margin-bottom:6px;">'
        f'<span style="font-size:16px;flex-shrink:0;">🚨</span>'
        f'<div><div style="font-size:12px;font-weight:700;color:#c0392b;">{it.get("descripcion","")}</div>'
        f'<div style="font-size:10px;color:#888;margin-top:2px;">Responsable: {it.get("responsable","—")} '
        f'· Urgencia: <b style="color:#e74c3c;">{it.get("urgencia","").upper()}</b></div></div></div>'
        for it in items
    )
    return (
        f'<div class="sec" style="border:2px solid #e74c3c;border-radius:8px;padding:14px 16px;'
        f'background:#fff5f5;">'
        f'<div class="sh" style="color:#c0392b;border-bottom-color:#e74c3c;">🚨 Solicitudes a Dirección — Respuesta Urgente</div>'
        f'{rows}</div>'
    )

def _logros_html(acta: dict) -> str:
    items = _parse_json_field(acta, "logros_tecnicos")
    if not items:
        return ""
    rows_parts = []
    for it in items:
        impacto_txt = (" · " + it["impacto"]) if it.get("impacto") else ""
        rows_parts.append(
            '<div style="display:flex;align-items:flex-start;gap:10px;padding:8px 10px;'
            'background:#f0faf4;border-radius:6px;margin-bottom:6px;">'
            '<span style="font-size:16px;flex-shrink:0;">✅</span>'
            '<div><div style="font-size:12px;font-weight:700;color:#27ae60;">' + it.get("descripcion","") + '</div>'
            '<div style="font-size:10px;color:#555;margin-top:2px;">'
            + it.get("mejora_de","") + ' → <b style="color:#27ae60;">' + it.get("mejora_a","") + '</b>'
            + impacto_txt + '</div></div></div>'
        )
    rows = "".join(rows_parts)
    return (
        '<div class="sec" style="border:2px solid #27ae60;border-radius:8px;padding:14px 16px;'
        'background:#f6fff9;">'
        '<div class="sh" style="color:#1e8449;border-bottom-color:#27ae60;">✅ Logros Técnicos / Optimizaciones</div>'
        + rows + '</div>'
    )

def _deftec_html(acta: dict) -> str:
    items = _parse_json_field(acta, "definiciones_tecnicas")
    if not items:
        return ""
    rows = "".join(
        f'<div style="display:grid;grid-template-columns:120px 140px 1fr;gap:8px;'
        f'padding:7px 0;border-bottom:1px solid #f0f2f8;font-size:11px;">'
        f'<span style="color:#94a3b8;font-weight:600;text-transform:uppercase;font-size:9px;">{it.get("categoria","")}</span>'
        f'<span style="font-weight:700;color:#1a1a2e;">{it.get("elemento","")}</span>'
        f'<span style="color:#374151;">{it.get("detalle","")}</span></div>'
        for it in items
    )
    return (
        f'<div class="sec"><div class="sh">📐 Definiciones Técnicas</div>'
        f'<div style="margin-top:6px;">{rows}</div></div>'
    )


def html_acta_diaria(acta: dict, imagenes=None) -> str:
    """HTML de previsualización para una acta diaria."""
    try:
        fecha_str = datetime.fromisoformat(acta["fecha"]).strftime("%A %d de %B de %Y").capitalize()
    except Exception:
        fecha_str = acta.get("fecha", "")

    secs = acta.get("intervenciones") or {}
    if isinstance(secs, str):
        try: secs = json.loads(secs)
        except: secs = {}

    sec_html = ""
    for g, c in secs.items():
        if c:
            sec_html += (
                f'<div style="margin-bottom:10px;">'
                f'<div style="font-size:11px;font-weight:700;color:#0f3460;text-transform:uppercase;'
                f'letter-spacing:.5px;margin-bottom:4px;">{g}</div>'
                f'<div style="font-size:12px;padding-left:10px;border-left:3px solid #e2e8f0;color:#374151;line-height:1.6;">'
                f'{str(c).replace(chr(10),"<br>")}</div></div>'
            )

    incs = acta.get("incidencias") or []
    if isinstance(incs, str):
        try: incs = json.loads(incs)
        except: incs = [incs]
    incs = [i.get("descripcion", str(i)) if isinstance(i, dict) else str(i) for i in incs]
    inc_html = "".join(
        f'<div style="background:#fdf2f2;border-left:3px solid #e94560;padding:7px 10px;'
        f'margin-bottom:5px;border-radius:0 4px 4px 0;font-size:12px;color:#c0392b;">⚠ {i}</div>'
        for i in incs
    )

    ag_html_block = _agenda_html(acta)

    _est_badge = {
        "borrador":  "background:#eef2ff;color:#3730a3;",
        "revisado":  "background:#fff8e1;color:#e65100;",
        "firmado":   "background:#f0faf4;color:#27ae60;",
    }.get(acta.get("estado","borrador"), "background:#eee;color:#333;")
    _prio_badge = {
        "urgente": "background:#fdf2f2;color:#c0392b;",
        "alta":    "background:#fff8e1;color:#e65100;",
        "normal":  "background:#f0faf4;color:#27ae60;",
    }.get(acta.get("prioridad","normal"), "background:#eee;color:#333;")

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Helvetica Neue',Arial,sans-serif;background:#f0f2f8;color:#1a1a2e;font-size:13px}}
  .doc{{max-width:820px;margin:16px auto;background:#fff;border-radius:10px;
        overflow:hidden;box-shadow:0 3px 20px rgba(0,0,0,.1)}}
  .hdr{{background:linear-gradient(135deg,#1a1a2e,#0f3460);color:#fff;padding:20px 28px;position:relative}}
  .hdr-title{{font-size:20px;font-weight:900}}
  .hdr-sub{{font-size:11px;opacity:.65;margin-top:4px}}
  .accent{{position:absolute;bottom:0;left:0;right:0;height:3px;background:#e94560}}
  .meta{{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid #e2e8f0;background:#fafbff}}
  .mc{{padding:11px 16px;border-right:1px solid #e2e8f0}}
  .mc:last-child{{border-right:none}}
  .ml{{font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#94a3b8;font-weight:600;margin-bottom:3px}}
  .mv{{font-size:13px;font-weight:700}}
  .body{{padding:22px 28px}}
  .sh{{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.8px;color:#1a1a2e;
       margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #e94560}}
  .sec{{margin-bottom:20px}}
  .gallery{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:10px}}
  .gallery-item{{position:relative;border-radius:8px;overflow:hidden;
                 box-shadow:0 2px 8px rgba(0,0,0,.08);aspect-ratio:4/3;background:#f8f9ff}}
  .gallery-item img{{width:100%;height:100%;object-fit:cover;display:block;transition:transform .3s ease}}
  .gallery-item:hover img{{transform:scale(1.03)}}
  .gallery-caption{{position:absolute;bottom:0;left:0;right:0;
                    background:linear-gradient(transparent,rgba(26,26,46,.9));
                    color:#fff;padding:24px 12px 10px;font-size:9px;
                    text-transform:uppercase;letter-spacing:1px;font-weight:600}}
  .gallery-item.highlight{{grid-column:span 2;grid-row:span 2}}
  .ftr{{background:#1a1a2e;padding:10px 28px;font-size:9px;color:rgba(255,255,255,.4);
        display:flex;justify-content:space-between}}
  @media print{{
    .gallery{{gap:8px}}
    .gallery-item{{page-break-inside:avoid;box-shadow:none;border:1px solid #e2e8f0}}
    .gallery-item:hover img{{transform:none}}
  }}
</style></head><body>
<div class="doc">
  <div class="hdr">
    <div style="font-size:9px;text-transform:uppercase;letter-spacing:2px;opacity:.5;margin-bottom:4px;">
      Nine Fitness · Brescia 19 · Acta Diaria
    </div>
    <div class="hdr-title">📋 {fecha_str}</div>
    <div class="hdr-sub">{acta.get('resumen','')}</div>
    <div class="accent"></div>
  </div>
  <div class="meta">
    <div class="mc"><div class="ml">Referencia</div><div class="mv" style="font-size:11px;">{acta.get('id','')}</div></div>
    <div class="mc"><div class="ml">Semana</div><div class="mv">S{acta.get('semana_obra','')}</div></div>
    <div class="mc"><div class="ml">Prioridad</div>
      <div class="mv"><span style="display:inline-block;padding:2px 8px;border-radius:20px;
        font-size:10px;font-weight:700;{_prio_badge}">{acta.get('prioridad','normal').title()}</span></div></div>
    <div class="mc"><div class="ml">Estado</div>
      <div class="mv"><span style="display:inline-block;padding:2px 8px;border-radius:20px;
        font-size:10px;font-weight:700;{_est_badge}">{acta.get('estado','borrador').title()}</span></div></div>
  </div>
  <div class="body">
    {_solicitudes_html(acta)}
    {_logros_html(acta)}
    {f'<div class="sec"><div class="sh">⚠ Incidencias</div>{inc_html}</div>' if inc_html else ''}
    {f'<div class="sec"><div class="sh">🔧 Intervenciones por Contrata</div>{sec_html}</div>' if sec_html else ''}
    {_deftec_html(acta)}
    {ag_html_block}
    {_gallery_html(imagenes) if imagenes else ''}
  </div>
  <div class="ftr">
    <span>NINE FITNESS GROUP S.L. · Brescia 19, 28028 Madrid</span>
    <span>Dir. Obra: Darío A. López · {acta.get('creado_por','')} · Confidencial</span>
  </div>
</div></body></html>"""

def html_semanal_completo(acta_sem: dict, diarias: list) -> str:
    sem    = acta_sem.get("semana_obra","?")
    fechas = " · ".join(datetime.fromisoformat(a["fecha"]).strftime("%d/%m") for a in diarias)
    bloques = ""
    for a in diarias:
        dia  = datetime.fromisoformat(a["fecha"]).strftime("%A %d/%m/%Y").capitalize()
        secs = a.get("intervenciones") or {}
        if isinstance(secs, str):
            try: secs = json.loads(secs)
            except: secs = {}
        sec_html = "".join(
            f'<div style="margin-bottom:6px;"><b style="font-size:11px;color:#0f3460;">{g}</b>'
            f'<div style="font-size:11px;padding-left:8px;border-left:2px solid #e2e6f0;color:#333;">'
            f'{str(c).replace(chr(10),"<br>")}</div></div>'
            for g, c in secs.items() if c
        )
        incs = a.get("incidencias") or []
        if isinstance(incs, str):
            try: incs = json.loads(incs)
            except: incs = [incs]
        inc_html = "".join(f'<div style="color:#c0392b;font-size:11px;">⚠ {i}</div>' for i in incs)
        _ag_items = _parse_agenda(a)
        _ag_line  = " · ".join(it["hora"] + " " + it["evento"] for it in _ag_items[:2]) if _ag_items else ""
        bloques += f"""
        <div style="border-left:4px solid #e94560;padding:12px 16px;margin-bottom:12px;
                    background:#fff;border-radius:0 8px 8px 0;box-shadow:0 1px 4px rgba(0,0,0,.06);">
          <b style="font-size:14px;color:#1a1a2e;">📋 {dia}</b>
          <div style="font-size:12px;color:#555;margin:5px 0 7px;">{a.get('resumen','')}</div>
          {sec_html}{inc_html}
          {f'<div style="font-size:10px;color:#888;border-top:1px solid #f0f2f7;padding-top:5px;margin-top:5px;">📅 {_ag_line[:220]}</div>' if _ag_line else ''}
        </div>"""
    desv = acta_sem.get("desviaciones_criticas") or []
    if isinstance(desv, str):
        try: desv = json.loads(desv)
        except: desv = [desv]
    desv_html = "".join(f"<li>{d}</li>" for d in desv) or "<li>Sin desviaciones.</li>"
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<style>@page{{size:A4;margin:12mm 10mm}}
body{{font-family:'Helvetica Neue',Arial,sans-serif;background:#fff;color:#1a1a2e;font-size:12px}}</style>
</head><body>
<div style="background:linear-gradient(135deg,#1a1a2e,#0f3460);color:#fff;padding:18px 22px;border-radius:6px;margin-bottom:16px;">
  <div style="font-size:15pt;font-weight:900;">ACTA SEMANAL EJECUTIVA — SEMANA {sem}</div>
  <div style="font-size:9pt;opacity:.7;margin-top:3px;">Nine Fitness · Brescia 19 · {fechas} · Dir. Obra: Darío A. López</div>
</div>
<div style="background:#fdf2f2;border-left:4px solid #e74c3c;padding:10px 14px;margin-bottom:14px;font-size:11px;border-radius:0 4px 4px 0;">
  <b>⚠ Gremios con desviaciones:</b><ul style="margin:4px 0 0 16px;">{desv_html}</ul>
</div>
{bloques}
<div style="text-align:center;font-size:8pt;color:#bbb;margin-top:16px;border-top:1px solid #e2e6f0;padding-top:8px;">
  NINE FITNESS GROUP S.L. · Brescia 19 · Ref: {acta_sem.get('id','')} · Confidencial
</div></body></html>"""


# ══════════════════════════════════════════════════════════════════
#  CSS GLOBAL
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #0e1117; }
  [data-testid="stSidebar"] { background: #161b27; }
  [data-testid="stSidebar"] * { color: #e0e3ed !important; }
  div[data-testid="stForm"] {
    background: #1a1f2e; border-radius: 10px; padding: 16px;
    border: 1px solid #2a2f3e;
  }
  .acta-card {
    border-left: 4px solid #e94560; padding: 12px 16px;
    background: #1a1f2e; border-radius: 0 8px 8px 0;
    box-shadow: 0 2px 6px rgba(0,0,0,.2); margin-bottom: 10px;
  }
  .acta-card.urgente { border-left-color: #c0392b; }
  .acta-card.alta    { border-left-color: #f39c12; }
  .badge {
    display:inline-block; padding:2px 8px; border-radius:4px;
    font-size:10px; font-weight:700;
  }
  .b-red    { background:#3d1515; color:#e74c3c; }
  .b-amber  { background:#3d2e0a; color:#f39c12; }
  .b-green  { background:#0d2e1a; color:#27ae60; }
  .b-blue   { background:#0d1f3d; color:#3498db; }
  iframe { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1a1a2e,#0f3460);padding:16px;border-radius:8px;
                margin-bottom:16px;text-align:center;">
      <div style="font-size:22px;">🏗️</div>
      <div style="font-size:13px;font-weight:900;color:#fff;margin-top:4px;">PMO BRESCIA 19</div>
      <div style="font-size:9px;color:rgba(255,255,255,.5);margin-top:2px;text-transform:uppercase;letter-spacing:1px;">Nine Fitness Group S.L.</div>
    </div>
    """, unsafe_allow_html=True)

    modulo = st.radio(
        "Panel operativo",
        ["📊 Dashboard y Gantt", "📝 Actas Diarias", "📁 Actas Semanales"],
        label_visibility="collapsed",
    )

    hoy       = date.today()
    hoy_dt    = datetime.combine(hoy, datetime.min.time())
    dias_rest = (FECHA_APERTURA - hoy_dt).days
    sem_actual = semana_obra(hoy)

    st.divider()
    st.markdown(f"""
    <div style="font-size:11px;line-height:1.9;color:#94a3b8;">
      📅 Hoy: <b style="color:#e0e3ed;">{hoy.strftime('%d/%m/%Y')}</b><br>
      🗓 Semana de obra: <b style="color:#e0e3ed;">S{sem_actual}</b><br>
      ⏳ Días para apertura: <b style="color:#e94560;font-size:14px;">{dias_rest}d</b><br>
      🚀 Apertura: <b style="color:#e0e3ed;">3–5 AGO 2026</b><br>
      💾 Backend: <b style="color:#e0e3ed;">{backend_info()}</b>
    </div>
    """, unsafe_allow_html=True)

    if modulo == "📊 Dashboard y Gantt":
        st.divider()
        st.markdown("**🗂️ Filtros Gantt**")
        df_full = cargar_datos()
        fases_sel = st.multiselect("Fase", FASES, default=FASES)
        resp_todos = sorted(df_full["RESPONSABLE"].unique().tolist())
        resp_sel   = st.multiselect("Responsable", resp_todos, default=resp_todos)
        estados_sel = st.multiselect("Estado", ESTADOS, default=ESTADOS)
        solo_criticos = st.checkbox("Solo hitos críticos", value=False)


# ══════════════════════════════════════════════════════════════════
#  MÓDULO 1 — DASHBOARD Y GANTT
# ══════════════════════════════════════════════════════════════════
if modulo == "📊 Dashboard y Gantt":
    df = cargar_datos()
    hoy_dt = datetime.combine(date.today(), datetime.min.time())

    avance_gl   = int(df["PROGRESO"].mean())
    alertas     = len(df[df["ESTADO"].isin(["ROJO","AMARILLO"])])
    completadas = len(df[df["ESTADO"] == "COMPLETADO"])
    en_proceso  = len(df[df["ESTADO"] == "EN PROCESO"])
    dias_rest   = (FECHA_APERTURA - hoy_dt).days

    st.title("🏗️ Planning Master — Nine Fitness Brescia 19")
    st.caption("C/ Brescia 19, 28028 Madrid · Promotor: Nine Fitness Group S.L. · DO: Darío A. López")

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("⏳ Días para Apertura", f"{dias_rest}d",
              delta="🟢 En plazo" if dias_rest > 45 else "🔴 Urgente", delta_color="off")
    k2.metric("📈 Avance Global", f"{avance_gl}%", delta=f"{completadas} completadas")
    k3.metric("🔵 En Proceso", f"{en_proceso} tareas")
    k4.metric("⚠️ Alertas Activas", f"{alertas} tareas", delta_color="inverse", delta="Rojo/Amarillo")
    k5.metric("📋 Total Partidas", f"{len(df)} tareas",
              delta=f"{len(df[df['HITO_CRITICO']=='Sí'])} hitos críticos")

    st.divider()

    mask = df["FASE"].isin(fases_sel) & df["RESPONSABLE"].isin(resp_sel) & df["ESTADO"].isin(estados_sel)
    if solo_criticos:
        mask &= df["HITO_CRITICO"] == "Sí"
    df_vis = df[mask].copy()

    st.subheader("📊 Diagrama de Gantt Interactivo")
    df_gantt = df_vis.copy()
    mismo_dia = df_gantt["FECHA_INICIO"] == df_gantt["FECHA_FIN"]
    df_gantt.loc[mismo_dia, "FECHA_FIN"] = df_gantt.loc[mismo_dia, "FECHA_FIN"] + pd.Timedelta(days=1)

    fig = px.timeline(
        df_gantt, x_start="FECHA_INICIO", x_end="FECHA_FIN", y="TAREA",
        color="ESTADO", color_discrete_map=COLOR_ESTADO,
        hover_data={"FASE":True,"RESPONSABLE":True,"PROGRESO":True,"HITO_CRITICO":True,
                    "FECHA_INICIO":"|%d-%b-%Y","FECHA_FIN":"|%d-%b-%Y"},
        title=f"Cronograma Maestro Brescia 19 · {len(df_vis)} partidas · Apertura 03-Ago-2026",
    )
    fig.add_vline(x=ts(hoy_dt.strftime("%Y-%m-%d")), line_width=2, line_dash="dash",
                  line_color="#FFFFFF", annotation_text=f"HOY {hoy_dt.strftime('%d %b')}",
                  annotation_font=dict(color="#FFFFFF", size=11))
    fig.add_vline(x=ts("2026-07-07"), line_width=2, line_dash="dot", line_color="#e74c3c",
                  annotation_text="Hersan 07-Jul ♿", annotation_font=dict(color="#e74c3c", size=11))
    fig.add_vline(x=ts("2026-08-03"), line_width=2, line_dash="dot", line_color="#FFD700",
                  annotation_text="APERTURA 🚀", annotation_font=dict(color="#FFD700", size=11))
    fig.add_vrect(x0=ts("2026-07-25"), x1=ts("2026-08-02"), fillcolor="#1ABC9C",
                  opacity=0.07, layer="below", line_width=0,
                  annotation_text="Limpieza/Licencias", annotation_font=dict(color="#1ABC9C", size=10))
    fig.update_layout(
        paper_bgcolor="#0e1117", plot_bgcolor="#161b27", font_color="#F0F2F6",
        height=max(500, len(df_vis) * 22 + 80),
        xaxis=dict(showgrid=True, gridcolor="#2a2f3e", tickformat="%d %b", tickangle=-40,
                   range=[FECHA_INICIO - pd.Timedelta(days=3), FECHA_APERTURA + pd.Timedelta(days=5)]),
        yaxis=dict(autorange="reversed", showgrid=False, tickfont=dict(size=10)),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=60, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("✏️ Editor de Planning")
    st.caption("Edita directamente en la tabla · Pulsa 💾 para guardar.")
    edited = st.data_editor(
        df_vis.copy(), use_container_width=True, num_rows="fixed", hide_index=True,
        column_config={
            "ID":           st.column_config.NumberColumn("ID", disabled=True, width="small"),
            "FASE":         st.column_config.SelectboxColumn("Fase", options=FASES, required=True, width="medium"),
            "TAREA":        st.column_config.TextColumn("Tarea / Partida", width="large"),
            "RESPONSABLE":  st.column_config.TextColumn("Responsable", width="medium"),
            "FECHA_INICIO": st.column_config.DateColumn("Inicio", format="DD/MM/YYYY", width="small"),
            "FECHA_FIN":    st.column_config.DateColumn("Fin", format="DD/MM/YYYY", width="small"),
            "PROGRESO":     st.column_config.NumberColumn("% Avance", min_value=0, max_value=100, step=5, format="%d%%", width="small"),
            "ESTADO":       st.column_config.SelectboxColumn("Estado", options=ESTADOS, required=True, width="medium"),
            "HITO_CRITICO": st.column_config.SelectboxColumn("Hito", options=["Sí","No"], width="small"),
        }, key="editor_planning",
    )
    c1, c2, c3 = st.columns([2,1,1])
    with c1:
        if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
            df_updated = df.copy()
            for _, row in edited.iterrows():
                df_updated.loc[df_updated["ID"] == row["ID"], edited.columns] = row.values
            guardar_datos(df_updated)
            st.success(f"✅ {len(edited)} partidas guardadas en `{ARCHIVO_CSV}`")
            st.rerun()
    with c2:
        st.download_button("⬇️ Exportar CSV", data=df.to_csv(index=False).encode("utf-8"),
                           file_name=ARCHIVO_CSV, mime="text/csv", use_container_width=True)
    with c3:
        if st.button("🔄 Recargar", use_container_width=True):
            st.cache_data.clear(); st.rerun()

    st.divider()
    st.subheader("📋 Resumen por Fase")
    resumen = (df.groupby("FASE").agg(
        Tareas=("ID","count"),
        Completadas=("ESTADO", lambda x: (x=="COMPLETADO").sum()),
        En_Proceso=("ESTADO", lambda x: (x=="EN PROCESO").sum()),
        Alertas=("ESTADO", lambda x: x.isin(["ROJO","AMARILLO"]).sum()),
        Avance_Medio=("PROGRESO","mean"),
    ).reset_index())
    resumen["Avance_Medio"] = resumen["Avance_Medio"].round(0).astype(int)
    resumen.columns = ["Fase","Tareas","Completadas","En Proceso","Alertas","% Avance"]
    st.dataframe(resumen, use_container_width=True, hide_index=True,
                 column_config={"% Avance": st.column_config.ProgressColumn("% Avance", min_value=0, max_value=100, format="%d%%")})


# ══════════════════════════════════════════════════════════════════
#  MÓDULO 2 — ACTAS DIARIAS
# ══════════════════════════════════════════════════════════════════
elif modulo == "📝 Actas Diarias":
    st.title("📝 Actas Diarias de Obra")
    st.caption(f"Backend: {backend_info()}")

    tab_hist, tab_nueva, tab_rapida = st.tabs(["📚 Histórico", "✍️ Nueva Acta", "⚡ Ingesta Rápida"])

    with tab_hist:
        fc1, fc2, fc3, fc4 = st.columns([1.2, 1.2, 1, 1])
        with fc1: f_desde = st.date_input("Desde", value=date(2026, 5, 1))
        with fc2: f_hasta = st.date_input("Hasta", value=date(2026, 8, 31))
        with fc3: f_prio  = st.selectbox("Prioridad", ["todas","urgente","alta","normal"])
        with fc4: f_est   = st.selectbox("Estado", ["todos","borrador","revisado","firmado"])

        actas = list_actas_diarias(f_desde.isoformat(), f_hasta.isoformat(), f_prio, f_est)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Actas", len(actas))
        k2.metric("Incidencias", sum(len(a.get("incidencias") or []) for a in actas))
        k3.metric("Urgentes", sum(1 for a in actas if a.get("prioridad") == "urgente"))
        k4.metric("Firmadas", sum(1 for a in actas if a.get("estado") == "firmado"))

        st.divider()

        col_lista, col_visor = st.columns([1, 1.6])

        with col_lista:
            if not actas:
                st.info("Sin actas en el rango.")
            for acta in actas:
                _fstr = datetime.fromisoformat(acta["fecha"]).strftime("%a %d/%m/%Y").capitalize()
                _prio = acta.get("prioridad","normal")
                _cls  = {"urgente":"b-red","alta":"b-amber","normal":"b-green"}.get(_prio,"b-green")
                _incs = acta.get("incidencias") or []
                if isinstance(_incs, str):
                    try: _incs = json.loads(_incs)
                    except: _incs = [_incs]
                _gi = acta.get("gremios_incidencia") or []
                if isinstance(_gi, str):
                    try: _gi = json.loads(_gi)
                    except: _gi = [_gi]
                _gi_tags = " ".join(f'<span class="badge b-blue" style="font-size:9px;">{g}</span>' for g in _gi)

                clicked = st.button(
                    f"**{_fstr}** · S{acta.get('semana_obra','?')}  {'⚠' if _incs else ''}",
                    key=f"sel_{acta['id']}", use_container_width=True
                )
                if clicked:
                    st.session_state["acta_vista"] = acta

        with col_visor:
            acta_v = st.session_state.get("acta_vista")
            if not acta_v:
                st.info("Selecciona un acta de la lista para visualizarla.")
            else:
                html_v = html_acta_diaria(acta_v)
                components.html(html_v, height=580, scrolling=True)
                st.divider()
                dl1, dl2, dl3 = st.columns(3)
                with dl1:
                    st.download_button("⬇️ HTML", data=html_v.encode("utf-8"),
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

    with tab_nueva:
        col_form, col_prev = st.columns([1, 1.2], gap="large")
        with col_form:
            st.markdown("### ✍️ Nueva Acta Diaria")
            with st.form("form_nueva_acta", clear_on_submit=True):
                f_fecha    = st.date_input("Fecha", value=date.today())
                texto_raw  = st.text_area("Notas de campo (texto libre)", height=260,
                                          placeholder="- Luis (Elecrea): cuadro CGMP pendiente.\n- Jose (Servitec): inicio conductos altillo.\n- Mañana 08:30 reunión contratas.")
                resumen_m  = st.text_input("Resumen ejecutivo (opcional)")
                fotos      = st.file_uploader("📸 Fotos (máx. 3)", type=["jpg","jpeg","png","webp"],
                                              accept_multiple_files=True, key="fotos_nueva")
                c1, c2 = st.columns(2)
                with c1: prioridad = st.selectbox("Prioridad", ["normal","alta","urgente"])
                with c2: estado    = st.selectbox("Estado",    ["borrador","revisado","firmado"])
                guardar = st.form_submit_button("💾 Guardar", use_container_width=True, type="primary")

            if guardar:
                if not texto_raw.strip():
                    st.warning("Escribe las notas antes de guardar.")
                else:
                    p    = parsear(texto_raw)
                    imgs = _imgs_b64(fotos[:3] if fotos else [])
                    _id  = f"ACT-{f_fecha.strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
                    nueva = {
                        "id":                    _id,
                        "fecha":                 f_fecha.isoformat(),
                        "semana_obra":           semana_obra(f_fecha),
                        "obra":                  "Brescia 19",
                        "texto_original":        texto_raw,
                        "resumen":               resumen_m.strip() or f"Acta S{semana_obra(f_fecha)} · {f_fecha.strftime('%d/%m/%Y')}",
                        "intervenciones":        json.dumps(p["intervenciones"],     ensure_ascii=False),
                        "definiciones_tecnicas": json.dumps({},                      ensure_ascii=False),
                        "agenda_proxima":        json.dumps(p["agenda_proxima"],     ensure_ascii=False),
                        "incidencias":           json.dumps(p["incidencias"],        ensure_ascii=False),
                        "gremios_incidencia":    json.dumps(p["gremios_incidencia"], ensure_ascii=False),
                        "prioridad":             prioridad,
                        "estado":                estado,
                        "creado_por":            "Darío A. López",
                    }
                    upsert_acta_diaria(nueva)
                    st.session_state["acta_preview_nueva"] = nueva
                    st.session_state["acta_preview_imgs"]  = imgs
                    st.success(f"✅ Acta **{_id}** guardada.")
                    st.rerun()

        with col_prev:
            st.markdown("### 🔍 Preview")
            prev_nueva = st.session_state.get("acta_preview_nueva")
            if prev_nueva:
                components.html(html_acta_diaria(prev_nueva, st.session_state.get("acta_preview_imgs")), height=500, scrolling=True)
            else:
                st.info("El preview aparecerá aquí tras guardar.")


    with tab_rapida:
        st.markdown("### ⚡ Ingesta Rápida — Transcripción de Campo")
        st.caption("Pega tus notas de voz o texto libre. El parser detecta gremios, incidencias, replanteos y agenda automáticamente.")

        col_in, col_out = st.columns([1, 1], gap="large")

        with col_in:
            ir_fecha  = st.date_input("Fecha", value=date.today(), key="ir_fecha")
            ir_texto  = st.text_area(
                "Notas de campo",
                height=320,
                key="ir_texto",
                placeholder=(
                    "Ej:\n"
                    "- Luis Elecrea: baja de operario, cuadrilla insuficiente, jornada improductiva.\n"
                    "- Jose Servitec: inicio montaje conductos en altillo 9:30, continúa mañana.\n"
                    "- Mohamed Munir: replanteo tabique salas colectivas 5.50m x altura pendiente.\n"
                    "- Cuarto técnico eléctrico: dimensiones cerradas 2.30 × 2.00m.\n"
                    "- Mañana 08:30 reunión general contratas."
                ),
            )
            ir_fotos  = st.file_uploader("📸 Fotos (máx. 3)", type=["jpg","jpeg","png","webp"],
                                         accept_multiple_files=True, key="ir_fotos")
            ir_prio   = st.selectbox("Prioridad", ["normal", "alta", "urgente"], key="ir_prio")
            procesar  = st.button("🚀 Procesar y Publicar", use_container_width=True, type="primary", key="ir_btn")

        with col_out:
            st.markdown("### 🔍 Resultado del Parser")
            if procesar:
                if not ir_texto.strip():
                    st.warning("Escribe las notas antes de procesar.")
                else:
                    p    = procesar_texto_bruto_a_json(ir_texto)
                    imgs = _imgs_b64(ir_fotos[:3] if ir_fotos else [])
                    _id  = f"ACT-{ir_fecha.strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
                    acta = {
                        "id":                    _id,
                        "fecha":                 ir_fecha.isoformat(),
                        "semana_obra":           semana_obra(ir_fecha),
                        "obra":                  "Brescia 19",
                        "texto_original":        ir_texto,
                        "resumen":               f"Ingesta rápida S{semana_obra(ir_fecha)} · {ir_fecha.strftime('%d/%m/%Y')}",
                        "intervenciones":        json.dumps(p["intervenciones"],     ensure_ascii=False),
                        "definiciones_tecnicas": json.dumps(p["replanteos"],         ensure_ascii=False),
                        "agenda_proxima":        json.dumps(p["agenda_proxima"],     ensure_ascii=False),
                        "incidencias":           json.dumps([i["descripcion"] for i in p["incidencias"]], ensure_ascii=False),
                        "gremios_incidencia":    json.dumps(p["gremios_incidencia"], ensure_ascii=False),
                        "prioridad":             ir_prio,
                        "estado":                "borrador",
                        "creado_por":            "Darío A. López",
                    }
                    upsert_acta_diaria(acta)
                    st.session_state["ir_resultado"] = p
                    st.session_state["ir_acta"]      = acta
                    st.session_state["ir_imgs"]      = imgs
                    st.success(f"✅ **{_id}** guardada y publicada.")

            res = st.session_state.get("ir_resultado")
            if res:
                if res["incidencias"]:
                    st.markdown("**⚠️ Incidencias detectadas**")
                    for inc in res["incidencias"]:
                        color = "#e74c3c" if inc["prioridad"] == "alta" else "#f39c12"
                        st.markdown(
                            f'<div style="border-left:3px solid {color};padding:6px 10px;'
                            f'background:#1a1a2e;border-radius:0 4px 4px 0;margin-bottom:4px;font-size:12px;">'
                            f'<b>{inc["gremio"]}</b> · {inc["descripcion"]}</div>',
                            unsafe_allow_html=True,
                        )
                if res["avances"]:
                    st.markdown("**✅ Avances**")
                    for av in res["avances"]:
                        st.markdown(
                            f'<div style="border-left:3px solid #2ecc71;padding:6px 10px;'
                            f'background:#1a1a2e;border-radius:0 4px 4px 0;margin-bottom:4px;font-size:12px;">'
                            f'<b>{av["gremio"]}</b> · {av["descripcion"]}</div>',
                            unsafe_allow_html=True,
                        )
                if res["replanteos"]:
                    st.markdown("**📐 Replanteos / Definiciones técnicas**")
                    st.dataframe(
                        pd.DataFrame(res["replanteos"]),
                        use_container_width=True, hide_index=True,
                    )
                if res["agenda"]:
                    st.markdown("**📅 Agenda próxima jornada**")
                    for ag in res["agenda"]:
                        st.markdown(f'`{ag["hora"]}` — {ag["evento"]}')

                if st.session_state.get("ir_acta"):
                    st.divider()
                    components.html(
                        html_acta_diaria(st.session_state["ir_acta"], st.session_state.get("ir_imgs")),
                        height=420, scrolling=True,
                    )
            else:
                st.info("Aquí aparecerá el análisis estructurado tras procesar.")


# ══════════════════════════════════════════════════════════════════
#  MÓDULO 3 — ACTAS SEMANALES
# ══════════════════════════════════════════════════════════════════
elif modulo == "📁 Actas Semanales":
    st.title("📁 Consolidación y Actas Semanales")
    st.caption("Agrupa automáticamente las actas diarias de la semana para generar el reporte a Dirección.")

    tab_gen, tab_hist = st.tabs(["⚙️ Generar", "📚 Historial"])

    with tab_gen:
        cs1, cs2 = st.columns([1, 2])
        with cs1:
            sem_sel = st.number_input("Semana de obra", min_value=1, max_value=52, value=semana_obra(date.today()))
            gen_btn = st.button("⚙️ Consolidar semana", use_container_width=True, type="primary")

        if gen_btn:
            borrador = consolidar_semana(sem_sel)
            if borrador:
                st.session_state["borrador_semanal"] = borrador
                n = len([i for i in borrador["actas_diarias_ids"].split(",") if i])
                st.success(f"Borrador S{sem_sel} con {n} actas diarias generado.")
            else:
                st.warning(f"Sin actas diarias para la semana {sem_sel}.")

        if "borrador_semanal" in st.session_state:
            b = st.session_state["borrador_semanal"]
            st.divider()
            st.markdown(f"#### Borrador: {b['semana_ano']} &nbsp; ({b['fecha_inicio']} → {b['fecha_fin']})")

            col_ed, col_pv = st.columns([1, 1.3])
            with col_ed:
                resumen_edit = st.text_area("Resumen ejecutivo", value=b.get("resumen_ejecutivo",""), height=160)
                estado_ap    = st.selectbox("Estado de aprobación", ["borrador","pendiente_firma","aprobado"])
                aprobado_por = st.text_input("Aprobado por", value="Darío A. López")

                cg, cd = st.columns(2)
                with cg:
                    if st.button("💾 Guardar acta semanal", use_container_width=True, type="primary"):
                        b["resumen_ejecutivo"] = resumen_edit
                        b["estado_aprobacion"] = estado_ap
                        b["aprobado_por"]      = aprobado_por
                        upsert_acta_semanal(b)
                        st.success(f"✅ {b['id']} guardada.")
                        del st.session_state["borrador_semanal"]
                        st.rerun()

                ids_list    = [i for i in b["actas_diarias_ids"].split(",") if i]
                diarias_sem = [a for a in list_actas_diarias(b["fecha_inicio"], b["fecha_fin"]) if a["id"] in ids_list]
                html_rep    = html_semanal_completo(b, diarias_sem)
                with cd:
                    st.download_button("⬇️ HTML", data=html_rep.encode("utf-8"),
                                       file_name=f"ACTA_{b['id']}.html", mime="text/html",
                                       use_container_width=True)

            with col_pv:
                ids_list    = [i for i in b["actas_diarias_ids"].split(",") if i]
                diarias_sem = [a for a in list_actas_diarias(b["fecha_inicio"], b["fecha_fin"]) if a["id"] in ids_list]
                html_rep    = html_semanal_completo(b, diarias_sem)
                components.html(html_rep, height=520, scrolling=True)

    with tab_hist:
        sem_list = list_actas_semanales()
        if not sem_list:
            st.info("No hay actas semanales guardadas.")
        for s in sem_list:
            ea  = s.get("estado_aprobacion","borrador")
            _ec = {"borrador":"b-blue","pendiente_firma":"b-amber","aprobado":"b-green"}.get(ea,"b-blue")
            ids_list = [i for i in (s.get("actas_diarias_ids") or "").split(",") if i]
            with st.expander(f"📅 {s.get('semana_ano','')} · {s.get('fecha_inicio','')} → {s.get('fecha_fin','')}"):
                st.markdown(f'<span class="badge {_ec}">{ea.replace("_"," ").title()}</span>'
                            f' &nbsp; Aprobado por: **{s.get("aprobado_por","—")}**',
                            unsafe_allow_html=True)
                st.markdown(s.get("resumen_ejecutivo",""))
                c1, c2 = st.columns(2)
                with c1:
                    diarias_p = [a for a in list_actas_diarias(s["fecha_inicio"], s["fecha_fin"]) if a["id"] in ids_list]
                    html_dl = html_semanal_completo(s, diarias_p)
                    st.download_button("⬇️ Descargar HTML", data=html_dl.encode("utf-8"),
                                       file_name=f"ACTA_{s['id']}.html", mime="text/html",
                                       use_container_width=True, key=f"dl_sem_{s['id']}")
                with c2:
                    if st.button(f"🗑️ Eliminar", key=f"del_sem_{s['id']}", use_container_width=True, type="secondary"):
                        delete_acta_semanal(s["id"]); st.rerun()
