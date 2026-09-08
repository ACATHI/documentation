# -*- coding: utf-8 -*-
import uuid
import json
import logging
import requests
from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AcathiFirmaSession(models.Model):
    _name = 'acathi.firma.session'
    _description = 'Sessió de firma per a un firmant'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    document_id = fields.Many2one(
        'acathi.firma.document', string='Document',
        required=True, ondelete='cascade')
    person_id = fields.Many2one(
        'acathi.person', string='Persona atesa')
    signatory_name = fields.Char(
        string='Nom del firmant',
        compute='_compute_signatory_name', store=True, readonly=False)
    phone = fields.Char(
        string='Telèfon (WhatsApp)',
        compute='_compute_phone', store=True, readonly=False)
    token = fields.Char(
        string='Token', default=lambda self: str(uuid.uuid4()),
        readonly=True, copy=False)
    state = fields.Selection([
        ('pending', 'Pendent'),
        ('signed', 'Firmat'),
        ('expired', 'Caducat'),
    ], default='pending', string='Estat', tracking=True)
    expiry_date = fields.Datetime(
        string='Caducitat',
        default=lambda self: datetime.now() + timedelta(days=15))
    portal_url = fields.Char(
        string='URL del portal', compute='_compute_urls')
    qr_url = fields.Char(
        string='URL del QR', compute='_compute_urls')
    signed_document = fields.Binary(
        string='PDF firmat', attachment=True, readonly=True)
    signed_document_filename = fields.Char(readonly=True)
    signature_image = fields.Binary(
        string='Imatge de la firma', attachment=True, readonly=True)
    signed_date = fields.Datetime(string='Data de firma', readonly=True)
    whatsapp_msg = fields.Char(
        string='Missatge WhatsApp', compute='_compute_whatsapp_msg')

    sig_x_pct = fields.Float(string='Posició X (%)', default=55.0, digits=(6, 2))
    sig_y_pct = fields.Float(string='Posició Y (% des baix)', default=8.0, digits=(6, 2))
    sig_page = fields.Integer(string='Pàgina (0=última)', default=0)

    @api.depends('person_id')
    def _compute_signatory_name(self):
        for rec in self:
            if rec.person_id and not rec.signatory_name:
                rec.signatory_name = rec.person_id.name

    @api.depends('person_id')
    def _compute_phone(self):
        for rec in self:
            if rec.person_id and not rec.phone:
                partner = rec.person_id.partner_id
                rec.phone = partner.mobile or partner.phone or ''

    @api.depends('token')
    def _compute_urls(self):
        base = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url', 'http://localhost:8069')
        for rec in self:
            rec.portal_url = f"{base}/firma/{rec.token}"
            rec.qr_url = f"{base}/firma/{rec.token}/qr"

    @api.depends('document_id', 'portal_url', 'signatory_name')
    def _compute_whatsapp_msg(self):
        for rec in self:
            doc = rec.document_id.name or 'document'
            name = rec.signatory_name or ''
            url = rec.portal_url or ''
            rec.whatsapp_msg = (
                f"Hola {name},\n\nT'enviem el document «{doc}» perquè el signis "
                f"digitalment des del teu mòbil.\n\n🔗 {url}\n\n"
                f"L'enllaç caduca el {rec.expiry_date.strftime('%d/%m/%Y') if rec.expiry_date else ''}."
            )

    def action_send_whatsapp(self):
        self.ensure_one()
        if not self.phone:
            raise UserError('Cal indicar el telèfon del firmant.')
        webhook = self.env['ir.config_parameter'].sudo().get_param(
            'acathi.n8n.whatsapp_webhook')
        if not webhook:
            raise UserError(
                'Configura el paràmetre acathi.n8n.whatsapp_webhook a '
                'Ajustos → Paràmetres tècnics.')
        payload = {
            'phone': self.phone,
            'message': self.whatsapp_msg,
            'token': self.token,
            'document': self.document_id.name,
            'session_id': self.id,
        }
        try:
            r = requests.post(webhook, json=payload, timeout=10)
            r.raise_for_status()
        except Exception as e:
            raise UserError(f'Error enviant WhatsApp: {e}')
        self.message_post(
            body=f'WhatsApp enviat a {self.phone}',
            message_type='comment')

    def action_open_position_picker(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/firma-pos/{self.id}',
            'target': 'new',
        }

    def action_expire(self):
        self.state = 'expired'

    def action_reset(self):
        self.write({
            'token': str(uuid.uuid4()),
            'state': 'pending',
            'expiry_date': datetime.now() + timedelta(days=15),
            'signed_document': False,
            'signature_image': False,
            'signed_date': False,
        })
