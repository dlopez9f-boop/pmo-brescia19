"""
setup_google_sheet.py
Ejecutar UNA VEZ para crear las pestañas del Google Sheet y
cargar los datos iniciales desde el tracker (estado 22/09/2026).

Uso:
    python setup_google_sheet.py

Requisitos:
    - .streamlit/secrets.toml configurado con gcp_service_account y sheet_name
    - pip install gspread google-auth streamlit
"""
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# ── Datos iniciales (estado 22/09/2026) ──────────────────────────────────────
PRESUPUESTOS_INICIALES = [
    ["RFQ-JOS-2609",        "Cañaveral 2",  "Suministro rejilla fachada (27,5×31,5 cm) aluminio antracita",       "Josevi",              0,    "Pte. recibir",              "CRÍTICO", "25/09/2026", "100% al terminar", "OPEX-CAN-CERR",  "Rejilla negra id. existentes. URGENTE viernes 26/sáb 27 sept."],
    ["RFQ-MUN-2609-001",    "Cañaveral 2",  "Apertura hueco fachada para rejilla clima (60×60 cm) + remate",      "Munir (Ziad)",        0,    "Pte. recibir",              "ALTA",    "24/09/2026", "50% inicio / 50% fin", "OPEX-CAN-CIVIL", "Coordinar con Josevi — Munir abre, Josevi coloca rejilla."],
    ["RFQ-MUN-2609-002",    "Cañaveral",    "Reparación gotera forjado parking — impermeabilización y sellado",   "Munir (Ziad)",        0,    "Pte. recibir",              "CRÍTICO", "22/09/2026", "100% al terminar", "OPEX-CAN-FONT",  "Gotera activa. URGENTE."],
    ["RFQ-RAM-001",         "Red / Varios", "Portes material F1 y tarimas — Arganda → Caña 2 → Brescia → WAK",   "RAMONTransportes",  150,    "Aprobado",                  "NORMAL",  "programado", "100% al terminar", "OPEX-RED-TRANSP","Ruta múltiple confirmada."],
    ["RFQ-MUN-CAN2-SUELO",  "Cañaveral 2",  "Instalación nuevo suelo zonas comunes — alto tránsito",              "Munir (Ziad)",     3125,    "Aprobado",                  "ALTA",    "25/09/2026", "50% inicio / 50% fin", "CAPEX-CAN-CIVIL","Ppto APROBADO 3.125€ sin IVA. Inicio viernes 25-09."],
    ["RFQ-JOS-ACA-BOX",     "Acacias",      "Estructura de boxeo — brazos 80×80mm + anillas",                     "Josevi",            270,    "Recibido · pte. aprobación","NORMAL",  "viernes",    "—",                "CAPEX-ACA-EQUIP","Precio 270€+IVA. Inicio viernes previsto. Pte. aprobación."],
    ["RFQ-JOS-CAN-MAMP",    "Cañaveral",    "Mampara tornos — pantalla/mampara fija lateral (41×76 cm)",          "Josevi",              0,    "Pte. recibir",              "NORMAL",  "",           "—",                "CAPEX-CAN-CARP", "Pte. presupuesto Josevi."],
    ["RFQ-CAN1-ARMCYII",    "Cañaveral",    "Puerta armario CYII — lamas oscuras para tapar armario agua",        "Munir (Ziad)",        0,    "Pte. recibir",              "NORMAL",  "",           "—",                "OPEX-CAN-CERR",  "Revisar martes con Munir."],
    ["RFQ-FUE-FONT",        "Fuenterrabía", "Intervenciones eléctricas Elecrea — Fuerterrabía + Cañaveral + Retiro","Elecrea (Luis)",   0,    "Terminado · pte. factura",  "CRÍTICO", "ejecutado",  "100% al terminar", "OPEX-FUE-ELEC",  "Ejecutado: enchufe+interruptor+focos Fuerterrabía. Pte factura conjunta."],
    ["RFQ-LUIS-ELECREA-CONJ","Red / Varios","Factura conjunta Elecrea — Fuenterrabía + Cañaveral + Retiro LEDs",  "Elecrea (Luis)",      0,    "Pte. recibir",              "CRÍTICO", "URGENTE",    "100% al terminar", "OPEX-RED-ELEC",  "Solicitada factura/ppto conjunto. Ver mail 21/09."],
]

