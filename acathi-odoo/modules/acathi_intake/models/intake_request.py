# -*- coding: utf-8 -*-
import logging
from datetime import timedelta

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

# --- Catálogos congelados (catalogos_v1_bot_acathi.md v1.1). Fuente única de verdad. ---
SOURCE_CHANNELS = [
    ("whatsapp", "WhatsApp"),
    ("telegram", "Telegram"),
    ("web_form", "Formulario web"),
    ("instagram_dm", "Instagram DM"),
    ("facebook_messenger", "Facebook Messenger"),
    ("manual", "Manual"),
    ("email", "Email"),
]
REQUEST_TYPES = [
    ("asilo_lgtbi", "Asilo / protección internacional LGTBIQ+"),
    ("extranjeria_regularizacion", "Extranjería y regularización"),
    ("social", "Atención social"),
    ("vivienda", "Vivienda o alojamiento"),
    ("salud_psicologica", "Salud o apoyo psicológico"),
    ("violencia_discriminacion", "Violencia o discriminación"),
    ("actividades", "Actividades comunitarias"),
    ("voluntariado", "Voluntariado"),
    ("donaciones", "Donaciones o colaboración"),
    ("seguimiento", "Seguimiento / cita existente"),
    ("empleo", "Empleo y formación"),
    ("menores", "Persona menor en riesgo"),
    ("trata", "Trata / explotación grave"),
    ("administracion", "Administración / otros"),
    ("otro", "Otro motivo"),
]
APPOINTMENT_TYPES = [
    ("primera_acogida", "Primera acogida"),
    ("juridica_asilo", "Jurídica — asilo"),
    ("juridica_extranjeria", "Jurídica — extranjería"),
    ("regularizacion", "Regularización"),
    ("social", "Social"),
    ("vivienda", "Vivienda"),
    ("salud_psicologica", "Salud / psicológico"),
    ("seguimiento", "Seguimiento"),
    ("comunitaria", "Comunitaria"),
    ("voluntariado", "Voluntariado"),
    ("administracion", "Administración"),
    ("donaciones_colaboracion", "Donaciones / colaboración"),
]
TEAMS = [
    ("acogida", "Acogida"),
    ("juridica", "Jurídica"),
    ("social", "Social"),
    ("vivienda", "Vivienda"),
    ("salud_psicologica", "Salud / psicológico"),
    ("comunidad", "Comunidad"),
    ("voluntariado", "Voluntariado"),
    ("administracion", "Administración"),
    ("captacion", "Captación"),
    ("coordinacion", "Coordinación"),
    ("direccion", "Dirección"),
]
LANGUAGES = [
    ("es", "Español"), ("ca", "Català"), ("en", "English"), ("fr", "Français"),
    ("pt", "Português"), ("ar", "العربية"), ("ru", "Русский"), ("uk", "Українська"),
    ("other", "Otro"), ("unknown", "Sin definir"),
]

# Mapa por defecto request_type -> (team, appointment_type). Sugerencia, revisable
# por el equipo; la clasificación por menú no decide, propone (catalogos §3).
DEFAULT_TEAM_MAP = {
    "asilo_lgtbi": ("juridica", "juridica_asilo"),
    "extranjeria_regularizacion": ("juridica", "juridica_extranjeria"),
    "social": ("social", "social"),
    "vivienda": ("social", "vivienda"),
    "salud_psicologica": ("salud_psicologica", "salud_psicologica"),
    "violencia_discriminacion": ("salud_psicologica", "primera_acogida"),
    "actividades": ("comunidad", "comunitaria"),
    "voluntariado": ("voluntariado", "voluntariado"),
    "donaciones": ("captacion", "donaciones_colaboracion"),
    "seguimiento": (False, False),
    "administracion": ("administracion", "administracion"),
    "empleo": ("social", "social"),
    "menores": ("coordinacion", "primera_acogida"),
    "trata": ("coordinacion", "primera_acogida"),
    "otro": ("acogida", "primera_acogida"),
}


class AcathiIntakeRequest(models.Model):
    _name = "acathi.intake.request"
    _description = "Solicitud de primera acogida ACATHI"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "priority desc, create_date desc"

    name = fields.Char(
        string="Referencia", required=True, copy=False, readonly=True,
        default=lambda self: _("Nueva"), tracking=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company)

    # --- Persona (reutiliza res.partner) ---
    partner_id = fields.Many2one("res.partner", string="Contacto", tracking=True, index=True)
    partner_phone = fields.Char(related="partner_id.phone", readonly=False, string="Teléfono")

    # --- Canal / origen ---
    source_channel = fields.Selection(SOURCE_CHANNELS, string="Canal de origen", tracking=True, index=True)
    channel_external_id = fields.Char(string="ID externo (hilo/usuario)", copy=False, index=True)

    # --- Clasificación ---
    request_type = fields.Selection(REQUEST_TYPES, string="Tipo de solicitud", tracking=True, index=True)
    request_subtype = fields.Char(string="Subtipo")

    # --- Prioridad y riesgo: DOS ejes distintos (catálogos §4) ---
    priority = fields.Selection(
        [("low", "Baja"), ("normal", "Normal"), ("high", "Alta"), ("urgent", "Urgente")],
        default="normal", tracking=True, index=True,
    )
    risk_level = fields.Selection(
        [("green", "Verde"), ("yellow", "Amarillo"), ("orange", "Naranja"), ("red", "Rojo")],
        string="Nivel de riesgo", tracking=True, index=True,
    )
    risk_flags = fields.Char(string="Banderas de riesgo", help="CSV de la lista cerrada del catálogo §4")

    # --- Idioma / interpretación ---
    language = fields.Selection(LANGUAGES, string="Idioma preferido", default="unknown", tracking=True)
    needs_interpreter = fields.Boolean(string="Necesita interpretación")
    interpreter_language = fields.Char(string="Idioma de interpretación")
    interpreter_available = fields.Boolean(string="Interpretación disponible")

    # --- Consentimiento RGPD ---
    consent_ok = fields.Boolean(string="Consentimiento", tracking=True)
    consent_date = fields.Datetime(string="Fecha consentimiento")
    consent_source = fields.Char(string="Canal del consentimiento")
    consent_text_version = fields.Char(string="Versión del texto")

    # --- Asignación ---
    team = fields.Selection(TEAMS, string="Equipo", tracking=True, index=True)
    assigned_user_id = fields.Many2one("res.users", string="Responsable", tracking=True)

    # --- Cita (reutiliza calendar.event) ---
    appointment_needed = fields.Boolean(string="Necesita cita")
    suggested_appointment_type = fields.Selection(APPOINTMENT_TYPES, string="Cita sugerida")
    appointment_id = fields.Many2one("calendar.event", string="Cita", copy=False)
    human_confirmation_required = fields.Boolean(string="Requiere confirmación humana", default=True)

    # --- Estado ---
    state = fields.Selection(
        [
            ("new", "Nueva"), ("consent_pending", "Pendiente consentimiento"),
            ("triage", "Triaje"), ("queued", "En cola"),
            ("waiting_user", "Esperando a la persona"),
            ("appointment_proposed", "Cita propuesta"),
            ("appointment_scheduled", "Cita agendada"),
            ("assigned", "Asignada"), ("in_progress", "En curso"),
            ("closed", "Cerrada"), ("cancelled", "Cancelada"),
        ],
        string="Estado", default="new", required=True, tracking=True, index=True,
        group_expand="_group_expand_state",
    )
    closure_reason = fields.Char(string="Motivo de cierre")
    closed_date = fields.Datetime(string="Fecha de cierre")
    needs_human_review = fields.Boolean(string="Requiere revisión humana", tracking=True)

    # --- Campos IA (SENSIBLES). En el MVP no hay IA en tiempo real, pero el contrato existe. ---
    bot_status = fields.Selection(
        [
            ("not_required", "No requerida"), ("queued", "En cola"),
            ("processing", "Procesando"), ("completed", "Completada"),
            ("timeout", "Timeout"), ("failed", "Fallida"), ("human_review", "Revisión humana"),
        ],
        string="Estado IA", default="not_required",
        groups="acathi_intake.group_acathi_sensitive",
    )
    bot_detected_intent = fields.Char(string="Intención IA", groups="acathi_intake.group_acathi_sensitive")
    bot_confidence = fields.Float(string="Confianza IA", groups="acathi_intake.group_acathi_sensitive")
    bot_safe_reply = fields.Text(string="Respuesta sugerida IA", groups="acathi_intake.group_acathi_sensitive")
    bot_summary = fields.Text(string="Resumen interno IA", groups="acathi_intake.group_acathi_sensitive")
    bot_model_version = fields.Char(string="Modelo/versión IA", groups="acathi_intake.group_acathi_sensitive")
    human_decision = fields.Selection(
        [
            ("pendiente", "Pendiente"), ("aceptada", "Aceptada"),
            ("modificada", "Modificada"), ("rechazada", "Rechazada"),
        ],
        string="Decisión humana", default="pendiente", tracking=True,
    )

    # --- Contenido ---
    summary = fields.Char(string="Resumen breve")  # no sensible: apto para listas
    description = fields.Text(
        string="Mensaje original", groups="acathi_intake.group_acathi_sensitive",
    )

    # --- Auditoría / indicadores ---
    document_received = fields.Boolean(string="Documento recibido")
    last_inbound_message_date = fields.Datetime(string="Último mensaje entrante")
    last_outbound_message_date = fields.Datetime(string="Último mensaje saliente")
    first_response_seconds = fields.Integer(string="Segundos a 1ª respuesta")

    # OJO: no llamar 'message_ids' — colisiona con el del chatter (mail.thread).
    channel_message_ids = fields.One2many("acathi.intake.message", "request_id", string="Mensajes del canal")
    channel_message_count = fields.Integer(compute="_compute_channel_message_count", string="Nº mensajes")

    # --- Vinculación con ACATHI Social ---
    person_id = fields.Many2one(
        "acathi.person", string="Persona atendida",
        tracking=True, copy=False, index=True,
        help="Persona atendida en ACATHI Social vinculada a esta solicitud de acogida.",
    )

    @api.model
    def _group_expand_state(self, states, domain, order):
        # Muestra todas las columnas del kanban aunque estén vacías.
        return [s[0] for s in type(self).state.selection]

    @api.depends("channel_message_ids")
    def _compute_channel_message_count(self):
        for rec in self:
            rec.channel_message_count = len(rec.channel_message_ids)

    @api.onchange("request_type")
    def _onchange_request_type(self):
        """Prefill de equipo y cita sugerida según el mapa por defecto (revisable)."""
        for rec in self:
            if rec.request_type and rec.request_type in DEFAULT_TEAM_MAP:
                team, appt = DEFAULT_TEAM_MAP[rec.request_type]
                if team and not rec.team:
                    rec.team = team
                if appt and not rec.suggested_appointment_type:
                    rec.suggested_appointment_type = appt

    @api.onchange("assigned_user_id")
    def _onchange_assigned_user(self):
        # Al asignar responsable, avanza de triaje/cola a "Asignada" (feedback inmediato).
        for rec in self:
            if rec.assigned_user_id and rec.state in ("new", "consent_pending", "triage", "queued"):
                rec.state = "assigned"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == _("Nueva"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "acathi.intake.request"
                ) or _("Nueva")
            # Prefill de equipo/cita si vienen sin ellos (altas desde n8n).
            rtype = vals.get("request_type")
            if rtype in DEFAULT_TEAM_MAP:
                team, appt = DEFAULT_TEAM_MAP[rtype]
                vals.setdefault("team", team or False)
                vals.setdefault("suggested_appointment_type", appt or False)
            # Alto riesgo: menores y trata SIEMPRE rojo/urgente + revisión humana
            # (defensa en profundidad, aunque n8n no lo marque).
            if rtype in ("menores", "trata"):
                vals["risk_level"] = "red"
                vals["priority"] = "urgent"
                vals["needs_human_review"] = True
        return super().create(vals_list)

    # --- Acciones de equipo ---
    def action_handoff_human(self):
        """Deriva a revisión humana y crea una actividad para el equipo."""
        for rec in self:
            rec.needs_human_review = True
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                summary=_("Revisar solicitud de acogida %s") % rec.name,
                note=_("Derivada a revisión humana."),
            )
            rec.message_post(body=_("Derivada a revisión humana."))
        return True

    def action_close(self):
        for rec in self:
            rec.write({"state": "closed", "closed_date": fields.Datetime.now()})
        return True

    def action_assign_me(self):
        """Asigna la solicitud a quien pulsa y la pasa a 'Asignada' si estaba en triaje."""
        for rec in self:
            vals = {"assigned_user_id": self.env.user.id}
            if rec.state in ("new", "consent_pending", "triage", "queued"):
                vals["state"] = "assigned"
            rec.write(vals)
        return True

    def action_start_progress(self):
        self.write({"state": "in_progress"})
        return True

    def action_reopen(self):
        self.write({"state": "in_progress", "closed_date": False})
        return True

    # --- Integración ACATHI Social ---
    def action_create_or_link_person(self):
        """Crea o vincula una acathi.person desde esta solicitud de acogida.

        Busca por email o teléfono antes de crear para evitar duplicados.
        Si el partner_id ya existe en el intake, lo reutiliza (evita
        crear un segundo res.partner en acathi_social).
        """
        self.ensure_one()
        PersonModel = self.env.get("acathi.person")
        if PersonModel is None:
            raise UserError(_("El módulo ACATHI Social no está instalado."))
        if self.person_id:
            return self.action_view_person()

        partner = self.partner_id

        # Deduplicar: buscar persona existente por email o teléfono
        existing = self.env["acathi.person"]
        if partner and partner.email:
            existing = PersonModel.search([("email", "=", partner.email)], limit=1)
        if not existing and partner and partner.phone:
            existing = PersonModel.search([("phone", "=", partner.phone)], limit=1)

        if existing:
            self.person_id = existing.id
            self.message_post(
                body=_("Solicitud vinculada a persona atendida existente: %s (%s)")
                     % (existing.name, existing.reference)
            )
        else:
            name = (partner.name if partner else False) or (_("Persona %s") % self.name)
            if not name:
                raise UserError(_("No hay nombre de contacto en esta solicitud. Añade un contacto antes de crear la persona."))
            vals = {
                "name": name,
                "partner_id": partner.id if partner else False,
                "phone": partner.phone if partner else False,
                "email": partner.email if partner else False,
                "gdpr_consent": self.consent_ok,
                "gdpr_consent_date": self.consent_date.date() if self.consent_date else False,
            }
            person = PersonModel.create(vals)
            self.person_id = person.id
            self.message_post(
                body=_("Creada persona atendida: %s (%s). Completa su ficha en ACATHI Social.")
                     % (person.name, person.reference)
            )

        return self.action_view_person()

    def action_view_person(self):
        self.ensure_one()
        if not self.person_id:
            return {"type": "ir.actions.act_window_close"}
        return {
            "type": "ir.actions.act_window",
            "name": _("Persona atendida"),
            "res_model": "acathi.person",
            "res_id": self.person_id.id,
            "view_mode": "form",
            "target": "current",
        }

    # --- Retención RGPD ---
    @api.model
    def _gc_retention(self):
        """Purga de contenido antiguo. DESACTIVADA por defecto.

        La política de retención NO se fija por código: depende de la decisión de
        la asesoría/EIPD y del choque con la justificación de subvenciones
        (ver EIPD §6). Se activa poniendo el parámetro del sistema
        'acathi_intake.retention_days' a un entero > 0.
        Purga el payload/cuerpo de los mensajes de solicitudes cerradas más
        antiguas que ese plazo, sin borrar el registro (indicadores agregados).
        """
        days = int(self.env["ir.config_parameter"].sudo().get_param(
            "acathi_intake.retention_days", "0") or "0")
        if days <= 0:
            return  # desactivado hasta que la asesoría fije el plazo
        limit = fields.Datetime.now() - timedelta(days=days)
        old = self.sudo().search([("state", "in", ["closed", "cancelled"]),
                                  ("closed_date", "<", limit)])
        old.channel_message_ids.sudo().write({"body": False, "raw_payload": False})
        old.sudo().write({"description": False, "bot_summary": False, "bot_safe_reply": False})
        _logger.info("acathi_intake retención: purgadas %s solicitudes (>%s días).", len(old), days)
