from odoo import fields, models


class GrantCollaborator(models.Model):
    _name = 'grant.collaborator'
    _description = 'Entitat col·laboradora del projecte'
    _order = 'sequence, id'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Entitat',
        ondelete='set null',
    )
    name = fields.Char(
        string='Nom de l\'entitat',
        compute='_compute_name',
        store=True,
        readonly=False,
    )
    role = fields.Char(string='Rol en el projecte')
    contribution_html = fields.Html(string='Contribució')

    def _compute_name(self):
        for rec in self:
            if rec.partner_id and not rec.name:
                rec.name = rec.partner_id.name
            elif not rec.name:
                rec.name = False


class GrantCofunding(models.Model):
    _name = 'grant.cofunding'
    _description = 'Cofinançament del projecte'
    _order = 'sequence, id'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    administration = fields.Char(
        string='Administració / entitat',
        required=True,
        help='Nom de l\'entitat que cofinança (administració, fundació, etc.)',
    )
    concept = fields.Char(string='Concepte / programa')
    currency_id = fields.Many2one(
        related='application_id.currency_id',
        string='Moneda',
    )
    amount = fields.Monetary(
        string='Import',
        currency_field='currency_id',
        required=True,
    )
    cofunding_state = fields.Selection(
        selection=[
            ('sol_licitat', 'Sol·licitat'),
            ('concedit', 'Concedit'),
            ('confirmat', 'Confirmat'),
        ],
        string='Estat',
        default='sol_licitat',
    )


class GrantSaiAction(models.Model):
    """Accions coordinades amb Xarxa SAI LGBTI (COSIFE Línia C) — Fase 7"""
    _name = 'grant.sai.action'
    _description = 'Acció coordinada Xarxa SAI LGBTI'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    action_name = fields.Char(string='Acció', required=True)
    sai_entity = fields.Char(string='Entitat SAI')
    description = fields.Text(string='Descripció')
