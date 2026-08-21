from odoo import fields, models


class GrantPenalSchedule(models.Model):
    """Temporització per mes i centre penitenciari (SMPRAV)."""
    _name = 'grant.penal.schedule'
    _description = 'Planificació temporal per centre penitenciari (SMPRAV)'
    _order = 'month, center_id'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    month = fields.Selection(
        selection=[
            ('01', 'Gener'), ('02', 'Febrer'), ('03', 'Març'),
            ('04', 'Abril'), ('05', 'Maig'), ('06', 'Juny'),
            ('07', 'Juliol'), ('08', 'Agost'), ('09', 'Setembre'),
            ('10', 'Octubre'), ('11', 'Novembre'), ('12', 'Desembre'),
        ],
        string='Mes',
        required=True,
    )
    center_id = fields.Many2one(
        comodel_name='grant.penal.center',
        string='Centre penitenciari',
        required=True,
        ondelete='restrict',
    )
    activity_description = fields.Char(
        string='Activitat / intervenció',
        required=True,
    )
    hours = fields.Float(
        string='Hores d\'intervenció',
        digits=(6, 2),
    )
    num_participants = fields.Integer(
        string='Nre. participants (previsió)',
    )
    notes = fields.Char(string='Observacions')


class GrantDeviceContact(models.Model):
    """Contacte de referència per centre penitenciari (SMPRAV)."""
    _name = 'grant.device.contact'
    _description = 'Contacte per centre penitenciari (SMPRAV)'
    _order = 'center_id, id'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    center_id = fields.Many2one(
        comodel_name='grant.penal.center',
        string='Centre penitenciari',
        required=True,
        ondelete='restrict',
    )
    contact_name = fields.Char(string='Nom i cognoms', required=True)
    contact_role = fields.Char(
        string='Càrrec',
        help='Ex: Director/a, Cap de Tractament, Educador/a...',
    )
    contact_phone = fields.Char(string='Telèfon')
    contact_email = fields.Char(string='Correu electrònic')
