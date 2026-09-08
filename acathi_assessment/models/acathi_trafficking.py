# ══════════════════════════════════════════════════════════════════════════════
# Cribratge d'Indicadors de Tràfic d'Éssers Humans
# DADES DE MÀXIMA SENSIBILITAT — accés restringit
# ══════════════════════════════════════════════════════════════════════════════

from odoo import api, fields, models

SCALE_TRAFF = [
    ('0', '0 — No / Desconegut'),
    ('1', '1 — Possible'),
    ('2', '2 — Sí'),
]

_TRAFF_FIELDS = (
    'a1', 'a2', 'a3', 'a4', 'a5',
    'b1', 'b2', 'b3', 'b4',
    'c1', 'c2', 'c3', 'c4', 'c5',
    'd1', 'd2', 'd3', 'd4',
)


class AcathiTraffickingScreen(models.Model):
    _name = 'acathi.trafficking.screen'
    _description = "Cribratge d'Indicadors de Tràfic d'Éssers Humans"
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
        'Puntuació total (màx. 36)',
        compute='_compute_score', store=True, digits=(6, 2),
    )
    risk_level = fields.Selection(
        [
            ('low', 'Risc baix'),
            ('medium', 'Risc moderat — Investigar'),
            ('high', 'Risc alt — Activar protocol'),
        ],
        string='Nivell de risc',
        compute='_compute_score', store=True,
    )
    severity = fields.Char(
        'Nivell / Interpretació',
        compute='_compute_score', store=True,
    )
    notes = fields.Text('Observacions')

    # ── Grup A — Control i coacció (a1–a5) ────────────────────────────────────
    a1 = fields.Selection(SCALE_TRAFF, required=True, default='0',
                          string='A1. La persona sembla controlada per un tercer '
                                 '(moviments, comunicació, diners)')
    a2 = fields.Selection(SCALE_TRAFF, required=True, default='0',
                          string='A2. La persona té por de parlar lliurement o sembla vigilada')
    a3 = fields.Selection(SCALE_TRAFF, required=True, default='0',
                          string='A3. La persona no controla els seus propis documents d\'identitat')
    a4 = fields.Selection(SCALE_TRAFF, required=True, default='0',
                          string="A4. La persona viu on treballa o en condicions de dependència "
                                 "de l'explotador")
    a5 = fields.Selection(SCALE_TRAFF, required=True, default='0',
                          string='A5. La persona fa referència a haver rebut amenaces '
                                 '(directes o a la família)')

    # ── Grup B — Engany i captació (b1–b4) ────────────────────────────────────
    b1 = fields.Selection(SCALE_TRAFF, required=True, default='0',
                          string='B1. La persona va ser captada amb promeses falses '
                                 '(feina, allotjament, parella)')
    b2 = fields.Selection(SCALE_TRAFF, required=True, default='0',
                          string='B2. La persona va arribar al país a través d\'intermediaris o xarxes')
    b3 = fields.Selection(SCALE_TRAFF, required=True, default='0',
                          string="B3. La persona deu diners al captador/a ('deute de transport')")
    b4 = fields.Selection(SCALE_TRAFF, required=True, default='0',
                          string='B4. La persona desconeix la seva situació legal o la van '
                                 'enganyar respecte als papers')

    # ── Grup C — Explotació (c1–c5) ───────────────────────────────────────────
    c1 = fields.Selection(SCALE_TRAFF, required=True, default='0',
                          string='C1. Hi ha indicis d\'explotació sexual (passat o present)')
    c2 = fields.Selection(SCALE_TRAFF, required=True, default='0',
                          string='C2. Hi ha indicis d\'explotació laboral '
                                 '(condicions abusives, sense remuneració)')
    c3 = fields.Selection(SCALE_TRAFF, required=True, default='0',
                          string='C3. La persona ha estat forçada a demanar o a delinquir')
    c4 = fields.Selection(SCALE_TRAFF, required=True, default='0',
                          string="C4. La persona fa referència a haver servit en una llar "
                                 "en condicions d'esclavatge")
    c5 = fields.Selection(SCALE_TRAFF, required=True, default='0',
                          string="C5. La persona ha estat explotada per motiu de la seva "
                                 "orientació sexual o identitat de gènere")

    # ── Grup D — Vulnerabilitat (d1–d4) ───────────────────────────────────────
    d1 = fields.Selection(SCALE_TRAFF, required=True, default='0',
                          string='D1. La persona es troba en situació irregular administrativa')
    d2 = fields.Selection(SCALE_TRAFF, required=True, default='0',
                          string='D2. La persona no té xarxa de suport ni família accessible')
    d3 = fields.Selection(SCALE_TRAFF, required=True, default='0',
                          string='D3. La persona ha patit violència, abús sexual o tortura prèvia')
    d4 = fields.Selection(SCALE_TRAFF, required=True, default='0',
                          string='D4. La persona presenta símptomes de trauma greu '
                                 '(dissociació, flashbacks, por extrema)')

    # ── Càlcul ────────────────────────────────────────────────────────────────
    @api.depends(*_TRAFF_FIELDS)
    def _compute_score(self):
        for rec in self:
            total = sum(int(rec[f] or '0') for f in _TRAFF_FIELDS)
            rec.score = float(total)
            if total <= 4:
                rec.risk_level = 'low'
                rec.severity = 'Risc baix'
            elif total <= 10:
                rec.risk_level = 'medium'
                rec.severity = 'Risc moderat — Investigar'
            else:
                rec.risk_level = 'high'
                rec.severity = 'Risc alt — Activar protocol'
