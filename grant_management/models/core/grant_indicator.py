from odoo import api, fields, models


class GrantIndicator(models.Model):
    _name = 'grant.indicator'
    _description = 'Indicador de seguiment del projecte'
    _order = 'sequence, id'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Nom de l\'indicador', required=True)
    indicator_type = fields.Selection(
        selection=[
            ('quantitatiu', 'Quantitatiu'),
            ('qualitatiu', 'Qualitatiu'),
        ],
        string='Tipus',
        default='quantitatiu',
        required=True,
    )
    source = fields.Char(
        string='Font de verificació',
        help='Document, registre o instrument que acredita l\'assoliment',
    )
    expected_value = fields.Char(string='Valor previst (text)')
    expected_value_num = fields.Float(
        string='Valor previst (numèric)',
        digits=(10, 2),
    )
    achieved_value = fields.Char(string='Valor assolit (text)')
    achieved_value_num = fields.Float(
        string='Valor assolit (numèric)',
        digits=(10, 2),
    )
    achievement_pct = fields.Float(
        string='% assoliment',
        compute='_compute_achievement',
        store=True,
        digits=(5, 1),
    )
    traffic_light = fields.Selection(
        selection=[
            ('verd', 'Verd (≥ 80%)'),
            ('groc', 'Groc (50-79%)'),
            ('vermell', 'Vermell (< 50%)'),
        ],
        string='Semàfor',
        compute='_compute_achievement',
        store=True,
    )

    @api.depends('expected_value_num', 'achieved_value_num')
    def _compute_achievement(self):
        for rec in self:
            if rec.expected_value_num:
                pct = (rec.achieved_value_num / rec.expected_value_num) * 100
                rec.achievement_pct = pct
                if pct >= 80:
                    rec.traffic_light = 'verd'
                elif pct >= 50:
                    rec.traffic_light = 'groc'
                else:
                    rec.traffic_light = 'vermell'
            else:
                rec.achievement_pct = 0.0
                rec.traffic_light = False


class GrantHistoricalIndicator(models.Model):
    """Evolució temporal 4 anys (Generalitat DS sec.8.2) — Fase 6"""
    _name = 'grant.historical.indicator'
    _description = 'Indicador històric (evolució pluriennal)'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(string='Indicador', required=True)
    value_y1 = fields.Float(string='Any N-3', digits=(10, 2))
    value_y2 = fields.Float(string='Any N-2', digits=(10, 2))
    value_y3 = fields.Float(string='Any N-1', digits=(10, 2))
    value_y4 = fields.Float(string='Any actual (previsió)', digits=(10, 2))
