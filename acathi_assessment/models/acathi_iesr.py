# ══════════════════════════════════════════════════════════════════════════════
# IES-R — Impact of Event Scale - Revised (Escala d'Impacte de l'Esdeveniment)
# ══════════════════════════════════════════════════════════════════════════════

from odoo import api, fields, models

SCALE_PCL = [
    ('0', '0 — Gens'),
    ('1', '1 — Una mica'),
    ('2', '2 — Moderadament'),
    ('3', '3 — Bastant'),
    ('4', '4 — Extremament'),
]

# Mapeig de subescales
_INTRUSION = (1, 2, 3, 6, 9, 14, 16, 20)
_AVOIDANCE = (5, 7, 8, 11, 12, 13, 17, 22)
_HYPERAROUSAL = (4, 10, 15, 18, 19, 21)


class AcathiIesr(models.Model):
    _name = 'acathi.iesr'
    _description = "IES-R — Escala d'Impacte de l'Esdeveniment (Revisada)"
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
    event_description = fields.Char("Descripció de l'esdeveniment")
    score = fields.Float(
        'Puntuació total',
        compute='_compute_score', store=True, digits=(6, 2),
    )
    intrusion_score = fields.Float(
        'Subescala Intrusió',
        compute='_compute_score', store=True, digits=(4, 1),
    )
    avoidance_score = fields.Float(
        'Subescala Evitació',
        compute='_compute_score', store=True, digits=(4, 1),
    )
    hyperarousal_score = fields.Float(
        'Subescala Hiperactivació',
        compute='_compute_score', store=True, digits=(4, 1),
    )
    severity = fields.Char(
        'Nivell / Interpretació',
        compute='_compute_score', store=True,
    )
    notes = fields.Text('Observacions')

    # ── Ítems IES-R (escala 0–4) ──────────────────────────────────────────────
    q1 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='1. Qualsevol recordatori em tornava a portar sentiments sobre això',
    )
    q2 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='2. Tenia dificultats per continuar dormint',
    )
    q3 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="3. Altres coses em feien pensar en l'esdeveniment constantment",
    )
    q4 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='4. Sentia irritació i ràbia',
    )
    q5 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="5. Intentava no pertorbar-me quan en pensava o se me'n recordava",
    )
    q6 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='6. Hi pensava sense voler fer-ho',
    )
    q7 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='7. Sentia com si no hagués passat o no fos real',
    )
    q8 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="8. M'allunyava de les recordances",
    )
    q9 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="9. Imatges de l'esdeveniment em venien a la ment",
    )
    q10 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="10. Estava nerviós/a i m'espaventava fàcilment",
    )
    q11 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='11. Intentava no pensar-hi',
    )
    q12 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='12. Era conscient que hi havia molts sentiments, però no els vaig abordar',
    )
    q13 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='13. Els meus sentiments estaven com adormits',
    )
    q14 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='14. Em trobava actuant o sentint com si estigués de nou en aquell moment',
    )
    q15 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="15. Tenia problemes per adormir-me",
    )
    q16 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='16. Tenia onades de sentiments forts al respecte',
    )
    q17 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="17. Intentava esborrar-ho de la memòria",
    )
    q18 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='18. Tenia dificultats per concentrar-me',
    )
    q19 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='19. El que em recordava l\'esdeveniment em causava reaccions físiques '
               '(suor, cor palpitant, nàusea)',
    )
    q20 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="20. Tenia somnis sobre l'esdeveniment",
    )
    q21 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='21. Em sentia vigilant i en guarda',
    )
    q22 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="22. Intentava no parlar-ne",
    )

    # ── Càlcul ────────────────────────────────────────────────────────────────
    @api.depends(
        'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10', 'q11',
        'q12', 'q13', 'q14', 'q15', 'q16', 'q17', 'q18', 'q19', 'q20', 'q21', 'q22',
    )
    def _compute_score(self):
        for rec in self:
            vals = {i: int(rec[f'q{i}'] or '0') for i in range(1, 23)}
            i_score = sum(vals[q] for q in _INTRUSION)
            e_score = sum(vals[q] for q in _AVOIDANCE)
            h_score = sum(vals[q] for q in _HYPERAROUSAL)
            total = i_score + e_score + h_score
            rec.intrusion_score = float(i_score)
            rec.avoidance_score = float(e_score)
            rec.hyperarousal_score = float(h_score)
            rec.score = float(total)
            sub = f'(I:{i_score} E:{e_score} H:{h_score})'
            if total < 24:
                rec.severity = f'Baix — Resposta normal {sub}'
            elif total <= 32:
                rec.severity = f'Moderat — Seguiment recomanat {sub}'
            elif total <= 36:
                rec.severity = f'Probable TEPT — Avaluació clínica {sub}'
            else:
                rec.severity = f'TEPT probable — Derivació recomanada {sub}'
