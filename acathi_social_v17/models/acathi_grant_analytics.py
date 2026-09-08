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

    # Nom soc_* per no xocar amb grant_activity_ids (grant.activity) de grant_management
    soc_intervention_ids = fields.One2many(
        'acathi.intervention', 'grant_application_id',
        string='Intervencions socials',
    )
    soc_intervention_count = fields.Integer(
        compute='_compute_social_counts',
        string='Intervencions',
    )
    soc_activity_ids = fields.One2many(
        'acathi.activity', 'grant_application_id',
        string='Activitats socials',
    )
    soc_activity_count = fields.Integer(
        compute='_compute_social_counts',
        string='Activitats',
    )
    soc_aid_ids = fields.One2many(
        'acathi.aid', 'grant_application_id',
        string='Ajudes econòmiques',
    )
    soc_aid_count = fields.Integer(
        compute='_compute_social_counts',
        string='Ajudes',
    )
    soc_person_count = fields.Integer(
        compute='_compute_social_counts',
        string='Persones ateses',
    )

    @api.depends('soc_intervention_ids', 'soc_activity_ids', 'soc_aid_ids')
    def _compute_social_counts(self):
        for rec in self:
            rec.soc_intervention_count = len(rec.soc_intervention_ids)
            rec.soc_activity_count = len(rec.soc_activity_ids)
            rec.soc_aid_count = len(rec.soc_aid_ids)
            persons = rec.soc_intervention_ids.mapped('person_id')
            persons |= rec.soc_aid_ids.mapped('person_id')
            rec.soc_person_count = len(persons)

    def action_view_soc_interventions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Intervencions',
            'res_model': 'acathi.intervention',
            'view_mode': 'tree,form',
            'domain': [('grant_application_id', '=', self.id)],
            'context': {'default_grant_application_id': self.id},
        }

    def action_view_soc_activities(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Activitats',
            'res_model': 'acathi.activity',
            'view_mode': 'tree,form',
            'domain': [('grant_application_id', '=', self.id)],
            'context': {'default_grant_application_id': self.id},
        }

    def action_view_soc_aids(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ajudes econòmiques',
            'res_model': 'acathi.aid',
            'view_mode': 'tree,form',
            'domain': [('grant_application_id', '=', self.id)],
            'context': {'default_grant_application_id': self.id},
        }

    def action_view_soc_persons(self):
        self.ensure_one()
        persons = self.soc_intervention_ids.mapped('person_id')
        persons |= self.soc_aid_ids.mapped('person_id')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Persones ateses',
            'res_model': 'acathi.person',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', persons.ids)],
        }


class GrantApplicationHR(models.Model):
    _inherit = 'grant.application'

    soc_hr_allocation_ids = fields.One2many(
        'grant.hr.allocation', 'grant_application_id',
        string='Imputació de personal',
    )
    soc_hr_allocation_count = fields.Integer(
        compute='_compute_soc_hr_counts', string='Registres personal',
    )
    soc_hr_total_hours = fields.Float(
        compute='_compute_soc_hr_counts', string='Hores imputades',
        digits=(10, 1),
    )
    soc_hr_total_cost = fields.Float(
        compute='_compute_soc_hr_counts', string='Cost personal (€)',
        digits=(10, 2),
    )

    @api.depends(
        'soc_hr_allocation_ids.imputed_hours',
        'soc_hr_allocation_ids.total_cost',
    )
    def _compute_soc_hr_counts(self):
        for rec in self:
            allocs = rec.soc_hr_allocation_ids
            rec.soc_hr_allocation_count = len(allocs)
            rec.soc_hr_total_hours = sum(allocs.mapped('imputed_hours'))
            rec.soc_hr_total_cost = sum(allocs.mapped('total_cost'))

    def action_view_soc_hr_allocations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Imputació de personal',
            'res_model': 'grant.hr.allocation',
            'view_mode': 'tree,form',
            'domain': [('grant_application_id', '=', self.id)],
            'context': {'default_grant_application_id': self.id},
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
                rec.achieved_value_num = len(app.soc_intervention_ids)
            elif rec.social_source == 'activities':
                rec.achieved_value_num = len(app.soc_activity_ids)
            elif rec.social_source == 'aids':
                rec.achieved_value_num = len(app.soc_aid_ids)
            elif rec.social_source == 'persons':
                persons = app.soc_intervention_ids.mapped('person_id')
                persons |= app.soc_aid_ids.mapped('person_id')
                rec.achieved_value_num = len(persons)
