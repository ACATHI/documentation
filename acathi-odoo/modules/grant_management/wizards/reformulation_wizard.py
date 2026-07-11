from odoo import api, fields, models, _


class GrantReformulationWizard(models.TransientModel):
    _name = 'grant.reformulation.wizard'
    _description = 'Assistent per iniciar una reformulació'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        related='application_id.currency_id',
    )
    original_amount = fields.Monetary(
        string='Import sol·licitat',
        related='application_id.amount_requested',
        currency_field='currency_id',
    )
    resolution_amount = fields.Monetary(
        string='Import proposat pel finançador',
        required=True,
        currency_field='currency_id',
    )
    reduction_pct = fields.Float(
        string='% de reducció',
        compute='_compute_reduction_pct',
        digits=(5, 2),
    )
    copy_expenses = fields.Boolean(
        string='Copiar les línies de despesa com a punt de partida',
        default=True,
    )
    notes = fields.Text(string='Notes inicials de la reformulació')

    @api.depends('original_amount', 'resolution_amount')
    def _compute_reduction_pct(self):
        for rec in self:
            if rec.original_amount:
                rec.reduction_pct = (
                    (rec.original_amount - rec.resolution_amount)
                    / rec.original_amount * 100
                )
            else:
                rec.reduction_pct = 0.0

    @api.constrains('resolution_amount', 'original_amount')
    def _check_amounts(self):
        for rec in self:
            if rec.resolution_amount <= 0:
                from odoo.exceptions import ValidationError
                raise ValidationError(_('L\'import proposat ha de ser positiu.'))
            if rec.resolution_amount >= rec.original_amount:
                from odoo.exceptions import ValidationError
                raise ValidationError(_(
                    'L\'import proposat (%.2f€) ha de ser inferior '
                    'al sol·licitat (%.2f€).'
                ) % (rec.resolution_amount, rec.original_amount))

    def action_confirm(self):
        self.ensure_one()
        reformulation = self.env['grant.reformulation'].create({
            'application_id': self.application_id.id,
            'resolution_amount': self.resolution_amount,
            'justification_html': self.notes or False,
            'state': 'pendent',
            'decision': 'pendent',
        })
        self.application_id.write({'state': 'en_reformulacio'})
        if self.copy_expenses:
            reformulation.action_populate_expenses()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reformulació'),
            'res_model': 'grant.reformulation',
            'res_id': reformulation.id,
            'view_mode': 'form',
            'target': 'current',
        }
