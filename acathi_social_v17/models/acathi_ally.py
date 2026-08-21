# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AcathiAlly(models.Model):
    _name = 'acathi.ally'
    _description = 'Aliado / Entidad colaboradora ACATHI'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char('Nombre de la entidad', required=True)
    partner_id = fields.Many2one('res.partner', string='Contacto en agenda')
    active = fields.Boolean('Activo', default=True)
    ally_type = fields.Selection([
        ('ngo', 'ONG / Asociación'),
        ('public', 'Servicio público'),
        ('health', 'Centro de salud'),
        ('legal', 'Servicio jurídico'),
        ('housing', 'Recurso habitacional'),
        ('employment', 'Servicio de empleo'),
        ('education', 'Centro educativo'),
        ('religious', 'Entidad religiosa'),
        ('media', 'Medios de comunicación'),
        ('company', 'Empresa'),
        ('network', 'Red / Federación'),
        ('international', 'Organismo internacional'),
        ('other', 'Otros'),
    ], string='Tipo de entidad', required=True)
    state = fields.Selection([
        ('active', 'Colaboración activa'),
        ('occasional', 'Colaboración ocasional'),
        ('inactive', 'Inactiva'),
        ('potential', 'Potencial'),
    ], string='Estado de la relación', default='active', tracking=True)
    services = fields.Text('Servicios que ofrecen')
    contact_name = fields.Char('Persona de contacto')
    contact_phone = fields.Char('Teléfono')
    contact_email = fields.Char('Email')
    website = fields.Char('Web')
    address = fields.Char('Dirección')
    city = fields.Char('Ciudad')
    agreement_type = fields.Selection([
        ('formal', 'Convenio formal'),
        ('informal', 'Acuerdo informal'),
        ('protocol', 'Protocolo de derivación'),
        ('none', 'Sin acuerdo formal'),
    ], string='Tipo de acuerdo')
    agreement_date = fields.Date('Fecha acuerdo')
    agreement_expiry = fields.Date('Caducidad acuerdo')
    notes = fields.Text('Observaciones')
    referral_ids = fields.One2many('acathi.ally.referral', 'ally_id', string='Derivaciones')
    referral_count = fields.Integer('Nº derivaciones', compute='_compute_referral_count')

    @api.depends('referral_ids')
    def _compute_referral_count(self):
        for rec in self:
            rec.referral_count = len(rec.referral_ids)


class AcathiAllyReferral(models.Model):
    _name = 'acathi.ally.referral'
    _description = 'Derivación a aliado'
    _order = 'date desc'

    ally_id = fields.Many2one('acathi.ally', string='Entidad', required=True)
    person_id = fields.Many2one('acathi.person', string='Persona')
    case_id = fields.Many2one('acathi.case', string='Caso')
    date = fields.Date('Fecha derivación', default=fields.Date.today)
    service = fields.Char('Servicio solicitado')
    reason = fields.Text('Motivo de derivación')
    professional_id = fields.Many2one('hr.employee', string='Profesional ACATHI')
    state = fields.Selection([
        ('sent', 'Enviada'),
        ('accepted', 'Aceptada'),
        ('waiting', 'En espera'),
        ('rejected', 'No aceptada'),
        ('completed', 'Completada'),
    ], string='Estado', default='sent')
    result = fields.Text('Resultado')
