from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class GrantFunder(models.Model):
    _name = 'grant.funder'
    _description = 'Finançador de subvencions'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Nom complet', required=True)
    short_name = fields.Char(
        string='Abreviació',
        required=True,
        help='Codi curt per a títols i etiquetes (ex: AMB, DIBA, GEN_DS, COSIFE, SMPRAV)',
    )
    funder_type = fields.Selection(
        selection=[
            ('administracio_local', 'Administració local'),
            ('diputacio', 'Diputació'),
            ('generalitat', 'Generalitat'),
            ('estat', 'Administració de l\'Estat'),
            ('privat', 'Entitat privada / fundació'),
            ('ue', 'Unió Europea'),
            ('internacional', 'Internacional'),
        ],
        string='Tipus',
        required=True,
        default='administracio_local',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner Odoo',
        ondelete='set null',
    )
    logo = fields.Binary(string='Logo oficial', attachment=True)
    logo_specs_html = fields.Html(
        string='Normes d\'ús del logo',
        help='Dimensions, espai protegit, text obligatori, etc.',
    )
    requires_entity_report = fields.Boolean(
        string='Requereix memòria d\'entitat separada',
        default=False,
        help='Actiu per a SMPRAV (formulari J-SP2311A)',
    )
    single_project_per_call = fields.Boolean(
        string='Un sol projecte per convocatòria',
        default=False,
        help='Actiu per a COSIFE: una entitat no pot presentar-se a més d\'una línia',
    )
    has_penal_context = fields.Boolean(
        string='Formulari context penitenciari',
        default=False,
        help='Actiu per a SMPRAV: habilita camps específics de centres penitenciaris',
    )
    active = fields.Boolean(default=True)

    call_ids = fields.One2many(
        comodel_name='grant.call',
        inverse_name='funder_id',
        string='Convocatòries',
    )
    call_count = fields.Integer(
        string='Nre. convocatòries',
        compute='_compute_call_count',
    )

    @api.depends('call_ids')
    def _compute_call_count(self):
        for rec in self:
            rec.call_count = len(rec.call_ids)

    def action_view_calls(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Convocatòries de %s') % self.name,
            'res_model': 'grant.call',
            'view_mode': 'tree,form',
            'domain': [('funder_id', '=', self.id)],
            'context': {'default_funder_id': self.id},
        }


class GrantCall(models.Model):
    _name = 'grant.call'
    _description = 'Convocatòria de subvenció'
    _order = 'year desc, name'

    name = fields.Char(string='Nom de la convocatòria', required=True)
    funder_id = fields.Many2one(
        comodel_name='grant.funder',
        string='Finançador',
        required=True,
        ondelete='restrict',
    )
    year = fields.Integer(
        string='Any',
        required=True,
        default=lambda self: fields.Date.today().year,
    )
    call_code = fields.Char(
        string='Codi intern del finançador',
        help='Referència administrativa del finançador per a aquesta convocatòria',
    )
    line_code = fields.Char(
        string='Codi de línia',
        help='Ex: B.1, C.2, E.1, 1.1.3',
    )
    subline_name = fields.Char(string='Nom de la sublínia')
    is_pluriannual = fields.Boolean(
        string='Pluriennal',
        default=False,
        help='Projecte amb execució de 2 o més anys',
    )
    execution_years = fields.Integer(
        string='Anys d\'execució',
        default=1,
        help='Nombre d\'anys d\'execució (1 o 2)',
    )
    date_open = fields.Date(string='Data obertura')
    date_close = fields.Date(string='Data tancament sol·licituds')
    date_resolution = fields.Date(string='Data prevista resolució')
    date_justification = fields.Date(string='Data límit justificació')
    max_grant_pct = fields.Float(
        string='% màxim subvencionable',
        digits=(5, 2),
        help='Percentatge màxim subvencionable sobre despeses totals elegibles',
    )
    reformulation_days = fields.Integer(
        string='Dies per reformular',
        default=10,
        help='Dies hàbils per presentar reformulació de pressupost',
    )
    config_id = fields.Many2one(
        comodel_name='grant.call.config',
        string='Configuració',
        ondelete='restrict',
        help='Defineix quins camps, validacions i plantilles s\'apliquen',
    )
    url_bases = fields.Char(
        string='URL bases reguladores',
        help='Enllaç a les bases de la convocatòria (BOPB, DOGC, etc.)',
    )
    state = fields.Selection(
        selection=[
            ('oberta', 'Oberta'),
            ('tancada', 'Tancada (en resolució)'),
            ('resolucio', 'Resolució publicada'),
            ('arxivada', 'Arxivada'),
        ],
        string='Estat',
        default='oberta',
        required=True,
    )

    @api.constrains('execution_years', 'is_pluriannual')
    def _check_execution_years(self):
        for rec in self:
            if rec.is_pluriannual and rec.execution_years < 2:
                raise ValidationError(
                    _('Una convocatòria pluriennal ha de tenir com a mínim 2 anys d\'execució.')
                )

    @api.constrains('date_open', 'date_close')
    def _check_dates(self):
        for rec in self:
            if rec.date_open and rec.date_close and rec.date_open > rec.date_close:
                raise ValidationError(
                    _('La data d\'obertura no pot ser posterior a la data de tancament.')
                )


