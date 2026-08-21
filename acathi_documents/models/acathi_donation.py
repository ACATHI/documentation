from odoo import models, fields, api


class AcathiDonation(models.Model):
    _name = 'acathi.donation'
    _description = 'Donació a ACATHI'
    _order = 'date_received desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Referència', compute='_compute_name', store=True)

    donor_id = fields.Many2one(
        'acathi.donor',
        string='Donant',
        required=True,
        index=True,
        tracking=True,
    )
    # Dades del donant (readonly, des de acathi.donor)
    donor_type = fields.Selection(related='donor_id.donor_type', string='Tipus', readonly=True, store=True)
    donor_email = fields.Char(related='donor_id.email', string='Email donant', readonly=True)
    donor_phone = fields.Char(related='donor_id.phone', string='Telèfon donant', readonly=True)

    amount = fields.Float(string='Import (€)', required=True, digits=(10, 2), tracking=True)
    date_received = fields.Date(
        string='Data de recepció del diners',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )
    purpose = fields.Text(
        string='Finalitat / destinació dels fons',
        required=True,
        help='A quins fins es destinaran els fons rebuts',
    )
    state = fields.Selection([
        ('draft', 'Esborrany'),
        ('confirmed', 'Confirmada'),
        ('receipt_sent', 'Rebut enviat'),
    ], string='Estat', default='draft', tracking=True)
    certificate_attachment_id = fields.Many2one('ir.attachment', string='Certificat generat', readonly=True)
    notes = fields.Text(string='Notes')

    @api.depends('donor_id', 'date_received', 'amount')
    def _compute_name(self):
        for rec in self:
            donor = rec.donor_id.name or ''
            date = rec.date_received.strftime('%Y-%m') if rec.date_received else ''
            amount = f'{rec.amount:.0f}€' if rec.amount else ''
            rec.name = f'DON-{date}-{donor[:20]}-{amount}' if donor else 'DON-nou'

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_mark_receipt_sent(self):
        self.write({'state': 'receipt_sent'})

    def action_generate_certificate(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'acathi.generate.document.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_template_type': 'donation',
                'default_donation_id': self.id,
            },
        }
