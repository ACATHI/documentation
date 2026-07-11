# -*- coding: utf-8 -*-
from odoo import models, fields


class AcathiDonor(models.Model):
    _name = 'acathi.donor'
    _description = 'Donante ACATHI'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char('Nombre', required=True)
    partner_id = fields.Many2one('res.partner', string='Contacto')
    active = fields.Boolean('Activo', default=True)
    donor_type = fields.Selection([
        ('individual', 'Persona física'),
        ('company', 'Empresa'),
        ('foundation', 'Fundación'),
        ('other', 'Otros'),
    ], string='Tipo de donante')
    email = fields.Char('Email')
    phone = fields.Char('Teléfono')
    first_donation_date = fields.Date('Primera donación')
    last_donation_date = fields.Date('Última donación')
    total_donated = fields.Float('Total donado (€)')
    donation_type = fields.Selection([
        ('one_time', 'Puntual'),
        ('recurring', 'Recurrente'),
        ('both', 'Ambos'),
    ], string='Tipo de donación')
    gdpr_consent = fields.Boolean('Consentimiento RGPD')
    notes = fields.Text('Observaciones')
