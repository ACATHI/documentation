from odoo import fields, models


class GrantPenalCenter(models.Model):
    _name = 'grant.penal.center'
    _description = 'Centre penitenciari de Catalunya'
    _order = 'name'

    name = fields.Char(string='Nom del centre', required=True)
    code = fields.Char(string='Codi', required=True)
    province = fields.Char(string='Província')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'El codi de centre penitenciari ha de ser únic.'),
    ]
