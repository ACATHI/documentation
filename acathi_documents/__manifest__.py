{
    'name': 'ACATHI Documents',
    'version': '17.0.1.0.0',
    'category': 'ACATHI',
    'summary': 'Plantilles Word per a certificats, donacions i informes. Gestió de donants.',
    'depends': ['acathi_social', 'mail', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/acathi_document_template_views.xml',
        'views/acathi_donation_views.xml',
        'views/acathi_person_views.xml',
        'views/acathi_activity_views.xml',  # placeholder, activitat sense form view estable

        'wizard/generate_document_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'external_dependencies': {'python': ['docx']},
}
