from odoo import api, fields, models, _


class GrantEconomicJustification(models.Model):
    _name = 'grant.economic.justification'
    _description = 'Justificació econòmica'
    _inherit = ['mail.thread']
    _order = 'id desc'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
        tracking=True,
    )
    name = fields.Char(
        string='Referència',
        compute='_compute_name',
        store=True,
    )
    currency_id = fields.Many2one(
        related='application_id.currency_id',
    )
    line_ids = fields.One2many(
        comodel_name='grant.economic.justification.line',
        inverse_name='justification_id',
        string='Línies per categoria',
    )
    total_granted = fields.Monetary(
        string='Import concedit',
        related='application_id.amount_granted',
        currency_field='currency_id',
    )
    total_justified = fields.Monetary(
        string='Total justificat',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    total_executed = fields.Monetary(
        string='Total executat',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    amount_to_return = fields.Monetary(
        string='Import a retornar',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='Import concedit − import justificat. Positiu = cal retorn.',
    )
    state = fields.Selection(
        selection=[
            ('esborrany', 'Esborrany'),
            ('completa', 'Completa'),
            ('presentada', 'Presentada'),
        ],
        string='Estat',
        default='esborrany',
        required=True,
        tracking=True,
    )
    notes = fields.Html(string='Observacions')

    @api.depends('application_id.name')
    def _compute_name(self):
        for rec in self:
            rec.name = _('Just. econòmica — %s') % (rec.application_id.name or '')

    @api.depends('line_ids.amount_justified', 'line_ids.amount_executed')
    def _compute_totals(self):
        for rec in self:
            rec.total_justified = sum(rec.line_ids.mapped('amount_justified'))
            rec.total_executed = sum(rec.line_ids.mapped('amount_executed'))
            granted = rec.total_granted or 0.0
            rec.amount_to_return = max(0.0, granted - rec.total_justified)

    def action_sync_from_budget(self):
        """Sincronitza les línies a partir del pressupost de l'expedient, agrupat per categoria."""
        self.ensure_one()
        self.line_ids.unlink()
        grouped = {}
        for exp in self.application_id.budget_expense_ids:
            key = exp.category_id.id
            if key not in grouped:
                grouped[key] = {
                    'justification_id': self.id,
                    'category_id': key,
                    'amount_requested': 0.0,
                    'amount_reformulated': 0.0,
                    'amount_executed': 0.0,
                    'amount_justified': 0.0,
                    'num_docs': 0,
                }
            grouped[key]['amount_requested'] += exp.amount_requested
            grouped[key]['amount_reformulated'] += (exp.amount_granted or exp.amount_requested)
            grouped[key]['amount_executed'] += exp.amount_executed
            grouped[key]['amount_justified'] += exp.amount_justified
        self.env['grant.economic.justification.line'].create(list(grouped.values()))
        self.write({'state': 'completa'})

    def action_submit(self):
        self.write({'state': 'presentada'})
        self.application_id.write({
            'amount_justified': self.total_justified,
            'state': 'tancada',
        })


class GrantEconomicJustificationLine(models.Model):
    _name = 'grant.economic.justification.line'
    _description = 'Línia de justificació econòmica per categoria'
    _order = 'sequence, id'

    justification_id = fields.Many2one(
        comodel_name='grant.economic.justification',
        string='Justificació',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    category_id = fields.Many2one(
        comodel_name='grant.budget.category',
        string='Categoria',
        required=True,
        ondelete='restrict',
    )
    currency_id = fields.Many2one(
        related='justification_id.currency_id',
    )
    amount_requested = fields.Monetary(
        string='Sol·licitat',
        currency_field='currency_id',
    )
    amount_reformulated = fields.Monetary(
        string='Reformulat',
        currency_field='currency_id',
    )
    amount_executed = fields.Monetary(
        string='Executat',
        currency_field='currency_id',
    )
    amount_justified = fields.Monetary(
        string='Justificat',
        currency_field='currency_id',
    )
    difference = fields.Monetary(
        string='Diferència (sol·l. − just.)',
        compute='_compute_difference',
        store=True,
        currency_field='currency_id',
    )
    num_docs = fields.Integer(
        string='Nre. documents',
        help='Nombre de factures, nòmines o justificants vinculats',
    )

    @api.depends('amount_requested', 'amount_justified')
    def _compute_difference(self):
        for rec in self:
            rec.difference = rec.amount_requested - rec.amount_justified


class GrantRequirement(models.Model):
    _name = 'grant.requirement'
    _description = 'Requeriment d\'esmena del finançador'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_requirement desc'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    date_requirement = fields.Date(
        string='Data del requeriment',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )
    concept = fields.Char(
        string='Concepte',
        required=True,
        help='Resum breu del que demana el finançador',
        tracking=True,
    )
    description_html = fields.Html(
        string='Descripció del requeriment',
        help='Text íntegre o resum del requeriment rebut',
    )
    response_html = fields.Html(
        string='Resposta de l\'entitat',
    )
    date_response = fields.Date(
        string='Data límit de resposta',
        tracking=True,
    )
    date_responded = fields.Date(
        string='Data de resposta efectiva',
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('pendent', 'Pendent'),
            ('respost', 'Respost'),
            ('tancat', 'Tancat'),
        ],
        string='Estat',
        default='pendent',
        required=True,
        tracking=True,
    )

    def action_mark_responded(self):
        self.write({
            'state': 'respost',
            'date_responded': fields.Date.today(),
        })

    def action_close(self):
        self.write({'state': 'tancat'})
