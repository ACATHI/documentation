# -*- coding: utf-8 -*-
{
    "name": "ACATHI Intake (Primera acogida)",
    "version": "17.0.1.0.0",
    "summary": "Solicitudes de primera acogida multicanal (Telegram/WhatsApp/web) con triaje, "
               "consentimiento RGPD y derivación humana. Orquestación en n8n.",
    "description": """
Columna vertebral en Odoo del sistema de primera acogida de ACATHI.

Fase MVP: el canal (Telegram) y la orquestación (n8n) crean/actualizan aquí el
contacto, la solicitud y el hilo de mensajes. La clasificación es por menú
(determinista), NO por IA en tiempo real.

RGPD: el contenido libre potencialmente sensible (mensaje original, resúmenes,
cuerpo de los mensajes, marca de beneficiario/a) está restringido al grupo
"Acogida / Datos sensibles". El resto del equipo ve la solicitud (estado,
prioridad, riesgo, equipo, idioma) sin el contenido íntimo.

La retención NO está fijada por código: es un parámetro
(acathi_intake.retention_days, 0 = desactivado) pendiente de la asesoría/EIPD.
""",
    "author": "ACATHI",
    "website": "https://www.acathi.org",
    "category": "Services",
    "license": "LGPL-3",
    "depends": ["base", "mail", "contacts", "calendar", "acathi_social"],
    "data": [
        "security/intake_security.xml",
        "security/ir.model.access.csv",
        "data/intake_sequence.xml",
        "data/intake_cron.xml",
        "views/intake_request_views.xml",
        "views/intake_message_views.xml",
        "views/res_partner_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "installable": True,
}
