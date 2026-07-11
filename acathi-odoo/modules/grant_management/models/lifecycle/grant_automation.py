from datetime import timedelta

from odoo import api, fields, models, _


class GrantApplicationDeadlines(models.Model):
    """Afegeix camps de termini i lògica de cron a grant.application."""
    _inherit = 'grant.application'

    deadline_submission = fields.Date(
        string='Termini de presentació',
        help='Data límit oficial per enviar la sol·licitud al finançador',
        tracking=True,
    )
    deadline_justification = fields.Date(
        string='Termini de justificació',
        help='Data límit oficial per enviar la memòria de justificació',
        tracking=True,
    )

    @api.model
    def _cron_check_deadlines(self):
        """Comprova terminis i publica avisos al chatter quan queden 30/14/7 dies."""
        today = fields.Date.today()
        checks = [
            {
                'field': 'deadline_submission',
                'states': ['esborrany', 'presentada'],
                'label': _('presentació de la sol·licitud'),
            },
            {
                'field': 'deadline_justification',
                'states': ['en_execucio'],
                'label': _('justificació'),
            },
        ]
        for days in [30, 14, 7]:
            target = today + timedelta(days=days)
            for check in checks:
                apps = self.search([
                    ('state', 'in', check['states']),
                    (check['field'], '=', target),
                ])
                for app in apps:
                    app.message_post(
                        body=_(
                            '<b>Avís de termini:</b> El termini de <b>%(label)s</b> '
                            "és d'aquí a <b>%(days)d dies</b> (%(date)s)."
                        ) % {
                            'label': check['label'],
                            'days': days,
                            'date': target.strftime('%d/%m/%Y'),
                        },
                        message_type='comment',
                        subtype_xmlid='mail.mt_note',
                    )


class GrantRequirementNotify(models.Model):
    """Notifica al chatter de l'expedient quan es crea un requeriment pendent."""
    _inherit = 'grant.requirement'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for req in records:
            if req.state == 'pendent' and req.application_id:
                req.application_id.message_post(
                    body=_(
                        '<b>Nou requeriment:</b> %(concept)s'
                        '<br/>Data límit de resposta: %(deadline)s'
                    ) % {
                        'concept': req.concept,
                        'deadline': (
                            req.date_response.strftime('%d/%m/%Y')
                            if req.date_response else '—'
                        ),
                    },
                    message_type='comment',
                    subtype_xmlid='mail.mt_note',
                )
        return records
