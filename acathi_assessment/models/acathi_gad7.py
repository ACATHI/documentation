# ══════════════════════════════════════════════════════════════════════════════
# GAD-7 — Generalized Anxiety Disorder (Escala d'Ansietat Generalitzada)
# ══════════════════════════════════════════════════════════════════════════════

from odoo import api, fields, models

SCALE_PHQ = [
    ('0', '0 — Mai'),
    ('1', '1 — Alguns dies'),
    ('2', '2 — Més de la meitat dels dies'),
    ('3', '3 — Quasi cada dia'),
]


class AcathiGad7(models.Model):
    _name = 'acathi.gad7'
    _description = "GAD-7 — Escala d'Ansietat Generalitzada"
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
        'Puntuació total',
        compute='_compute_score', store=True, digits=(6, 2),
    )
    severity = fields.Char(
        'Nivell / Interpretació',
        compute='_compute_score', store=True,
    )
    notes = fields.Text('Observacions')

    # ── Ítems GAD-7 (escala 0–3) ──────────────────────────────────────────────
    q1 = fields.Selection(
        SCALE_PHQ, required=True, default='0',
        string="1. Sentir-se nerviós/a, ansiós/a o a la vora del precipici",
    )
    q2 = fields.Selection(
        SCALE_PHQ, required=True, default='0',
        string='2. No poder aturar o controlar la preocupació',
    )
    q3 = fields.Selection(
        SCALE_PHQ, required=True, default='0',
        string='3. Preocupar-se massa per coses diverses',
    )
    q4 = fields.Selection(
        SCALE_PHQ, required=True, default='0',
        string='4. Dificultats per relaxar-se',
    )
    q5 = fields.Selection(
        SCALE_PHQ, required=True, default='0',
        string="5. Estar tan inquiet/a que és difícil estar quiet/a",
    )
    q6 = fields.Selection(
        SCALE_PHQ, required=True, default='0',
        string='6. Enfadar-se o irritar-se fàcilment',
    )
    q7 = fields.Selection(
        SCALE_PHQ, required=True, default='0',
        string='7. Sentir por com si pogués passar alguna cosa terrible',
    )

    # ── Càlcul ────────────────────────────────────────────────────────────────
    @api.depends('q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7')
    def _compute_score(self):
        for rec in self:
            total = sum(int(rec[f'q{i}'] or '0') for i in range(1, 8))
            rec.score = float(total)
            if total <= 4:
                rec.severity = 'Ansietat mínima'
            elif total <= 9:
                rec.severity = 'Ansietat lleu'
            elif total <= 14:
                rec.severity = 'Ansietat moderada'
            else:
                rec.severity = 'Ansietat greu'
