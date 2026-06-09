#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bbdd_brescia19.py — Módulo de Base de Datos Excel para PMO Brescia 19
Fuente única de verdad: BBDD_Brescia19_Planning.xlsx
Soporta sincronización bidireccional: App → Excel y Excel → App.
"""
from pathlib import Path
import pandas as pd

# Import Streamlit una sola vez al nivel de módulo.
# El IDE puede marcar esto como "not found" si su intérprete configurado
# no es Miniconda — es un falso positivo; en runtime funciona correctamente.
try:
    import streamlit as st  # type: ignore[import-not-found]
    _HAS_ST = True
except ImportError:
    st = None   # type: ignore[assignment]
    _HAS_ST = False

# ─── RUTA CANÓNICA ──────────────────────────────────────────────────────────
EXCEL_PATH = Path(
    r"C:\Users\dario\OneDrive - NEW FITNESS ARANJUEZ SL"
    r"\00_PROYECTOS\BRESCIA_19\05_OBRAS\01_PLANIFICACION"
    r"\BBDD_Brescia19_Planning.xlsx"
)

COLUMNAS = [
    "ID Tarea",
    "Contrata",
    "Tipo de Partida / FASE",
    "Descripción de la Tarea",
    "Fecha de Inicio",
    "Fecha de Fin Prevista",
    "Estado",
    "% de Avance",
]

ESTADOS_VALIDOS = ["Pendiente", "En curso", "Pausado", "Completado"]

FASES_VALIDAS = [
    "DEMOLICIÓN", "TRABAJOS PREVIOS", "ALBAÑILERÍA", "FONTANERÍA",
    "ELECTRICIDAD", "CLIMATIZACIÓN", "PCI", "ACCESIBILIDAD PMR",
    "CARPINTERÍA", "VINILOS", "DATOS / TELECO", "PUESTA A PUNTO", "APERTURA",
]

# ─── DATOS INICIALES — Desglose completo por partida (S11 · 05/06/2026) ─────
# Formato: (ID, Contrata, Fase, Descripción, Fecha Inicio, Fecha Fin, Estado, % Avance)
DATOS_INICIALES = [

    # ── DEMOLICIÓN ──────────────────────────────────────────────────────────
    ("T-001", "Munir",                "DEMOLICIÓN",        "Demolición y vaciado — local diáfano 760 m²",              "23/04/2026", "30/05/2026", "Completado", 100),

    # ── TRABAJOS PREVIOS ────────────────────────────────────────────────────
    ("T-002", "PMO - Darío",          "TRABAJOS PREVIOS",  "Recibir presupuestos de contratas",                        "04/05/2026", "14/05/2026", "Completado", 100),
    ("T-003", "PMO - Darío",          "TRABAJOS PREVIOS",  "Adjudicar y firmar contratas",                             "04/05/2026", "18/05/2026", "Completado", 100),
    ("T-004", "PMO - Darío",          "TRABAJOS PREVIOS",  "Cerrar planning de obra",                                  "04/05/2026", "22/05/2026", "Completado", 100),
    ("T-005", "Servitec - José",      "TRABAJOS PREVIOS",  "Pedido fabricación equipos clima Daikin",                  "15/05/2026", "17/05/2026", "Completado", 100),
    ("T-006", "Elecrea - Luis",       "TRABAJOS PREVIOS",  "Pedido cuadros eléctricos",                                "16/05/2026", "20/05/2026", "Completado", 100),
    ("T-007", "Munir",                "TRABAJOS PREVIOS",  "Fabricación mueble recepción y mostrador",                 "25/05/2026", "12/06/2026", "En curso",    20),

    # ── ALBAÑILERÍA ─────────────────────────────────────────────────────────
    ("T-008", "Munir",                "ALBAÑILERÍA",       "Replanteo general + trazado tabiquería",                   "25/05/2026", "27/05/2026", "Completado", 100),
    ("T-009", "Munir",                "ALBAÑILERÍA",       "Hueco técnico para conductos clima",                       "25/05/2026", "28/05/2026", "Completado", 100),
    ("T-010", "Munir",                "ALBAÑILERÍA",       "Estructura de tabiquería — 100% COMPLETADA (S11)",         "18/05/2026", "05/06/2026", "Completado", 100),
    ("T-011", "Munir",                "ALBAÑILERÍA",       "Tabique humedad PLACO Glasroc X — vestuarios",             "09/06/2026", "14/06/2026", "Pendiente",    0),
    ("T-012", "Munir",                "ALBAÑILERÍA",       "Tabique grandes alturas — sala de máquinas",               "09/06/2026", "14/06/2026", "Pendiente",    0),
    ("T-013", "Munir",                "ALBAÑILERÍA",       "Tabique sala colectiva + CT + limpieza",                   "09/06/2026", "14/06/2026", "Pendiente",    0),
    ("T-014", "Munir",                "ALBAÑILERÍA",       "Tabiques staff y zonas técnicas",                          "09/06/2026", "12/06/2026", "Pendiente",    0),
    ("T-015", "Munir",                "ALBAÑILERÍA",       "Trasdosado acústico Silentboard — muro colindante",        "10/06/2026", "20/06/2026", "Pendiente",    0),
    ("T-016", "Munir",                "ALBAÑILERÍA",       "Trasdosado acústico Silentboard 181 m² — fachada",         "10/06/2026", "20/06/2026", "Pendiente",    0),
    ("T-017", "Munir",                "ALBAÑILERÍA",       "Falsas vigas cajón técnico 54 m",                          "10/06/2026", "20/06/2026", "Pendiente",    0),
    ("T-018", "Munir",                "ALBAÑILERÍA",       "Tabique EI-120 — compartimentación sala principal (P-03)", "22/06/2026", "07/07/2026", "Pendiente",    0),
    ("T-019", "Munir",                "ALBAÑILERÍA",       "Solado y solera zonas húmedas",                            "22/06/2026", "04/07/2026", "Pendiente",    0),
    ("T-020", "Munir",                "ALBAÑILERÍA",       "Pintura general y remates finales",                        "08/07/2026", "20/07/2026", "Pendiente",    0),

    # ── FONTANERÍA ──────────────────────────────────────────────────────────
    ("T-021", "Munir",                "FONTANERÍA",        "Rozas para fontanería",                                    "27/05/2026", "08/06/2026", "En curso",    90),
    ("T-022", "Munir",                "FONTANERÍA",        "Fontanería general — vestuarios y aseos",                  "27/05/2026", "20/06/2026", "En curso",    65),
    ("T-023", "Munir",                "FONTANERÍA",        "Acometida agua + colector saneamiento",                    "01/06/2026", "14/06/2026", "En curso",    40),

    # ── ELECTRICIDAD ────────────────────────────────────────────────────────
    ("T-024", "Elecrea - Luis",       "ELECTRICIDAD",      "Canalización eléctrica — 1ª fase (P-02)",                  "18/05/2026", "14/06/2026", "En curso",    70),
    ("T-025", "Elecrea - Luis",       "ELECTRICIDAD",      "Cuadros eléctricos y distribución general",                "15/06/2026", "25/06/2026", "Pendiente",    0),
    ("T-026", "Elecrea - Luis",       "ELECTRICIDAD",      "Cierre líneas de fuerza — cardio y fuerza libre",          "15/06/2026", "01/07/2026", "Pendiente",    0),
    ("T-027", "Elecrea - Luis",       "ELECTRICIDAD",      "Foseados e iluminación LED (P-04)",                        "02/07/2026", "18/07/2026", "Pendiente",    0),
    ("T-028", "Elecrea - Luis",       "ELECTRICIDAD",      "Circuitos emergencia y señalización evacuación",           "02/07/2026", "18/07/2026", "Pendiente",    0),

    # ── CLIMATIZACIÓN ───────────────────────────────────────────────────────
    ("T-029", "Servitec - José",      "CLIMATIZACIÓN",     "Conductos distribución Daikin + recuperadora SECO",        "29/05/2026", "25/06/2026", "En curso",    80),
    ("T-030", "Servitec - José",      "CLIMATIZACIÓN",     "Cassettes unidades interiores — sala principal (S12)",     "09/06/2026", "20/06/2026", "Pendiente",    0),
    ("T-031", "Servitec - José",      "CLIMATIZACIÓN",     "Manta térmica Danosa — cubierta (S12)",                    "09/06/2026", "15/06/2026", "Pendiente",    0),
    ("T-032", "Servitec - José",      "CLIMATIZACIÓN",     "Conexión final recuperadora + pruebas de funcionamiento",  "16/06/2026", "20/06/2026", "Pendiente",    0),

    # ── PCI ─────────────────────────────────────────────────────────────────
    ("T-033", "Troser - Leo",         "PCI",               "Detectores sala principal — 51 ud (S11)",                  "04/06/2026", "12/06/2026", "En curso",    25),
    ("T-034", "Troser - Leo",         "PCI",               "Detectores vestuarios y zonas auxiliares",                 "15/06/2026", "22/06/2026", "Pendiente",    0),
    ("T-035", "Troser - Leo",         "PCI",               "BIEs y bocas de incendio equipadas",                       "22/06/2026", "30/06/2026", "Pendiente",    0),
    ("T-036", "Troser - Leo",         "PCI",               "Rociadores sala colectiva y accesos",                      "22/06/2026", "30/06/2026", "Pendiente",    0),
    ("T-037", "Troser - Leo",         "PCI",               "Legalización e inspección PCI — OCA",                      "01/07/2026", "10/07/2026", "Pendiente",    0),

    # ── ACCESIBILIDAD PMR ───────────────────────────────────────────────────
    ("T-038", "Hersan (PMR)",         "ACCESIBILIDAD PMR", "Arrancar fabricación plataforma acceso Hersan",            "25/05/2026", "15/06/2026", "Completado", 100),
    ("T-039", "Hersan (PMR)",         "ACCESIBILIDAD PMR", "🔴 Montaje salvaescaleras PMR en obra (P-05) — CRÍTICO",   "07/07/2026", "11/07/2026", "Pendiente",    0),

    # ── CARPINTERÍA ─────────────────────────────────────────────────────────
    ("T-040", "Josevi",               "CARPINTERÍA",       "Estructuras metálicas de puertas (S12)",                   "09/06/2026", "13/06/2026", "Pendiente",    0),
    ("T-041", "Josevi",               "CARPINTERÍA",       "Cerramiento sala colectiva — mampara (S12)",               "09/06/2026", "20/06/2026", "Pendiente",    0),
    ("T-042", "Josevi",               "CARPINTERÍA",       "Puerta corredera y acceso sala colectiva",                 "16/06/2026", "25/06/2026", "Pendiente",    0),
    ("T-043", "Josevi",               "CARPINTERÍA",       "Suelo técnico de goma — zona peso libre (P-06)",           "01/07/2026", "18/07/2026", "Pendiente",    0),
    ("T-044", "Josevi",               "CARPINTERÍA",       "Carpintería a medida — recepción y vestuarios (P-07)",     "10/07/2026", "24/07/2026", "Pendiente",    0),
    ("T-045", "Josevi",               "CARPINTERÍA",       "Frisos y remates perimetrales sala principal",             "10/07/2026", "22/07/2026", "Pendiente",    0),

    # ── VINILOS ─────────────────────────────────────────────────────────────
    ("T-046", "Publicidad (Julio)",   "VINILOS",           "Vinilos ventanas exteriores — PAUSADO (cambio negro)",     "04/06/2026", "13/06/2026", "Pausado",     10),
    ("T-047", "Publicidad (Julio)",   "VINILOS",           "Rotulación interior + señalética normativa",               "15/07/2026", "25/07/2026", "Pendiente",    0),

    # ── DATOS / TELECO ───────────────────────────────────────────────────────
    ("T-048", "Sale Systems - Javier","DATOS / TELECO",    "Rack datos + cableado UTP Cat6 y patcheo",                "01/07/2026", "14/07/2026", "Pendiente",    0),
    ("T-049", "Sale Systems - Javier","DATOS / TELECO",    "APs WiFi y controlador central",                          "08/07/2026", "18/07/2026", "Pendiente",    0),
    ("T-050", "Sale Systems - Javier","DATOS / TELECO",    "Sistema audio ambiental y pantallas TV",                  "15/07/2026", "22/07/2026", "Pendiente",    0),

    # ── PUESTA A PUNTO ──────────────────────────────────────────────────────
    ("T-051", "Equipamiento (Laura)", "PUESTA A PUNTO",    "Recepción y montaje maquinaria Matrix",                    "24/07/2026", "31/07/2026", "Pendiente",    0),
    ("T-052", "PMO - Darío",          "PUESTA A PUNTO",    "Montaje maquinaria cardio y fuerza libre",                 "24/07/2026", "31/07/2026", "Pendiente",    0),
    ("T-053", "PMO - Darío",          "PUESTA A PUNTO",    "Pruebas domótica, audio y sistemas",                       "25/07/2026", "01/08/2026", "Pendiente",    0),
    ("T-054", "PMO - Darío",          "PUESTA A PUNTO",    "Limpieza fina de obra (P-08)",                             "25/07/2026", "02/08/2026", "Pendiente",    0),
    ("T-055", "PMO - Darío",          "PUESTA A PUNTO",    "Revisión OCA y tramitación licencia de apertura",          "28/07/2026", "02/08/2026", "Pendiente",    0),

    # ── APERTURA ────────────────────────────────────────────────────────────
    ("T-056", "Nine Fitness Group",   "APERTURA",          "🚀 APERTURA NINE FITNESS BRESCIA 19 — Madrid",             "03/08/2026", "05/08/2026", "Pendiente",    0),
]


# ════════════════════════════════════════════════════════════════════════════
# 1. INICIALIZACIÓN  — crea el Excel si no existe
# ════════════════════════════════════════════════════════════════════════════
def init_excel(forzar: bool = False) -> None:
    """Crea el Excel con datos iniciales. Si ya existe, no lo sobreescribe
    salvo que `forzar=True`."""
    if EXCEL_PATH.exists() and not forzar:
        print(f"[BBDD] Excel ya existe: {EXCEL_PATH.name}  (usa forzar=True para recrear)")
        return

    EXCEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(DATOS_INICIALES, columns=COLUMNAS)

    with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl", datetime_format="DD/MM/YYYY") as writer:
        df.to_excel(writer, sheet_name="Planning", index=False)
        ws = writer.sheets["Planning"]
        # Ajuste de anchos de columna automático
        anchos = {"ID Tarea": 10, "Contrata": 22, "Tipo de Partida / FASE": 20,
                  "Descripción de la Tarea": 52, "Fecha de Inicio": 14,
                  "Fecha de Fin Prevista": 18, "Estado": 14, "% de Avance": 12}
        for i, col in enumerate(COLUMNAS, start=1):
            ws.column_dimensions[chr(64 + i)].width = anchos.get(col, 15)

    print(f"[BBDD] Excel creado: {EXCEL_PATH}")
    print(f"       {len(df)} tareas · {len(df['Contrata'].unique())} contratas")


# ════════════════════════════════════════════════════════════════════════════
# 2. LECTURA  — función pura + caché condicional
# ════════════════════════════════════════════════════════════════════════════
def _read_excel() -> pd.DataFrame:
    """Lee el Excel del disco sin caché (función base)."""
    if not EXCEL_PATH.exists():
        init_excel()
    df = pd.read_excel(EXCEL_PATH, sheet_name="Planning", engine="openpyxl",
                       dtype={"% de Avance": float})
    # Normalizar fechas a string DD/MM/AAAA si pandas las convirtió a datetime
    for col in ("Fecha de Inicio", "Fecha de Fin Prevista"):
        if col in df.columns and pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime("%d/%m/%Y")
    return df


# Aplicar @st.cache_data solo cuando Streamlit está disponible.
# En standalone (script Python), load_datos = _read_excel sin caché.
if _HAS_ST:
    load_datos = st.cache_data(ttl=None)(_read_excel)  # type: ignore[misc]
else:
    load_datos = _read_excel


# ════════════════════════════════════════════════════════════════════════════
# 3. ESCRITURA PERSISTENTE  — sincronización App → Excel
# ════════════════════════════════════════════════════════════════════════════
_ANCHOS_COL = {
    "ID Tarea": 10, "Contrata": 22, "Tipo de Partida / FASE": 20,
    "Descripción de la Tarea": 52, "Fecha de Inicio": 14,
    "Fecha de Fin Prevista": 18, "Estado": 14, "% de Avance": 12,
}


def save_datos(df: pd.DataFrame) -> None:
    """
    Guardado a prueba de fallos.  Orden obligatorio:
      A) Escribe en disco (Excel) — fuente de verdad permanente
      B) Actualiza st.session_state — UI no flickea
      C) Invalida caché — próxima lectura va al disco, no al snapshot anterior
    """
    # A) Disco
    EXCEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl", datetime_format="DD/MM/YYYY") as writer:
        df.to_excel(writer, sheet_name="Planning", index=False)
        ws = writer.sheets["Planning"]
        for i, col in enumerate(df.columns, start=1):
            ws.column_dimensions[chr(64 + i)].width = _ANCHOS_COL.get(col, 15)

    if _HAS_ST:
        st.session_state["df_planning"] = df   # B — UI no flickea
        load_datos.clear()                      # C — invalida caché anterior


# ════════════════════════════════════════════════════════════════════════════
# 4. HELPER DE INICIALIZACIÓN DE SESSION STATE  (llamar al top de cada página)
# ════════════════════════════════════════════════════════════════════════════
def init_session_state() -> None:
    """Carga el Excel en session_state si no está ya cargado."""
    if _HAS_ST and "df_planning" not in st.session_state:  # type: ignore[union-attr]
        st.session_state["df_planning"] = load_datos()  # type: ignore[union-attr]


# ════════════════════════════════════════════════════════════════════════════
# EJECUCIÓN STANDALONE  — python bbdd_brescia19.py  →  crea el Excel inicial
# ════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    forzar = "--forzar" in sys.argv
    init_excel(forzar=forzar)
    df = load_datos()
    # print seguro en Windows (evita crash por emojis en cp1252)
    for _, row in df.iterrows():
        linea = f"  {row['ID Tarea']:6}  {row['Contrata'][:22]:22}  {row['Estado']:12}  {row['% de Avance']:>4.0f}%  {row['Descripción de la Tarea'][:45]}"
        print(linea.encode("ascii", errors="replace").decode("ascii"))
