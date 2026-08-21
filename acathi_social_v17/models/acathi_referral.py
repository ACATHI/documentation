# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AcathiAllyReferralSOC06(models.Model):
    _name = 'acathi.ally.referral'
    _inherit = ['acathi.ally.referral', 'mail.thread', 'mail.activity.mixin']

    state = fields.Selection(tracking=True)
    follow_up_date = fields.Date(string='Data seguiment')
    notes = fields.Text(string='Observacions internes')


class AcathiPersonSOC06(models.Model):
    _inherit = 'acathi.person'

    referral_ids = fields.One2many('acathi.ally.referral', 'person_id', string='Derivacions')
    referral_count = fields.Integer(compute='_compute_referral_count', string='Derivacions')

    @api.depends('referral_ids')
    def _compute_referral_count(self):
        for rec in self:
            rec.referral_count = len(rec.referral_ids)

    def action_view_person_referrals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Derivacions',
            'res_model': 'acathi.ally.referral',
            'view_mode': 'tree,form',
            'domain': [('person_id', '=', self.id)],
            'context': {'default_person_id': self.id},
        }


class AcathiCaseSOC06(models.Model):
    _inherit = 'acathi.case'

    referral_ids = fields.One2many('acathi.ally.referral', 'case_id', string='Derivacions')
    referral_count = fields.Integer(compute='_compute_referral_count', string='Derivacions')

    @api.depends('referral_ids')
    def _compute_referral_count(self):
        for rec in self:
            rec.referral_count = len(rec.referral_ids)

    def action_view_case_referrals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Derivacions',
            'res_model': 'acathi.ally.referral',
            'view_mode': 'tree,form',
            'domain': [('case_id', '=', self.id)],
            'context': {'default_case_id': self.id},
        }
