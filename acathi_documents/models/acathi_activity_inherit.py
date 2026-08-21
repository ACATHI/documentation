from odoo import models


class AcathiActivityDocuments(models.Model):
    _inherit = 'acathi.activity'

    def action_generate_certificates(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'acathi.generate.document.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_template_type': 'certificate',
                'default_activity_id': self.id,
            },
        }
