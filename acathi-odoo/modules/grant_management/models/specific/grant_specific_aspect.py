from odoo import fields, models


class GrantSpecificAspect(models.Model):
    """Aspectes específics per àmbit 1-8 de la Diputació de Barcelona."""
    _name = 'grant.specific.aspect'
    _description = 'Aspecte específic per àmbit (Diputació BCN)'
    _order = 'ambit_number, sequence'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    ambit_number = fields.Selection(
        selection=[
            ('1', 'Àmbit 1 — Benestar social'),
            ('2', 'Àmbit 2 — Salut'),
            ('3', 'Àmbit 3 — Igualtat i feminisme'),
            ('4', 'Àmbit 4 — Joventut'),
            ('5', 'Àmbit 5 — Educació'),
            ('6', 'Àmbit 6 — Cultura'),
            ('7', 'Àmbit 7 — Medi ambient'),
            ('8', 'Àmbit 8 — Cooperació internacional'),
        ],
        string='Àmbit',
        required=True,
    )
    aspect_name = fields.Char(
        string='Aspecte específic',
        required=True,
        help='Títol de l\'aspecte específic de la línia DIBA',
    )
    description_html = fields.Html(string='Descripció')
    link_to_diba_program = fields.Char(
        string='Vincle amb el programa DIBA',
        help='Codi o nom del programa de la Diputació al qual s\'adreça',
    )


class GrantActivityGender(models.Model):
    """Taula activitat + metodologia + indicadors de gènere (COSIFE sec.2.1)."""
    _name = 'grant.activity.gender'
    _description = 'Activitat amb perspectiva de gènere (COSIFE)'
    _order = 'sequence, id'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    activity_name = fields.Char(
        string='Activitat / acció',
        required=True,
    )
    methodology = fields.Text(
        string='Metodologia amb perspectiva de gènere',
        help='Com s\'incorpora la perspectiva de gènere en l\'execució d\'aquesta activitat',
    )
    gender_indicator = fields.Char(
        string='Indicador de gènere',
        help='Indicador específic per mesurar l\'impacte de gènere',
    )
    target_value = fields.Char(
        string='Valor objectiu',
        help='Ex: 60% de dones, paritat de gènere en formació...',
    )
    verification_source = fields.Char(
        string='Font de verificació',
    )
