# -*- coding: utf-8 -*-
{
    "name": "ACATHI Colaboraciones",
    "summary": "Altas de voluntariado, empleo, prácticas y empresas (datos ordinarios, "
               "segregados de la acogida)",
    "description": """
Registro de personas y entidades que quieren colaborar con ACATHI:
voluntariado, candidaturas de empleo, prácticas y empresas.

Datos ORDINARIOS (no categoría especial). Modelo, grupos y menús SEPARADOS del
módulo de acogida (acathi_intake) para no mezclar datos de sensibilidad distinta.
Recibe altas desde el widget de chat / formularios web vía n8n.
""",
    "version": "1.0.0",
    "category": "Services",
    "author": "ACATHI",
    "license": "LGPL-3",
    "depends": ["base", "mail", "contacts"],
    "data": [
        "security/collab_security.xml",
        "security/ir.model.access.csv",
        "data/collab_sequence.xml",
        "views/collab_views.xml",
    ],
    "application": True,
    "installable": True,
}
