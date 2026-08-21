from odoo import api, fields, models


class GrantProject(models.Model):
    _name = 'grant.project'
    _description = 'Projecte social base'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Nom del projecte', required=True, tracking=True)
    area = fields.Char(string='Àrea temàtica')
    estado = fields.Selection([
        ('borrador', 'Esborrany'),
        ('activo', 'Actiu'),
        ('completado', 'Completat'),
        ('archivado', 'Arxivat'),
    ], string='Estat', default='borrador', tracking=True)
    objetivo = fields.Text(string='Objectiu general')
    descripcion = fields.Text(string='Descripció')
    actividades = fields.Text(string='Activitats principals')
    metodologia = fields.Text(string='Metodologia / avaluació')
    presupuesto = fields.Float(string='Pressupost estimat (€)', digits=(10, 2))
    duracion = fields.Char(string='Durada')

    application_ids = fields.One2many(
        comodel_name='grant.application',
        inverse_name='project_id',
        string='Expedients vinculats',
    )
    application_count = fields.Integer(
        string='Nº expedients',
        compute='_compute_application_count',
    )

    @api.depends('application_ids')
    def _compute_application_count(self):
        for rec in self:
            rec.application_count = len(rec.application_ids)

    def action_view_applications(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Expedients',
            'res_model': 'grant.application',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }
