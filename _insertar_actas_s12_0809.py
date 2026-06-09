#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inserta las actas diarias S12 del 08/06 y 09/06 en actas_diarias.json.
python _insertar_actas_s12_0809.py
"""
import json
from pathlib import Path

JSON_PATH = Path("actas_data/actas_diarias.json")

ACTA_0809 = {
  "id": "ACT-20260609-1300",
  "fecha": "2026-06-09",
  "semana_obra": 12,
  "obra": "Brescia 19",
  "resumen": (
    "S12 · 09/06 · REUNIÓN SEMANAL — Pleno de gremios. "
    "Saneamiento baño femenino en curso, falta baño masculino. "
    "Electricidad: todos los puntos definidos (fachada, entrada, escaleras, recepción, "
    "staff, baños, sala completa, sala colectiva) — plano actualizado pendiente 10/06. "
    "PCI Leo: vías cerradas, límite primeros julio para certificación — requiere aprobado Ángel (<1 mes). "
    "Munir: revisión presupuesto en mano con mediciones — partidas cerrables, "
    "necesita firma Darío. Climatización José: conductos vistos, termo agua → altillo, "
    "cassette 2×1 Boadilla pendiente fecha. "
    "🔴 BLOQUEO: Munir necesita mediciones sanitarios reutilizados de Mario "
    "(fenólicos duchas, lavabos baños, encimeras) para poder replantear."
  ),
  "texto_original": (
    "Reunión semanal S12: José (Clima), Sergio/Elecrea (Electricidad encargado), "
    "Munir (Albañilería), Leo (PCI), Darío (PMO). "
    "Saneamiento: baño femenino en curso, falta baño masculino. "
    "Se dejan definidos tramos de espejos, vías, alturas y últimos cambios. "
    "Electricidad: vistos todos los puntos (fachada exterior, entrada, escaleras, recepción, "
    "staff, baños, sala completa, sala colectiva). Plano actualizado pendiente — entrega 10/06. "
    "Leo/PCI: vías bien definidas. Límite primeros julio para iniciar certificación. "
    "Necesitan aprobado de Ángel sin que tarde más de un mes. "
    "Munir: necesita revisión presupuesto con mediciones — partidas que ya va cerrando para facturar. "
    "Necesita firma Darío. Trabajar con presupuesto en mano. "
    "José/Climatización: conductos vistos, huecos máquinas extracción y rejillas, "
    "termo agua → altillo, coordinado con electricidad lo que necesita desde su cuadro. "
    "Pendiente aprobar fecha para sacar cassette 2×1 de Boadilla del Monte. "
    "Munir: URGENTE mediciones de elementos reutilizados (fenólicos duchas, "
    "lavabos baños, encimeras) — hablar con Mario para que se acerque. "
    "Sin medidas no puede replantear bien. "
    "Luis Electricidad: pedidas 2 tiras LED para que los chicos trabajen en zonas cerradas."
  ),
  "asistencia": [
    {"gremio": "🏗️ PMO (Darío)", "estado": "PRESENTE", "horas": "Reunión + obra", "avance": "Dirección de reunión semanal S12"},
    {"gremio": "🧱 Albañilería (Munir)", "estado": "PRESENTE", "horas": "Jornada completa", "avance": "Saneamiento baño femenino en curso. Revisión presupuesto."},
    {"gremio": "⚡ Electricidad (Elecrea/Sergio)", "estado": "PRESENTE", "horas": "Reunión + obra", "avance": "Todos los puntos vistos. Plano actualizado: entrega 10/06."},
    {"gremio": "❄️ Climatización (Servitec/José)", "estado": "PRESENTE", "horas": "Reunión + obra", "avance": "Conductos vistos. Termo altillo. Pendiente fecha cassette Boadilla."},
    {"gremio": "🔥 PCI (Troser/Leo)", "estado": "PRESENTE", "horas": "Reunión", "avance": "Vías definidas. Certificación: objetivo 1ª semana julio."}
  ],
  "intervenciones": {
    "🧱 Albañilería (Munir)": (
      "Saneamiento baño femenino avanzando, falta baño masculino. "
      "Revisión presupuesto con Darío: partidas que cierra progresivamente habilitadas para facturar. "
      "Requiere firma Darío para formalizar. URGENTE: necesita mediciones de "
      "sanitarios reutilizados (Mario) — fenólicos en duchas, lavabos baños, encimeras — "
      "sin estas medidas no puede replantear correctamente."
    ),
    "⚡ Electricidad (Elecrea/Sergio)": (
      "Todos los puntos de obra vistos y definidos: fachada exterior, entrada, "
      "escaleras, recepción, staff, aseos, sala principal, sala colectiva. "
      "Pendiente: plano actualizado con los pequeños cambios surgidos. "
      "Entrega prevista mañana 10/06. "
      "Se han pedido 2 tiras LED para iluminar zonas ya cerradas durante los trabajos."
    ),
    "❄️ Climatización (Servitec/José)": (
      "Conductos de distribución vistos en obra. Definidos huecos para máquinas "
      "de extracción y rejillas. Termo de agua caliente → ubicación en altillo. "
      "Climatización coordinada con cuadro eléctrico (Electricidad confirma puntos). "
      "PENDIENTE: acordar fecha para retirar y reutilizar el cassette 2×1 de la "
      "instalación de Boadilla del Monte."
    ),
    "🔥 PCI (Troser/Leo)": (
      "Todas las vías de PCI bien definidas en reunión. "
      "Objetivo de certificación: primeros de julio. "
      "CONDICIÓN CRÍTICA: aprobado de Ángel (arquitecto) necesario. "
      "No debe tardar más de 1 mes desde la solicitud. "
      "Coordinar con Darío para envío a Ángel esta semana."
    ),
    "🔴 BLOQUEO — Mediciones sanitarios (Mario)": (
      "Munir necesita con urgencia las medidas exactas de los elementos reutilizados "
      "de la instalación de Boadilla del Monte: fenólicos para duchas, lavabos para "
      "baños y encimeras. Sin estas medidas no puede hacer el replanteo correcto. "
      "ACCIÓN: Darío contacta a Mario para que se acerque a obra o envíe las medidas."
    ),
    "💰 Control Económico — Munir (Presupuesto)": (
      "Trabajo con presupuesto en mano y mediciones. "
      "Partidas que Munir va cerrando progresivamente: habilitadas para facturar "
      "una vez Darío las revisa y firma. "
      "Objetivo: no incrementar más el presupuesto. Cerrar partidas por orden de ejecución."
    )
  },
  "riesgos": [
    {
      "codigo": "RIESGO-04",
      "tipo": "BLOQUEO TÉCNICO",
      "descripcion": (
        "Munir sin mediciones de sanitarios reutilizados (Mario) — "
        "fenólicos duchas, lavabos baños, encimeras. "
        "Bloquea replanteo y ejecución de zonas húmedas."
      ),
      "accion": "Darío contacta Mario esta semana. Mario acude a obra o envía medidas.",
      "responsable": "Darío A. López / Mario",
      "estado": "ACTIVO",
      "prioridad": "alta"
    },
    {
      "codigo": "RIESGO-05",
      "tipo": "PLAZO CRÍTICO",
      "descripcion": (
        "PCI: certificación objetivo primeros julio. "
        "Requiere aprobado Ángel. Si Ángel tarda >1 mes = retraso apertura."
      ),
      "accion": "Enviar solicitud a Ángel esta semana. Confirmar plazo de respuesta.",
      "responsable": "Darío A. López / Ángel Rodríguez",
      "estado": "ACTIVO",
      "prioridad": "critica"
    }
  ],
  "alertas_dashboard": [
    {
      "codigo": "ALERTA-D08",
      "tipo": "BLOQUEO URGENTE",
      "descripcion": "Mediciones sanitarios reutilizados (Mario): Munir bloqueado para replantear fenólicos, lavabos y encimeras. Contactar Mario HOY.",
      "prioridad": "critica",
      "estado": "ACTIVA"
    },
    {
      "codigo": "ALERTA-D09",
      "tipo": "PLANO PENDIENTE",
      "descripcion": "Plano actualizado Electricidad: entrega comprometida 10/06. Verificar recepción.",
      "prioridad": "alta",
      "estado": "ACTIVA"
    },
    {
      "codigo": "ALERTA-D10",
      "tipo": "PENDIENTE FIRMA",
      "descripcion": "Presupuesto Munir: partidas cerrables pendientes de revisión y firma Darío. Trabajar con presupuesto en mano.",
      "prioridad": "alta",
      "estado": "ACTIVA"
    },
    {
      "codigo": "ALERTA-D11",
      "tipo": "COORDINACIÓN PCI",
      "descripcion": "PCI certificación: enviar solicitud a Ángel esta semana. Objetivo primeros julio. Ángel no debe tardar >1 mes.",
      "prioridad": "critica",
      "estado": "ACTIVA"
    },
    {
      "codigo": "ALERTA-D12",
      "tipo": "PENDIENTE FECHA",
      "descripcion": "Cassette 2×1 Boadilla (Climatización): acordar fecha de retirada con José. No bloquea S12 pero condiciona S13.",
      "prioridad": "normal",
      "estado": "ACTIVA"
    }
  ],
  "definiciones_tecnicas": [
    {
      "categoria": "Fontanería / Baños",
      "elemento": "Saneamiento",
      "detalle": "Baño femenino en curso (90%). Baño masculino: pendiente inicio. Ambos condicionados a resolución fuga vecino (verificada 09/06)."
    },
    {
      "categoria": "Climatización — Decisión técnica",
      "elemento": "Termo agua caliente",
      "detalle": "Ubicación definitiva: ALTILLO. Definido en reunión 09/06 con José y Electricidad."
    },
    {
      "categoria": "Climatización — Pendiente",
      "elemento": "Cassette 2×1 Boadilla del Monte",
      "detalle": "Reutilización prevista. Pendiente acordar fecha entre Darío y José para retirada."
    },
    {
      "categoria": "PCI — Hito",
      "elemento": "Certificación PCI",
      "detalle": "Objetivo: iniciar primeros de julio. Condición: aprobado Ángel en <1 mes. Solicitar esta semana."
    },
    {
      "categoria": "Electricidad — Pendiente",
      "elemento": "Plano actualizado",
      "detalle": "Pequeños cambios surgidos en reunión 09/06. Sergio/Luis entregan plano actualizado el 10/06."
    },
    {
      "categoria": "Materiales — BLOQUEO",
      "elemento": "Mediciones sanitarios reutilizados (Mario)",
      "detalle": "Fenólicos duchas, lavabos baños, encimeras. Sin medidas Munir no puede replantear. Contactar Mario urgente."
    }
  ],
  "logros_tecnicos": [
    {
      "descripcion": "Reunión semanal S12 completada con pleno de gremios",
      "mejora_de": "Coordinación bilateral",
      "mejora_a": "Reunión plena: Civil + Clima + Electricidad + PCI",
      "impacto": "Todas las interferencias técnicas entre gremios definidas y coordinadas."
    },
    {
      "descripcion": "Electricidad: 100% puntos de obra vistos y definidos",
      "mejora_de": "Parcialmente definido S11",
      "mejora_a": "Completo: fachada + escaleras + recepción + staff + baños + sala + sala colectiva",
      "impacto": "Desbloquea cierre de tabiques conforme Electricidad termina su fase."
    },
    {
      "descripcion": "Climatización: conductos y huecos técnicos 100% definidos",
      "mejora_de": "En ejecución 80%",
      "mejora_a": "Conductos, huecos extracción y rejillas definidos. Termo ubicado.",
      "impacto": "Elimina incertidumbre técnica para cierre de techos S13."
    },
    {
      "descripcion": "PCI: vías de instalación completamente definidas",
      "mejora_de": "En ejecución 25%",
      "mejora_a": "Vías cerradas. Objetivo certificación: 1ª semana julio",
      "impacto": "Camino crítico PCI alineado con hito apertura agosto."
    }
  ],
  "solicitudes_direccion": [
    {
      "descripcion": "URGENTE — Contactar Mario para mediciones sanitarios reutilizados (fenólicos, lavabos, encimeras). Munir bloqueado.",
      "responsable": "Darío A. López",
      "urgencia": "crítica"
    },
    {
      "descripcion": "Enviar solicitud de aprobado PCI a Ángel esta semana. Plazo máximo respuesta: 1 mes.",
      "responsable": "Darío A. López / Ángel Rodríguez",
      "urgencia": "crítica"
    },
    {
      "descripcion": "Revisión presupuesto Munir con mediciones. Firma Darío sobre partidas cerrables. Trabajar esta semana.",
      "responsable": "Darío A. López / Munir",
      "urgencia": "alta"
    },
    {
      "descripcion": "Verificar recepción plano actualizado Electricidad el 10/06.",
      "responsable": "Darío A. López / Sergio (Elecrea)",
      "urgencia": "alta"
    },
    {
      "descripcion": "Acordar fecha con José para retirar cassette 2×1 de Boadilla del Monte.",
      "responsable": "Darío A. López / José (Servitec)",
      "urgencia": "normal"
    }
  ],
  "agenda_proxima": {
    "items": [
      {"hora": "10/06 — Urgente", "evento": "Contactar Mario: mediciones fenólicos/lavabos/encimeras para Munir."},
      {"hora": "10/06 — Urgente", "evento": "Enviar solicitud aprobado PCI a Ángel (Arquitecto COAM_12399)."},
      {"hora": "10/06 — Mañana", "evento": "Verificar entrega plano actualizado Electricidad (Sergio/Luis)."},
      {"hora": "10/06 — Semana", "evento": "Revisión presupuesto Munir + firma partidas cerrables. En obra con mediciones."},
      {"hora": "S12 — Semana", "evento": "Josevi: estructuras metálicas puertas + cerramiento sala colectiva."},
      {"hora": "S12 — Semana", "evento": "PCI Leo: continuación detectores (objetivo cierre 12/06)."},
      {"hora": "S12 — Por definir", "evento": "Fecha retirada cassette 2×1 Boadilla (José + Darío)."}
    ]
  },
  "incidencias": [
    {
      "gremio": "🔴 Munir / Mario",
      "descripcion": "Bloqueo técnico: mediciones sanitarios reutilizados pendientes. Munir no puede replantear fenólicos, lavabos ni encimeras.",
      "prioridad": "urgente"
    },
    {
      "gremio": "🔥 PCI (Leo) / Ángel",
      "descripcion": "Certificación PCI condicionada a aprobado Ángel. Solicitar esta semana para no comprometer hito julio.",
      "prioridad": "urgente"
    },
    {
      "gremio": "💰 Munir / Darío",
      "descripcion": "Presupuesto Munir: partidas cerrables pendientes de revisión y firma Darío.",
      "prioridad": "alta"
    },
    {
      "gremio": "⚡ Electricidad (Sergio)",
      "descripcion": "Plano actualizado comprometido para 10/06. Verificar entrega.",
      "prioridad": "alta"
    }
  ],
  "gremios_incidencia": ["🔴 Munir / Mario", "🔥 PCI (Leo) / Ángel", "💰 Munir / Darío", "⚡ Electricidad"],
  "prioridad": "alta",
  "estado": "borrador",
  "creado_por": "Darío A. López",
  "created_at": "2026-06-09T13:00:00"
}

ACTA_0806 = {
  "id": "ACT-20260608-1800",
  "fecha": "2026-06-08",
  "semana_obra": 12,
  "obra": "Brescia 19",
  "resumen": (
    "S12 · 08/06 · Lunes — Electricidad y Munir coordinados en obra. "
    "Todos los tabiques replanteados, inicio de cierre por una cara. "
    "Fuga agua vecino: contactado, fontanero acude mañana 09/06. "
    "BLOQUEO ACTIVO: cierre baño femenino condicionado a reparación fuga. "
    "Todos los puntos de luz y electricidad vistos y marcados."
  ),
  "texto_original": (
    "Electricidad trabajando con Munir. Todos los tabiques replanteados. "
    "Se empieza a cubrir y en la gran mayoría ya está cerrado por una cara. "
    "Vecino contactado — se ha hablado con él. Confirmado: mañana 09/06 pasará "
    "el fontanero a arreglar la pérdida de agua. Prioridad porque nos retrasa "
    "para cerrar el baño femenino. Se dejan vistos todos los puntos necesarios "
    "de luz y electricidad."
  ),
  "asistencia": [
    {
      "gremio": "🧱 Albañilería (Munir)",
      "estado": "PRESENTE",
      "horas": "Jornada completa",
      "avance": "Tabiques replanteados 100%. Inicio cierre por una cara."
    },
    {
      "gremio": "⚡ Electricidad (Elecrea/Sergio)",
      "estado": "PRESENTE",
      "horas": "Jornada completa",
      "avance": "Coordinado con Munir. Todos los puntos de luz vistos y marcados."
    },
    {
      "gremio": "❄️ Climatización (Servitec/José)",
      "estado": "AUSENTE",
      "horas": "—",
      "avance": "Arranque previsto 09/06"
    },
    {
      "gremio": "🔥 PCI (Troser/Leo)",
      "estado": "AUSENTE",
      "horas": "—",
      "avance": "Sin actividad lunes"
    },
    {
      "gremio": "🚪 Carpintería (Josevi)",
      "estado": "AUSENTE",
      "horas": "—",
      "avance": "Arranque previsto 09/06"
    }
  ],
  "intervenciones": {
    "🧱 Albañilería + ⚡ Electricidad (coordinados)": (
      "Trabajo conjunto en obra. Todos los tabiques replanteados al 100%. "
      "Se inicia el cierre por una cara. Electricidad supervisa y marca todos "
      "los puntos necesarios de luz antes del cierre definitivo. "
      "Coordinación efectiva: sin interferencias entre gremios."
    ),
    "💧 Fuga Agua Vecino — ACTIVA / En gestión": (
      "Se ha contactado con el vecino del local colindante. "
      "Confirmado: su fontanero acudirá mañana 09/06 a reparar la pérdida de agua. "
      "Esta fuga está retrasando el cierre del baño femenino. "
      "ACCIÓN 09/06: verificar a primera hora que la reparación se realiza."
    ),
    "🚫 Baño Femenino — Cierre bloqueado": (
      "El cierre del baño femenino está condicionado a la resolución de la "
      "fuga de agua del vecino. Se desbloquea en cuanto el fontanero del vecino "
      "realice la reparación (09/06). Prioritario para continuar con saneamiento."
    )
  },
  "riesgos": [
    {
      "codigo": "RIESGO-03",
      "tipo": "ACTIVO",
      "descripcion": (
        "Fuga agua vecino activa — bloquea cierre baño femenino. "
        "Fontanero del vecino acude 09/06. Resolución esperada mañana."
      ),
      "accion": "Verificar a primera hora 09/06 que la reparación se realiza. Escalar si no se resuelve.",
      "responsable": "Munir / Darío A. López",
      "estado": "ACTIVO — RESOLUCIÓN ESPERADA 09/06",
      "prioridad": "alta"
    }
  ],
  "alertas_dashboard": [
    {
      "codigo": "ALERTA-D06",
      "tipo": "BLOQUEO ACTIVO",
      "descripcion": "Baño femenino bloqueado por fuga agua vecino. Fontanero 09/06. Verificar reparación a primera hora.",
      "prioridad": "alta",
      "estado": "ACTIVA"
    },
    {
      "codigo": "ALERTA-D07",
      "tipo": "COORDINACIÓN ACTIVA",
      "descripcion": "Electricidad + Munir coordinados. Todos los puntos de luz vistos antes del cierre de tabiques. Cubrir progresivamente.",
      "prioridad": "normal",
      "estado": "ACTIVA"
    }
  ],
  "definiciones_tecnicas": [
    {
      "categoria": "Estado Tabiquería S12",
      "elemento": "Replanteo completado",
      "detalle": "100% de tabiques replanteados. Inicio cierre por una cara. Electricidad marca puntos antes del cierre definitivo."
    },
    {
      "categoria": "Coordinación técnica",
      "elemento": "Electricidad + Albañilería",
      "detalle": "Todos los puntos de luz vistos y marcados en tabiques antes del cierre. Evita rozas posteriores."
    },
    {
      "categoria": "Incidencia activa",
      "elemento": "Fuga agua vecino",
      "detalle": "Fontanero del vecino acude 09/06. Resolución esperada. Desbloquea saneamiento baño femenino."
    }
  ],
  "logros_tecnicos": [
    {
      "descripcion": "Replanteo 100% de tabiques completado — S12 arranca",
      "mejora_de": "Estructura lista S11",
      "mejora_a": "Replanteo 100% + inicio cierre por una cara",
      "impacto": "Tabiquería avanza sin bloqueos estructurales."
    },
    {
      "descripcion": "Coordinación Electricidad + Albañilería en obra",
      "mejora_de": "Gremios en obra separados",
      "mejora_a": "Trabajo conjunto coordinado",
      "impacto": "Puntos de luz integrados antes del cierre. Evita rerrozas."
    },
    {
      "descripcion": "Gestión fuga vecino — Fontanero confirmado 09/06",
      "mejora_de": "Vecino sin contactar",
      "mejora_a": "Fontanero confirmado para mañana",
      "impacto": "Bloqueo baño femenino se levantará el 09/06."
    }
  ],
  "solicitudes_direccion": [
    {
      "descripcion": "09/06 primera hora: verificar que el fontanero del vecino realiza la reparación. Desbloquea baño femenino.",
      "responsable": "Munir / Darío A. López",
      "urgencia": "alta"
    },
    {
      "descripcion": "Confirmar asistencia todas las contratas a reunión semanal 09/06 13:00h.",
      "responsable": "Darío A. López",
      "urgencia": "normal"
    }
  ],
  "agenda_proxima": {
    "items": [
      {"hora": "09/06 — Primera hora", "evento": "Verificar reparación fuga agua vecino. Desbloqueo baño femenino."},
      {"hora": "09/06 13:00h", "evento": "REUNIÓN SEMANAL S12 — Todas las contratas."},
      {"hora": "09/06 — Mañana", "evento": "Climatización (José): arranque — cassettes + conductos."},
      {"hora": "09/06 — Mañana", "evento": "Josevi: inicio estructuras metálicas de puertas + cerramiento sala colectiva."},
      {"hora": "09/06 — Mañana", "evento": "PCI (Leo): continuación detectores sala."}
    ]
  },
  "incidencias": [
    {
      "gremio": "💧 Vecino colindante",
      "descripcion": "Fuga agua activa. Fontanero del vecino acude 09/06. Bloquea cierre baño femenino hasta reparación.",
      "prioridad": "alta"
    }
  ],
  "gremios_incidencia": ["💧 Vecino colindante"],
  "prioridad": "alta",
  "estado": "borrador",
  "creado_por": "Darío A. López",
  "created_at": "2026-06-08T18:00:00"
}


def main():
    with open(JSON_PATH, encoding="utf-8") as f:
        actas = json.load(f)

    ids_existentes = {a["id"] for a in actas}
    nuevas = []
    for acta in [ACTA_0809, ACTA_0806]:
        if acta["id"] in ids_existentes:
            print(f"[SKIP] {acta['id']} ya existe")
        else:
            nuevas.append(acta)
            print(f"[ADD]  {acta['id']} — {acta['fecha']}")

    actas_actualizadas = nuevas + actas
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(actas_actualizadas, f, ensure_ascii=False, indent=2)

    print(f"\nTotal actas en BD: {len(actas_actualizadas)}")


if __name__ == "__main__":
    main()
