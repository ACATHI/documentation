# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AcathiFollowupPlan(models.Model):
    _name = 'acathi.followup.plan'
    _description = 'Plan de Seguimiento ACATHI'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_created desc'

    name = fields.Char('Título del plan', required=True)
    case_id = fields.Many2one('acathi.case', string='Caso', required=True, ondelete='restrict')
    person_id = fields.Many2one('acathi.person', string='Persona',
        related='case_id.person_id', store=True, readonly=True)

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Activo'),
        ('reviewed', 'Revisado'),
        ('closed', 'Cerrado'),
    ], string='Estado', default='draft', tracking=True)

    date_created = fields.Date('Fecha elaboración', default=fields.Date.today)
    date_review = fields.Date('Próxima revisión')
    responsible_id = fields.Many2one('hr.employee', string='Profesional responsable')

    initial_assessment = fields.Text('Valoración inicial')
    activated_resources = fields.Text('Recursos activados')
    observations = fields.Text('Observaciones')

    objective_ids = fields.One2many('acathi.followup.objective', 'plan_id', string='Objetivos')

    total_objectives = fields.Integer('Total objetivos', compute='_compute_stats')
    achieved_objectives = fields.Integer('Objetivos conseguidos', compute='_compute_stats')
    achievement_rate = fields.Float('% logro', compute='_compute_stats')

    @api.depends('objective_ids', 'objective_ids.state')
    def _compute_stats(self):
        for rec in self:
            total = len(rec.objective_ids)
            achieved = len(rec.objective_ids.filtered(lambda o: o.state == 'achieved'))
            rec.total_objectives = total
            rec.achieved_objectives = achieved
            rec.achievement_rate = (achieved / total * 100) if total > 0 else 0.0

    def action_activate(self):
        self.state = 'active'

    def action_review(self):
        self.state = 'reviewed'

    def action_close(self):
        self.state = 'closed'


class AcathiFollowupObjective(models.Model):
    _name = 'acathi.followup.objective'
    _description = 'Objetivo del Plan de Seguimiento'
    _order = 'area, deadline'

    plan_id = fields.Many2one('acathi.followup.plan', string='Plan',
        required=True, ondelete='cascade')

    area = fields.Selection([
        ('legal', 'Legal / Documentación'),
        ('housing', 'Alojamiento'),
        ('health', 'Salud'),
        ('mental_health', 'Salud mental'),
        ('labor', 'Empleo / Formación laboral'),
        ('education', 'Formación / Idiomas'),
        ('social', 'Integración social'),
        ('economic', 'Situación económica'),
        ('family', 'Situación familiar'),
        ('psychological', 'Apoyo psicológico'),
        ('other', 'Otros'),
    ], string='Área', required=True)

    description = fields.Text('Objetivo', required=True)
    indicator = fields.Text('Indicador de logro')
    deadline = fields.Date('Plazo')
    responsible_id = fields.Many2one('hr.employee', string='Responsable')

    state = fields.Selection([
        ('pending', 'Pendiente'),
        ('in_progress', 'En curso'),
        ('achieved', 'Conseguido'),
        ('not_achieved', 'No conseguido'),
        ('reformulated', 'Reformulado'),
    ], string='Estado', default='pending', tracking=True)

    observations = fields.Text('Observaciones / Evolución')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Alta'),
        ('2', 'Urgente'),
    ], string='Prioridad', default='0')
