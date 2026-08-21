from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class GrantApplication(models.Model):
    _name = 'grant.application'
    _description = 'Expedient de subvenció'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    # ── IDENTIFICACIÓ ────────────────────────────────────────────────────────

    name = fields.Char(
        string='Referència',
        required=True,
        copy=False,
        tracking=True,
        default=lambda self: _('Nou expedient'),
    )
    project_id = fields.Many2one(
        comodel_name='grant.project',
        string='Projecte base',
        ondelete='set null',
        tracking=True,
    )
    call_id = fields.Many2one(
        comodel_name='grant.call',
        string='Convocatòria',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    funder_id = fields.Many2one(
        comodel_name='grant.funder',
        related='call_id.funder_id',
        string='Finançador',
        store=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Entitat sol·licitant',
        required=True,
        ondelete='restrict',
    )
    nif = fields.Char(
        string='NIF / CIF',
        compute='_compute_nif',
        store=True,
        readonly=False,
    )
    state = fields.Selection(
        selection=[
            ('esborrany', 'Esborrany'),
            ('presentada', 'Sol·licitud presentada'),
            ('concedida', 'Concedida'),
            ('en_reformulacio', 'En reformulació'),
            ('denegada', 'Denegada'),
            ('en_execucio', 'En execució'),
            ('justificada', 'Justificada'),
            ('tancada', 'Tancada'),
        ],
        string='Estat',
        default='esborrany',
        required=True,
        tracking=True,
    )
    date_start = fields.Date(string='Data inici del projecte')
    date_end = fields.Date(string='Data fi del projecte')
    date_submitted = fields.Date(string='Data de presentació', tracking=True)

    # ── CAMPS DE VISIBILITAT (mirrored des de call.config) ───────────────────
    # Necessaris perquè la vista XML pugui usar-los en invisible=

    show_revaluation_plan = fields.Boolean(
        related='call_id.config_id.show_revaluation_plan', store=False)
    show_penal_fields = fields.Boolean(
        related='call_id.config_id.show_penal_fields', store=False)
    show_counting_units = fields.Boolean(
        related='call_id.config_id.show_counting_units', store=False)
    show_volunteer_table = fields.Boolean(
        related='call_id.config_id.show_volunteer_table', store=False)
    show_device_table = fields.Boolean(
        related='call_id.config_id.show_device_table', store=False)
    show_sai_network = fields.Boolean(
        related='call_id.config_id.show_sai_network', store=False)
    show_law_19_2020 = fields.Boolean(
        related='call_id.config_id.show_law_19_2020', store=False)
    show_gender_table = fields.Boolean(
        related='call_id.config_id.show_gender_table', store=False)
    show_objectives_table = fields.Boolean(
        related='call_id.config_id.show_objectives_table', store=False)
    show_ambit_selector = fields.Boolean(
        related='call_id.config_id.show_ambit_selector', store=False)
    show_social_clauses = fields.Boolean(
        related='call_id.config_id.show_social_clauses', store=False)
    show_catalan_policy = fields.Boolean(
        related='call_id.config_id.show_catalan_policy', store=False)
    show_ecosocial = fields.Boolean(
        related='call_id.config_id.show_ecosocial', store=False)
    show_intercultural = fields.Boolean(
        related='call_id.config_id.show_intercultural', store=False)
    is_pluriannual = fields.Boolean(related='call_id.is_pluriannual', store=False)

    # ── CONTACTES ────────────────────────────────────────────────────────────

    contact_person = fields.Char(string='Persona de contacte')
    contact_phone = fields.Char(string='Telèfon de contacte')
    contact_email = fields.Char(string='Correu de contacte')
    notification_email = fields.Char(
        string='Correu de notificacions',
        help='Adreça on enviar avisos de terminis i requeriments',
    )

    # ── ENTITAT ──────────────────────────────────────────────────────────────

    entity_years_activity = fields.Integer(
        string='Anys d\'activitat de l\'entitat',
    )
    entity_feminist_trajectory_html = fields.Html(
        string='Trajectòria feminista de l\'entitat',
    )
    federation_member = fields.Boolean(
        string='Membre d\'una federació o xarxa',
        default=False,
    )
    federation_names = fields.Char(string='Nom(s) de la(les) federació(ns)')

    # ── ÀMBIT I PROGRAMA ─────────────────────────────────────────────────────

    call_line = fields.Char(string='Línia de la convocatòria')
    call_subline = fields.Char(string='Sublínia')
    program = fields.Char(string='Programa')
    ambit = fields.Char(string='Àmbit territorial')
    linia_diputacio = fields.Char(
        string='Línia Diputació (àmbit 1-8)',
        help='Camp específic per a Diputació de Barcelona',
    )

    # ── CONTINGUT NARRATIU ───────────────────────────────────────────────────

    background_html = fields.Html(
        string='Context i justificació de la necessitat social',
        help='Descripció del context, diagnosi i necessitat que motiva el projecte',
    )
    description_html = fields.Html(string='Descripció del projecte')
    target_group_html = fields.Html(string='Grup destinatari')
    general_objective = fields.Text(string='Objectiu general')
    specific_objectives_html = fields.Html(string='Objectius específics')
    methodology_html = fields.Html(string='Metodologia')

    # ── PERSPECTIVES TRANSVERSALS ─────────────────────────────────────────────

    gender_perspective_html = fields.Html(string='Perspectiva de gènere')
    ecosocial_perspective_html = fields.Html(string='Perspectiva ecosocial')
    intercultural_perspective_html = fields.Html(string='Perspectiva intercultural')
    lgbti_inequalities_html = fields.Html(string='Desigualtats LGBTI')

    # ── PLA D'EXECUCIÓ ────────────────────────────────────────────────────────

    grant_activity_ids = fields.One2many(
        comodel_name='grant.activity',
        inverse_name='application_id',
        string='Activitats',
    )
    indicator_ids = fields.One2many(
        comodel_name='grant.indicator',
        inverse_name='application_id',
        string='Indicadors',
    )

    # ── UNITATS DE RECOMPTE (Generalitat DS) ──────────────────────────────────

    counting_unit = fields.Char(
        string='Unitat de recompte',
        help='Ex: persones ateses, sessions realitzades',
    )
    counting_unit_2025 = fields.Float(string='Unitats 2025', digits=(10, 0))
    counting_unit_2026 = fields.Float(string='Unitats 2026', digits=(10, 0))

    # ── BENEFICIARIS ──────────────────────────────────────────────────────────

    num_participants = fields.Integer(
        string='Nombre de participants / beneficiaris',
    )

    # ── PRESSUPOST ────────────────────────────────────────────────────────────

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
        readonly=True,
    )
    budget_expense_ids = fields.One2many(
        comodel_name='grant.budget.expense',
        inverse_name='application_id',
        string='Despeses',
    )
    budget_income_ids = fields.One2many(
        comodel_name='grant.budget.income',
        inverse_name='application_id',
        string='Ingressos',
    )
    total_expenses = fields.Monetary(
        string='Total despeses',
        compute='_compute_budget_totals',
        store=True,
        currency_field='currency_id',
    )
    total_income = fields.Monetary(
        string='Total ingressos',
        compute='_compute_budget_totals',
        store=True,
        currency_field='currency_id',
    )
    balance = fields.Monetary(
        string='Balanç (ingressos − despeses)',
        compute='_compute_budget_totals',
        store=True,
        currency_field='currency_id',
    )
    amount_requested = fields.Monetary(
        string='Import sol·licitat',
        tracking=True,
        currency_field='currency_id',
        help='Import demanat al finançador. Ha de respectar el % màxim subvencionable.',
    )
    amount_granted = fields.Monetary(
        string='Import concedit',
        tracking=True,
        currency_field='currency_id',
    )
    amount_reformulated = fields.Monetary(
        string='Import reformulat',
        tracking=True,
        currency_field='currency_id',
    )
    amount_justified = fields.Monetary(
        string='Import justificat',
        tracking=True,
        currency_field='currency_id',
    )
    grant_pct = fields.Float(
        string='% subvenció / despeses',
        compute='_compute_grant_pct',
        store=True,
        digits=(5, 2),
        help='Import sol·licitat com a % sobre el total de despeses del projecte',
    )

    # ── COMUNICACIÓ ───────────────────────────────────────────────────────────

    communication_plan_html = fields.Html(string='Pla de comunicació')
    communication_products = fields.Char(
        string='Productes de comunicació',
        help='Materials, publicacions, cartells, RRSS, etc.',
    )
    communication_message = fields.Text(
        string='Missatge comunicatiu del projecte',
    )

    # ── AVALUACIÓ ─────────────────────────────────────────────────────────────

    evaluation_plan = fields.Text(string='Pla d\'avaluació')
    quality_system_html = fields.Html(string='Sistema de qualitat')

    # ── PLA DE REVALORACIÓ (Ajuntament BCN sec.14) ────────────────────────────

    revaluation_plan_html = fields.Html(string='Pla de Revaloració')

    # ── CLÀUSULES SOCIALS (COSIFE + SMPRAV) ───────────────────────────────────

    reconciliation_measures_html = fields.Html(string='Mesures de conciliació')
    vulnerable_staff_count = fields.Integer(string='Personal en situació de vulnerabilitat')
    harassment_protocol_html = fields.Html(string='Protocol d\'assetjament')
    permanent_staff_pct = fields.Float(
        string='% personal indefinit',
        digits=(5, 2),
    )

    # ── LLEI 19/2020 (COSIFE Línia E) ─────────────────────────────────────────

    law_19_2020_link_html = fields.Html(string='Vinculació amb la Llei 19/2020')
    equality_plan_date = fields.Date(string='Data aprovació pla d\'igualtat')
    discrimination_axes_count = fields.Integer(string='Eixos de discriminació abordats')
    positive_actions_html = fields.Html(string='Accions positives')

    # ── SAI LGBTI (COSIFE Línia C) ────────────────────────────────────────────

    homophobia_prevention_html = fields.Html(string='Prevenció de l\'homofòbia')
    adult_training_html = fields.Html(string='Formació a professionals adults')

    # ── POLÍTICA LINGÜÍSTICA (COSIFE sec.5) ───────────────────────────────────

    catalan_policy_html = fields.Html(
        string='Política d\'ús del català',
        help='COSIFE sec.5: descripció de la política lingüística de l\'entitat',
    )

    # ── CONTEXT PENITENCIARI (SMPRAV) ─────────────────────────────────────────

    penal_medium = fields.Selection(
        selection=[
            ('obert', 'Medi obert'),
            ('tancat', 'Medi tancat'),
            ('tots', 'Tots dos'),
        ],
        string='Medi penitenciari',
    )
    penal_duration = fields.Integer(string='Durada en mesos')
    contribution_type = fields.Char(string='Tipus de contribució')
    person_centered_html = fields.Html(string='Enfocament centrat en la persona')
    num_internal_beneficiaries = fields.Integer(string='Beneficiaris interns (persones privades de llibertat)')
    hours_direct_intervention = fields.Float(
        string='Hores d\'intervenció directa',
        digits=(10, 2),
    )

    # ── VIABILITAT ECONÒMICA ──────────────────────────────────────────────────

    own_funding_pct = fields.Float(
        string='% finançament propi',
        digits=(5, 2),
    )
    project_budget_pct_entity = fields.Float(
        string='% pressupost projecte / pressupost entitat',
        digits=(5, 2),
    )
    cofunding_ids = fields.One2many(
        comodel_name='grant.cofunding',
        inverse_name='application_id',
        string='Cofinançament',
    )
    collaborator_ids = fields.One2many(
        comodel_name='grant.collaborator',
        inverse_name='application_id',
        string='Entitats col·laboradores',
    )

    # ── GENERALITAT DS ────────────────────────────────────────────────────────

    staff_ids = fields.One2many(
        comodel_name='grant.staff',
        inverse_name='application_id',
        string='Personal del projecte',
    )
    device_ids = fields.One2many(
        comodel_name='grant.device',
        inverse_name='application_id',
        string='Dispositius / serveis',
    )
    line_ids = fields.One2many(
        comodel_name='grant.line',
        inverse_name='application_id',
        string='Línies de la convocatòria',
    )
    historical_indicator_ids = fields.One2many(
        comodel_name='grant.historical.indicator',
        inverse_name='application_id',
        string='Indicadors històrics (4 anys)',
    )
    justif_user_ids = fields.One2many(
        comodel_name='grant.justif.user',
        inverse_name='application_id',
        string='Beneficiaris per franja d\'edat',
    )

    # ── DIPUTACIÓ BCN ─────────────────────────────────────────────────────────

    specific_aspect_ids = fields.One2many(
        comodel_name='grant.specific.aspect',
        inverse_name='application_id',
        string='Aspectes específics (DIBA)',
    )

    # ── COSIFE ────────────────────────────────────────────────────────────────

    objective_link_ids = fields.One2many(
        comodel_name='grant.objective.link',
        inverse_name='application_id',
        string='Vincles OG × OE Pla de Govern',
    )
    activity_gender_ids = fields.One2many(
        comodel_name='grant.activity.gender',
        inverse_name='application_id',
        string='Activitats amb perspectiva de gènere',
    )
    sai_action_ids = fields.One2many(
        comodel_name='grant.sai.action',
        inverse_name='application_id',
        string='Accions Xarxa SAI LGBTI',
    )

    # ── SMPRAV ────────────────────────────────────────────────────────────────

    penal_center_ids = fields.Many2many(
        comodel_name='grant.penal.center',
        string='Centres penitenciaris on s\'actua',
    )
    penal_schedule_ids = fields.One2many(
        comodel_name='grant.penal.schedule',
        inverse_name='application_id',
        string='Planificació per mes i centre',
    )
    device_contact_ids = fields.One2many(
        comodel_name='grant.device.contact',
        inverse_name='application_id',
        string='Contactes per centre penitenciari',
    )
    entity_report_ids = fields.One2many(
        comodel_name='grant.entity.report',
        inverse_name='application_id',
        string='Memòries d\'entitat',
    )
    direct_staff_employed = fields.Integer(
        string='Personal directe contractat al projecte',
    )
    direct_staff_total = fields.Integer(
        string='Total personal que participa en el projecte',
    )

    # ── RELACIONS AMB EL CICLE DE VIDA ────────────────────────────────────────

    reformulation_ids = fields.One2many(
        comodel_name='grant.reformulation',
        inverse_name='application_id',
        string='Reformulacions',
    )
    reformulation_count = fields.Integer(compute='_compute_lifecycle_counts')
    communication_plan_count = fields.Integer(compute='_compute_lifecycle_counts')
    justification_ids = fields.One2many(
        comodel_name='grant.justification',
        inverse_name='application_id',
        string='Memòries de justificació',
    )
    justification_count = fields.Integer(
        compute='_compute_lifecycle_counts',
    )
    economic_justification_ids = fields.One2many(
        comodel_name='grant.economic.justification',
        inverse_name='application_id',
        string='Justificacions econòmiques',
    )
    requirement_ids = fields.One2many(
        comodel_name='grant.requirement',
        inverse_name='application_id',
        string='Requeriments d\'esmena',
    )
    requirement_count = fields.Integer(
        compute='_compute_lifecycle_counts',
    )
    requirement_pending_count = fields.Integer(
        compute='_compute_lifecycle_counts',
    )
    communication_plan_ids = fields.One2many(
        comodel_name='grant.communication.plan',
        inverse_name='application_id',
        string='Plans de comunicació',
    )

    # ── COMPUTED ──────────────────────────────────────────────────────────────

    @api.depends(
        'reformulation_ids',
        'justification_ids',
        'requirement_ids',
        'requirement_ids.state',
        'communication_plan_ids',
    )
    def _compute_lifecycle_counts(self):
        for rec in self:
            rec.reformulation_count = len(rec.reformulation_ids)
            rec.justification_count = len(rec.justification_ids)
            rec.requirement_count = len(rec.requirement_ids)
            rec.requirement_pending_count = len(
                rec.requirement_ids.filtered(lambda r: r.state == 'pendent')
            )
            rec.communication_plan_count = len(rec.communication_plan_ids)

    @api.depends('partner_id.vat')
    def _compute_nif(self):
        for rec in self:
            rec.nif = rec.partner_id.vat or False

    @api.depends(
        'budget_expense_ids.amount_requested',
        'budget_income_ids.amount',
    )
    def _compute_budget_totals(self):
        for rec in self:
            rec.total_expenses = sum(rec.budget_expense_ids.mapped('amount_requested'))
            rec.total_income = sum(rec.budget_income_ids.mapped('amount'))
            rec.balance = rec.total_income - rec.total_expenses

    @api.depends('amount_requested', 'total_expenses')
    def _compute_grant_pct(self):
        for rec in self:
            rec.grant_pct = (
                (rec.amount_requested / rec.total_expenses * 100)
                if rec.total_expenses else 0.0
            )

    @api.constrains('budget_expense_ids', 'budget_income_ids', 'state')
    def _check_budget_balance(self):
        for rec in self:
            if (rec.state == 'esborrany'
                    or not rec.call_id.config_id.budget_must_balance):
                continue
            if abs(rec.balance) > 0.01:
                raise ValidationError(_(
                    'El pressupost de "%s" no quadra: '
                    'despeses %.2f€ ≠ ingressos %.2f€ (diferència: %.2f€).'
                ) % (rec.name, rec.total_expenses, rec.total_income, rec.balance))

    # ── TRANSICIONS D'ESTAT ───────────────────────────────────────────────────

    def action_submit(self):
        self.write({'state': 'presentada', 'date_submitted': fields.Date.today()})

    def action_grant(self):
        self.write({'state': 'concedida'})

    def action_start_reformulation(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Iniciar reformulació'),
            'res_model': 'grant.reformulation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_application_id': self.id},
        }

    def action_deny(self):
        self.write({'state': 'denegada'})

    def action_start_execution(self):
        self.write({'state': 'en_execucio'})

    def action_start_justification(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Iniciar justificació'),
            'res_model': 'grant.justification.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_application_id': self.id},
        }

    def action_view_reformulations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reformulacions'),
            'res_model': 'grant.reformulation',
            'view_mode': 'tree,form',
            'domain': [('application_id', '=', self.id)],
            'context': {'default_application_id': self.id},
        }

    def action_view_justifications(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Memòries de justificació'),
            'res_model': 'grant.justification',
            'view_mode': 'tree,form',
            'domain': [('application_id', '=', self.id)],
            'context': {'default_application_id': self.id},
        }

    def action_view_requirements(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Requeriments d\'esmena'),
            'res_model': 'grant.requirement',
            'view_mode': 'tree,form',
            'domain': [('application_id', '=', self.id)],
            'context': {'default_application_id': self.id},
        }

    def action_view_communication_plan(self):
        self.ensure_one()
        plan = self.communication_plan_ids[:1]
        if not plan:
            plan = self.env['grant.communication.plan'].create({
                'application_id': self.id,
            })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Pla de comunicació'),
            'res_model': 'grant.communication.plan',
            'res_id': plan.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_close(self):
        self.write({'state': 'tancada'})

    def action_reset_draft(self):
        self.write({'state': 'esborrany'})

    def action_open_duplicate_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Duplicar expedient'),
            'res_model': 'grant.duplicate.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_application_id': self.id},
        }
