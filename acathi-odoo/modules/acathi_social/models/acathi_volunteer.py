# -*- coding: utf-8 -*-
from odoo import models, fields


class AcathiVolunteer(models.Model):
    _name = 'acathi.volunteer'
    _description = 'Voluntario/a ACATHI'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char('Nombre completo', required=True)
    partner_id = fields.Many2one('res.partner', string='Contacto')
    active = fields.Boolean('Activo', default=True)
    state = fields.Selection([
        ('active', 'Activo/a'),
        ('inactive', 'Inactivo/a'),
        ('training', 'En formación'),
    ], string='Estado', default='active', tracking=True)
    email = fields.Char('Email')
    phone = fields.Char('Teléfono')
    entry_date = fields.Date('Fecha de alta', default=fields.Date.today)
    exit_date = fields.Date('Fecha de baja')
    skills = fields.Text('Habilidades y competencias')
    availability = fields.Text('Disponibilidad horaria')
    area_ids = fields.Selection([
        ('legal', 'Asesoría jurídica'),
        ('psychosocial', 'Apoyo psicosocial'),
        ('training', 'Formación'),
        ('admin', 'Administración'),
        ('communication', 'Comunicación'),
        ('other', 'Otros'),
    ], string='Área de voluntariado')
    gdpr_consent = fields.Boolean('Consentimiento RGPD')
    notes = fields.Text('Observaciones')
