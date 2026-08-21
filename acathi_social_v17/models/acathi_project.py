# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AcathiProject(models.Model):
    _name = 'acathi.project'
    _description = 'Proyecto ACATHI'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char('Nombre del proyecto', required=True)
    active = fields.Boolean('Activo', default=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Activo'),
        ('closed', 'Cerrado'),
    ], string='Estado', default='draft', tracking=True)
    date_start = fields.Date('Fecha inicio')
    date_end = fields.Date('Fecha fin')
    responsible_id = fields.Many2one('hr.employee', string='Responsable')
    description = fields.Text('Descripción')
    funder = fields.Char('Financiador')
    budget = fields.Float('Presupuesto (€)')
    notes = fields.Text('Observaciones')
