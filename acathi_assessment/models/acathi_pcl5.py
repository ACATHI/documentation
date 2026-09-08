# ══════════════════════════════════════════════════════════════════════════════
# PCL-5 — PTSD Checklist (Llista de Verificació del TEPT, DSM-5)
# ══════════════════════════════════════════════════════════════════════════════

from odoo import api, fields, models

SCALE_PCL = [
    ('0', '0 — Gens'),
    ('1', '1 — Una mica'),
    ('2', '2 — Moderadament'),
    ('3', '3 — Bastant'),
    ('4', '4 — Extremament'),
]


class AcathiPcl5(models.Model):
    _name = 'acathi.pcl5'
    _description = 'PCL-5 — Llista de Verificació del TEPT (DSM-5)'
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
    trauma_event = fields.Char("Esdeveniment traumàtic de referència")
    score = fields.Float(
        'Puntuació total',
        compute='_compute_score', store=True, digits=(6, 2),
    )
    severity = fields.Char(
        'Nivell / Interpretació',
        compute='_compute_score', store=True,
    )
    notes = fields.Text('Observacions')

    # ── Ítems PCL-5 (escala 0–4) ──────────────────────────────────────────────
    q1 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="1. Records repetitius, molestos i no desitjats de l'experiència",
    )
    q2 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="2. Somnis pertorbadors sobre l'experiència",
    )
    q3 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="3. Sentir-se o actuar com si l'experiència estigués passant de nou (flashback)",
    )
    q4 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="4. Sentir-se molt alterat/ada quan alguna cosa recorda l'experiència",
    )
    q5 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="5. Reaccions físiques intenses davant recordatoris "
               "(cor que batega fort, suor, dificultat per respirar)",
    )
    q6 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="6. Evitar records, pensaments o sentiments relacionats amb l'experiència",
    )
    q7 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="7. Evitar persones, llocs, converses o situacions que recorden l'experiència",
    )
    q8 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="8. Problemes per recordar parts importants de l'experiència",
    )
    q9 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='9. Creences negatives fortes sobre vostè mateix/a, els altres o el món',
    )
    q10 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="10. Culpar-se a vostè mateix/a o als altres del que va passar",
    )
    q11 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='11. Sentiments negatius intensos (por, horror, ràbia, culpa, vergonya)',
    )
    q12 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='12. Pèrdua de interès en activitats que abans gaudia',
    )
    q13 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='13. Sentir-se distant o desconnectat/ada de les altres persones',
    )
    q14 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='14. Dificultats per experimentar sentiments positius',
    )
    q15 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='15. Comportament irritable, explosions de ràbia o agressivitat',
    )
    q16 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='16. Assumir riscos o fer coses que podrien causar danys',
    )
    q17 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string="17. Estar en alerta màxima, vigilant o guardant-se",
    )
    q18 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='18. Sobresaltar-se fàcilment',
    )
    q19 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='19. Dificultats per concentrar-se',
    )
    q20 = fields.Selection(
        SCALE_PCL, required=True, default='0',
        string='20. Dificultats per adormir-se',
    )

    # ── Càlcul ────────────────────────────────────────────────────────────────
    @api.depends(
        'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10',
        'q11', 'q12', 'q13', 'q14', 'q15', 'q16', 'q17', 'q18', 'q19', 'q20',
    )
    def _compute_score(self):
        for rec in self:
            total = sum(int(rec[f'q{i}'] or '0') for i in range(1, 21))
            rec.score = float(total)
            if total < 31:
                rec.severity = 'Per sota del llindar (TEPT poc probable)'
            elif total < 50:
                rec.severity = 'Llindar probable de TEPT — Avaluació clínica recomanada'
            else:
                rec.severity = 'TEPT probable — Derivació urgent recomanada'
