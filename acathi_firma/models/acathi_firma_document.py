# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AcathiFirmaDocument(models.Model):
    _name = 'acathi.firma.document'
    _description = 'Document per a firma digital'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Nom del document', required=True, tracking=True)
    description = fields.Text(string='Descripció / instruccions per al firmant')
    document_file = fields.Binary(string='PDF', attachment=True, required=True)
    document_filename = fields.Char(string='Nom del fitxer')
    session_ids = fields.One2many(
        'acathi.firma.session', 'document_id', string='Firmants')
    state = fields.Selection([
        ('draft', 'Esborrany'),
        ('active', 'En circulació'),
        ('completed', 'Completat'),
        ('cancelled', 'Cancel·lat'),
    ], default='draft', string='Estat', tracking=True)

    total_firmants = fields.Integer(
        string='Total firmants', compute='_compute_counts')
    signed_count = fields.Integer(
        string='Firmats', compute='_compute_counts')
    signed_master = fields.Binary(
        string='PDF final (totes les firmes)', attachment=True, readonly=True)
    signed_master_filename = fields.Char(readonly=True)

    @api.depends('session_ids.state')
    def _compute_counts(self):
        for rec in self:
            rec.total_firmants = len(rec.session_ids)
            rec.signed_count = len(
                rec.session_ids.filtered(lambda s: s.state == 'signed'))

    def action_view_sessions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sessions de firma',
            'res_model': 'acathi.firma.session',
            'view_mode': 'tree,form',
            'domain': [('document_id', '=', self.id)],
            'context': {'default_document_id': self.id},
        }

    def action_activate(self):
        self.state = 'active'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_draft(self):
        self.state = 'draft'
