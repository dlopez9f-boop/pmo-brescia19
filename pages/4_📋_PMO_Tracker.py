"""
pages/4_📋_PMO_Tracker.py
PMO Live Tracker — Presupuestos y Obras (centros operativos, excluye Chamartín y Brescia)
Lectura/escritura bidireccional con Google Sheets vía gspread.
"""
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="PMO Tracker · Nine", layout="wide", page_icon="📋")

# ── CONSTANTES ────────────────────────────────────────────────────────────────
CENTROS = [
    "Cañaveral", "Cañaveral 2", "Retiro", "Guindalera", "Acacias",
    "Valdebebas", "Chamberí", "Pozuelo", "Fuenterrabía", "Red / Varios",
]
PROVEEDORES = [
    "Munir (Ziad)", "Cador (Luis/Nacho)", "Elecrea (Luis)", "Josevi",
    "Álvaro Medina", "Álvaro Chuso", "Thomas Wellness", "Constherba",
    "Robisipe", "Rafael Cifuentes", "Climatec", "Natalio (Fontanería)",
    "Troser PCI", "RAMONTransportes", "Otro",
]
GREMIOS = [
    "Civil / Fontanería", "Climatización / Ventilación", "Electricidad",
    "Carpintería / Cerrajería", "PCI", "Accesos / Seguridad", "General",
]
ESTADOS_PRES = [
    "Pte. recibir", "Recibido · pte. aprobación", "Aprobado",
    "En ejecución", "50% pagado · pte. 50%", "Terminado · pte. factura",
    "Pagado · cerrado", "Rechazado",
]
ESTADOS_OBRA = [
    "En licitación", "Contratado", "En ejecución",
    "Bloqueado", "Terminado · pte. certificación", "Cerrado",
]
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
SHEET_PRES  = "Presupuestos"
SHEET_OBRAS = "Obras"

# ── CONEXIÓN GOOGLE SHEETS ────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def _get_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    return gspread.authorize(creds)

def _open_sheet():
    return _get_client().open(st.secrets["sheet_name"])

@st.cache_data(ttl=30, show_spinner=False)
def load_tab(tab: str) -> pd.DataFrame:
    try:
        ws = _open_sheet().worksheet(tab)
        rows = ws.get_all_records()
        return pd.DataFrame(rows) if rows else pd.DataFrame(columns=_cols(tab))
    except gspread.exceptions.WorksheetNotFound:
        return pd.DataFrame(columns=_cols(tab))
    except Exception as e:
        st.error(f"Error cargando '{tab}': {e}")
        return pd.DataFrame(columns=_cols(tab))

def _cols(tab: str) -> list[str]:
    if tab == SHEET_PRES:
        return ["Ref","Centro","Concepto","Proveedor","Importe","Estado",
                "Urgencia","PlazoResp","FormaPago","Codigo","Notas"]
    return ["Centro","Descripcion","Gremio","Estado","Importe",
            "FechaInicio","FechaFinEst","Responsable","Notas"]

def save_tab(df: pd.DataFrame, tab: str) -> bool:
    try:
        ws = _open_sheet().worksheet(tab)
        data = df.fillna("").astype(str)
        ws.clear()
        ws.update([data.columns.tolist()] + data.values.tolist())
        load_tab.clear()           # invalida caché
        return True
    except Exception as e:
        st.error(f"Error guardando '{tab}': {e}")
        return False

# ── HELPERS UI ────────────────────────────────────────────────────────────────
NAV_CSS = """
<style>
  [data-testid="stMetricValue"]{font-size:1.6rem!important}
  div[data-testid="stDataFrameResizable"]{border-radius:4px;border:1px solid #DEDAD4}
  .save-bar{display:flex;align-items:center;gap:12px;padding:8px 0}
</style>
"""
st.markdown(NAV_CSS, unsafe_allow_html=True)

NAVY = "#0B1F3A"
GOLD = "#C9A96E"

