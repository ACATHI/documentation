from odoo import fields, models, _


# Camps del cicle de vida que NO s'han de duplicar mai
_LIFECYCLE_FIELDS = (
    'reformulation_ids',
    'justification_ids',
    'economic_justification_ids',
    'requirement_ids',
    'communication_plan_ids',
    'historical_indicator_ids',
    'justif_user_ids',
    'entity_report_ids',
)


class GrantDuplicateWizard(models.TransientModel):
    _name = 'grant.duplicate.wizard'
    _description = 'Duplicar expedient per a nova convocatòria'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient original',
        required=True,
        ondelete='cascade',
    )
    call_id = fields.Many2one(
        comodel_name='grant.call',
        string='Nova convocatòria',
        required=True,
    )
    copy_budget = fields.Boolean(
        string='Copiar línies de pressupost',
        default=True,
    )
    copy_activities = fields.Boolean(
        string='Copiar activitats i indicadors',
        default=True,
    )
    copy_staff = fields.Boolean(
        string='Copiar personal i dispositius',
        default=False,
    )
    copy_specific = fields.Boolean(
        string='Copiar aspectes específics (DIBA, COSIFE, SMPRAV)',
        default=False,
    )

    def action_duplicate(self):
        self.ensure_one()
        app = self.application_id

        # Obtenim el dict de còpia amb els overrides bàsics
        vals = app.copy_data({
            'call_id': self.call_id.id,
            'name': app.name,
            'state': 'esborrany',
            'date_submitted': False,
            'amount_granted': 0.0,
            'amount_reformulated': 0.0,
            'amount_justified': 0.0,
            'deadline_submission': False,
            'deadline_justification': False,
        })[0]

        # Sempre eliminem camps de cicle de vida
        for fld in _LIFECYCLE_FIELDS:
            vals.pop(fld, None)

        # Eliminació condicional de contingut
        if not self.copy_budget:
            vals.pop('budget_expense_ids', None)
            vals.pop('budget_income_ids', None)
            vals.pop('cofunding_ids', None)

        if not self.copy_activities:
            vals.pop('grant_activity_ids', None)
            vals.pop('indicator_ids', None)
            vals.pop('objective_link_ids', None)

        if not self.copy_staff:
            vals.pop('staff_ids', None)
            vals.pop('device_ids', None)
            vals.pop('line_ids', None)

        if not self.copy_specific:
            vals.pop('specific_aspect_ids', None)
            vals.pop('activity_gender_ids', None)
            vals.pop('sai_action_ids', None)
            vals.pop('penal_schedule_ids', None)
            vals.pop('device_contact_ids', None)

        new_app = self.env['grant.application'].create(vals)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Expedient duplicat'),
            'res_model': 'grant.application',
            'view_mode': 'form',
            'res_id': new_app.id,
            'target': 'current',
        }
