# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AcathiIntervention(models.Model):
    _name = 'acathi.intervention'
    _description = 'Intervención ACATHI'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char('Título', required=True)
    case_id = fields.Many2one('acathi.case', string='Caso', required=True,
        ondelete='restrict', tracking=True)
    person_id = fields.Many2one('acathi.person', string='Persona',
        related='case_id.person_id', store=True, readonly=True)

    date = fields.Datetime('Fecha y hora', required=True,
        default=fields.Datetime.now, tracking=True)
    duration = fields.Float('Duración (minutos)', default=30.0)

    intervention_type = fields.Selection([
        ('interview', 'Entrevista'),
        ('phone', 'Llamada telefónica'),
        ('email', 'Email/Mensaje'),
        ('accompaniment', 'Acompañamiento'),
        ('management', 'Gestión/Trámite'),
        ('coordination', 'Coordinación con entidad'),
        ('group', 'Actividad grupal'),
        ('visit', 'Visita domiciliaria'),
        ('other', 'Otras'),
    ], string='Tipo de intervención', required=True)

    modality = fields.Selection([
        ('in_person', 'Presencial'),
        ('phone', 'Telefónica'),
        ('online', 'Online/Videollamada'),
        ('home', 'Domicilio'),
        ('external', 'En entidad externa'),
        ('prison', 'En prisión'),
    ], string='Modalidad', required=True, default='in_person')

    professional_id = fields.Many2one('hr.employee', string='Profesional',
        required=True, tracking=True)

    description = fields.Text('Descripción de la intervención', required=True)
    agreements = fields.Text('Acuerdos y compromisos')
    next_action = fields.Text('Próxima acción')
    next_date = fields.Date('Fecha próxima cita')

    calendar_event_id = fields.Many2one('calendar.event', string='Evento de calendario')

    attachment_ids = fields.Many2many('ir.attachment',
        'acathi_intervention_attachment_rel',
        'intervention_id', 'attachment_id',
        string='Documentos adjuntos')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.next_date and rec.professional_id and rec.professional_id.user_id:
                event = self.env['calendar.event'].create({
                    'name': f"Seguimiento: {rec.person_id.name}",
                    'start': str(rec.next_date),
                    'stop': str(rec.next_date),
                    'allday': True,
                    'user_id': rec.professional_id.user_id.id,
                    'description': rec.next_action or '',
                })
                rec.calendar_event_id = event.id
        return records
