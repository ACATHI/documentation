from odoo import api, fields, models


class GrantStaff(models.Model):
    _name = 'grant.staff'
    _description = 'Personal del projecte'
    _order = 'sequence, id'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Nom i cognoms', required=True)
    role = fields.Char(string='Càrrec / rol en el projecte')
    staff_type = fields.Selection(
        selection=[
            ('professional_propi', 'Professional propi (nòmina entitat)'),
            ('professional_extern', 'Professional extern (contractat)'),
            ('voluntari', 'Voluntari/ària'),
        ],
        string='Tipus',
        required=True,
        default='professional_propi',
    )
    professional_category = fields.Char(
        string='Categoria professional',
        help='Ex: Treballador/a social, Educador/a social, Psicòleg/a...',
    )
    dedication_pct = fields.Float(
        string='% dedicació al projecte',
        digits=(5, 2),
    )
    hours_year = fields.Float(
        string='Hores/any al projecte',
        digits=(10, 2),
    )
    currency_id = fields.Many2one(
        related='application_id.currency_id',
    )
    cost_requested = fields.Monetary(
        string='Cost imputat al projecte (€)',
        currency_field='currency_id',
        help='Import imputable a la subvenció',
    )
    cost_total = fields.Monetary(
        string='Cost total anual (€)',
        currency_field='currency_id',
        help='Cost total en nòmina o contracte (brut + SS empresa)',
    )


class GrantDevice(models.Model):
    _name = 'grant.device'
    _description = 'Dispositiu / servei del projecte (Generalitat DS)'
    _order = 'sequence, id'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Nom del dispositiu / servei', required=True)
    device_type = fields.Char(
        string='Tipus de servei',
        help='Ex: Centre de dia, Servei d\'atenció domiciliària, Servei residencial...',
    )
    municipality = fields.Char(string='Municipi')
    address = fields.Char(string='Adreça')
    schedule = fields.Char(
        string='Horari d\'atenció',
        help='Ex: Dilluns a divendres 9-17h',
    )
    capacity = fields.Integer(string='Capacitat màxima (places)')
    current_users = fields.Integer(string='Usuaris actuals')
    beneficiary_summary_ids = fields.One2many(
        comodel_name='grant.beneficiary.summary',
        inverse_name='device_id',
        string='Resum de beneficiaris',
    )


class GrantBeneficiarySummary(models.Model):
    _name = 'grant.beneficiary.summary'
    _description = 'Resum de beneficiaris per dispositiu'
    _order = 'device_id, age_range'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    device_id = fields.Many2one(
        comodel_name='grant.device',
        string='Dispositiu',
        ondelete='cascade',
    )
    age_range = fields.Selection(
        selection=[
            ('0_17', '0-17 anys'),
            ('18_29', '18-29 anys'),
            ('30_44', '30-44 anys'),
            ('45_64', '45-64 anys'),
            ('65_plus', '65 anys i més'),
            ('total', 'TOTAL'),
        ],
        string='Franja d\'edat',
        required=True,
    )
    num_women = fields.Integer(string='Dones')
    num_men = fields.Integer(string='Homes')
    num_other = fields.Integer(string='Altres / No binari')
    total = fields.Integer(
        string='Total',
        compute='_compute_total',
        store=True,
    )

    @api.depends('num_women', 'num_men', 'num_other')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.num_women + rec.num_men + rec.num_other


class GrantLine(models.Model):
    _name = 'grant.line'
    _description = 'Línia de convocatòria amb unitat de recompte (Generalitat DS)'
    _order = 'sequence, id'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    line_code = fields.Char(string='Codi de línia')
    name = fields.Char(string='Nom de la línia / servei', required=True)
    counting_unit = fields.Char(
        string='Unitat de recompte',
        help='Ex: persones ateses, sessions, places cobertes',
    )
    planned_units_y1 = fields.Float(
        string='Unitats previstes any 1',
        digits=(10, 0),
    )
    planned_units_y2 = fields.Float(
        string='Unitats previstes any 2 (pluriennal)',
        digits=(10, 0),
    )
