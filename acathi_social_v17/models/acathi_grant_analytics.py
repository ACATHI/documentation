# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AcathiInterventionSUB02(models.Model):
    _inherit = 'acathi.intervention'

    grant_application_id = fields.Many2one(
        'grant.application',
        string='Subvenció',
        index=True,
        ondelete='set null',
    )


class AcathiActivitySUB02(models.Model):
    _inherit = 'acathi.activity'

    grant_application_id = fields.Many2one(
        'grant.application',
        string='Subvenció',
        index=True,
        ondelete='set null',
    )


class AcathiAidSUB02(models.Model):
    _inherit = 'acathi.aid'

    grant_application_id = fields.Many2one(
        'grant.application',
        string='Subvenció',
        index=True,
        ondelete='set null',
    )


class GrantApplicationSUB02(models.Model):
    _inherit = 'grant.application'

    intervention_ids = fields.One2many(
        'acathi.intervention', 'grant_application_id',
        string='Intervencions',
    )
    intervention_count = fields.Integer(
        compute='_compute_social_counts',
        string='Intervencions',
    )
    activity_ids = fields.One2many(
        'acathi.activity', 'grant_application_id',
        string='Activitats',
    )
    activity_count = fields.Integer(
        compute='_compute_social_counts',
        string='Activitats',
    )
    aid_ids = fields.One2many(
        'acathi.aid', 'grant_application_id',
        string='Ajudes econòmiques',
    )
    aid_count = fields.Integer(
        compute='_compute_social_counts',
        string='Ajudes',
    )
    person_count = fields.Integer(
        compute='_compute_social_counts',
        string='Persones ateses',
    )

    @api.depends('intervention_ids', 'activity_ids', 'aid_ids')
    def _compute_social_counts(self):
        for rec in self:
            rec.intervention_count = len(rec.intervention_ids)
            rec.activity_count = len(rec.activity_ids)
            rec.aid_count = len(rec.aid_ids)
            persons = rec.intervention_ids.mapped('person_id')
            persons |= rec.aid_ids.mapped('person_id')
            rec.person_count = len(persons)

    def action_view_interventions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Intervencions',
            'res_model': 'acathi.intervention',
            'view_mode': 'tree,form',
            'domain': [('grant_application_id', '=', self.id)],
            'context': {'default_grant_application_id': self.id},
        }

    def action_view_activities(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Activitats',
            'res_model': 'acathi.activity',
            'view_mode': 'tree,form',
            'domain': [('grant_application_id', '=', self.id)],
            'context': {'default_grant_application_id': self.id},
        }

    def action_view_grant_aids(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ajudes econòmiques',
            'res_model': 'acathi.aid',
            'view_mode': 'tree,form',
            'domain': [('grant_application_id', '=', self.id)],
            'context': {'default_grant_application_id': self.id},
        }

    def action_view_grant_persons(self):
        self.ensure_one()
        persons = self.intervention_ids.mapped('person_id')
        persons |= self.aid_ids.mapped('person_id')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Persones ateses',
            'res_model': 'acathi.person',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', persons.ids)],
        }


class GrantIndicatorSUB02(models.Model):
    _inherit = 'grant.indicator'

    social_source = fields.Selection([
        ('manual', 'Manual'),
        ('interventions', 'Intervencions'),
        ('activities', 'Activitats'),
        ('aids', 'Ajudes econòmiques'),
        ('persons', 'Persones ateses (úniques)'),
    ], string='Font automàtica', default='manual')

    def action_compute_from_social(self):
        for rec in self:
            if rec.social_source == 'manual' or not rec.application_id:
                continue
            app = rec.application_id
            if rec.social_source == 'interventions':
                rec.achieved_value_num = len(app.intervention_ids)
            elif rec.social_source == 'activities':
                rec.achieved_value_num = len(app.activity_ids)
            elif rec.social_source == 'aids':
                rec.achieved_value_num = len(app.aid_ids)
            elif rec.social_source == 'persons':
                persons = app.intervention_ids.mapped('person_id')
                persons |= app.aid_ids.mapped('person_id')
                rec.achieved_value_num = len(persons)
