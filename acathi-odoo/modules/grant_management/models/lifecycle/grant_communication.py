from odoo import fields, models


class GrantCommunicationPlan(models.Model):
    _name = 'grant.communication.plan'
    _description = 'Pla de comunicació del projecte'
    _inherit = ['mail.thread']

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    action_ids = fields.One2many(
        comodel_name='grant.comm.action',
        inverse_name='plan_id',
        string='Accions de comunicació',
    )
    notes = fields.Html(string='Notes i estratègia general')
    done_count = fields.Integer(
        string='Accions realitzades',
        compute='_compute_done_count',
    )
    total_count = fields.Integer(
        string='Total accions',
        compute='_compute_done_count',
    )

    def action_view_done(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Accions realitzades',
            'res_model': 'grant.comm.action',
            'view_mode': 'tree',
            'domain': [('plan_id', '=', self.id), ('done', '=', True)],
        }

    def _compute_done_count(self):
        for rec in self:
            rec.total_count = len(rec.action_ids)
            rec.done_count = len(rec.action_ids.filtered('done'))


class GrantCommAction(models.Model):
    _name = 'grant.comm.action'
    _description = 'Acció de comunicació'
    _order = 'date, id'

    plan_id = fields.Many2one(
        comodel_name='grant.communication.plan',
        string='Pla de comunicació',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(string='Acció', required=True)
    channel = fields.Selection(
        selection=[
            ('rrss', 'Xarxes socials'),
            ('web', 'Web / blog'),
            ('cartell', 'Cartell / fulletó'),
            ('premsa', 'Nota de premsa'),
            ('acte', 'Acte públic / presentació'),
            ('newsletter', 'Newsletter / butlletí'),
            ('other', 'Altres'),
        ],
        string='Canal',
        required=True,
        default='rrss',
    )
    date = fields.Date(string='Data prevista / realitzada')
    description = fields.Char(string='Descripció')
    done = fields.Boolean(string='Realitzada', default=False)
    evidence_notes = fields.Text(
        string='Evidències',
        help='Enllaç, descripció o referència de la documentació acreditativa',
    )
