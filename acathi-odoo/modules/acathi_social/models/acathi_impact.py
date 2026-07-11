# -*- coding: utf-8 -*-
from odoo import models, fields


class AcathiImpact(models.Model):
    _name = 'acathi.impact'
    _description = 'Indicador de Impacto ACATHI'
    _inherit = ['mail.thread']
    _order = 'year desc, period'

    name = fields.Char('Nombre del indicador', required=True)
    year = fields.Integer('Año', required=True)
    period = fields.Selection([
        ('q1', 'T1 (Enero-Marzo)'),
        ('q2', 'T2 (Abril-Junio)'),
        ('q3', 'T3 (Julio-Septiembre)'),
        ('q4', 'T4 (Octubre-Diciembre)'),
        ('annual', 'Anual'),
    ], string='Período', default='annual')
    area = fields.Selection([
        ('legal', 'Legal / Asilo'),
        ('psychosocial', 'Psicosocial'),
        ('labor', 'Empleo'),
        ('housing', 'Alojamiento'),
        ('health', 'Salud'),
        ('community', 'Comunidad'),
        ('training', 'Formación'),
        ('general', 'General'),
    ], string='Área')
    expected_value = fields.Float('Valor esperado')
    actual_value = fields.Float('Valor real')
    achievement_rate = fields.Float('% logro', compute='_compute_rate', store=True)
    notes = fields.Text('Observaciones')

    def _compute_rate(self):
        for rec in self:
            if rec.expected_value:
                rec.achievement_rate = (rec.actual_value / rec.expected_value) * 100
            else:
                rec.achievement_rate = 0.0
