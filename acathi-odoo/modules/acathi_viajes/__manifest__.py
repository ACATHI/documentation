# -*- coding: utf-8 -*-
{
    "name": "ACATHI Viajes (Radar de Viajes)",
    "version": "17.0.1.3.0",
    "summary": "Solicitudes de viaje y resultados del Radar (motor en n8n). Base y resultados en Odoo.",
    "description": """
Gestiona las solicitudes de viaje de ACATHI y muestra los resultados que calcula
el motor externo (n8n: SerpApi + scoring + Ollama + Nextcloud).

Fase 1: Odoo es la ENTRADA (formulario) y la VISTA DE RESULTADOS. El motor sigue
en n8n+Google Sheets. Un botón envía la solicitud a n8n (webhook) y n8n devuelve
las opciones puntuadas y el enlace al informe.

RGPD: los campos de identidad (PII) están restringidos al grupo "Viajes / Datos
personales (PII)". El resto del equipo ve la solicitud y los resultados sin la
identidad.
""",
    "author": "ACATHI",
    "website": "https://www.acathi.org",
    "category": "Human Resources/Travel",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/viajes_security.xml",
        "security/ir.model.access.csv",
        "data/viaje_sequence.xml",
        "views/viaje_views.xml",
    ],
    "application": True,
    "installable": True,
}
