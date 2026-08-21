from odoo import fields, models


class GrantActivity(models.Model):
    _name = 'grant.activity'
    _description = 'Activitat del pla d\'execució'
    _order = 'sequence, id'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Nom de l\'activitat', required=True)
    description_html = fields.Html(string='Descripció')
    date_start = fields.Date(string='Data inici')
    date_end = fields.Date(string='Data fi')
    responsible = fields.Char(string='Responsable')
    execution_months = fields.Char(
        string='Mesos d\'execució',
        help='Ex: Gen-Mar, Abr-Jun. COSIFE Línia B: cal especificar cada mes.',
    )
    target_group = fields.Char(string='Grup destinatari específic')


class GrantObjectiveLink(models.Model):
    """Taula OG × OE del Pla de Govern (COSIFE sec.1.3) — Fase 7"""
    _name = 'grant.objective.link'
    _description = 'Vincle objectiu general × objectiu específic (COSIFE)'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    general_objective = fields.Char(string='Objectiu general del Pla de Govern')
    specific_objective = fields.Char(string='Objectiu específic del projecte')
    justification = fields.Text(string='Justificació del vincle')