OBRAS_INICIALES = [
    ["Cañaveral 2",  "Remates exteriores: fachada, rejilla clima, suelo zonas comunes, alicatado entrada","Civil / Fontanería", "En ejecución", 0, "",           "27/09/2026", "Darío", "Pending: Josevi+Munir. Suelo aprobado 3.125€, inicio viernes."],
    ["Cañaveral 2",  "Remates entrada — rematar alicatado y paredes",                                     "Civil / Fontanería", "En ejecución", 0, "",           "",           "Munir (Ziad)", "Garantía Munir. Sin coste."],
    ["Cañaveral",    "Suelos abombados — revisar y repegar zonas levantadas",                             "Civil / Fontanería", "En ejecución", 0, "",           "26/09/2026", "Munir (Ziad)", "Garantía Munir. Revisión viernes."],
    ["Cañaveral",    "Puerta emergencia — rematar detalles constructivos",                                 "Civil / Fontanería", "En ejecución", 0, "",           "",           "Munir (Ziad)", "Garantía Munir. Pte. revisión."],
    ["Cañaveral",    "Informe acústico — propuesta actuación por vibraciones",                            "General",            "Bloqueado",    0, "",           "",           "Darío",        "Pte. envío a propiedad."],
    ["Cañaveral",    "Protección LGA Contadores — cableado eléctrico expuesto en cuarto contadores",     "Electricidad",       "En ejecución", 0, "",           "",           "Darío",        "Reclamación garantía Elecrea/Luis."],
    ["Cañaveral",    "Salida de emergencia Local 1 — estado y remates",                                  "General",            "En ejecución", 0, "",           "",           "Darío",        "Local 1."],
    ["Cañaveral",    "Cuadros eléctricos Local 1 — revisión y remates",                                  "Electricidad",       "En ejecución", 0, "",           "",           "Darío",        "Local 1."],
    ["Cañaveral 2",  "Interior / pintura Local 2",                                                        "General",            "En ejecución", 0, "",           "",           "Darío",        "Local 2."],
    ["Cañaveral",    "Interruptor foco condenado — no se puede encender ni apagar",                      "Electricidad",       "Bloqueado",    0, "",           "",           "Darío",        "Remate Elecrea/Luis."],
    ["Guindalera",   "Salida de emergencia — puerta",                                                     "Carpintería / Cerrajería","Terminado · pte. certificación",0,"","", "Darío",        "EJECUTADO. Ok visto."],
    ["Guindalera",   "Salida de emergencia — rampa",                                                      "Carpintería / Cerrajería","Terminado · pte. certificación",0,"","", "Darío",        "EJECUTADO. Listo, revisado."],
    ["Guindalera",   "Climatización sala colectiva — tapa unidad + puesta a punto",                      "Climatización / Ventilación","En ejecución",0,"",     "",           "Darío",        "Falta colocar tapa + puesta a punto."],
    ["Guindalera",   "Domótica — sincronizar audio con micrófono",                                       "General",            "En ejecución", 0, "",           "mañana tarde","Darío",       "Previsto mañana por la tarde."],
    ["Guindalera",   "Control acceso — lector puerta automática + garaje parking",                       "Accesos / Seguridad","Bloqueado",    0, "",           "",           "Darío",        "Esperando lector. Contestación Luis pendiente."],
    ["Retiro",       "Enchufes antigua sala de rayos — revisión y arreglo",                              "Electricidad",       "Bloqueado",    0, "",           "",           "Darío",        "Pendiente visita Luis."],
    ["Retiro",       "Climatización sala colectiva — pérdida agua en estiramientos",                     "Climatización / Ventilación","En ejecución",0,"",     "22/09/2026", "Darío",        "Viene fontanero+clima martes mañana."],
    ["Retiro",       "Zona de racks — espejo (pendiente instalación)",                                   "General",            "Bloqueado",    0, "",           "",           "Darío",        "Enviar foto a Luis y que venga."],
    ["Fuenterrabía", "Remate tótem — enchufe parte baja nuevo muro + toma de datos",                    "Electricidad",       "En ejecución", 0, "",           "pdte fecha", "Darío",        "Foto enviada a Luis. Remate Elecrea."],
    ["Retiro",       "Iluminación LED — LEDs dejaron de iluminar (nueva incidencia)",                    "Electricidad",       "Bloqueado",    0, "",           "urgente",    "Darío",        "Foto enviada a Luis. Pte. diagnóstico."],
]

CABECERA_PRES  = ["Ref","Centro","Concepto","Proveedor","Importe","Estado",
                   "Urgencia","PlazoResp","FormaPago","Codigo","Notas"]
CABECERA_OBRAS = ["Centro","Descripcion","Gremio","Estado","Importe",
                   "FechaInicio","FechaFinEst","Responsable","Notas"]

def main():
    # Cargar credentials desde secrets.toml
    secrets = st.secrets
    creds = Credentials.from_service_account_info(
        secrets["gcp_service_account"], scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet_name = secrets["sheet_name"]

    try:
        sh = client.open(sheet_name)
        print(f"✅ Google Sheet '{sheet_name}' encontrado.")
    except gspread.SpreadsheetNotFound:
        sh = client.create(sheet_name)
        # Compartir con el email de servicio y con el propietario
        sh.share(None, perm_type="anyone", role="writer")
        print(f"✅ Google Sheet '{sheet_name}' creado. URL: {sh.url}")

    # ── Pestaña Presupuestos ──────────────────────────────────────────────
    try:
        ws_pres = sh.worksheet("Presupuestos")
        ws_pres.clear()
        print("🔄 Pestaña 'Presupuestos' limpiada.")
    except gspread.WorksheetNotFound:
        ws_pres = sh.add_worksheet("Presupuestos", rows=200, cols=len(CABECERA_PRES))
        print("✅ Pestaña 'Presupuestos' creada.")

    ws_pres.update([CABECERA_PRES] + PRESUPUESTOS_INICIALES)
    ws_pres.format("A1:K1", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.04, "green": 0.12, "blue": 0.23}})
    print(f"   → {len(PRESUPUESTOS_INICIALES)} presupuestos cargados.")

    # ── Pestaña Obras ─────────────────────────────────────────────────────
    try:
        ws_obras = sh.worksheet("Obras")
        ws_obras.clear()
        print("🔄 Pestaña 'Obras' limpiada.")
    except gspread.WorksheetNotFound:
        ws_obras = sh.add_worksheet("Obras", rows=200, cols=len(CABECERA_OBRAS))
        print("✅ Pestaña 'Obras' creada.")

    ws_obras.update([CABECERA_OBRAS] + OBRAS_INICIALES)
    ws_obras.format("A1:I1", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.04, "green": 0.12, "blue": 0.23}})
    print(f"   → {len(OBRAS_INICIALES)} obras cargadas.")

    print(f"\n🎉 Setup completo. URL del Sheet: {sh.url}")
    print("   Comparte este Sheet con la cuenta de servicio si aún no lo has hecho.")

if __name__ == "__main__":
    main()
