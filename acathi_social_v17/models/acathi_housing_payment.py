# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AcathiHousingPayment(models.Model):
    _name = 'acathi.housing.payment'
    _description = 'Pagament habitatge'
    _inherit = ['mail.thread']
    _order = 'period_year desc, period_month desc'

    occupant_id = fields.Many2one(
        'acathi.housing.occupant',
        string='Ocupant',
        required=True,
        ondelete='cascade',
        index=True,
    )
    housing_id = fields.Many2one(
        'acathi.housing',
        string='Pis',
        related='occupant_id.housing_id',
        store=True,
        readonly=True,
    )
    person_id = fields.Many2one(
        'acathi.person',
        string='Persona',
        related='occupant_id.person_id',
        store=True,
        readonly=True,
    )
    period_month = fields.Selection(
        [
            ('1', '01 - Gener'), ('2', '02 - Febrer'), ('3', '03 - Març'),
            ('4', '04 - Abril'), ('5', '05 - Maig'), ('6', '06 - Juny'),
            ('7', '07 - Juliol'), ('8', '08 - Agost'), ('9', '09 - Setembre'),
            ('10', '10 - Octubre'), ('11', '11 - Novembre'), ('12', '12 - Desembre'),
        ],
        string='Mes',
        required=True,
    )
    period_year = fields.Integer(string='Any', required=True)
    amount = fields.Float(string='Import acordat (€)', digits=(10, 2))
    amount_paid = fields.Float(string='Import pagat (€)', digits=(10, 2))
    due_date = fields.Date(string='Data venciment')
    payment_date = fields.Date(string='Data pagament')
    state = fields.Selection(
        [
            ('pendent', 'Pendent'),
            ('pagat', 'Pagat'),
            ('parcial', 'Pagament parcial'),
            ('exempt', 'Exempt'),
        ],
        string='Estat',
        default='pendent',
        tracking=True,
    )
    notes = fields.Text(string='Observacions')

    _sql_constraints = [
        (
            'unique_occupant_period',
            'UNIQUE(occupant_id, period_year, period_month)',
            'Ja existeix un registre de pagament per aquest ocupant i període.',
        ),
    ]


class AcathiHousingOccupantViv02(models.Model):
    _inherit = 'acathi.housing.occupant'

    monthly_contribution = fields.Float(
        string='Aportació mensual (€)',
        digits=(10, 2),
        help='Import acordat de contribució mensual al manteniment del pis.',
    )
    payment_ids = fields.One2many(
        'acathi.housing.payment',
        'occupant_id',
        string='Pagaments',
    )
    payment_count = fields.Integer(
        string='Nº pagaments',
        compute='_compute_payment_count',
    )

    @api.depends('payment_ids')
    def _compute_payment_count(self):
        for rec in self:
            rec.payment_count = len(rec.payment_ids)


class AcathiCaseViv02(models.Model):
    _inherit = 'acathi.case'

    def action_close(self):
        res = super().action_close()
        if self.person_id:
            occupants = self.env['acathi.housing.occupant'].search([
                ('person_id', '=', self.person_id.id),
                ('state', '=', 'active'),
            ])
            if occupants:
                occupants.write({
                    'state': 'ended',
                    'date_out': fields.Date.today(),
                })
        return res
