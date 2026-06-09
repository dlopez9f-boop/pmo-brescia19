#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.pmo/dashboard_brescia19.py — PMO Dashboard + Gantt Editor
Fuente de verdad: BBDD_Brescia19_Planning.xlsx (bidireccional)
streamlit run .pmo/dashboard_brescia19.py
"""

import sys
import streamlit as st          # type: ignore[import-not-found]
import pandas as pd
import plotly.express as px    # type: ignore[import-not-found]
from datetime import datetime
from pathlib import Path

# bbdd_brescia19.py está en el directorio raíz del proyecto (padre de .pmo/)
sys.path.insert(0, str(Path(__file__).parent.parent))
from bbdd_brescia19 import load_datos, save_datos  # type: ignore[import]

st.set_page_config(
    page_title="PMO Brescia 19 — Gantt & Control",
    page_icon="🏗️",
    layout="wide",
)

st.markdown("""
<style>
  [data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; }
  [data-testid="stMetricDelta"]  { font-size: 0.85rem; }
  .block-container { padding-top: 1.5rem; }
  .btn-primary > button {
    background: linear-gradient(135deg, #e94560, #c0392b) !important;
    color: #fff !important; font-weight: 800 !important;
    font-size: 15px !important; border: none !important;
    box-shadow: 0 3px 10px rgba(233,69,96,.35) !important;
  }
  .btn-reload > button {
    background: linear-gradient(135deg, #0f3460, #1a4a7a) !important;
    color: #fff !important; font-weight: 700 !important;
    border: none !important;
  }
  div[data-testid="stDataEditor"] { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Rutas ──────────────────────────────────────────────────────────────────
GANTT_CSV = Path("actas_data/gantt_tareas.csv")   # conservado para compatibilidad
PROG_CSV  = Path("actas_data/control_obra.csv")

FECHA_APERTURA = datetime(2026, 8, 3)
FECHA_INICIO   = datetime(2026, 5, 18)
hoy            = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

# ── Opciones para selectboxes del editor ──────────────────────────────────
CONTRATAS_VALIDAS = [
    "Munir", "Elecrea - Luis", "Servitec - José", "Troser - Leo",
    "Josevi", "Hersan (PMR)", "Sale Systems - Javier",
    "Equipamiento (Laura)", "Publicidad (Julio)", "PMO - Darío",
    "Nine Fitness Group",
]
FASES_VALIDAS = [
    "DEMOLICIÓN", "TRABAJOS PREVIOS", "ALBAÑILERÍA", "FONTANERÍA",
    "ELECTRICIDAD", "CLIMATIZACIÓN", "PCI", "ACCESIBILIDAD PMR",
    "CARPINTERÍA", "VINILOS", "DATOS / TELECO", "PUESTA A PUNTO", "APERTURA",
]
ESTADOS_VALIDOS = ["Pendiente", "En curso", "Pausado", "Completado"]

# ── Colores por contrata (Gantt visual) ───────────────────────────────────
CONTRATA_COLORS = {
    "Munir":                  "#4A90D9",
    "Elecrea - Luis":         "#F5A623",
    "Servitec - José":        "#00BCD4",
    "Troser - Leo":           "#FF4B4B",
    "Josevi":                 "#9B59B6",
    "Hersan (PMR)":           "#E94560",
    "Sale Systems - Javier":  "#2ECC71",
    "Equipamiento (Laura)":   "#1ABC9C",
    "Publicidad (Julio)":     "#FF9800",
    "PMO - Darío":            "#607D8B",
    "Nine Fitness Group":     "#FFD700",
}

# ══════════════════════════════════════════════════════════════════
#  HELPERS: conversión Excel ↔ Gantt
# ══════════════════════════════════════════════════════════════════

def planning_to_gantt(df_pl: pd.DataFrame) -> pd.DataFrame:
    """Convierte df_planning (Excel) al DataFrame que necesita Plotly timeline."""
    df = df_pl.copy()
    df["Inicio"] = pd.to_datetime(df["Fecha de Inicio"],      format="%d/%m/%Y", errors="coerce")
    df["Fin"]    = pd.to_datetime(df["Fecha de Fin Prevista"], format="%d/%m/%Y", errors="coerce")
    df = df.rename(columns={
        "Descripción de la Tarea": "Partida",
        "Contrata":                "Gremio",
        "Tipo de Partida / FASE":  "Fase",
    })
    df = df.dropna(subset=["Inicio", "Fin"])
    return df[["Fase", "Partida", "Gremio", "Inicio", "Fin", "Estado", "% de Avance"]].copy()


def df_to_editor(df_pl: pd.DataFrame) -> pd.DataFrame:
    """Prepara df_planning para st.data_editor (fechas como objetos date)."""
    df = df_pl.copy()
    for col in ("Fecha de Inicio", "Fecha de Fin Prevista"):
        df[col] = pd.to_datetime(df[col], format="%d/%m/%Y", errors="coerce").dt.date
    df["% de Avance"] = pd.to_numeric(df["% de Avance"], errors="coerce").fillna(0).astype(int)
    return df


def editor_to_planning(df_edited: pd.DataFrame) -> pd.DataFrame:
    """Convierte el resultado del editor de vuelta a formato guardable."""
    df = df_edited.copy()
    for col in ("Fecha de Inicio", "Fecha de Fin Prevista"):
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%d/%m/%Y")
    return df


# ══════════════════════════════════════════════════════════════════
#  DATOS DE PROGRESO (CSV auxiliar)
# ══════════════════════════════════════════════════════════════════

@st.cache_data
def load_progreso() -> pd.DataFrame:
    return pd.read_csv(PROG_CSV)


def save_progreso(df: pd.DataFrame):
    df.to_csv(PROG_CSV, index=False)


# ══════════════════════════════════════════════════════════════════
#  INICIALIZACIÓN SESSION STATE
# ══════════════════════════════════════════════════════════════════

if "df_planning" not in st.session_state:
    st.session_state["df_planning"] = load_datos()

if "df_tareas" not in st.session_state:
    # Gantt derivado del Excel — fuente única de verdad
    st.session_state["df_tareas"] = planning_to_gantt(st.session_state["df_planning"])

if "df_prog" not in st.session_state:
    st.session_state["df_prog"] = load_progreso()

if "planning_borrador" not in st.session_state:
    st.session_state["planning_borrador"] = False

# ══════════════════════════════════════════════════════════════════
#  CABECERA + KPIs
# ══════════════════════════════════════════════════════════════════

st.title("🏗️ Planificación Maestra — Nine Fitness Brescia 19")
st.caption("Promotor: Nine Fitness Group S.L. | DO: Darío A. López | C/ Brescia 19, 28028 Madrid")

dias_restantes     = (FECHA_APERTURA - hoy).days
dias_transcurridos = max(0, (hoy - FECHA_INICIO).days)
duracion_total     = (FECHA_APERTURA - FECHA_INICIO).days
pct_tiempo         = round((dias_transcurridos / duracion_total) * 100, 1)
dias_hersan        = (datetime(2026, 7, 7) - hoy).days

df_pl = st.session_state["df_planning"]
n_completadas = int((df_pl["Estado"] == "Completado").sum())
n_en_curso    = int((df_pl["Estado"] == "En curso").sum())
n_total       = len(df_pl)
pct_avance    = round(pd.to_numeric(df_pl["% de Avance"], errors="coerce").fillna(0).mean(), 1)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("⏳ Días para Apertura", f"{dias_restantes}d",
          delta="🟢 En plazo" if dias_restantes > 45 else ("🟡 Alerta" if dias_restantes > 20 else "🔴 Crítico"))
c2.metric("📅 Día de Obra", f"Día {dias_transcurridos}", "Inicio: 18-May-2026")
c3.metric("📊 % Avance Global", f"{pct_avance}%", f"{n_completadas}/{n_total} tareas ✅")
c4.metric("🔄 Tareas En Curso", f"{n_en_curso}", f"{n_total - n_completadas - n_en_curso} pendientes")
c5.metric("♿ Hito Hersan", f"{dias_hersan}d", "07-Jul-2026 · CRÍTICO", delta_color="inverse")

st.divider()

col_oscar, col_mkt, col_rrhh = st.columns(3)
with col_oscar:
    st.info(f"**{'🟢' if dias_restantes > 45 else '🟡'} Óscar (Dirección):** Sin solapamientos. Próximo hito: Hersan 07-Jul.")
with col_mkt:
    st.warning("**📢 Marketing:** Hito preventa: Fachada disponible tras Josevi → **07-Jul**.")
with col_rrhh:
    st.success("**👥 RRHH / Ops:** Entrega vestuarios para formaciones → **24-Jul**.")

st.divider()

# ══════════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════════

tab_gantt, tab_editor, tab_prog = st.tabs(["📊 Gantt", "✏️ Editor Planning (Excel)", "📈 Progreso Contratas"])


# ─── TAB 1: GANTT ─────────────────────────────────────────────────────────
with tab_gantt:
    if st.session_state["planning_borrador"]:
        st.warning("⚠️ Hay cambios sin guardar. Ve al **Editor Planning** y pulsa **💾 Guardar en Excel**.")

    df = st.session_state["df_tareas"].copy()

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fases_sel = st.multiselect(
            "Filtrar por Fase / Tipo de Partida",
            options=sorted(df["Fase"].dropna().unique().tolist()),
            default=df["Fase"].dropna().unique().tolist(),
            key="gantt_fases",
        )
    with col_f2:
        gremios_sel = st.multiselect(
            "Filtrar por Contrata",
            options=sorted(df["Gremio"].dropna().unique().tolist()),
            default=df["Gremio"].dropna().unique().tolist(),
            key="gantt_gremios",
        )

    df_vis = df[df["Fase"].isin(fases_sel) & df["Gremio"].isin(gremios_sel)].copy()

    # Hitos de 1 día: añadir mínimo de visibilidad
    mask_hito = df_vis["Inicio"] == df_vis["Fin"]
    df_vis.loc[mask_hito, "Fin"] = df_vis.loc[mask_hito, "Fin"] + pd.Timedelta(days=1)

    # Etiqueta para hover: incluye Estado y % Avance
    df_vis["Info"] = df_vis.apply(
        lambda r: f"{r.get('Estado','—')} · {int(r.get('% de Avance', 0))}%", axis=1
    )

    fig = px.timeline(
        df_vis,
        x_start="Inicio", x_end="Fin",
        y="Partida", color="Gremio",
        color_discrete_map=CONTRATA_COLORS,
        hover_data={"Gremio": True, "Fase": True, "Info": True,
                    "Inicio": "|%d-%b-%Y", "Fin": "|%d-%b-%Y"},
        labels={"Partida": "Tarea", "Gremio": "Contrata"},
        title="Diagrama de Gantt — Planificación Maestra Brescia 19 · Apertura 03-Ago-2026",
    )

    def ts(d):
        return pd.Timestamp(d).timestamp() * 1000

    fig.add_vline(x=ts(hoy.strftime("%Y-%m-%d")), line_width=2, line_dash="dash",
                  line_color="#FFFFFF",
                  annotation_text=f"◀ HOY {hoy.strftime('%d %b')}",
                  annotation_position="top right",
                  annotation_font=dict(color="#FFFFFF", size=11))
    fig.add_vline(x=ts("2026-07-07"), line_width=2, line_dash="dot", line_color="#FF4B4B",
                  annotation_text="Hersan 07-Jul ♿", annotation_position="top left",
                  annotation_font=dict(color="#FF4B4B", size=11))
    fig.add_vline(x=ts("2026-08-03"), line_width=2, line_dash="dot", line_color="#FFD700",
                  annotation_text="APERTURA 03-Ago 🚀", annotation_position="top left",
                  annotation_font=dict(color="#FFD700", size=11))
    fig.add_vrect(x0=ts("2026-07-24"), x1=ts("2026-08-02"),
                  fillcolor="#1ABC9C", opacity=0.08, layer="below", line_width=0,
                  annotation_text="Margen limpieza/licencias", annotation_position="top left",
                  annotation_font=dict(color="#1ABC9C", size=10))

    fig.update_layout(
        paper_bgcolor="#0e1117", plot_bgcolor="#161b27", font_color="#F0F2F6",
        height=700,
        xaxis=dict(showgrid=True, gridcolor="#2a2f3e", tickformat="%d %b", tickangle=-40,
                   dtick="M0.5",
                   range=[FECHA_INICIO - pd.Timedelta(days=3),
                          FECHA_APERTURA + pd.Timedelta(days=5)]),
        yaxis=dict(autorange="reversed", showgrid=False, tickfont=dict(size=11)),
        legend=dict(orientation="h", yanchor="bottom", y=1.01,
                    xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=70, b=40),
        title_font=dict(size=14),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabla estado contractual
    st.divider()
    st.subheader("📋 Estado Contractual por Contrata")
    estado_df = pd.DataFrame([
        {"Gremio": "❄️ Climatización (Servitec/José)", "Límite": "25-Jun-2026", "Estado": "🟢 En Plazo",  "Riesgo": "Cassettes y conexión recuperadora en S12."},
        {"Gremio": "🔥 PCI (Troser/Leo)",               "Límite": "30-Jun-2026", "Estado": "🟢 En Plazo",  "Riesgo": "51 detectores. Previsión cierre 12/06."},
        {"Gremio": "⚡ Electricidad (Elecrea/Luis)",     "Límite": "01-Jul-2026", "Estado": "🟡 Atención",  "Riesgo": "Presupuesto visto bueno. Pendiente firma Luis."},
        {"Gremio": "♿ Salvaescaleras (Hersan)",          "Límite": "07-Jul-2026", "Estado": "🔴 CRÍTICO",   "Riesgo": "Deadline 05/06 VENCIDO. Escalar lunes 08/06."},
        {"Gremio": "🪵 Carpintería/Acabados (Josevi)",   "Límite": "07-Jul-2026", "Estado": "🟢 En Plazo",  "Riesgo": "Entra lunes 09/06: estructuras puertas."},
        {"Gremio": "🧱 Civil/Fontanería (Munir)",        "Límite": "Continuo",    "Estado": "🟢 En Plazo",  "Riesgo": "Estructura tabiquería 100% completada S11."},
        {"Gremio": "🖼️ Vinilos (Julio/Javi)",            "Límite": "13-Jun-2026", "Estado": "⏸️ Pausado",   "Riesgo": "Cambio a color negro. Pendiente confirmación Javi."},
    ])
    st.dataframe(estado_df, use_container_width=True, hide_index=True)


# ─── TAB 2: EDITOR PLANNING (EXCEL) ──────────────────────────────────────
with tab_editor:

    # ── Encabezado visual ─────────────────────────────────────────────────
    col_tit, col_ruta = st.columns([2, 3])
    with col_tit:
        st.markdown("### ✏️ Editor de Planning — Base de Datos Excel")
    with col_ruta:
        st.caption(
            "📂 Fuente única de verdad:  "
            "`BRESCIA_19/05_OBRAS/01_PLANIFICACION/BBDD_Brescia19_Planning.xlsx`"
        )

    # ── KPIs del planning ────────────────────────────────────────────────
    df_pl = st.session_state["df_planning"]
    n_tot  = len(df_pl)
    n_comp = int((df_pl["Estado"] == "Completado").sum())
    n_cur  = int((df_pl["Estado"] == "En curso").sum())
    n_pau  = int((df_pl["Estado"] == "Pausado").sum())
    n_pen  = int((df_pl["Estado"] == "Pendiente").sum())
    avg_av = round(pd.to_numeric(df_pl["% de Avance"], errors="coerce").fillna(0).mean(), 1)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("📋 Total tareas",   n_tot)
    k2.metric("✅ Completadas",    n_comp, f"{round(n_comp/n_tot*100)}%")
    k3.metric("🔄 En curso",       n_cur)
    k4.metric("⏸️ Pausadas",       n_pau)
    k5.metric("📊 Avance medio",   f"{avg_av}%")

    # ── Banner borrador ───────────────────────────────────────────────────
    if st.session_state["planning_borrador"]:
        st.warning("⚠️ Tienes cambios sin guardar. Pulsa **💾 Guardar en Excel** para persistirlos.")
    else:
        st.info(
            "🔄 **Sincronización bidireccional activa.** "
            "Edita aquí y guarda → Excel actualizado. "
            "Edita el Excel a mano y pulsa ↺ Recargar → tabla actualizada."
        )

    st.divider()

    # ── Data editor principal ─────────────────────────────────────────────
    df_edit = df_to_editor(st.session_state["df_planning"])

    edited = st.data_editor(
        df_edit,
        column_config={
            "ID Tarea": st.column_config.TextColumn(
                "ID", width="small", disabled=True,
            ),
            "Contrata": st.column_config.SelectboxColumn(
                "Contrata", options=CONTRATAS_VALIDAS, width="medium", required=True,
            ),
            "Tipo de Partida / FASE": st.column_config.SelectboxColumn(
                "Fase / Tipo", options=FASES_VALIDAS, width="medium", required=True,
            ),
            "Descripción de la Tarea": st.column_config.TextColumn(
                "Descripción de la Tarea", width="large",
            ),
            "Fecha de Inicio": st.column_config.DateColumn(
                "Inicio", format="DD/MM/YYYY", width="small",
            ),
            "Fecha de Fin Prevista": st.column_config.DateColumn(
                "Fin Previsto", format="DD/MM/YYYY", width="small",
            ),
            "Estado": st.column_config.SelectboxColumn(
                "Estado", options=ESTADOS_VALIDOS, width="small", required=True,
            ),
            "% de Avance": st.column_config.ProgressColumn(
                "% Avance", min_value=0, max_value=100, format="%d%%", width="small",
            ),
        },
        num_rows="dynamic",
        use_container_width=True,
        key="excel_editor",
        height=520,
    )

    # Marcar borrador si algo cambió
    if not edited.equals(df_edit):
        st.session_state["planning_borrador"] = True

    st.divider()

    # ── Botones de acción ────────────────────────────────────────────────
    col_save, col_reload, col_spacer = st.columns([2, 2, 3])

    with col_save:
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        btn_guardar = st.button(
            "💾 Guardar en Excel + Actualizar Gantt",
            type="primary",
            use_container_width=True,
            key="btn_guardar_excel",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_reload:
        st.markdown('<div class="btn-reload">', unsafe_allow_html=True)
        btn_reload = st.button(
            "↺ Recargar desde Excel",
            use_container_width=True,
            key="btn_reload_excel",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Lógica GUARDAR ────────────────────────────────────────────────────
    if btn_guardar:
        # Validación: Inicio ≤ Fin
        df_val = edited.copy()
        fi = pd.to_datetime(df_val["Fecha de Inicio"], errors="coerce")
        ff = pd.to_datetime(df_val["Fecha de Fin Prevista"], errors="coerce")
        invalidas = df_val[(fi > ff) & fi.notna() & ff.notna()]

        if not invalidas.empty:
            st.error(
                f"❌ {len(invalidas)} tarea(s) tienen Fecha Inicio > Fecha Fin. "
                "Corrígelas antes de guardar."
            )
            with st.expander("Ver tareas con error"):
                st.dataframe(invalidas[["ID Tarea", "Descripción de la Tarea",
                                        "Fecha de Inicio", "Fecha de Fin Prevista"]],
                             hide_index=True)
        else:
            # A) Convertir fechas a string DD/MM/AAAA
            df_save = editor_to_planning(edited)

            # B) Guardar en Excel (A=disco B=session_state C=clear caché)
            save_datos(df_save)

            # C) Sincronizar Gantt desde el nuevo df_planning
            st.session_state["df_tareas"] = planning_to_gantt(df_save)
            st.session_state["planning_borrador"] = False

            # D) Feedback visual inmediato
            n_edit = len(edited)
            avg_new = round(pd.to_numeric(edited["% de Avance"], errors="coerce").fillna(0).mean(), 1)
            st.success(
                f"✅ **Excel actualizado correctamente.** "
                f"{n_edit} tareas guardadas · Avance medio: **{avg_new}%** · "
                f"Gantt sincronizado al instante."
            )
            st.balloons()
            st.rerun()

    # ── Lógica RECARGAR ──────────────────────────────────────────────────
    if btn_reload:
        load_datos.clear()
        df_fresh = load_datos()
        st.session_state["df_planning"]       = df_fresh
        st.session_state["df_tareas"]         = planning_to_gantt(df_fresh)
        st.session_state["planning_borrador"] = False
        st.success("↺ Datos recargados desde Excel. Gantt actualizado.")
        st.rerun()

    # ── Vista compacta por contrata ──────────────────────────────────────
    st.divider()
    st.markdown("#### 📊 Resumen de Avance por Contrata")

    df_resumen = (
        df_pl.copy()
        .assign(**{"% de Avance": pd.to_numeric(df_pl["% de Avance"], errors="coerce").fillna(0)})
        .groupby("Contrata")
        .agg(
            Tareas=("ID Tarea", "count"),
            Avance_medio=("% de Avance", "mean"),
            Completadas=("Estado", lambda x: (x == "Completado").sum()),
        )
        .reset_index()
        .sort_values("Avance_medio", ascending=False)
    )

    for _, row in df_resumen.iterrows():
        c_nm, c_pr, c_st = st.columns([3, 5, 2])
        with c_nm:
            color_dot = CONTRATA_COLORS.get(str(row["Contrata"]), "#94a3b8")
            st.markdown(
                f'<span style="color:{color_dot};font-size:18px;">●</span> '
                f'**{row["Contrata"]}**  '
                f'<small style="color:#94a3b8;">{int(row["Tareas"])} tareas · '
                f'{int(row["Completadas"])} completadas</small>',
                unsafe_allow_html=True,
            )
        with c_pr:
            st.progress(int(row["Avance_medio"]) / 100)
        with c_st:
            av = int(row["Avance_medio"])
            color_av = "#27ae60" if av >= 80 else ("#e67e22" if av >= 30 else "#c0392b")
            st.markdown(
                f'<b style="color:{color_av};font-size:16px;">{av}%</b>',
                unsafe_allow_html=True,
            )


# ─── TAB 3: PROGRESO CONTRATAS ────────────────────────────────────────────
with tab_prog:
    st.markdown("### 📈 Progreso de Ejecución por Contrata")
    st.info("Edita el progreso (%) y el estado de cada gremio. Pulsa **💾 Guardar Progreso** para actualizar.")

    df_p = st.session_state["df_prog"].copy()

    edited_prog = st.data_editor(
        df_p,
        column_config={
            "Gremio":       st.column_config.TextColumn("Gremio / Empresa", width="large"),
            "Responsable":  st.column_config.TextColumn("Responsable", width="medium"),
            "Fecha_Inicio": st.column_config.DateColumn("Inicio", format="YYYY-MM-DD"),
            "Fecha_Limite": st.column_config.DateColumn("Límite", format="YYYY-MM-DD"),
            "Progreso":     st.column_config.NumberColumn("Progreso %", min_value=0, max_value=100, step=1),
            "Estado":       st.column_config.SelectboxColumn("Estado",
                                options=["Al día", "Alerta", "Crítico", "Completado"]),
        },
        num_rows="dynamic",
        use_container_width=True,
        key="prog_editor",
        height=280,
    )

    if st.button("💾 Guardar Progreso", type="primary", key="btn_guardar_prog"):
        save_progreso(edited_prog)
        st.session_state["df_prog"] = edited_prog
        load_progreso.clear()
        st.success("✅ Progreso actualizado.")
        st.rerun()

    st.divider()
    st.subheader("Barras de progreso actuales")
    for _, row in st.session_state["df_prog"].iterrows():
        c_txt, c_bar, c_st = st.columns([2, 5, 1])
        with c_txt:
            st.markdown(f"**{row['Gremio']}**  \n*Límite: {row['Fecha_Limite']}*")
        with c_bar:
            st.progress(int(row["Progreso"]) / 100)
        with c_st:
            icono = ("🟢" if row["Estado"] == "Al día" else
                     "🟡" if row["Estado"] == "Alerta" else
                     "✅" if row["Estado"] == "Completado" else "🔴")
            st.caption(f"{icono} {int(row['Progreso'])}%")


st.divider()
st.caption(
    f"PMO Brescia 19 · Darío A. López · "
    f"BD: BBDD_Brescia19_Planning.xlsx (Excel bidireccional) · "
    f"{hoy.strftime('%d-%b-%Y')}"
)
