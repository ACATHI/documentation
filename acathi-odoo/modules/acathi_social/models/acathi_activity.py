# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AcathiActivity(models.Model):
    _name = 'acathi.activity'
    _description = 'Actividad / Servicio ACATHI'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char('Nombre de la actividad', required=True)
    project_id = fields.Many2one('acathi.project', string='Proyecto')
    active = fields.Boolean('Activo', default=True)
    activity_type = fields.Selection([
        ('legal', 'Asesoría jurídica'),
        ('psychosocial', 'Apoyo psicosocial'),
        ('community', 'Actividad comunitaria'),
        ('training', 'Formación / Taller'),
        ('advocacy', 'Incidencia política'),
        ('health', 'Salud'),
        ('employment', 'Empleo / Orientación laboral'),
        ('housing', 'Alojamiento'),
        ('living_library', 'Biblioteca Viviente'),
        ('leisure', 'Ocio e integración'),
        ('coordination', 'Coordinación interinstitucional'),
        ('other', 'Otros'),
    ], string='Tipo de actividad', required=True)
    state = fields.Selection([
        ('planned', 'Planificada'),
        ('done', 'Realizada'),
        ('cancelled', 'Cancelada'),
    ], string='Estado', default='planned', tracking=True)
    date = fields.Date('Fecha', required=True)
    time_start = fields.Float('Hora inicio')
    time_end = fields.Float('Hora fin')
    duration = fields.Float('Duración (horas)', compute='_compute_duration')
    location = fields.Char('Lugar')
    online = fields.Boolean('Online/Virtual')
    responsible_id = fields.Many2one('hr.employee', string='Responsable')
    facilitator_ids = fields.Many2many('hr.employee',
        'acathi_activity_facilitator_rel', 'activity_id', 'employee_id',
        string='Facilitadores/as')
    participant_ids = fields.Many2many('acathi.person',
        'acathi_activity_participant_rel', 'activity_id', 'person_id',
        string='Participantes')
    participant_count = fields.Integer('Nº participantes', compute='_compute_participant_count')
    external_participants = fields.Integer('Participantes externos')
    total_participants = fields.Integer('Total participantes', compute='_compute_participant_count')
    profile_notes = fields.Text('Perfil general de participantes')
    description = fields.Text('Descripción de la actividad')
    results = fields.Text('Resultados obtenidos')
    satisfaction_score = fields.Float('Puntuación satisfacción (1-10)')
    incidents = fields.Text('Incidencias o aprendizajes')
    attendance_list = fields.Boolean('Lista de asistencia guardada')
    photos_authorized = fields.Boolean('Fotos autorizadas')
    report_done = fields.Boolean('Informe realizado')
    materials = fields.Text('Materiales utilizados')

    @api.depends('time_start', 'time_end')
    def _compute_duration(self):
        for rec in self:
            rec.duration = max(0, rec.time_end - rec.time_start) if rec.time_end > rec.time_start else 0

    @api.depends('participant_ids', 'external_participants')
    def _compute_participant_count(self):
        for rec in self:
            rec.participant_count = len(rec.participant_ids)
            rec.total_participants = rec.participant_count + (rec.external_participants or 0)
