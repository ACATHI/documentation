# -*- coding: utf-8 -*-
{
    'name': 'ACATHI Firma Digital',
    'version': '17.0.1.0.0',
    'category': 'Social',
    'summary': 'Firma digital de documents via portal mòbil i WhatsApp',
    'author': 'ACATHI',
    'website': 'https://www.acathi.org',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'web', 'acathi_social'],
    'data': [
        'security/ir.model.access.csv',
        'views/acathi_firma_document_views.xml',
        'views/acathi_firma_session_views.xml',
        'views/acathi_firma_menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/icon.png'],
}
