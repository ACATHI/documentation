from odoo import models, fields, api


class AcathiPersonConsent(models.Model):
    _inherit = 'acathi.person'

    consent_request_ids = fields.One2many('acathi.consent.request', 'person_id', string='Consentiments RGPD')
    consent_request_count = fields.Integer(compute='_compute_consent_count')
    consent_signed_count = fields.Integer(compute='_compute_consent_count')

    @api.depends('consent_request_ids', 'consent_request_ids.state')
    def _compute_consent_count(self):
        for rec in self:
            rec.consent_request_count = len(rec.consent_request_ids)
            rec.consent_signed_count = len(rec.consent_request_ids.filtered(lambda r: r.state == 'signed'))

    def action_view_consent_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Consentiments RGPD',
            'res_model': 'acathi.consent.request',
            'view_mode': 'list,form',
            'domain': [('person_id', '=', self.id)],
            'context': {'default_person_id': self.id},
        }

    def action_create_consent_request(self):
        self.ensure_one()
        req = self.env['acathi.consent.request'].create({'person_id': self.id})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nou consentiment',
            'res_model': 'acathi.consent.request',
            'view_mode': 'form',
            'res_id': req.id,
            'target': 'new',
        }
