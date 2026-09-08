# -*- coding: utf-8 -*-
import uuid
from odoo import api, fields, models


class AcathiAssessmentSession(models.Model):
    _name = 'acathi.assessment.session'
    _description = "Sessió d'avaluació (portal mòbil)"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    person_id = fields.Many2one(
        'acathi.person', string='Persona atesa',
        required=True, ondelete='restrict', tracking=True,
    )
    case_id = fields.Many2one(
        'acathi.case', string='Cas',
        domain="[('person_id','=',person_id)]",
        ondelete='set null',
    )
    professional_id = fields.Many2one(
        'hr.employee', string='Professional',
        required=True, tracking=True,
    )
    instrument = fields.Selection([
        ('phq9',  'PHQ-9 (Depressió)'),
        ('gad7',  'GAD-7 (Ansietat)'),
        ('pcl5',  'PCL-5 (Trauma / PTSD)'),
        ('hscl25','HSCL-25 (Ansietat i Depressió)'),
        ('iesr',  'IES-R (Estrès Posttraumàtic)'),
        ('whodas','WHODAS 2.0 (Funcionament)'),
    ], string='Instrument', required=True, tracking=True)
    language = fields.Selection([
        ('ca', 'Català'),
        ('es', 'Castellà'),
        ('en', 'English'),
        ('fr', 'Français'),
        ('ar', 'عربي'),
        ('ru', 'Русский'),
        ('uk', 'Українська'),
    ], string='Idioma del formulari', default='ca', required=True)

    token = fields.Char('Token', readonly=True, copy=False, index=True)
    state = fields.Selection([
        ('pending',   'Pendent'),
        ('completed', 'Completada'),
        ('expired',   'Caducada'),
    ], string='Estat', default='pending', tracking=True, readonly=True)
    expiry_date = fields.Datetime('Caducitat', tracking=True)

    portal_url = fields.Char('URL del formulari', compute='_compute_portal_url', store=False)
    qr_url = fields.Char('URL del QR', compute='_compute_portal_url', store=False)
    whatsapp_msg = fields.Char('Text WhatsApp', compute='_compute_portal_url', store=False)

    # Resultats (un per instrument)
    result_phq9_id    = fields.Many2one('acathi.phq9',               readonly=True, string='PHQ-9')
    result_gad7_id    = fields.Many2one('acathi.gad7',               readonly=True, string='GAD-7')
    result_pcl5_id    = fields.Many2one('acathi.pcl5',               readonly=True, string='PCL-5')
    result_hscl25_id  = fields.Many2one('acathi.hscl25',             readonly=True, string='HSCL-25')
    result_iesr_id    = fields.Many2one('acathi.iesr',               readonly=True, string='IES-R')
    result_whodas_id  = fields.Many2one('acathi.whodas',             readonly=True, string='WHODAS')

    @api.depends('token')
    def _compute_portal_url(self):
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        for rec in self:
            if rec.token:
                url = f'{base}/avaluacio/{rec.token}'
                rec.portal_url = url
                rec.qr_url = f'{url}/qr'
                rec.whatsapp_msg = (
                    f'Hola! Necessitem que completis un breu qüestionari. '
                    f'Pots fer-ho des del teu mòbil en el teu idioma: {url}'
                )
            else:
                rec.portal_url = ''
                rec.qr_url = ''
                rec.whatsapp_msg = ''

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('token'):
                vals['token'] = str(uuid.uuid4()).replace('-', '')
            if not vals.get('expiry_date'):
                vals['expiry_date'] = fields.Datetime.add(
                    fields.Datetime.now(), days=7
                )
        return super().create(vals_list)

    def action_send_whatsapp(self):
        """Envia l'URL per WhatsApp via webhook n8n."""
        self.ensure_one()
        webhook_url = self.env['ir.config_parameter'].sudo().get_param(
            'acathi.n8n.whatsapp_webhook', ''
        )
        if not webhook_url:
            return self._notify('warning', 'Configuració pendent',
                'Cal configurar el paràmetre acathi.n8n.whatsapp_webhook '
                'a Ajustos → Paràmetres tècnics.')
        phone = (
            self.person_id.phone
            or (self.person_id.partner_id and self.person_id.partner_id.phone)
            or ''
        )
        if not phone:
            return self._notify('warning', 'Sense telèfon',
                'La persona atesa no té telèfon registrat.')
        import requests as _req
        try:
            _req.post(webhook_url, json={
                'phone': phone,
                'message': self.whatsapp_msg,
                'token': self.token,
                'instrument': self.instrument,
                'session_id': self.id,
            }, timeout=10)
        except Exception as exc:
            return self._notify('danger', 'Error enviant', str(exc))
        return self._notify('success', 'WhatsApp enviat', f'Missatge enviat a {phone}')

    def action_expire(self):
        """Marca la sessió com a caducada."""
        self.ensure_one()
        self.state = 'expired'

    def action_reset(self):
        """Regenera el token i torna a pendent."""
        self.ensure_one()
        self.token = str(uuid.uuid4()).replace('-', '')
        self.state = 'pending'
        self.expiry_date = fields.Datetime.add(fields.Datetime.now(), days=7)

    def _notify(self, ntype, title, message):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'title': title, 'message': message, 'type': ntype},
        }

    @api.model
    def _cron_expire_sessions(self):
        """Cron diari: marca com a caducades les sessions no completades."""
        expired = self.search([
            ('state', '=', 'pending'),
            ('expiry_date', '<', fields.Datetime.now()),
        ])
        expired.write({'state': 'expired'})
