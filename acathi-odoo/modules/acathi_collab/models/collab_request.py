# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

# --- Catálogos propios del módulo de colaboraciones (datos ordinarios) ---
COLLAB_TYPES = [
    ("voluntariado", "Voluntariado"),
    ("empleo", "Trabajar en ACATHI"),
    ("practicas", "Prácticas"),
    ("empresa", "Empresa / colaboración"),
    ("evento_benefico", "Evento benéfico / recaudación"),
]
SOURCE_CHANNELS = [
    ("web_chat", "Chat web"),
    ("web_form", "Formulario web"),
    ("manual", "Manual"),
    ("email", "Email"),
]
LANGUAGES = [
    ("es", "Español"), ("ca", "Català"), ("en", "English"), ("fr", "Français"),
    ("other", "Otro"), ("unknown", "Sin definir"),
]
# Subtipos de "Team ACATHI" (iniciativas solidarias / P2P fundraising).
EVENT_SUBTYPES = [
    ("cumpleanos", "Cumpleaños solidario"),
    ("carrera", "Carrera o ruta"),
    ("cena", "Cena solidaria"),
    ("concierto", "Concierto"),
    ("yoga", "Clase de yoga"),
    ("reto_redes", "Reto en redes"),
    ("otro", "Otro"),
]
# Equipo por defecto según tipo (sugerencia, revisable por el equipo).
DEFAULT_TEAM_MAP = {
    "voluntariado": "voluntariado",
    "empleo": "coordinacion",
    "practicas": "coordinacion",
    "empresa": "captacion",
    "evento_benefico": "direccion",
}
# Tipos que SIEMPRE requieren revisión humana (uso de marca, custodia de fondos…).
ALWAYS_HUMAN_REVIEW = ("evento_benefico",)
TEAMS = [
    ("voluntariado", "Voluntariado"),
    ("coordinacion", "Coordinación"),
    ("captacion", "Captación"),
    ("comunidad", "Comunidad"),
    ("administracion", "Administración"),
    ("direccion", "Dirección"),
]


class AcathiCollabRequest(models.Model):
    _name = "acathi.collab.request"
    _description = "Solicitud de colaboración ACATHI"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(
        string="Referencia", required=True, copy=False, readonly=True,
        default=lambda self: _("Nueva"), tracking=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company)

    collab_type = fields.Selection(COLLAB_TYPES, string="Tipo de colaboración",
                                    required=True, tracking=True, index=True)
    partner_id = fields.Many2one("res.partner", string="Contacto", tracking=True, index=True)

    # --- Datos de contacto (ordinarios) ---
    contact_name = fields.Char(string="Nombre")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Teléfono")
    has_whatsapp = fields.Boolean(string="El teléfono tiene WhatsApp")
    language = fields.Selection(LANGUAGES, string="Idioma", default="unknown", tracking=True)

    # --- Específicos por tipo ---
    company_name = fields.Char(string="Empresa")            # empresa
    study_center = fields.Char(string="Centro de estudios")  # prácticas
    area = fields.Char(string="Área de interés")             # voluntariado/empleo/prácticas
    availability = fields.Char(string="Disponibilidad")      # voluntariado
    collaboration_kind = fields.Char(string="Tipo de aportación")  # empresa
    event_subtype = fields.Selection(EVENT_SUBTYPES, string="Tipo de evento")  # evento_benefico
    event_date = fields.Date(string="Fecha del evento")      # evento_benefico
    message = fields.Text(string="Mensaje")

    # --- Canal / consentimiento ---
    source_channel = fields.Selection(SOURCE_CHANNELS, string="Canal", tracking=True, index=True)
    channel_external_id = fields.Char(string="ID externo (sesión)", copy=False, index=True)
    consent_ok = fields.Boolean(string="Consentimiento", tracking=True)
    consent_date = fields.Datetime(string="Fecha consentimiento")
    consent_text_version = fields.Char(string="Versión del texto")

    # --- Asignación / estado ---
    team = fields.Selection(TEAMS, string="Equipo", tracking=True, index=True)
    assigned_user_id = fields.Many2one("res.users", string="Responsable", tracking=True)
    needs_human_review = fields.Boolean(string="Requiere revisión humana", tracking=True)
    state = fields.Selection(
        [
            ("new", "Nueva"), ("in_review", "En revisión"),
            ("contacted", "Contactada"), ("accepted", "Aceptada"),
            ("closed", "Cerrada"), ("cancelled", "Cancelada"),
        ],
        string="Estado", default="new", required=True, tracking=True, index=True,
        group_expand="_group_expand_state",
    )

    @api.model
    def _group_expand_state(self, states, domain, order):
        return [s[0] for s in type(self).state.selection]

    @api.onchange("collab_type")
    def _onchange_collab_type(self):
        for rec in self:
            if rec.collab_type in DEFAULT_TEAM_MAP and not rec.team:
                rec.team = DEFAULT_TEAM_MAP[rec.collab_type]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == _("Nueva"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "acathi.collab.request") or _("Nueva")
            ctype = vals.get("collab_type")
            if ctype in DEFAULT_TEAM_MAP:
                vals.setdefault("team", DEFAULT_TEAM_MAP[ctype])
            # Tipos sensibles de gobernanza (uso de marca / fondos): revisión humana.
            if ctype in ALWAYS_HUMAN_REVIEW:
                vals["needs_human_review"] = True
        records = super().create(vals_list)
        for rec in records:
            if rec.collab_type in ALWAYS_HUMAN_REVIEW:
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary=_("Revisar propuesta: %s") % rec.name,
                    note=_("Evento benéfico / recaudación: validar uso de marca y "
                           "custodia de fondos antes de aceptar."),
                )
        return records

    def action_mark_contacted(self):
        self.write({"state": "contacted"})
        return True

    def action_close(self):
        self.write({"state": "closed"})
        return True
