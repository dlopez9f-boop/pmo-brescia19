#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_insertar_actas_s13_1517.py
Inserta actas S13: 15/06 (diaria), 16/06 (semanal) y 17/06 (diaria) en actas_diarias.json
"""
import json
from pathlib import Path

JSON_PATH = Path("actas_data/actas_diarias.json")
data = json.loads(JSON_PATH.read_text(encoding="utf-8"))

IDS_EXISTENTES = {r["id"] for r in data}

NUEVAS = [

# ============================================================
#  ACT-20260615-1800  |  LUNES S13  |  15/06/2026
# ============================================================
{
  "id": "ACT-20260615-1800",
  "fecha": "2026-06-15",
  "semana_obra": 13,
  "obra": "Brescia 19",
  "resumen": "S13 · 15/06 · Lunes — Arranque semana 13. Munir inicia muro perimetral con solución bicapa fónica. Josevi comienza rastreles metálicos para espejos y subestructura mampara sala colectiva. Climatización (José) arranca colocación cajas de clima en baños. Electricidad: PRIMERA AUSENCIA sin justificación — puntos marcados, plano entregado, sin actividad. PCI Leo: continuación instalación detectores sala principal.",
  "texto_original": "Lunes 15/06 — Inicio semana S13. Munir en obra: comienza la ejecución del muro perimetral del local con sistema bicapa fónico (placa YL + membrana acústica + placa fónica). Josevi arranca: rastreles y montantes metálicos para fijación de espejos sala principal, y subestructura mampara sala colectiva. José (Servitec): colocación de cajas de clima / plenums técnicos en baños. Electricidad (Elecrea/Luis): sin presentarse en obra. Todos los puntos marcados y plano entregado el 10/06. PCI (Leo): trabajo en detectores sala principal.",
  "asistencia": [
    {"gremio": "🏗️ PMO (Darío)", "estado": "PRESENTE", "horas": "Jornada", "avance": "Supervisión arranque S13. Control avance gremios."},
    {"gremio": "🧱 Albañilería (Munir)", "estado": "PRESENTE", "horas": "Jornada completa", "avance": "Inicio muro perimetral — bicapa fónica."},
    {"gremio": "🚪 Carpintería (Josevi)", "estado": "PRESENTE", "horas": "Jornada completa", "avance": "Rastreles metálicos espejos + subestructura mampara."},
    {"gremio": "❄️ Climatización (Servitec/José)", "estado": "PRESENTE", "horas": "Media jornada", "avance": "Colocación cajas de clima baños F/M."},
    {"gremio": "⚡ Electricidad (Elecrea/Luis)", "estado": "AUSENTE", "horas": "—", "avance": "PRIMERA AUSENCIA — sin justificación."},
    {"gremio": "🔥 PCI (Troser/Leo)", "estado": "PRESENTE", "horas": "Jornada completa", "avance": "Detectores sala principal — continuación."}
  ],
  "intervenciones": {
    "🧱 Albañilería (Munir)": "Inicio ejecución muro perimetral local. Solución técnica: sistema bicapa fónico — Placa de yeso laminado + Membrana acústica intermedia + Placa fónica. Ejecución correcta y sin incidencias. Este paramento, al terminarse, libera la superficie para replanteo de rastreles de espejos.",
    "🚪 Carpintería (Josevi)": "Inicio inmediato S13: rastreles y montantes metálicos sobre paramentos para fijación de espejos 2,40m sala principal. Subestructura mampara sala colectiva en proceso. Buen ritmo.",
    "❄️ Climatización (Servitec/José)": "Arranque colocación plenums técnicos (cajas de clima) en baño femenino y masculino. Coordinación con Munir para no interferir con cierre de tabiques.",
    "🔴 BLOQUEO — Electricidad (Elecrea/Luis)": "PRIMERA AUSENCIA SIN JUSTIFICACIÓN. Puntos de instalación marcados físicamente en obra. Plano de replanteo entregado formalmente el 10/06. Sin actividad registrada. Se pone en conocimiento del responsable de PMO. Impacto: retrasa cierre técnico de tabiques en baños y sala colectiva (Munir no puede cerrar sin paso previo de instalaciones).",
    "🔥 PCI (Leo/Troser)": "Continuación instalación de detectores en sala principal. Ritmo adecuado para el objetivo de primeros de julio."
  },
  "riesgos": [
    {
      "codigo": "RIESGO-06",
      "tipo": "ALERTA GREMIO",
      "descripcion": "Electricidad (Elecrea/Luis): primera ausencia injustificada lunes 15/06. Puntos marcados y plano entregado. Sin actividad. Bloquea cierre tabiques baños y sala colectiva (Munir).",
      "accion": "Contactar a Luis Elecrea hoy para exigir presencia mañana 16/06. Documentar incidencia.",
      "responsable": "Darío A. López",
      "estado": "ACTIVO",
      "prioridad": "alta"
    }
  ],
  "alertas_dashboard": [
    {"codigo": "ALERTA-D13", "tipo": "AUSENCIA GREMIO", "descripcion": "Electricidad (Elecrea/Luis): 1er día ausente sin justificación. Bloquea cierre tabiques Munir. Contactar HOY.", "prioridad": "alta", "estado": "ACTIVA"},
    {"codigo": "ALERTA-D14", "tipo": "AVANCE POSITIVO", "descripcion": "Muro perimetral (Munir) — bicapa fónica iniciada. Josevi en obra con rastreles. Buen arranque S13.", "prioridad": "normal", "estado": "ACTIVA"}
  ],
  "definiciones_tecnicas": [
    {"categoria": "Obra Civil — S13", "elemento": "Muro perimetral bicapa fónica", "detalle": "Sistema: Placa YL + Membrana acústica + Placa fónica. Ejecutado por Munir. Libera superficie para rastreles de espejos al completarse."},
    {"categoria": "Carpintería — S13", "elemento": "Rastreles metálicos espejos", "detalle": "Josevi: montantes y rastreles para espejos 2,40m sala principal + subestructura mampara sala colectiva."},
    {"categoria": "Climatización — S13", "elemento": "Cajas de clima / Plenums técnicos", "detalle": "Baño femenino y masculino. Colocación en curso. Coordinar cierres con Munir."}
  ],
  "logros_tecnicos": [
    {"descripcion": "Inicio muro perimetral con bicapa fónica — Munir", "mejora_de": "Pendiente", "mejora_a": "En ejecución", "impacto": "Al cerrarse libera zona de espejos."},
    {"descripcion": "Josevi arranca rastreles espejos + mampara — Josevi", "mejora_de": "Pendiente arranque", "mejora_a": "En ejecución S13", "impacto": "Lunes 22/06: fijación espejos."},
    {"descripcion": "Cajas de clima baños en curso — Servitec", "mejora_de": "Pendiente", "mejora_a": "En colocación", "impacto": "Cierre técnico baños habilitado para S13."}
  ],
  "solicitudes_direccion": [
    {"descripcion": "URGENTE — Contactar Luis (Elecrea) por ausencia injustificada. Exigir presencia 16/06 con equipo.", "responsable": "Darío A. López", "urgencia": "alta"},
    {"descripcion": "Confirmar avance muro perimetral Munir — ¿cuándo libera zona espejos?", "responsable": "Munir / Darío", "urgencia": "normal"}
  ],
  "agenda_proxima": {
    "items": [
      {"hora": "16/06 — 13:00h", "evento": "REUNIÓN SEMANAL S13 — Pleno de gremios en obra."},
      {"hora": "16/06 — Urgente", "evento": "Electricidad (Luis): exigir presencia. Segundo día = escalado formal."},
      {"hora": "16/06 — Obra", "evento": "Munir: continuación muro perimetral bicapa fónica."},
      {"hora": "16/06 — Obra", "evento": "Josevi: avance rastreles espejos + mampara."}
    ]
  },
  "incidencias": [
    {"gremio": "⚡ Electricidad (Elecrea/Luis)", "descripcion": "Primera ausencia injustificada lunes 15/06. Bloquea cierre tabiques Munir en baños y sala colectiva.", "prioridad": "alta"}
  ],
  "gremios_incidencia": ["⚡ Electricidad (Elecrea/Luis)"],
  "prioridad": "alta",
  "estado": "cerrado",
  "creado_por": "Darío A. López",
  "created_at": "2026-06-15T18:00:00"
},

# ============================================================
#  ACT-20260616-1300  |  REUNION SEMANAL S13  |  16/06/2026
# ============================================================
{
  "id": "ACT-20260616-1300",
  "fecha": "2026-06-16",
  "semana_obra": 13,
  "obra": "Brescia 19",
  "resumen": "S13 · 16/06 · REUNIÓN SEMANAL — Gremios presentes: Munir, Josevi, José (Clima). AUSENTE sin justificación: Electricidad (Elecrea/Luis) — 2do día consecutivo con plano entregado. BLOQUEO CRÍTICO: impide cierre tabiques Munir en baños femenino/masculino y sala colectiva. Hitos semana: muro perimetral bicapa fónica en avance; rastreles espejos Josevi completados para lunes 22/06; cajas clima baños completadas. Recepción maquinaria O'Donnell en obra. Altura libre baños verificada: BF 2,81m / BM 2,85m — cotas revisadas para cuadros y registros. Próxima acción: escalado formal a Luis si no se incorpora hoy 16/06.",
  "texto_original": "Reunión semanal S13 — martes 16/06. Munir, Josevi, José (Servitec), Darío. Electricidad (Luis) ausente por segundo día consecutivo. No hay excusa comunicada. Todos los puntos de luz marcados, plano entregado el 10/06. Bloquea a Munir en cierre de tabiques de baños y sala colectiva. Muro perimetral bicapa avanzando bien. Josevi: rastreles terminados para los espejos del lunes. Cajas de clima colocadas en baños. José ha recibido la maquinaria de clima de O'Donnell — en acopio en obra. Se miden a láser las alturas libres de baños tras instalación de conductos: BF 2,81m, BM 2,85m. Cuadros y registros deben bajarse a esta cota.",
  "asistencia": [
    {"gremio": "🏗️ PMO (Darío)", "estado": "PRESENTE", "horas": "Reunión + supervisión", "avance": "Dirección reunión semanal S13"},
    {"gremio": "🧱 Albañilería (Munir)", "estado": "PRESENTE", "horas": "Reunión + jornada", "avance": "Muro bicapa avanzando. BLOQUEADO cierre baños por electricidad."},
    {"gremio": "🚪 Carpintería (Josevi)", "estado": "PRESENTE", "horas": "Reunión + jornada", "avance": "Rastreles espejos COMPLETADOS. Mampara en ejecución."},
    {"gremio": "❄️ Climatización (Servitec/José)", "estado": "PRESENTE", "horas": "Reunión + jornada", "avance": "Cajas clima baños completadas. Maquinaria O'Donnell recibida en obra."},
    {"gremio": "⚡ Electricidad (Elecrea/Luis)", "estado": "AUSENTE", "horas": "—", "avance": "2DO DIA CONSECUTIVO AUSENTE. Sin justificación. BLOQUEO ACTIVO."},
    {"gremio": "🔥 PCI (Troser/Leo)", "estado": "AUSENTE", "horas": "—", "avance": "Sin presencia en reunión."}
  ],
  "intervenciones": {
    "🧱 Albañilería (Munir)": "Muro perimetral con solución bicapa fónica en avance. Al completarse libera zona de espejos. BLOQUEADO para cierre de tabiques en baños femenino/masculino y sala colectiva: necesita que Electricidad pase sus instalaciones interiores antes del cierre técnico. Sin Electricidad = tabiques abiertos = retraso en cascada.",
    "🚪 Carpintería (Josevi)": "HITO: Rastreles y montantes metálicos para espejos 2,40m COMPLETADOS. Listos para fijación de espejos el lunes 22/06. Subestructura mampara sala colectiva en ejecución.",
    "❄️ Climatización (Servitec/José)": "Cajas de clima (plenums técnicos) en baño femenino y masculino COMPLETADAS. HITO: Recepción y acopio en obra de la nueva maquinaria de climatización procedente de la sede de O'Donnell. Maquinaria asegurada y lista para su instalación.",
    "🔴 BLOQUEO CRÍTICO — Electricidad (Elecrea/Luis)": "SEGUNDO DÍA CONSECUTIVO AUSENTE. Plano de replanteo entregado formalmente el 10/06. Todos los puntos de instalación marcados a pie de obra. SIN EXCUSA COMUNICADA. Impacto directo: Munir no puede cerrar los tabiques en baños ni sala colectiva sin el paso previo de los tubos y cajas de electricidad. DIRECTRIZ PMO: Se establece escalado formal. Si Luis no se presenta hoy 16/06, se documenta incumplimiento contractual.",
    "📐 Mediciones y Cotas — Verificación Láser": "Se verifican a láser las alturas libres en zonas húmedas tras instalación de conductos de clima: Baño Femenino: 2,81m. Baño Masculino: 2,85m. ACCIÓN TÉCNICA: Cuadros de electricidad y cajas de registro deben reubicarse a estas nuevas cotas reales. Cubicar impacto económico con presupuesto base.",
    "💰 Oficina Técnica — Pendientes": "1) Techo baños: valorar y comparar partidas con presupuesto base firmado. 2) Vigas y recrecidos Munir: omisión detectada en medición original — cubicar m² reales en obra para comparar precio unitario con contrata."
  },
  "riesgos": [
    {
      "codigo": "RIESGO-07",
      "tipo": "INCUMPLIMIENTO GREMIO — CRÍTICO",
      "descripcion": "Electricidad (Elecrea/Luis): 2 días consecutivos de ausencia injustificada. Plano entregado, puntos marcados. Bloquea cierre tabiques Munir en baños y sala colectiva. Riesgo camino crítico apertura agosto.",
      "accion": "Escalado formal: llamada directa a Luis exigiendo incorporación inmediata. Si no se resuelve hoy = comunicación escrita de incumplimiento. Evaluar penalizaciones contractuales.",
      "responsable": "Darío A. López",
      "estado": "ACTIVO",
      "prioridad": "critica"
    },
    {
      "codigo": "RIESGO-08",
      "tipo": "DESVIACION ECONOMICA",
      "descripcion": "Vigas y recrecidos Munir: medición original omitida en presupuesto base. Riesgo de contradictorio. Cubicar urgente para evitar reclamación no controlada.",
      "accion": "Cubicación en obra esta semana. Comparar precio unitario con contrata. Formalizar ajuste antes de Certificación N2.",
      "responsable": "Darío A. López / Munir",
      "estado": "ACTIVO",
      "prioridad": "alta"
    }
  ],
  "alertas_dashboard": [
    {"codigo": "ALERTA-D15", "tipo": "BLOQUEO CRITICO GREMIO", "descripcion": "Electricidad (Luis): 2 dias consecutivos ausente — escalado formal. Munir bloqueado en cierre baños + sala colectiva. ACCION INMEDIATA.", "prioridad": "critica", "estado": "ACTIVA"},
    {"codigo": "ALERTA-D16", "tipo": "COTA REVISADA", "descripcion": "Alturas libres baños: BF 2,81m / BM 2,85m. Cuadros electricos y registros deben bajarse a nuevas cotas. Coordinar con Luis cuando se incorpore.", "prioridad": "alta", "estado": "ACTIVA"},
    {"codigo": "ALERTA-D17", "tipo": "HITO CUMPLIDO", "descripcion": "Maquinaria clima O'Donnell recibida en obra. Rastreles espejos completados. Cajas clima baños completadas.", "prioridad": "normal", "estado": "ACTIVA"},
    {"codigo": "ALERTA-D18", "tipo": "OFICINA TECNICA", "descripcion": "Cubicacion vigas/recrecidos Munir pendiente — omision en presupuesto base. Valorar techo baños vs. presupuesto.", "prioridad": "alta", "estado": "ACTIVA"}
  ],
  "definiciones_tecnicas": [
    {"categoria": "Cota revisada — BF", "elemento": "Altura libre Bano Femenino", "detalle": "2,81 metros tras instalacion conductos clima. Cuadros electricos y cajas de registro deben bajarse a esta cota."},
    {"categoria": "Cota revisada — BM", "elemento": "Altura libre Bano Masculino", "detalle": "2,85 metros tras instalacion conductos clima. Misma accion que BF."},
    {"categoria": "Climatizacion — Hito", "elemento": "Maquinaria O'Donnell", "detalle": "Recibida y acopiada en obra el 16/06. Procede de sede O'Donnell. Lista para instalacion."},
    {"categoria": "Carpinteria — Hito", "elemento": "Rastreles espejos", "detalle": "Completados. Fijacion de espejos 2,40m programada para lunes 22/06."},
    {"categoria": "Oficina Tecnica — Pendiente", "elemento": "Vigas y recrecidos Munir", "detalle": "Omision medicion en presupuesto base. Cubicar m² reales. Comparar precio unitario contrata. Formalizar antes de Cert. N2."}
  ],
  "logros_tecnicos": [
    {"descripcion": "Rastreles metálicos espejos COMPLETADOS — Josevi", "mejora_de": "Pendiente", "mejora_a": "100% completado", "impacto": "Espejos se fijan el lunes 22/06. Hito de sala principal cumplido."},
    {"descripcion": "Cajas clima baños completadas — Servitec", "mejora_de": "En ejecución", "mejora_a": "Completadas BF+BM", "impacto": "Habilita cierre técnico baños cuando Electricidad pase instalaciones."},
    {"descripcion": "Maquinaria clima O'Donnell recibida en obra", "mejora_de": "Pendiente recepción", "mejora_a": "Acopiada en obra", "impacto": "Eliminado riesgo de retraso por suministro de equipos."}
  ],
  "solicitudes_direccion": [
    {"descripcion": "ESCALADO CRÍTICO — Llamada formal a Luis (Elecrea). Incorporación inmediata exigida. Documentar si no se resuelve hoy.", "responsable": "Darío A. López", "urgencia": "crítica"},
    {"descripcion": "Cubicar vigas y recrecidos Munir en obra esta semana. Comparar precio unitario presupuesto. Cerrar antes de Cert. N2.", "responsable": "Darío A. López / Munir", "urgencia": "alta"},
    {"descripcion": "Valorar económicamente partida techo baños vs. presupuesto base firmado.", "responsable": "Darío A. López / Valentina", "urgencia": "alta"},
    {"descripcion": "Confirmar fecha fijación espejos con Josevi — lunes 22/06 como objetivo.", "responsable": "Josevi / Darío", "urgencia": "normal"}
  ],
  "agenda_proxima": {
    "items": [
      {"hora": "16/06 — HOY URGENTE", "evento": "Escalado formal Luis (Elecrea): incorporación inmediata exigida."},
      {"hora": "17/06 — Miércoles", "evento": "Verificar si Electricidad se incorpora. 3er día = comunicación escrita formal."},
      {"hora": "17/06 — Obra", "evento": "Munir: continuación muro perimetral + inicio cierre baños si Electricidad se incorpora."},
      {"hora": "Semana S13", "evento": "Cubicar vigas/recrecidos Munir. Valorar techo baños."},
      {"hora": "22/06 — Lunes", "evento": "Fijación definitiva espejos 2,40m sala principal (Josevi)."},
      {"hora": "Semana S13-S14", "evento": "Desplazamiento Pozuelo: cubicacion e inventario material técnico reutilizable."}
    ]
  },
  "incidencias": [
    {"gremio": "⚡ Electricidad (Elecrea/Luis)", "descripcion": "2 dias consecutivos ausente sin justificacion. Bloquea cierre tabiques Munir en baños y sala colectiva. Escalado formal.", "prioridad": "urgente"},
    {"gremio": "💰 Munir — Oficina Técnica", "descripcion": "Medicion vigas/recrecidos omitida en presupuesto base. Riesgo contradictorio. Cubicar urgente.", "prioridad": "alta"}
  ],
  "gremios_incidencia": ["⚡ Electricidad (Elecrea/Luis)", "💰 Oficina Técnica"],
  "prioridad": "critica",
  "estado": "cerrado",
  "creado_por": "Darío A. López",
  "created_at": "2026-06-16T13:00:00"
},

# ============================================================
#  ACT-20260617-1800  |  MIÉRCOLES S13  |  17/06/2026
# ============================================================
{
  "id": "ACT-20260617-1800",
  "fecha": "2026-06-17",
  "semana_obra": 13,
  "obra": "Brescia 19",
  "resumen": "S13 · 17/06 · Miércoles — Munir: cerramiento muro perimetral con bicapa fónica completado — libera zona espejos. Josevi: rastreles + subestructura mampara terminados — espejos el lunes 22/06. Climatización (José): cajas clima BF+BM completadas, maquinaria O'Donnell acopiada. BLOQUEO CRÍTICO — Electricidad: 2do día consecutivo ausente sin justificación con puntos marcados y plano entregado. Paraliza cierre tabiques Munir en baños y sala colectiva. DIRECTRIZ: acceso al cuadro general confinado — si Electricidad necesita andamio, lo monta bajo su responsabilidad. Alturas láser verificadas: BF 2,81m / BM 2,85m. Pendiente: valoración techo baños y cubicación vigas/recrecidos Munir vs. presupuesto. Lunes 22/06: fijación espejos. Semana próxima: inventario Pozuelo.",
  "texto_original": "Miercoles 17/06/2026. Munir: se ha ejecutado con exito la solucion tecnica bicapa fonica en el muro perimetral del local: Placa de yeso laminado + Membrana acustica intermedia + Placa fonica. Libera superficie para replanteo rastreles espejos. Josevi: hito diario completado — rastreles y montantes estructurales para espejos instalados en paramentos, subestructura mampara sala colectiva terminada. Espejos se fijan el lunes proximo. Climatizacion (Jose): cajas de clima colocadas en bano femenino y masculino, y confirmada recepcion en obra de la nueva maquinaria de climatizacion procedente de la sede de O'Donnell. Electricidad (Luis/Elecrea): por segundo dia consecutivo el equipo de electricidad no se presenta en obra. Puntos fisicos marcados, plano de replanteo entregado formalmente. Sin avance. Bloquea a Munir en paso de instalaciones para cierre de tabiques en banos femeninos y sala colectiva. El sector del cuadro general ha quedado confinado y cerrado: si la contrata necesita acceder debera montar y desmontar andamio bajo sus propios medios. Alturas libres verificadas a laser tras conductos clima: BF 2,81m, BM 2,85m. Accion: bajar cuadros electricos y cajas de registro a nueva cota. Pendientes oficina tecnica: 1) valorar economicamente partida techo baños vs. presupuesto base. 2) cubicar vigas y recrecidos Munir — omision detectada en medicion original, cubicar m² para comparar precio unitario y evitar contradictorio. Proximos hitos: lunes 22/06 montaje y fijacion definitiva espejos. Semana proxima: desplazamiento Pozuelo — medicion, cubicacion e inventario material tecnico recuperable.",
  "asistencia": [
    {"gremio": "🏗️ PMO (Darío)", "estado": "PRESENTE", "horas": "Jornada completa", "avance": "Supervisión, mediciones láser, gestión bloqueo Electricidad."},
    {"gremio": "🧱 Albañilería (Munir)", "estado": "PRESENTE", "horas": "Jornada completa", "avance": "Muro perimetral bicapa fónica COMPLETADO. Bloqueado para cierre baños/sala colectiva."},
    {"gremio": "🚪 Carpintería (Josevi)", "estado": "PRESENTE", "horas": "Jornada completa", "avance": "Rastreles espejos COMPLETOS. Subestructura mampara sala colectiva COMPLETA."},
    {"gremio": "❄️ Climatización (Servitec/José)", "estado": "PRESENTE", "horas": "Media jornada", "avance": "Cajas clima BF+BM completadas. Maquinaria O'Donnell recibida y acopiada."},
    {"gremio": "⚡ Electricidad (Elecrea/Luis)", "estado": "AUSENTE", "horas": "—", "avance": "2DO DIA CONSECUTIVO — SIN JUSTIFICACIÓN. BLOQUEO ACTIVO."},
    {"gremio": "🔥 PCI (Troser/Leo)", "estado": "AUSENTE", "horas": "—", "avance": "Sin actividad registrada."}
  ],
  "intervenciones": {
    "🧱 Albañilería (Munir) — Muro perimetral": "COMPLETADO: ejecución de la solución técnica bicapa fónica en el muro perimetral del local. Sistema: Placa de yeso laminado + Membrana acústica intermedia + Placa fónica. Resultado: paramento ejecutado correctamente. Superficie liberada para inicio de replanteo y colocación de rastreles metálicos para espejos de sala. BLOQUEADO para cierre de tabiques en baños femenino/masculino y sala colectiva: requiere paso previo de instalaciones eléctricas interiores (tubos + cajas) — dependencia directa de Electricidad.",
    "🚪 Carpintería (Josevi) — Hito completado": "HITO DIARIO CUMPLIDO: instalados en paramentos todos los rastreles y montantes estructurales necesarios para la fijación definitiva de los espejos 2,40m el próximo lunes 22/06. Subestructura de mampara de sala colectiva completada. Josevi disponible el lunes para montaje final.",
    "❄️ Climatización (Servitec/José)": "COMPLETADO: colocación de cajas de clima (plenums técnicos) en baño femenino y masculino. HITO: Confirmada recepción y acopio en obra de la nueva maquinaria de climatización procedente de sede O'Donnell. Material asegurado y verificado físicamente.",
    "🔴 BLOQUEO CRÍTICO — Electricidad (Elecrea/Luis)": "SEGUNDO DÍA CONSECUTIVO sin presencia en obra. Sin justificación comunicada. Estado: todas las tomas físicas marcadas a pie de obra, plano de replanteo eléctrico entregado formalmente el 10/06/2026. SIN ACTIVIDAD REGISTRADA. IMPACTO DIRECTO: impide a Munir realizar el paso de instalaciones interiores para proceder al cierre técnico de los tabiques en baños femeninos y sala colectiva. Bloqueo en cascada. URGENTE incorporación para desbloquear estas salas. DIRECTRIZ CUADRO GENERAL: el sector del cuadro general ya ha quedado confinado y cerrado físicamente. Si la contrata de electricidad necesita acceder, deberá montar y desmontar andamio bajo sus propios medios y responsabilidad, en igualdad de condiciones que el resto de operarios.",
    "📐 Mediciones Láser — Cotas Verificadas": "Verificación a láser de alturas libres reales en zonas húmedas tras instalación de conductos de climatización: Baño Femenino → 2,81 metros. Baño Masculino → 2,85 metros. ACCIÓN TÉCNICA DERIVADA: se requiere bajar físicamente los cuadros de electricidad y las cajas de registro a estas nuevas cotas técnicas en ambos baños. Coordinar con Electricidad cuando se incorpore.",
    "💰 Oficina Técnica — Pendientes de valoración": "1) TECHO BAÑOS: realizar valoración económica de la partida y comparar con presupuesto base firmado para auditar posibles diferencias económicas. 2) CONCILIACIÓN MUNIR — VIGAS/RECRECIDOS: se detecta omisión o falta de medición original en presupuesto respecto a las partidas de vigas y recrecidos de pared. Proceder a cubicación de m² reales en obra. Comparar precios unitarios con contrata. Objetivo: evitar reclamaciones por contradictorios no controlados. Formalizar antes de Certificación N.º 2."
  },
  "riesgos": [
    {
      "codigo": "RIESGO-07",
      "tipo": "INCUMPLIMIENTO GREMIO — CRÍTICO",
      "descripcion": "Electricidad (Elecrea/Luis): 2 dias consecutivos ausente sin justificacion. Plano entregado 10/06. Puntos marcados. Bloquea cierre tabiques Munir en banos y sala colectiva. Riesgo directo camino critico apertura agosto.",
      "accion": "Comunicación escrita formal de incumplimiento. Activar cláusula de penalización si no se resuelve hoy 17/06. Darío contacta Luis directamente.",
      "responsable": "Darío A. López",
      "estado": "ACTIVO — ESCALADO",
      "prioridad": "critica"
    },
    {
      "codigo": "RIESGO-08",
      "tipo": "DESVIACION ECONOMICA",
      "descripcion": "Vigas y recrecidos Munir: medicion original omitida en presupuesto base. Riesgo contradictorio si no se cubica y formaliza antes de Cert. N2.",
      "accion": "Cubicacion en obra esta semana S13. Comparar precio unitario contrata. Cerrar antes de Cert. N2.",
      "responsable": "Darío A. López / Munir",
      "estado": "ACTIVO",
      "prioridad": "alta"
    }
  ],
  "alertas_dashboard": [
    {"codigo": "ALERTA-D19", "tipo": "BLOQUEO CRITICO — 2 DIAS", "descripcion": "Electricidad (Luis): 2do dia consecutivo ausente. Plano entregado, puntos marcados. MUNIR BLOQUEADO banos + sala colectiva. Comunicacion formal hoy.", "prioridad": "critica", "estado": "ACTIVA"},
    {"codigo": "ALERTA-D20", "tipo": "COTA REVISADA — ACCION", "descripcion": "BF 2,81m / BM 2,85m verificadas laser. Cuadros electricos y registros deben bajarse. Coordinar con Luis al incorporarse.", "prioridad": "alta", "estado": "ACTIVA"},
    {"codigo": "ALERTA-D21", "tipo": "OFICINA TECNICA", "descripcion": "Vigas/recrecidos Munir: cubicar m² reales esta semana. Techo baños: valorar vs. presupuesto base. Antes de Cert. N2.", "prioridad": "alta", "estado": "ACTIVA"},
    {"codigo": "ALERTA-D22", "tipo": "HITO LUNES", "descripcion": "22/06 lunes: fijacion definitiva espejos 2,40m sala principal (Josevi). Rastreles completados. Confirmar asistencia.", "prioridad": "normal", "estado": "ACTIVA"},
    {"codigo": "ALERTA-D23", "tipo": "AVANCE S13", "descripcion": "Muro bicapa fonica completado (Munir). Cajas clima baños completas. Maquinaria O'Donnell en obra. Josevi: rastreles y mampara OK.", "prioridad": "normal", "estado": "ACTIVA"}
  ],
  "definiciones_tecnicas": [
    {"categoria": "Obra Civil — Hito", "elemento": "Muro perimetral bicapa fónica", "detalle": "COMPLETADO. Sistema: Placa YL + Membrana acústica + Placa fónica. Libera zona para rastreles espejos."},
    {"categoria": "Carpintería — Hito", "elemento": "Rastreles espejos + Subestructura mampara", "detalle": "COMPLETADOS. Montaje definitivo espejos 2,40m: lunes 22/06."},
    {"categoria": "Climatización — Hito", "elemento": "Cajas clima BF+BM + Maquinaria O'Donnell", "detalle": "CAJAS COMPLETADAS. MAQUINARIA RECIBIDA Y ACOPIADA EN OBRA."},
    {"categoria": "Directriz técnica — Cuadro General", "elemento": "Acceso sector cuadro general", "detalle": "CONFINADO Y CERRADO. Electricidad: si necesita acceso, monta y desmonta andamio bajo sus propios medios. Igual que resto de operarios."},
    {"categoria": "Cotas verificadas — Láser", "elemento": "Alturas libres zonas húmedas", "detalle": "Bano Femenino: 2,81m. Bano Masculino: 2,85m. Cuadros electricos y registros deben bajarse a estas cotas."},
    {"categoria": "Pendiente OT — Contradictorios", "elemento": "Vigas y recrecidos Munir", "detalle": "Omision en medicion presupuesto original. Cubicar m² reales en obra. Comparar precio unitario contrata. Formalizar antes Cert. N2."}
  ],
  "logros_tecnicos": [
    {"descripcion": "Muro perimetral bicapa fónica COMPLETADO — Munir", "mejora_de": "En ejecución", "mejora_a": "100% COMPLETADO", "impacto": "Libera zona espejos. Calidad acústica garantizada."},
    {"descripcion": "Rastreles espejos + subestructura mampara COMPLETADOS — Josevi", "mejora_de": "En ejecución", "mejora_a": "100% COMPLETADO", "impacto": "Lunes 22/06: fijación espejos sala principal."},
    {"descripcion": "Cajas clima baños completadas — Servitec", "mejora_de": "En ejecución", "mejora_a": "BF+BM 100% COMPLETADAS", "impacto": "Habilita cierre técnico baños."},
    {"descripcion": "Maquinaria climatización O'Donnell recibida en obra", "mejora_de": "Pendiente recepción", "mejora_a": "ACOPIADA EN OBRA", "impacto": "Riesgo suministro eliminado. Instalación puede avanzar."}
  ],
  "solicitudes_direccion": [
    {"descripcion": "COMUNICACION FORMAL — Luis (Elecrea): 2do dia consecutivo. Exigir incorporacion inmediata. Activar clausula penalizacion si no resuelve HOY.", "responsable": "Darío A. López", "urgencia": "crítica"},
    {"descripcion": "Cuando Luis se incorpore: bajar cuadros electricos y cajas de registro a cotas BF 2,81m / BM 2,85m.", "responsable": "Luis (Elecrea) / Darío", "urgencia": "alta"},
    {"descripcion": "Cubicacion vigas/recrecidos Munir — esta semana S13. Comparar precio unitario. Cerrar antes Cert. N2.", "responsable": "Darío A. López / Munir", "urgencia": "alta"},
    {"descripcion": "Valoracion economica partida techo banos vs. presupuesto base firmado. Para Valentina.", "responsable": "Darío A. López / Valentina", "urgencia": "alta"},
    {"descripcion": "Confirmar asistencia Josevi lunes 22/06 para fijacion definitiva espejos 2,40m.", "responsable": "Josevi / Darío", "urgencia": "normal"},
    {"descripcion": "Planificar desplazamiento Pozuelo — medicion e inventario material tecnico recuperable.", "responsable": "Darío A. López", "urgencia": "normal"}
  ],
  "agenda_proxima": {
    "items": [
      {"hora": "17/06 — HOY", "evento": "Comunicación formal a Luis (Elecrea): incumplimiento 2 dias consecutivos. Exigir incorporacion hoy o mañana."},
      {"hora": "18/06 — Jueves", "evento": "Verificar presencia Electricidad. Si no aparece: 3er dia = escalado legal contractual."},
      {"hora": "Semana S13", "evento": "Cubicacion vigas/recrecidos Munir en obra. Valoracion techo banos."},
      {"hora": "22/06 — Lunes", "evento": "HITO: Montaje y fijacion definitiva espejos 2,40m sala principal (Josevi)."},
      {"hora": "22/06 — Lunes", "evento": "Ensamblaje estructura mampara sala colectiva (Josevi)."},
      {"hora": "Semana S14", "evento": "Desplazamiento Pozuelo: medicion, cubicacion e inventario material recuperable para Brescia 19."}
    ]
  },
  "incidencias": [
    {"gremio": "⚡ Electricidad (Elecrea/Luis)", "descripcion": "2do dia consecutivo ausente sin justificacion. Plano entregado 10/06. Puntos marcados. Bloquea Munir en cierre tabiques banos + sala colectiva. Comunicacion formal activada.", "prioridad": "urgente"},
    {"gremio": "💰 Oficina Tecnica", "descripcion": "Vigas y recrecidos Munir: medicion omitida en presupuesto base. Riesgo contradictorio. Cubicar urgente.", "prioridad": "alta"}
  ],
  "gremios_incidencia": ["⚡ Electricidad (Elecrea/Luis)", "💰 Oficina Tecnica"],
  "prioridad": "critica",
  "estado": "borrador",
  "creado_por": "Darío A. López",
  "created_at": "2026-06-17T18:00:00"
}

]  # fin NUEVAS

# ── Insertar solo las que no existen ────────────────────────────────────────
insertadas = 0
for acta in NUEVAS:
    if acta["id"] not in IDS_EXISTENTES:
        data.append(acta)
        insertadas += 1
        print(f"  INSERTADA: {acta['id']} — {acta['fecha']}")
    else:
        print(f"  YA EXISTE: {acta['id']} — omitida")

# Ordenar por fecha descendente
data.sort(key=lambda x: x.get("created_at", x.get("fecha", "")), reverse=True)

JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nOK — {insertadas} actas insertadas. Total en JSON: {len(data)}")