st.markdown(
    f"<div style='background:{NAVY};padding:12px 20px;border-bottom:2px solid {GOLD};"
    f"margin:-1rem -1rem 1rem -1rem;display:flex;align-items:center;gap:12px'>"
    f"<span style='color:{GOLD};font-weight:700;font-size:15px;letter-spacing:.1em'>"
    f"📋 PMO LIVE TRACKER</span>"
    f"<span style='color:#3a5a80;font-size:11px'>Centros operativos · excluye Chamartín y Brescia</span>"
    f"</div>",
    unsafe_allow_html=True,
)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab_pres, tab_obras = st.tabs(["📋 Presupuestos", "🏗 Obras Abiertas"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — PRESUPUESTOS
# ════════════════════════════════════════════════════════════════════════════
with tab_pres:
    # Inicializar session state
    if "pres_base" not in st.session_state:
        st.session_state.pres_base = load_tab(SHEET_PRES)

    df_pres = st.session_state.pres_base.copy()

    # ── KPIs ──────────────────────────────────────────────────────────────
    total   = len(df_pres)
    pte     = (df_pres.get("Estado","") == "Recibido · pte. aprobación").sum() if not df_pres.empty else 0
    aprobado = (df_pres.get("Estado","") == "Aprobado").sum() if not df_pres.empty else 0
    importe = pd.to_numeric(df_pres.get("Importe", pd.Series([], dtype=float)), errors="coerce").sum()
    criticos = (df_pres.get("Urgencia","") == "CRÍTICO").sum() if not df_pres.empty else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total", total)
    k2.metric("Pte. aprobación", pte)
    k3.metric("Aprobados", aprobado)
    k4.metric("Presupuestado", f"{importe:,.0f} €".replace(",","."))
    k5.metric("🔴 Críticos", criticos)

    st.divider()

    # ── FILTROS ───────────────────────────────────────────────────────────
    fc1, fc2, fc3, _, fr = st.columns([1.5, 1.5, 1.5, 2, 1])
    f_centro = fc1.selectbox("Centro", ["Todos"] + CENTROS, key="fp_c")
    f_estado = fc2.selectbox("Estado", ["Todos"] + ESTADOS_PRES, key="fp_e")
    f_buscar = fc3.text_input("Buscar", placeholder="concepto, proveedor…", key="fp_b")
    if fr.button("🔄 Actualizar", key="ref_pres", use_container_width=True):
        load_tab.clear()
        st.session_state.pres_base = load_tab(SHEET_PRES)
        st.rerun()

    mask = pd.Series([True] * len(df_pres))
    if not df_pres.empty:
        if f_centro != "Todos" and "Centro" in df_pres.columns:
            mask &= df_pres["Centro"] == f_centro
        if f_estado != "Todos" and "Estado" in df_pres.columns:
            mask &= df_pres["Estado"] == f_estado
        if f_buscar:
            q = f_buscar.lower()
            mask &= (
                df_pres.get("Concepto","").str.lower().str.contains(q, na=False) |
                df_pres.get("Proveedor","").str.lower().str.contains(q, na=False) |
                df_pres.get("Ref","").str.lower().str.contains(q, na=False)
            )
    df_view = df_pres[mask] if not df_pres.empty else df_pres

    # ── EDITOR ───────────────────────────────────────────────────────────
    st.caption(f"{len(df_view)} registro{'s' if len(df_view)!=1 else ''}")
    edited_pres = st.data_editor(
        df_view,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_pres",
        column_config={
            "Centro":      st.column_config.SelectboxColumn("Centro", options=CENTROS, width="medium"),
            "Proveedor":   st.column_config.SelectboxColumn("Proveedor", options=PROVEEDORES, width="medium"),
            "Estado":      st.column_config.SelectboxColumn("Estado", options=ESTADOS_PRES, width="medium"),
            "Urgencia":    st.column_config.SelectboxColumn("Urgencia", options=["NORMAL","ALTA","CRÍTICO"], width="small"),
            "FormaPago":   st.column_config.SelectboxColumn("Forma Pago",
                           options=["—","100% al terminar","50% inicio / 50% fin","100% al inicio","Por certificaciones"],
                           width="medium"),
            "Importe":     st.column_config.NumberColumn("Importe (€)", min_value=0, format="%.2f", width="small"),
            "Concepto":    st.column_config.TextColumn("Concepto", width="large"),
            "Notas":       st.column_config.TextColumn("Notas", width="large"),
        },
        hide_index=True,
    )

    # ── GUARDAR ──────────────────────────────────────────────────────────
    has_changes_pres = not edited_pres.equals(df_view)
    sb1, sb2, _ = st.columns([1, 1, 5])
    if has_changes_pres:
        if sb1.button("💾 Guardar cambios", type="primary", key="save_pres"):
            # Reconstruir df completo: filas no filtradas + edited
            if mask.all():
                full_df = edited_pres
            else:
                full_df = st.session_state.pres_base.copy()
                full_df.loc[mask.values, :] = edited_pres.values
            if save_tab(full_df, SHEET_PRES):
                st.session_state.pres_base = full_df.reset_index(drop=True)
                st.success("✅ Guardado en Google Sheets")
                st.rerun()
    else:
        sb1.button("💾 Sin cambios", disabled=True, key="save_pres_dis")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — OBRAS
# ════════════════════════════════════════════════════════════════════════════
with tab_obras:
    if "obras_base" not in st.session_state:
        st.session_state.obras_base = load_tab(SHEET_OBRAS)

    df_obras = st.session_state.obras_base.copy()

    # ── KPIs ──────────────────────────────────────────────────────────────
    tot_o   = len(df_obras)
    ejec_o  = (df_obras.get("Estado","") == "En ejecución").sum() if not df_obras.empty else 0
    bloq_o  = (df_obras.get("Estado","") == "Bloqueado").sum() if not df_obras.empty else 0
    term_o  = (df_obras.get("Estado","") == "Terminado · pte. certificación").sum() if not df_obras.empty else 0

    ko1, ko2, ko3, ko4 = st.columns(4)
    ko1.metric("Total obras", tot_o)
    ko2.metric("En ejecución", ejec_o)
    ko3.metric("🔴 Bloqueadas", bloq_o)
    ko4.metric("Pte. certificar", term_o)

    st.divider()

    # ── FILTROS ───────────────────────────────────────────────────────────
    oc1, oc2, oc3, _, or1 = st.columns([1.5, 1.5, 1.5, 2, 1])
    fo_centro = oc1.selectbox("Centro", ["Todos"] + CENTROS, key="fo_c")
    fo_estado = oc2.selectbox("Estado", ["Todos"] + ESTADOS_OBRA, key="fo_e")
    fo_buscar = oc3.text_input("Buscar", placeholder="descripción, gremio…", key="fo_b")
    if or1.button("🔄 Actualizar", key="ref_obras", use_container_width=True):
        load_tab.clear()
        st.session_state.obras_base = load_tab(SHEET_OBRAS)
        st.rerun()

    omask = pd.Series([True] * len(df_obras))
    if not df_obras.empty:
        if fo_centro != "Todos" and "Centro" in df_obras.columns:
            omask &= df_obras["Centro"] == fo_centro
        if fo_estado != "Todos" and "Estado" in df_obras.columns:
            omask &= df_obras["Estado"] == fo_estado
        if fo_buscar:
            q = fo_buscar.lower()
            omask &= (
                df_obras.get("Descripcion","").str.lower().str.contains(q, na=False) |
                df_obras.get("Gremio","").str.lower().str.contains(q, na=False)
            )
    df_obras_view = df_obras[omask] if not df_obras.empty else df_obras

    # ── EDITOR ───────────────────────────────────────────────────────────
    st.caption(f"{len(df_obras_view)} registro{'s' if len(df_obras_view)!=1 else ''}")
    edited_obras = st.data_editor(
        df_obras_view,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_obras",
        column_config={
            "Centro":       st.column_config.SelectboxColumn("Centro", options=CENTROS, width="medium"),
            "Gremio":       st.column_config.SelectboxColumn("Gremio", options=GREMIOS, width="medium"),
            "Estado":       st.column_config.SelectboxColumn("Estado", options=ESTADOS_OBRA, width="medium"),
            "Importe":      st.column_config.NumberColumn("Importe (€)", min_value=0, format="%.2f", width="small"),
            "Descripcion":  st.column_config.TextColumn("Descripción", width="large"),
            "Responsable":  st.column_config.TextColumn("Responsable", width="small"),
            "Notas":        st.column_config.TextColumn("Notas", width="large"),
        },
        hide_index=True,
    )

    # ── GUARDAR ──────────────────────────────────────────────────────────
    has_changes_obras = not edited_obras.equals(df_obras_view)
    ob1, ob2, _ = st.columns([1, 1, 5])
    if has_changes_obras:
        if ob1.button("💾 Guardar cambios", type="primary", key="save_obras"):
            if omask.all():
                full_o = edited_obras
            else:
                full_o = st.session_state.obras_base.copy()
                full_o.loc[omask.values, :] = edited_obras.values
            if save_tab(full_o, SHEET_OBRAS):
                st.session_state.obras_base = full_o.reset_index(drop=True)
                st.success("✅ Guardado en Google Sheets")
                st.rerun()
    else:
        ob1.button("💾 Sin cambios", disabled=True, key="save_obras_dis")
