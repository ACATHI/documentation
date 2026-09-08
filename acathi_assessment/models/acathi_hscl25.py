# ══════════════════════════════════════════════════════════════════════════════
# HSCL-25 — Hopkins Symptom Checklist (Llista de Símptomes Hopkins)
# ══════════════════════════════════════════════════════════════════════════════

from odoo import api, fields, models

SCALE_HSCL = [
    ('1', '1 — Gens'),
    ('2', '2 — Una mica'),
    ('3', '3 — Bastant'),
    ('4', '4 — Molt'),
]


class AcathiHscl25(models.Model):
    _name = 'acathi.hscl25'
    _description = 'HSCL-25 — Llista de Símptomes Hopkins'
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
        'Mitjana global (25 ítems)',
        compute='_compute_score', store=True, digits=(4, 2),
    )
    anxiety_score = fields.Float(
        'Mitjana ansietat',
        compute='_compute_score', store=True, digits=(4, 2),
    )
    depression_score = fields.Float(
        'Mitjana depressió',
        compute='_compute_score', store=True, digits=(4, 2),
    )
    severity = fields.Char(
        'Nivell / Interpretació',
        compute='_compute_score', store=True,
    )
    notes = fields.Text('Observacions')

    # ── Part I — Ansietat (a1–a10, escala 1–4) ────────────────────────────────
    a1 = fields.Selection(SCALE_HSCL, required=True, default='1', string='A1. Tremolors')
    a2 = fields.Selection(SCALE_HSCL, required=True, default='1', string='A2. Nerviosisme o agitació interior')
    a3 = fields.Selection(SCALE_HSCL, required=True, default='1', string='A3. Pors sobtades sense cap raó')
    a4 = fields.Selection(SCALE_HSCL, required=True, default='1', string='A4. Pors o pànic')
    a5 = fields.Selection(SCALE_HSCL, required=True, default='1', string='A5. Sentir-se atemoritzat/ada')
    a6 = fields.Selection(SCALE_HSCL, required=True, default='1', string='A6. El cor que batega fort')
    a7 = fields.Selection(SCALE_HSCL, required=True, default='1', string='A7. Tremolors a les mans')
    a8 = fields.Selection(SCALE_HSCL, required=True, default='1', string="A8. Sensació de tensió o d'estar en un nus")
    a9 = fields.Selection(SCALE_HSCL, required=True, default='1', string='A9. Atacs de pànic o terror')
    a10 = fields.Selection(SCALE_HSCL, required=True, default='1', string="A10. Estar tan inquiet/a que no pot estar quiet/a")

    # ── Part II — Depressió (d1–d15, escala 1–4) ─────────────────────────────
    d1 = fields.Selection(SCALE_HSCL, required=True, default='1', string='D1. Sentir-se adormit/ida o amb la ment en blanc')
    d2 = fields.Selection(SCALE_HSCL, required=True, default='1', string='D2. Sentir-se sol/a')
    d3 = fields.Selection(SCALE_HSCL, required=True, default='1', string='D3. Sentir-se trist/a')
    d4 = fields.Selection(SCALE_HSCL, required=True, default='1', string='D4. Preocupar-se massa per les coses')
    d5 = fields.Selection(SCALE_HSCL, required=True, default='1', string='D5. Sentir-se desanimat/ada respecte al futur')
    d6 = fields.Selection(SCALE_HSCL, required=True, default='1', string="D6. Sentir que tot és un esforç")
    d7 = fields.Selection(SCALE_HSCL, required=True, default='1', string='D7. Sentir-se sense esperança sobre el futur')
    d8 = fields.Selection(SCALE_HSCL, required=True, default='1', string='D8. Sentir que no val res')
    d9 = fields.Selection(SCALE_HSCL, required=True, default='1', string='D9. Sentir-se buit/ida per dins')
    d10 = fields.Selection(SCALE_HSCL, required=True, default='1', string='D10. Sentir que alguna cosa dolenta anirà a passar')
    d11 = fields.Selection(SCALE_HSCL, required=True, default='1', string='D11. Tenir ganes de plorar')
    d12 = fields.Selection(SCALE_HSCL, required=True, default='1', string='D12. Sentir-se atrapat/ada o encasellat/ada')
    d13 = fields.Selection(SCALE_HSCL, required=True, default='1', string='D13. Culpar-se de les coses')
    d14 = fields.Selection(SCALE_HSCL, required=True, default='1', string="D14. Sentir-se incapaç/aç de fer les coses")
    d15 = fields.Selection(SCALE_HSCL, required=True, default='1', string="D15. Tenir pensaments d'acabar amb la pròpia vida")

    # ── Càlcul ────────────────────────────────────────────────────────────────
    @api.depends(
        'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'a10',
        'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'd10',
        'd11', 'd12', 'd13', 'd14', 'd15',
    )
    def _compute_score(self):
        for rec in self:
            anx_sum = sum(int(rec[f'a{i}'] or '1') for i in range(1, 11))
            dep_sum = sum(int(rec[f'd{i}'] or '1') for i in range(1, 16))
            anx = anx_sum / 10.0
            dep = dep_sum / 15.0
            total = (anx_sum + dep_sum) / 25.0
            rec.anxiety_score = anx
            rec.depression_score = dep
            rec.score = total
            label = 'Distress clínic' if total > 1.75 else 'Sense significació clínica'
            rec.severity = f'{label} (Ansietat: {anx:.2f} / Depressió: {dep:.2f})'
