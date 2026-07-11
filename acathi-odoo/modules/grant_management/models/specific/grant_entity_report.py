from odoo import fields, models


class GrantEntityReport(models.Model):
    """Memòria anual de l'entitat — formulari J-SP2311A (SMPRAV)."""
    _name = 'grant.entity.report'
    _description = 'Memòria d\'entitat anual (SMPRAV J-SP2311A)'
    _inherit = ['mail.thread']
    _order = 'report_year desc'

    application_id = fields.Many2one(
        comodel_name='grant.application',
        string='Expedient',
        required=True,
        ondelete='cascade',
    )
    report_year = fields.Integer(
        string='Any de la memòria',
        required=True,
    )
    currency_id = fields.Many2one(
        related='application_id.currency_id',
    )

    # ── IDENTIFICACIÓ DE L'ENTITAT ────────────────────────────────────────────

    entity_mission_html = fields.Html(
        string='Missió de l\'entitat',
        help='Descripció de la finalitat i raó de ser de l\'organització',
    )
    entity_values_html = fields.Html(string='Valors i principis')
    entity_history_html = fields.Html(
        string='Breu història',
        help='Orígens, evolució i fites destacades de l\'entitat',
    )
    intervention_areas_html = fields.Html(
        string='Àrees d\'intervenció',
        help='Àmbits temàtics i col·lectius amb els quals treballa l\'entitat',
    )

    # ── ACTIVITAT ANUAL ────────────────────────────────────────────────────────

    annual_activities_html = fields.Html(
        string='Activitats i programes desenvolupats durant l\'any',
    )
    penal_programs_html = fields.Html(
        string='Programes en l\'àmbit penitenciari',
        help='Descripció dels programes desenvolupats als centres penitenciaris',
    )

    # ── RECURSOS HUMANS ────────────────────────────────────────────────────────

    total_staff = fields.Integer(
        string='Total personal remunerat',
        help='Nombre de persones a nòmina o contractades (equivalents a jornada completa)',
    )
    total_volunteers = fields.Integer(string='Total voluntaris/àries')
    total_beneficiaries = fields.Integer(
        string='Total beneficiaris atesos durant l\'any',
    )

    # ── RECURSOS ECONÒMICS ────────────────────────────────────────────────────

    annual_budget = fields.Monetary(
        string='Pressupost anual total de l\'entitat',
        currency_field='currency_id',
    )
    annual_income_sources_html = fields.Html(
        string='Origen dels ingressos',
        help='Distribució per tipus: administracions, quotes, donatius, serveis...',
    )

    # ── QUALITAT I TRANSPARÈNCIA ──────────────────────────────────────────────

    quality_system_html = fields.Html(
        string='Sistema de qualitat i avaluació',
    )
    transparency_html = fields.Html(
        string='Transparència i bon govern',
        help='Dades de transparència, publicació de comptes, memòria pública...',
    )
    notes = fields.Html(string='Observacions addicionals')
