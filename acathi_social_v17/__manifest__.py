# -*- coding: utf-8 -*-
{
    'name': 'ACATHI Social',
    'version': '17.0.1.1.0',
    'category': 'Social',
    'summary': 'Gestión social de personas atendidas, casos, intervenciones y pisos de acogida',
    'description': """
        Módulo de gestión social para ACATHI - Migración, refugio y diversidad LGBTIQ+
        Funcionalidades:
        - Ficha completa de personas atendidas (vinculada a res.partner)
        - Gestión de casos y expedientes
        - Registro de intervenciones (vinculado al calendario)
        - Planes de seguimiento con objetivos
        - Derivaciones a otras entidades
        - Gestión de pisos de acogida
        - Gestión de voluntariado
        - Gestión de donantes
        - Impacto social
    """,
    'author': 'ACATHI',
    'website': 'https://www.acathi.org',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'calendar',
        'contacts',
        'hr',
        'grant_management',
    ],
    'data': [
        'security/acathi_security.xml',
        'security/ir.model.access.csv',
        'data/acathi_data.xml',
        'data/acathi_document_cron.xml',
        'views/acathi_person_views.xml',
        'views/acathi_case_views.xml',
        'views/acathi_intervention_views.xml',
        'views/acathi_followup_views.xml',
        'views/acathi_housing_views.xml',
        'views/acathi_housing_payment_views.xml',
        'views/acathi_project_views.xml',
        'views/acathi_activity_views.xml',
        'views/acathi_ally_views.xml',
        'views/acathi_donor_views.xml',
        'views/acathi_volunteer_views.xml',
        'views/acathi_impact_views.xml',
        'views/acathi_document_views.xml',
        'views/acathi_referral_views.xml',
        'views/acathi_aid_views.xml',
        'views/acathi_grant_analytics_views.xml',
        'views/acathi_menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/icon.png'],
}
