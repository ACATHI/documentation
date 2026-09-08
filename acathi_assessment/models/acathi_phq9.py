# ══════════════════════════════════════════════════════════════════════════════
# PHQ-9 — Patient Health Questionnaire (Escala de Depressió)
# ══════════════════════════════════════════════════════════════════════════════

from odoo import api, fields, models

SCALE_PHQ = [
    ('0', '0 — Mai'),
    ('1', '1 — Alguns dies'),
    ('2', '2 — Més de la meitat dels dies'),
    ('3', '3 — Quasi cada dia'),
]


class AcathiPhq9(models.Model):
    _name = 'acathi.phq9'
    _description = 'PHQ-9 — Escala de Depressió'
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

    # ── Ítems PHQ-9 (escala 0–3) ──────────────────────────────────────────────
    q1 = fields.Selection(
        SCALE_PHQ, required=True, default='0',
        string='1. Tenir poc interès o plaer en fer les coses',
    )
    q2 = fields.Selection(
        SCALE_PHQ, required=True, default='0',
        string='2. Sentir-se desanimat/ada, deprimit/ida o sense esperança',
    )
    q3 = fields.Selection(
        SCALE_PHQ, required=True, default='0',
        string='3. Dificultats per adormir-se, continuar dormint o dormir massa',
    )
    q4 = fields.Selection(
        SCALE_PHQ, required=True, default='0',
        string='4. Sentir-se cansat/ada o tenir poca energia',
    )
    q5 = fields.Selection(
        SCALE_PHQ, required=True, default='0',
        string='5. Poc apetit o menjar en excés',
    )
    q6 = fields.Selection(
        SCALE_PHQ, required=True, default='0',
        string="6. Sentir-se malament amb vostè mateix/a, o pensar que ha fallat",
    )
    q7 = fields.Selection(
        SCALE_PHQ, required=True, default='0',
        string='7. Dificultats per concentrar-se (llegir, mirar la televisió, etc.)',
    )
    q8 = fields.Selection(
        SCALE_PHQ, required=True, default='0',
        string="8. Moure's o parlar tan lentament que la gent ho hagi notat, "
               "o estar tan inquiet/a que s'ha mogut molt",
    )
    q9 = fields.Selection(
        SCALE_PHQ, required=True, default='0',
        string="9. Pensaments que seria millor estar mort/a, o de fer-se mal",
    )

    # ── Càlcul ────────────────────────────────────────────────────────────────
    @api.depends('q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9')
    def _compute_score(self):
        for rec in self:
            total = sum(int(rec[f'q{i}'] or '0') for i in range(1, 10))
            rec.score = float(total)
            if total <= 4:
                rec.severity = 'Depressió mínima'
            elif total <= 9:
                rec.severity = 'Depressió lleu'
            elif total <= 14:
                rec.severity = 'Depressió moderada'
            elif total <= 19:
                rec.severity = 'Depressió moderadament greu'
            else:
                rec.severity = 'Depressió greu'