class GrantCallConfig(models.Model):
    """
    Cor de l'arquitectura extensible.
    Cada registre defineix el comportament complet d'una convocatòria:
    quins camps mostrar, quines validacions aplicar, quines plantilles generar.
    Afegir un finançador nou = crear un registre aquí. Zero codi Python nou.
    """
    _name = 'grant.call.config'
    _description = 'Configuració de convocatòria (extensibilitat per finançador)'
    _order = 'name'

    name = fields.Char(
        string='Nom de la configuració',
        required=True,
        help='Ex: Ajuntament BCN 2026, COSIFE Línia B 2026',
    )
    funder_id = fields.Many2one(
        comodel_name='grant.funder',
        string='Finançador',
        required=True,
        ondelete='restrict',
    )

    # ── SECCIONS VISIBLES ──────────────────────────────────────────────────────

    show_revaluation_plan = fields.Boolean(
        string='Pla de Revaloració',
        default=False,
        help='Ajuntament BCN sec.14',
    )
    show_penal_fields = fields.Boolean(
        string='Camps context penitenciari',
        default=False,
        help='SMPRAV: habilita centre penitenciari, ràtios interns, hores intervenció',
    )
    show_counting_units = fields.Boolean(
        string='Unitats de Recompte',
        default=False,
        help='Generalitat Drets Socials: unitat de mesura de l\'activitat',
    )
    show_volunteer_table = fields.Boolean(
        string='Taula de voluntariat',
        default=False,
        help='Generalitat DS sec.1.3: desglossi detallat de voluntaris',
    )
    show_device_table = fields.Boolean(
        string='Taula de dispositius',
        default=False,
        help='Generalitat DS sec.1.4: llista de serveis/equipaments del projecte',
    )
    show_sai_network = fields.Boolean(
        string='Coordinació Xarxa SAI LGBTI',
        default=False,
        help='COSIFE Línia C',
    )
    show_law_19_2020 = fields.Boolean(
        string='Seccions Llei 19/2020',
        default=False,
        help='COSIFE Línia E: llei per a la igualtat efectiva de dones i homes',
    )
    show_gender_table = fields.Boolean(
        string='Taula activitat+metodologia+indicadors gènere',
        default=False,
        help='COSIFE sec.2.1',
    )
    show_objectives_table = fields.Boolean(
        string='Taula OG×OE Pla de Govern',
        default=False,
        help='COSIFE sec.1.3: vincle entre objectius del projecte i el Pla de Govern',
    )
    show_ambit_selector = fields.Boolean(
        string='Selector àmbit 1-8 + línia',
        default=False,
        help='Diputació BCN: 8 àmbits de programa (benestar, cultura, medi ambient...)',
    )
    show_xfa_budget = fields.Boolean(
        string='Estructura pressupost XFA Diputació',
        default=False,
        help='Diputació BCN: categories AP (activitat pròpia) + EP (estructura) + RP (resta)',
    )
    show_social_clauses = fields.Boolean(
        string='Clàusules socials',
        default=False,
        help='COSIFE + SMPRAV: mesures conciliació, personal vulnerable, protocol assetjament',
    )
    show_catalan_policy = fields.Boolean(
        string='Política d\'ús del català',
        default=False,
        help='COSIFE sec.5',
    )
    show_ecosocial = fields.Boolean(
        string='Perspectiva ecosocial',
        default=False,
        help='Ajuntament BCN sec.7',
    )
    show_intercultural = fields.Boolean(
        string='Perspectiva intercultural',
        default=False,
        help='Ajuntament BCN sec.8',
    )

    # ── LÍMITS DE CARÀCTERS ────────────────────────────────────────────────────

    social_interest_max_chars = fields.Integer(
        string='Màx. caràcters necessitat social',
        default=0,
        help='0 = sense límit. Ex: 800 per a Generalitat DS',
    )
    brief_description_max_chars = fields.Integer(
        string='Màx. caràcters descripció breu',
        default=0,
    )
    communication_message_max_chars = fields.Integer(
        string='Màx. caràcters missatge comunicació',
        default=0,
        help='Ex: 400 caràcters per a COSIFE',
    )
    max_general_objectives = fields.Integer(
        string='Màx. objectius generals',
        default=0,
        help='0 = sense límit. Ex: 2 per a Generalitat DS',
    )
    max_specific_objectives = fields.Integer(
        string='Màx. objectius específics',
        default=0,
        help='0 = sense límit. Ex: 5 per a SMPRAV',
    )

    # ── PRESSUPOST ────────────────────────────────────────────────────────────

    budget_template = fields.Selection(
        selection=[
            ('ajuntament_bcn', 'Ajuntament de Barcelona'),
            ('diputacio_bcn', 'Diputació de Barcelona (XFA)'),
            ('generalitat_ds', 'Generalitat — Drets Socials'),
            ('cosife', 'COSIFE'),
            ('smprav', 'SMPRAV — Justícia'),
            ('generic', 'Genèric'),
        ],
        string='Plantilla de pressupost',
        default='generic',
        required=True,
    )
    budget_must_balance = fields.Boolean(
        string='El pressupost ha de quadrar',
        default=True,
        help='Valida que ingressos totals = despeses totals',
    )
    budget_category_ids = fields.Many2many(
        comodel_name='grant.budget.category',
        string='Categories de despesa habilitades',
        help='Deixar buit per permetre totes les categories actives',
    )

    # ── JUSTIFICACIÓ ──────────────────────────────────────────────────────────

    justification_template = fields.Selection(
        selection=[
            ('ajuntament_bcn', 'Memòria Ajuntament Barcelona'),
            ('diputacio_bcn', 'Memòria Diputació Barcelona'),
            ('generalitat_ds', 'Memòria Generalitat DS'),
            ('cosife_b', 'Memòria COSIFE Línia B (IM 99308)'),
            ('cosife_ce', 'Memòria COSIFE Línies C/E'),
            ('smprav', 'Memòria SMPRAV (J-SP2412)'),
            ('generic', 'Memòria genèrica'),
        ],
        string='Plantilla de justificació',
        default='generic',
        required=True,
    )
    requires_monthly_execution = fields.Boolean(
        string='Requereix mesos d\'execució',
        default=False,
        help='COSIFE Línia B: cal marcar els mesos en què s\'ha executat cada activitat',
    )
    requires_user_age_breakdown = fields.Boolean(
        string='Requereix beneficiaris per franja d\'edat',
        default=False,
        help='COSIFE + Generalitat DS',
    )


class GrantBudgetCategory(models.Model):
    _name = 'grant.budget.category'
    _description = 'Categoria de despesa de subvenció'
    _order = 'sequence, name'

    name = fields.Char(string='Nom', required=True)
    code = fields.Char(
        string='Codi',
        required=True,
        help='Codi intern per a regles i informes (ex: RRHH, CONT_EXT, LLOGUER)',
    )
    category_type = fields.Selection(
        selection=[
            ('corrents', 'Despeses corrents'),
            ('inversions', 'Inversions'),
        ],
        string='Tipus',
        required=True,
        default='corrents',
    )
    sequence = fields.Integer(default=10)
    description = fields.Char(
        string='Descripció addicional',
        help='Aclariment sobre quines despeses inclou aquesta categoria',
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'El codi de categoria ha de ser únic.'),
    ]
