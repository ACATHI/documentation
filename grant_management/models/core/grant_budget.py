from odoo import api, fields, models


class GrantBudgetExpense(models.Model):
    _name = 'grant.budget.expense'
    _description = 'Línia de despesa del pressupost'
    _order = 'sequence, id'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
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
    description = fields.Char(
        string='Descripció / detall',
        help='Descripció específica de la despesa dins de la categoria',
    )
    currency_id = fields.Many2one(
        related='application_id.currency_id',
        string='Moneda',
    )
    amount_requested = fields.Monetary(
        string='Sol·licitat',
        currency_field='currency_id',
    )
    amount_granted = fields.Monetary(
        string='Concedit',
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
    notes = fields.Char(string='Notes')


class GrantBudgetIncome(models.Model):
    _name = 'grant.budget.income'
    _description = 'Línia d\'ingressos del pressupost'
    _order = 'sequence, id'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    source_type = fields.Selection(
        selection=[
            ('grant_requested', 'Subvenció sol·licitada (aquest finançador)'),
            ('grant_other', 'Altra subvenció pública'),
            ('own_resources', 'Recursos propis de l\'entitat'),
            ('other', 'Altres ingressos'),
        ],
        string='Tipus d\'ingrés',
        required=True,
        default='grant_requested',
    )
    funder_id = fields.Many2one(
        comodel_name='grant.funder',
        string='Finançador (altra subvenció)',
        ondelete='set null',
    )
    description = fields.Char(string='Descripció')
    currency_id = fields.Many2one(
        related='application_id.currency_id',
        string='Moneda',
    )
    amount = fields.Monetary(
        string='Import',
        currency_field='currency_id',
        required=True,
    )
