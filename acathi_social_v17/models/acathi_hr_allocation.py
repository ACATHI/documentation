# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api


class GrantHrAllocation(models.Model):
    _name = 'grant.hr.allocation'
    _description = 'Imputació mensual d\'hores de personal a subvenció'
    _rec_name = 'display_name'
    _order = 'year desc, month_num desc, employee_id'

    display_name = fields.Char(compute='_compute_display_name', store=True)

    employee_id = fields.Many2one(
        'hr.employee', string='Empleat/da', required=True, index=True,
    )
    grant_application_id = fields.Many2one(
        'grant.application', string='Subvenció', required=True,
        index=True, ondelete='cascade',
    )
    year = fields.Integer(
        string='Any', required=True,
        default=lambda self: fields.Date.today().year,
    )
    month_num = fields.Selection([
        ('1', 'Gener'), ('2', 'Febrer'), ('3', 'Març'), ('4', 'Abril'),
        ('5', 'Maig'), ('6', 'Juny'), ('7', 'Juliol'), ('8', 'Agost'),
        ('9', 'Setembre'), ('10', 'Octubre'), ('11', 'Novembre'), ('12', 'Desembre'),
    ], string='Mes', required=True,
        default=lambda self: str(fields.Date.today().month),
    )
    percentage = fields.Float(
        string='% Dedicació', required=True, default=100.0,
        help='Percentatge de la jornada mensual dedicat a aquesta subvenció (0–100)',
    )
    attendance_hours = fields.Float(
        string='Hores treballades al mes',
        compute='_compute_attendance', store=True,
        help='Hores totals registrades a hr.attendance per aquest empleat i mes',
    )
    imputed_hours = fields.Float(
        string='Hores imputades',
        compute='_compute_imputed', store=True,
        digits=(10, 2),
    )
    hourly_cost = fields.Float(
        string='Cost/hora (€)', required=True, digits=(10, 4),
        help='Cost brut total per hora (salari + SS empresa)',
    )
    total_cost = fields.Float(
        string='Cost imputat (€)',
        compute='_compute_total_cost', store=True,
        digits=(10, 2),
    )
    notes = fields.Text(string='Notes')

    @api.depends('employee_id', 'year', 'month_num')
    def _compute_display_name(self):
        months = dict(self._fields['month_num'].selection)
        for rec in self:
            emp = rec.employee_id.name or '—'
            m = months.get(rec.month_num, '—')
            rec.display_name = f'{emp} — {m} {rec.year or ""}'

    @api.depends('employee_id', 'year', 'month_num')
    def _compute_attendance(self):
        Attendance = self.env['hr.attendance']
        for rec in self:
            if not rec.employee_id or not rec.year or not rec.month_num:
                rec.attendance_hours = 0.0
                continue
            m = int(rec.month_num)
            y = rec.year
            d_from = fields.Datetime.to_string(datetime(y, m, 1))
            if m == 12:
                d_to = fields.Datetime.to_string(datetime(y + 1, 1, 1))
            else:
                d_to = fields.Datetime.to_string(datetime(y, m + 1, 1))
            att = Attendance.search([
                ('employee_id', '=', rec.employee_id.id),
                ('check_in', '>=', d_from),
                ('check_in', '<', d_to),
            ])
            rec.attendance_hours = sum(att.mapped('worked_hours'))

    @api.depends('attendance_hours', 'percentage')
    def _compute_imputed(self):
        for rec in self:
            rec.imputed_hours = rec.attendance_hours * (rec.percentage / 100.0)

    @api.depends('imputed_hours', 'hourly_cost')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.imputed_hours * rec.hourly_cost

    def action_recompute_attendance(self):
        self._compute_attendance()
        self._compute_imputed()
        self._compute_total_cost()

    def action_suggest_percentage(self):
        """Suggereix % de dedicació basat en minuts d'intervencions registrades al mes."""
        self.ensure_one()
        if not self.employee_id or not self.year or not self.month_num:
            return {'type': 'ir.actions.client', 'tag': 'display_notification',
                    'params': {'title': 'Dades incompletes',
                               'message': 'Cal empleat, any i mes per calcular el suggeriment.',
                               'type': 'warning'}}

        m = int(self.month_num)
        y = self.year
        d_from = datetime(y, m, 1).date()
        d_to = datetime(y + 1, 1, 1).date() if m == 12 else datetime(y, m + 1, 1).date()

        Intervention = self.env['acathi.intervention']
        all_interventions = Intervention.search([
            ('professional_id', '=', self.employee_id.id),
            ('date', '>=', fields.Datetime.to_string(datetime(y, m, 1))),
            ('date', '<', fields.Datetime.to_string(
                datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)
            )),
        ])

        total_minutes = sum(all_interventions.mapped('duration')) or 0
        if total_minutes == 0:
            return {'type': 'ir.actions.client', 'tag': 'display_notification',
                    'params': {'title': 'Sense dades',
                               'message': 'No hi ha intervencions registrades per aquest professional i mes.',
                               'type': 'warning'}}

        grant_minutes = sum(
            all_interventions.filtered(
                lambda i: i.grant_application_id == self.grant_application_id
            ).mapped('duration')
        )
        suggested = round((grant_minutes / total_minutes) * 100, 1)
        months = dict(self._fields['month_num'].selection)
        month_name = months.get(self.month_num, '')
        note_line = (
            f'Suggeriment {month_name} {y}: {grant_minutes:.0f} min de {total_minutes:.0f} min '
            f'totals → {suggested}%'
        )
        self.percentage = suggested
        self.notes = (self.notes + '\n' + note_line) if self.notes else note_line
        return {'type': 'ir.actions.client', 'tag': 'display_notification',
                'params': {'title': 'Suggeriment aplicat',
                           'message': f'{suggested}% ({grant_minutes:.0f} min de {total_minutes:.0f})',
                           'type': 'success'}}
