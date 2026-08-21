{
    'name': 'ACATHI Consentiment RGPD',
    'version': '17.0.1.0.0',
    'category': 'ACATHI',
    'summary': 'Formulari de consentiment RGPD signable des del mòbil, integrat amb acathi_social',
    'depends': ['acathi_social', 'web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/acathi_consent_document_template.xml',
        'views/acathi_consent_request_views.xml',
        'views/acathi_person_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
