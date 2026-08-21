# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AcathiCase(models.Model):
    _name = 'acathi.case'
    _description = 'Caso / Expediente ACATHI'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_open desc'

    reference = fields.Char('Referencia', readonly=True, copy=False, default='Nuevo')
    person_id = fields.Many2one('acathi.person', string='Persona atendida',
        required=True, tracking=True, ondelete='restrict')
    name = fields.Char('Título del caso', required=True)

    case_type = fields.Selection([
        ('reception', 'Acogida'),
        ('legal', 'Legal / Asilo'),
        ('psychological', 'Psicológico'),
        ('labor', 'Laboral'),
        ('social', 'Social'),
        ('health', 'Salud'),
        ('prison', 'Prisión'),
        ('housing', 'Alojamiento'),
        ('education', 'Formación'),
        ('economic', 'Económico'),
        ('other', 'Otros'),
    ], string='Tipo de caso', required=True, tracking=True)

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Alta'),
        ('2', 'Urgente'),
    ], string='Prioridad', default='0', tracking=True)

    state = fields.Selection([
        ('new', 'Nuevo'),
        ('active', 'Activo'),
        ('followup', 'En seguimiento'),
        ('referred', 'Derivado'),
        ('closed', 'Cerrado'),
    ], string='Estado', default='new', tracking=True)

    responsible_id = fields.Many2one('hr.employee', string='Profesional responsable',
        required=True, tracking=True)
    co_professional_ids = fields.Many2many('hr.employee',
        'acathi_case_employee_rel', 'case_id', 'employee_id',
        string='Co-profesionales')

    date_open = fields.Date('Fecha apertura', default=fields.Date.today)
    date_close = fields.Date('Fecha cierre')
    close_reason = fields.Selection([
        ('resolved', 'Resuelto'),
        ('referred', 'Derivado'),
        ('abandoned', 'Abandono'),
        ('lost_contact', 'Pérdida de contacto'),
        ('other', 'Otros'),
    ], string='Motivo cierre')
    referral_entity_id = fields.Many2one('res.partner', string='Entidad derivación')

    description = fields.Text('Motivo de consulta')
    confidential = fields.Boolean('Confidencial')
    notes = fields.Text('Observaciones')

    intervention_ids = fields.One2many('acathi.intervention', 'case_id', string='Intervenciones')
    intervention_count = fields.Integer('Nº Intervenciones', compute='_compute_counts')
    followup_plan_ids = fields.One2many('acathi.followup.plan', 'case_id', string='Planes de seguimiento')
    followup_count = fields.Integer('Nº Planes', compute='_compute_counts')

    @api.depends('intervention_ids', 'followup_plan_ids')
    def _compute_counts(self):
        for rec in self:
            rec.intervention_count = len(rec.intervention_ids)
            rec.followup_count = len(rec.followup_plan_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'Nuevo') == 'Nuevo':
                vals['reference'] = self.env['ir.sequence'].next_by_code('acathi.case') or 'Nuevo'
        return super().create(vals_list)

    def action_activate(self):
        self.state = 'active'

    def action_followup(self):
        self.state = 'followup'

    def action_close(self):
        self.state = 'closed'
        self.date_close = fields.Date.today()

    def action_view_interventions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Intervenciones',
            'res_model': 'acathi.intervention',
            'view_mode': 'list,form,calendar',
            'domain': [('case_id', '=', self.id)],
            'context': {'default_case_id': self.id},
        }

    def action_view_followup(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Planes de Seguimiento',
            'res_model': 'acathi.followup.plan',
            'view_mode': 'list,form',
            'domain': [('case_id', '=', self.id)],
            'context': {'default_case_id': self.id},
        }
