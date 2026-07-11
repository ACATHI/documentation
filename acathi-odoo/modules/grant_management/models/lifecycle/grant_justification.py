from odoo import api, fields, models, _


class GrantJustification(models.Model):
    _name = 'grant.justification'
    _description = 'Memòria narrativa de justificació'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
        tracking=True,
    )
    name = fields.Char(
        string='Referència',
        compute='_compute_name',
        store=True,
    )
    justification_template = fields.Selection(
        related='application_id.call_id.config_id.justification_template',
        string='Plantilla',
    )
    state = fields.Selection(
        selection=[
            ('esborrany', 'Esborrany'),
            ('presentada', 'Presentada'),
            ('tancada', 'Tancada'),
        ],
        string='Estat',
        default='esborrany',
        required=True,
        tracking=True,
    )
    date_presented = fields.Date(string='Data de presentació', tracking=True)

    # ── MEMÒRIA D'EXECUCIÓ ────────────────────────────────────────────────────

    activities_report_html = fields.Html(
        string='Resum d\'activitats executades',
        help='Descripció de com s\'han dut a terme les activitats planificades',
    )
    deviations_html = fields.Html(
        string='Desviacions i incidències',
        help='Activitats no executades o modificades respecte el pla inicial',
    )
    target_group_actual_html = fields.Html(
        string='Grup destinatari real',
        help='Qui ha participat finalment al projecte',
    )
    num_participants_actual = fields.Integer(
        string='Participants reals',
    )

    # ── AVALUACIÓ ─────────────────────────────────────────────────────────────

    evaluation_actual_html = fields.Html(
        string='Avaluació dels resultats',
        help='Grau d\'assoliment dels objectius i indicadors',
    )
    lessons_learned_html = fields.Html(string='Aprenentatges i millores')

    # ── PERSPECTIVA DE GÈNERE ────────────────────────────────────────────────

    gender_actual_html = fields.Html(
        string='Perspectiva de gènere — execució',
        help='Com s\'ha aplicat la perspectiva de gènere durant l\'execució',
    )

    # ── COMUNICACIÓ ───────────────────────────────────────────────────────────

    communication_evidence_html = fields.Html(
        string='Evidències de comunicació',
        help='Captures de RRSS, webs, cartells, notes de premsa...',
    )

    # ── CLÀUSULES SOCIALS ─────────────────────────────────────────────────────

    social_clauses_report_html = fields.Html(
        string='Compliment clàusules socials',
    )

    # ── NOTES ─────────────────────────────────────────────────────────────────

    internal_notes = fields.Text(
        string='Notes internes',
        help='Notes de l\'equip, no apareixen als informes',
    )

    @api.depends('application_id.name')
    def _compute_name(self):
        for rec in self:
            rec.name = _('Memòria — %s') % (rec.application_id.name or '')

    def action_submit(self):
        self.write({
            'state': 'presentada',
            'date_presented': fields.Date.today(),
        })

    def action_close(self):
        self.write({'state': 'tancada'})

    def action_reset_draft(self):
        self.write({'state': 'esborrany'})


class GrantJustifUser(models.Model):
    """Beneficiaris per franja d'edat a la justificació (COSIFE + Generalitat DS) — Fase 7"""
    _name = 'grant.justif.user'
    _description = 'Beneficiaris per franja d\'edat (justificació)'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    age_range = fields.Selection(
        selection=[
            ('0_17', 'Menors de 18 anys'),
            ('18_29', '18-29 anys'),
            ('30_44', '30-44 anys'),
            ('45_64', '45-64 anys'),
            ('65_plus', '65 anys i més'),
        ],
        string='Franja d\'edat',
        required=True,
    )
    num_women = fields.Integer(string='Dones')
    num_men = fields.Integer(string='Homes')
    num_other = fields.Integer(string='Altres / No binari')
    total = fields.Integer(
        string='Total',
        compute='_compute_total',
        store=True,
    )

    @api.depends('num_women', 'num_men', 'num_other')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.num_women + rec.num_men + rec.num_other
