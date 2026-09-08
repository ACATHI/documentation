# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date, timedelta


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

    followup_snooze_date = fields.Date(
        'Silenciar avisos fins a',
        help='Si s\'estableix, no s\'enviaran avisos d\'inactivitat fins a aquesta data.',
    )
    last_intervention_date = fields.Datetime(
        'Darrera intervenció', compute='_compute_last_intervention', store=True,
    )

    @api.depends('intervention_ids', 'followup_plan_ids')
    def _compute_counts(self):
        for rec in self:
            rec.intervention_count = len(rec.intervention_ids)
            rec.followup_count = len(rec.followup_plan_ids)

    @api.depends('intervention_ids.date')
    def _compute_last_intervention(self):
        for rec in self:
            dates = rec.intervention_ids.mapped('date')
            rec.last_intervention_date = max(dates) if dates else False

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

    def action_reopen(self):
        self.ensure_one()
        self.state = 'active'
        self.date_close = False
        self.followup_snooze_date = False
        self.env['acathi.intervention'].create({
            'name': f'Reobertura — {fields.Date.today()}',
            'case_id': self.id,
            'person_id': self.person_id.id,
            'date': fields.Datetime.now(),
            'duration': 30.0,
            'intervention_type': 'administrative',
            'modality': 'in_person',
            'professional_id': self.responsible_id.id,
            'description': 'Reapertura del cas. Motiu pendent de documentar.',
        })

    @api.model
    def _cron_followup_alerts(self):
        threshold = fields.Date.today() - timedelta(days=30)
        today = fields.Date.today()
        cases = self.search([
            ('state', 'in', ['active', 'followup']),
            '|',
            ('followup_snooze_date', '=', False),
            ('followup_snooze_date', '<', today),
            '|',
            ('last_intervention_date', '=', False),
            ('last_intervention_date', '<', fields.Datetime.to_string(
                fields.Datetime.from_string(str(threshold))
            )),
        ])
        for case in cases:
            responsible = case.responsible_id.user_id
            if not responsible:
                continue
            case.message_post(
                body=(
                    f'<b>Avís de seguiment:</b> El cas <b>{case.name}</b> '
                    f'(<a href="/web#id={case.person_id.id}&model=acathi.person">'
                    f'{case.person_id.display_name}</a>) '
                    f'porta més de 30 dies sense intervenció registrada. '
                    f'Si no cal acció, pots silenciar els avisos des de la fitxa del cas.'
                ),
                partner_ids=[responsible.partner_id.id],
                subtype_xmlid='mail.mt_comment',
            )

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
