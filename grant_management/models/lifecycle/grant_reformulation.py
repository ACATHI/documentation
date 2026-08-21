from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class GrantReformulation(models.Model):
    _name = 'grant.reformulation'
    _description = 'Reformulació de subvenció'
    _inherit = ['mail.thread', 'mail.activity.mixin']
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
    original_amount = fields.Monetary(
        string='Import sol·licitat original',
        related='application_id.amount_requested',
        currency_field='currency_id',
    )
    resolution_amount = fields.Monetary(
        string='Import proposat pel finançador',
        required=True,
        currency_field='currency_id',
        tracking=True,
        help='Import que el finançador proposa concedir, inferior al sol·licitat',
    )
    reduction_amount = fields.Monetary(
        string='Reducció',
        compute='_compute_reduction',
        store=True,
        currency_field='currency_id',
    )
    reduction_pct = fields.Float(
        string='% de reducció',
        compute='_compute_reduction',
        store=True,
        digits=(5, 2),
    )
    justification_html = fields.Html(
        string='Justificació dels canvis',
        help='Explica com s\'adapta el projecte a la reducció pressupostària',
    )
    decision = fields.Selection(
        selection=[
            ('pendent', 'Pendent de decisió'),
            ('acceptar', 'Acceptar la reformulació'),
            ('renunciar', 'Renunciar a la subvenció'),
        ],
        string='Decisió',
        default='pendent',
        required=True,
        tracking=True,
    )
    decision_date = fields.Date(string='Data de la decisió', tracking=True)
    state = fields.Selection(
        selection=[
            ('pendent', 'Pendent'),
            ('acceptada', 'Acceptada'),
            ('renunciada', 'Renunciada'),
        ],
        string='Estat',
        default='pendent',
        required=True,
        tracking=True,
    )
    expense_ids = fields.One2many(
        comodel_name='grant.reformulation.expense',
        inverse_name='reformulation_id',
        string='Pressupost reformulat',
    )
    total_reformulated = fields.Monetary(
        string='Total pressupost reformulat',
        compute='_compute_total_reformulated',
        store=True,
        currency_field='currency_id',
    )

    @api.depends('application_id.name')
    def _compute_name(self):
        for rec in self:
            rec.name = _('Reformulació — %s') % (rec.application_id.name or '')

    @api.depends('original_amount', 'resolution_amount')
    def _compute_reduction(self):
        for rec in self:
            rec.reduction_amount = rec.original_amount - rec.resolution_amount
            rec.reduction_pct = (
                (rec.reduction_amount / rec.original_amount * 100)
                if rec.original_amount else 0.0
            )

    @api.depends('expense_ids.amount_reformulated')
    def _compute_total_reformulated(self):
        for rec in self:
            rec.total_reformulated = sum(rec.expense_ids.mapped('amount_reformulated'))

    @api.constrains('expense_ids', 'resolution_amount')
    def _check_balance(self):
        for rec in self:
            if not rec.expense_ids:
                continue
            if abs(rec.total_reformulated - rec.resolution_amount) > 0.01:
                raise ValidationError(_(
                    'El pressupost reformulat (%.2f€) no coincideix amb '
                    'l\'import proposat pel finançador (%.2f€).'
                ) % (rec.total_reformulated, rec.resolution_amount))

    def action_accept(self):
        self.ensure_one()
        self.write({
            'decision': 'acceptar',
            'state': 'acceptada',
            'decision_date': fields.Date.today(),
        })
        self.application_id.write({
            'state': 'concedida',
            'amount_granted': self.resolution_amount,
            'amount_reformulated': self.resolution_amount,
        })

    def action_renounce(self):
        self.ensure_one()
        self.write({
            'decision': 'renunciar',
            'state': 'renunciada',
            'decision_date': fields.Date.today(),
        })
        self.application_id.write({'state': 'denegada'})

    def action_populate_expenses(self):
        """Copia les línies de despesa de l'expedient com a punt de partida."""
        self.ensure_one()
        self.expense_ids.unlink()
        lines = []
        for expense in self.application_id.budget_expense_ids:
            lines.append({
                'reformulation_id': self.id,
                'category_id': expense.category_id.id,
                'description': expense.description,
                'amount_original': expense.amount_requested,
                'amount_reformulated': expense.amount_requested,
            })
        self.env['grant.reformulation.expense'].create(lines)


class GrantReformulationExpense(models.Model):
    _name = 'grant.reformulation.expense'
    _description = 'Línia de despesa reformulada'
    _order = 'sequence, id'

    reformulation_id = fields.Many2one(
        comodel_name='grant.reformulation',
        string='Reformulació',
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
    description = fields.Char(string='Descripció')
    currency_id = fields.Many2one(
        related='reformulation_id.currency_id',
    )
    amount_original = fields.Monetary(
        string='Import original',
        currency_field='currency_id',
    )
    amount_reformulated = fields.Monetary(
        string='Import reformulat',
        currency_field='currency_id',
        required=True,
    )
    difference = fields.Monetary(
        string='Diferència',
        compute='_compute_difference',
        store=True,
        currency_field='currency_id',
    )
    justification = fields.Char(
        string='Justificació del canvi',
        help='Explica per què s\'ha reduït o eliminat aquesta partida',
    )

    @api.depends('amount_original', 'amount_reformulated')
    def _compute_difference(self):
        for rec in self:
            rec.difference = rec.amount_reformulated - rec.amount_original
