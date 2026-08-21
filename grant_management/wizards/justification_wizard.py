from odoo import fields, models, _


class GrantJustificationWizard(models.TransientModel):
    _name = 'grant.justification.wizard'
    _description = 'Assistent per iniciar la justificació'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        readonly=True,
    )
    notes = fields.Text(string='Notes inicials')
    sync_budget = fields.Boolean(
        string='Sincronitzar línies de justificació econòmica des del pressupost',
        default=True,
    )

    def action_confirm(self):
        self.ensure_one()
        app = self.application_id
        justification = self.env['grant.justification'].create({
            'application_id': app.id,
            'internal_notes': self.notes or False,
        })
        eco_just = self.env['grant.economic.justification'].create({
            'application_id': app.id,
        })
        if self.sync_budget:
            eco_just.action_sync_from_budget()
        app.write({'state': 'justificada'})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Justificació'),
            'res_model': 'grant.justification',
            'res_id': justification.id,
            'view_mode': 'form',
            'target': 'current',
        }
