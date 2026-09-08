# ══════════════════════════════════════════════════════════════════════════════
# WHODAS 2.0 — WHO Disability Assessment Schedule (12 ítems)
# ══════════════════════════════════════════════════════════════════════════════

from odoo import api, fields, models

SCALE_WHO = [
    ('1', '1 — Cap'),
    ('2', '2 — Lleugera'),
    ('3', '3 — Moderada'),
    ('4', '4 — Greu'),
    ('5', '5 — Extrema / No pot fer-ho'),
]

_WHODAS_FIELDS = (
    's1_1', 's1_2',
    's2_1', 's2_2',
    's3_1', 's3_2',
    's4_1', 's4_2',
    's5_1', 's5_2',
    's6_1', 's6_2',
)


class AcathiWhodas(models.Model):
    _name = 'acathi.whodas'
    _description = 'WHODAS 2.0 — Avaluació de Discapacitat i Funcionament (12 ítems)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    # ── Camps generals ────────────────────────────────────────────────────────
    person_id = fields.Many2one(
        'acathi.person', string='Persona atesa',
        required=True, ondelete='restrict', tracking=True,
    )
    case_id = fields.Many2one(
        'acathi.case', string='Cas',
        domain="[('person_id', '=', person_id)]",
        ondelete='set null',
    )
    professional_id = fields.Many2one(
        'hr.employee', string='Professional',
        required=True, tracking=True,
    )
    date = fields.Date(
        "Data d'administració",
        required=True, default=fields.Date.today, tracking=True,
    )
    score = fields.Float(
        'Puntuació simple (0–48)',
        compute='_compute_score', store=True, digits=(6, 2),
    )
    score_pct = fields.Float(
        '% Discapacitat',
        compute='_compute_score', store=True, digits=(4, 1),
    )
    severity = fields.Char(
        'Nivell / Interpretació',
        compute='_compute_score', store=True,
    )
    notes = fields.Text('Observacions')

    # ── Dominis (escala 1–5) ──────────────────────────────────────────────────
    # Cognició
    s1_1 = fields.Selection(SCALE_WHO, required=True, default='1',
                            string='C1. Concentrar-se en fer alguna cosa durant deu minuts?')
    s1_2 = fields.Selection(SCALE_WHO, required=True, default='1',
                            string='C2. Recordar coses importants?')
    # Mobilitat
    s2_1 = fields.Selection(SCALE_WHO, required=True, default='1',
                            string='M1. Caminar llargues distàncies, com un quilòmetre?')
    s2_2 = fields.Selection(SCALE_WHO, required=True, default='1',
                            string="M2. Posar-se dempeus des que estava assegut/da?")
    # Autocura
    s3_1 = fields.Selection(SCALE_WHO, required=True, default='1',
                            string='Au1. Rentar-se tot el cos?')
    s3_2 = fields.Selection(SCALE_WHO, required=True, default='1',
                            string='Au2. Vestir-se?')
    # Relacions
    s4_1 = fields.Selection(SCALE_WHO, required=True, default='1',
                            string='R1. Relacionar-se amb persones que no coneix?')
    s4_2 = fields.Selection(SCALE_WHO, required=True, default='1',
                            string='R2. Mantenir una amistat?')
    # Activitats de vida
    s5_1 = fields.Selection(SCALE_WHO, required=True, default='1',
                            string='AV1. Les responsabilitats quotidianes a la llar?')
    s5_2 = fields.Selection(SCALE_WHO, required=True, default='1',
                            string='AV2. Les responsabilitats laborals o escolars principals?')
    # Participació
    s6_1 = fields.Selection(SCALE_WHO, required=True, default='1',
                            string='P1. Participar en activitats de la comunitat?')
    s6_2 = fields.Selection(SCALE_WHO, required=True, default='1',
                            string="P2. L'impacte dels problemes de salut en la seva vida en general?")

    # ── Càlcul ────────────────────────────────────────────────────────────────
    @api.depends(*_WHODAS_FIELDS)
    def _compute_score(self):
        for rec in self:
            simple = sum(int(rec[f] or '1') - 1 for f in _WHODAS_FIELDS)
            pct = simple / 48.0 * 100.0
            rec.score = float(simple)
            rec.score_pct = pct
            if pct == 0.0:
                rec.severity = 'Sense discapacitat (0%)'
            elif pct < 25.0:
                rec.severity = f'Discapacitat lleu ({pct:.1f}%)'
            elif pct < 50.0:
                rec.severity = f'Discapacitat moderada ({pct:.1f}%)'
            elif pct < 75.0:
                rec.severity = f'Discapacitat greu ({pct:.1f}%)'
            else:
                rec.severity = f'Discapacitat extrema ({pct:.1f}%)'
