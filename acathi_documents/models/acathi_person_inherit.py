from odoo import models


class AcathiPersonDocuments(models.Model):
    _inherit = 'acathi.person'

    def action_generate_document(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'acathi.generate.document.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_template_type': 'certificate',
                'default_person_id': self.id,
            },
        }
