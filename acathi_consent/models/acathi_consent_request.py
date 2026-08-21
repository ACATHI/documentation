import uuid
from odoo import models, fields, api


class AcathiConsentRequest(models.Model):
    _name = 'acathi.consent.request'
    _description = 'Sol·licitud de consentiment RGPD'
    _order = 'create_date desc'
    _rec_name = 'display_name'

    person_id = fields.Many2one('acathi.person', string='Persona atesa', required=True, ondelete='cascade', index=True)
    token = fields.Char(default=lambda self: str(uuid.uuid4()), readonly=True, copy=False, index=True)
    language = fields.Selection([
        ('ca', 'Català'),
        ('es', 'Castellano'),
        ('fr', 'Français'),
        ('en', 'English'),
        ('ar', 'العربية'),
        ('ru', 'Русский'),
        ('uk', 'Українська'),
    ], string='Idioma del formulari', default='ca', required=True)
    state = fields.Selection([
        ('pending', 'Pendent'),
        ('signed', 'Signat'),
        ('expired', 'Caducat'),
    ], string='Estat', default='pending', readonly=True)

    # Filled when signed
    signed_at = fields.Datetime(string='Data de signatura', readonly=True)
    signer_name = fields.Char(string='Nom signat', readonly=True)
    signer_doc = fields.Char(string='Document', readonly=True)
    consent_basic = fields.Boolean(string='Dades bàsiques', readonly=True)
    consent_legal = fields.Boolean(string='Situació migratòria', readonly=True)
    consent_identity = fields.Boolean(string='Identitat/orientació', readonly=True)
    consent_health = fields.Boolean(string='Salut', readonly=True)
    consent_economic = fields.Boolean(string='Econòmica/habitatge', readonly=True)
    consent_risk = fields.Boolean(string='Vulnerabilitat/risc', readonly=True)
    attachment_id = fields.Many2one('ir.attachment', string='Document signat', readonly=True)

    consent_url = fields.Char(string='Enllaç de consentiment', compute='_compute_consent_url')
    attachment_url = fields.Char(string='URL document signat', compute='_compute_attachment_url')

    @api.depends('token')
    def _compute_consent_url(self):
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url', 'http://localhost:8069')
        for rec in self:
            rec.consent_url = f"{base}/acathi/consent/{rec.token}"

    @api.depends('attachment_id')
    def _compute_attachment_url(self):
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url', 'http://localhost:8069')
        for rec in self:
            if rec.attachment_id:
                rec.attachment_url = f"{base}/web/content/{rec.attachment_id.id}?download=true"
            else:
                rec.attachment_url = False

    def action_open_form_url(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.consent_url,
            'target': 'new',
        }

    def action_view_document(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self.attachment_id.id}?download=true',
            'target': 'new',
        }

    def action_expire(self):
        self.filtered(lambda r: r.state == 'pending').write({'state': 'expired'})
