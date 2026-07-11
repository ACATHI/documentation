# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AcathiHousing(models.Model):
    _name = 'acathi.housing'
    _description = 'Piso de Acogida ACATHI'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nombre del piso', required=True)
    reference = fields.Char('Referencia interna')
    active = fields.Boolean('Activo', default=True)

    state = fields.Selection([
        ('available', 'Disponible'),
        ('full', 'Completo'),
        ('maintenance', 'En mantenimiento'),
        ('closed', 'Cerrado'),
    ], string='Estado', default='available', tracking=True)

    street = fields.Char('Dirección')
    city = fields.Char('Ciudad')
    zip_code = fields.Char('Código postal')
    province = fields.Char('Provincia')

    total_capacity = fields.Integer('Capacidad total (personas)')
    room_count = fields.Integer('Número de habitaciones')
    current_occupancy = fields.Integer('Ocupación actual', compute='_compute_occupancy', store=True)
    available_places = fields.Integer('Plazas disponibles', compute='_compute_occupancy', store=True)

    responsible_id = fields.Many2one('hr.employee', string='Profesional responsable')
    phone = fields.Char('Teléfono del piso')

    rent = fields.Float('Alquiler mensual (€)')
    contract_end = fields.Date('Fin de contrato')
    landlord = fields.Char('Propietario/a')
    landlord_phone = fields.Char('Teléfono propietario/a')

    has_wifi = fields.Boolean('WiFi')
    has_washing_machine = fields.Boolean('Lavadora')
    has_elevator = fields.Boolean('Ascensor')
    accessibility = fields.Boolean('Accesibilidad reducida')
    notes = fields.Text('Observaciones')

    occupant_ids = fields.One2many('acathi.housing.occupant', 'housing_id',
        string='Ocupantes actuales', domain=[('state', '=', 'active')])
    occupant_history_ids = fields.One2many('acathi.housing.occupant', 'housing_id',
        string='Historial de ocupantes')
    waiting_list_ids = fields.One2many('acathi.housing.waiting', 'housing_id',
        string='Lista de espera')
    waiting_count = fields.Integer('En lista de espera', compute='_compute_waiting')
    incident_ids = fields.One2many('acathi.housing.incident', 'housing_id',
        string='Incidencias')

    @api.depends('occupant_ids', 'total_capacity')
    def _compute_occupancy(self):
        for rec in self:
            current = len(rec.occupant_ids.filtered(lambda o: o.state == 'active'))
            rec.current_occupancy = current
            rec.available_places = max(0, rec.total_capacity - current)

    @api.depends('waiting_list_ids')
    def _compute_waiting(self):
        for rec in self:
            rec.waiting_count = len(rec.waiting_list_ids)


class AcathiHousingOccupant(models.Model):
    _name = 'acathi.housing.occupant'
    _description = 'Ocupante de Piso ACATHI'
    _order = 'date_in desc'

    housing_id = fields.Many2one('acathi.housing', string='Piso', required=True, ondelete='restrict')
    person_id = fields.Many2one('acathi.person', string='Persona', required=True, ondelete='restrict')
    room = fields.Char('Habitación')
    date_in = fields.Date('Fecha entrada', required=True, default=fields.Date.today)
    date_out = fields.Date('Fecha salida')
    date_out_planned = fields.Date('Fecha salida prevista')
    state = fields.Selection([
        ('active', 'Activo'),
        ('ended', 'Finalizado'),
    ], string='Estado', default='active')
    exit_reason = fields.Selection([
        ('autonomous', 'Autonomía conseguida'),
        ('referred', 'Derivado a otro recurso'),
        ('voluntary', 'Salida voluntaria'),
        ('expelled', 'Expulsión por incumplimiento'),
        ('other', 'Otros'),
    ], string='Motivo salida')
    notes = fields.Text('Observaciones')
    signed_rules = fields.Boolean('Normas de convivencia firmadas')
    signed_date = fields.Date('Fecha firma normas')


class AcathiHousingWaiting(models.Model):
    _name = 'acathi.housing.waiting'
    _description = 'Lista de espera piso ACATHI'
    _order = 'request_date'

    housing_id = fields.Many2one('acathi.housing', string='Piso')
    person_id = fields.Many2one('acathi.person', string='Persona', required=True)
    request_date = fields.Date('Fecha solicitud', default=fields.Date.today)
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Alta'),
        ('2', 'Urgente'),
    ], string='Prioridad', default='0')
    notes = fields.Text('Motivo / Observaciones')
    state = fields.Selection([
        ('waiting', 'En espera'),
        ('assigned', 'Asignada/o'),
        ('cancelled', 'Cancelada/o'),
    ], string='Estado', default='waiting')


class AcathiHousingIncident(models.Model):
    _name = 'acathi.housing.incident'
    _description = 'Incidencia en piso ACATHI'
    _order = 'date desc'

    housing_id = fields.Many2one('acathi.housing', string='Piso', required=True)
    date = fields.Date('Fecha', default=fields.Date.today)
    incident_type = fields.Selection([
        ('maintenance', 'Mantenimiento'),
        ('coexistence', 'Convivencia'),
        ('security', 'Seguridad'),
        ('other', 'Otras'),
    ], string='Tipo', required=True)
    description = fields.Text('Descripción', required=True)
    state = fields.Selection([
        ('open', 'Abierta'),
        ('in_progress', 'En gestión'),
        ('closed', 'Resuelta'),
    ], string='Estado', default='open')
    resolution = fields.Text('Resolución')
    responsible_id = fields.Many2one('hr.employee', string='Responsable')
