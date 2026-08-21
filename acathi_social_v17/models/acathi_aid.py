# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AcathiAid(models.Model):
    _name = 'acathi.aid'
    _description = 'Ajuda econòmica'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_request desc'

    person_id = fields.Many2one('acathi.person', string='Persona', required=True, index=True, ondelete='restrict')
    case_id = fields.Many2one('acathi.case', string='Cas', domain="[('person_id','=',person_id)]")
    professional_id = fields.Many2one('hr.employee', string='Professional responsable')

    aid_type = fields.Selection([
        ('transport', 'Transport'),
        ('food', 'Alimentació'),
        ('housing', 'Allotjament / habitatge'),
        ('medical', 'Despeses mèdiques'),
        ('legal', 'Taxes / despeses legals'),
        ('documentation', 'Documentació'),
        ('basic_needs', 'Necessitats bàsiques'),
        ('emergency', 'Emergència'),
        ('other', 'Altres'),
    ], string="Tipus d'ajuda", required=True)
    description = fields.Char(string='Descripció', required=True)
    amount = fields.Float(string='Import (€)', digits=(10, 2))
    payment_method = fields.Selection([
        ('cash', 'Efectiu'),
        ('transfer', 'Transferència'),
        ('voucher', 'Val / bo'),
        ('in_kind', 'En espècie'),
    ], string='Forma de pagament', default='cash')

    date_request = fields.Date(string='Data sol·licitud', default=fields.Date.today)
    date_approved = fields.Date(string='Data aprovació')
    date_paid = fields.Date(string='Data pagament')

    state = fields.Selection([
        ('draft', 'Esborrany'),
        ('requested', 'Sol·licitada'),
        ('approved', 'Aprovada'),
        ('paid', 'Pagada'),
        ('rejected', 'Denegada'),
        ('cancelled', 'Cancel·lada'),
    ], string='Estat', default='draft', tracking=True)

    funder = fields.Char(string='Font de finançament')
    notes = fields.Text(string='Observacions')

    def action_request(self):
        self.write({'state': 'requested'})

    def action_approve(self):
        self.write({'state': 'approved', 'date_approved': fields.Date.today()})

    def action_pay(self):
        self.write({'state': 'paid', 'date_paid': fields.Date.today()})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})


class AcathiPersonSOC07(models.Model):
    _inherit = 'acathi.person'

    aid_ids = fields.One2many('acathi.aid', 'person_id', string='Ajudes econòmiques')
    aid_count = fields.Integer(compute='_compute_aid_count', string='Ajudes')

    @api.depends('aid_ids')
    def _compute_aid_count(self):
        for rec in self:
            rec.aid_count = len(rec.aid_ids)

    def action_view_aids(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ajudes econòmiques',
            'res_model': 'acathi.aid',
            'view_mode': 'tree,form',
            'domain': [('person_id', '=', self.id)],
            'context': {'default_person_id': self.id},
        }


class AcathiCaseSOC07(models.Model):
    _inherit = 'acathi.case'

    aid_ids = fields.One2many('acathi.aid', 'case_id', string='Ajudes econòmiques')
    aid_count = fields.Integer(compute='_compute_aid_count', string='Ajudes')

    @api.depends('aid_ids')
    def _compute_aid_count(self):
        for rec in self:
            rec.aid_count = len(rec.aid_ids)

    def action_view_case_aids(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ajudes econòmiques',
            'res_model': 'acathi.aid',
            'view_mode': 'tree,form',
            'domain': [('case_id', '=', self.id)],
            'context': {'default_case_id': self.id},
        }
