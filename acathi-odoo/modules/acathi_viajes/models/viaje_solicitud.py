# -*- coding: utf-8 -*-
import json
import logging

import requests

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ViajeSolicitud(models.Model):
    _name = "acathi.viaje.solicitud"
    _description = "Solicitud de viaje (Radar)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    # request_id: clave de cruce con el motor n8n/Sheets. La genera Odoo (secuencia)
    # y se envía a n8n; n8n la usa como clave en todas sus hojas y la devuelve.
    name = fields.Char(
        string="Referencia", required=True, copy=False, readonly=True,
        default=lambda self: _("Nueva"), tracking=True,
    )

    # --- Identidad (PII) — RESTRINGIDO al grupo PII (RGPD) ---
    # copy=False: al Duplicar una solicitud (reutilizar criterios de búsqueda) NO se
    # arrastra la PII de la persona anterior. Minimización de datos sensibles.
    persona_viajera = fields.Char(
        string="Persona viajera", tracking=True, copy=False,
        groups="acathi_viajes.group_viajes_pii",
    )
    contacto = fields.Char(
        string="Contacto", copy=False, groups="acathi_viajes.group_viajes_pii",
    )
    motivo_viaje = fields.Text(
        string="Motivo del viaje", copy=False, groups="acathi_viajes.group_viajes_pii",
    )
    observaciones = fields.Text(
        string="Observaciones", copy=False, groups="acathi_viajes.group_viajes_pii",
    )

    # --- Solicitud (sin PII) ---
    solicitante = fields.Char(string="Solicitante (área/persona interna)")
    origen = fields.Char(string="Origen", required=True, help="Ciudad o código IATA")
    destino = fields.Char(string="Destino", required=True, help="Ciudad o código IATA")
    fecha_ida = fields.Date(string="Fecha de ida", required=True)
    fecha_vuelta = fields.Date(string="Fecha de vuelta")
    flexibilidad_dias = fields.Integer(string="Flexibilidad (días)", default=0)
    personas = fields.Integer(string="Personas", default=1)
    equipaje = fields.Selection(
        [("solo_mano", "Solo cabina"), ("facturado", "Con facturado")],
        string="Equipaje", default="solo_mano",
    )
    presupuesto_maximo = fields.Float(string="Presupuesto máximo (EUR)")
    perfil = fields.Selection(
        [
            ("personal", "Personal"),
            ("institucional", "Institucional"),
            ("subvencionado", "Subvencionado"),
        ],
        string="Perfil del viaje", required=True, default="institucional", tracking=True,
    )
    tipo_busqueda = fields.Selection(
        [
            ("ambos", "Vuelos y estadías"),
            ("solo_vuelos", "Solo vuelos"),
            ("solo_estadias", "Solo estadías"),
        ],
        string="Qué buscar", required=True, default="ambos", tracking=True,
        help="Limita la búsqueda del motor: solo vuelos, solo estadías, o ambos.",
    )
    proyecto_id = fields.Char(string="Proyecto")
    subvencion_id = fields.Char(string="Subvención")
    necesita_factura = fields.Boolean(string="Necesita factura")
    necesita_cancelacion = fields.Boolean(string="Necesita cancelación flexible")

    # --- Estado y resultados ---
    estado = fields.Selection(
        [
            ("borrador", "Borrador"),
            ("enviado", "Enviado a n8n"),
            ("buscando", "Buscando opciones"),
            ("opciones_listas", "Opciones listas"),
            ("informe_listo", "Informe listo"),
            ("decidido", "Decidido"),
            ("error", "Error"),
        ],
        string="Estado", default="borrador", required=True, tracking=True, copy=False,
    )
    # Resultados: copy=False → una solicitud duplicada nace limpia (sin informe ni
    # opciones viejas), lista para relanzar la búsqueda con los criterios copiados.
    informe_url = fields.Char(string="Informe (Nextcloud)", copy=False)
    informe_html = fields.Html(
        string="Informe", sanitize=False, readonly=True, copy=False,
        help="Informe de decisión renderizado (llega del motor n8n en un iframe aislado).",
    )
    opcion_ids = fields.One2many(
        "acathi.viaje.opcion", "solicitud_id", string="Opciones", copy=False,
    )
    opcion_recomendada_id = fields.Many2one(
        "acathi.viaje.opcion", string="Opción recomendada", copy=False,
        domain="[('solicitud_id', '=', id)]",
    )
    opciones_count = fields.Integer(
        string="Nº opciones", compute="_compute_opciones_count",
    )

    @api.depends("opcion_ids")
    def _compute_opciones_count(self):
        for rec in self:
            rec.opciones_count = len(rec.opcion_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == _("Nueva"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "acathi.viaje.solicitud"
                ) or _("Nueva")
        return super().create(vals_list)

    def _n8n_payload(self):
        """Datos que se envían a n8n. Incluye PII (n8n la separa en su hoja PII).
        Se lee con sudo() porque los campos PII están restringidos por grupo."""
        self.ensure_one()
        s = self.sudo()
        return {
            "request_id": s.name,
            "origen": s.origen,
            "destino": s.destino,
            "fecha_ida": s.fecha_ida and s.fecha_ida.isoformat() or "",
            "fecha_vuelta": s.fecha_vuelta and s.fecha_vuelta.isoformat() or "",
            "flexibilidad_dias": s.flexibilidad_dias or 0,
            "personas": s.personas or 1,
            "equipaje": s.equipaje or "",
            "presupuesto_maximo": s.presupuesto_maximo or 0.0,
            "perfil": s.perfil or "",
            "tipo_busqueda": s.tipo_busqueda or "ambos",
            "proyecto_id": s.proyecto_id or "",
            "subvencion_id": s.subvencion_id or "",
            "necesita_factura": bool(s.necesita_factura),
            "necesita_cancelacion": bool(s.necesita_cancelacion),
            # PII (frontera): n8n las guarda en su hoja PII restringida
            "persona_viajera": s.persona_viajera or "",
            "solicitante": s.solicitante or "",
            "contacto": s.contacto or "",
            "motivo_viaje": s.motivo_viaje or "",
            "observaciones": s.observaciones or "",
            "odoo_id": s.id,
        }

    def action_buscar_opciones(self):
        """Envía la solicitud al motor n8n (webhook). n8n responde rápido y procesa
        en segundo plano; luego escribe los resultados de vuelta en este registro."""
        self.ensure_one()
        url = self.env["ir.config_parameter"].sudo().get_param(
            "acathi_viajes.n8n_webhook_url"
        )
        if not url:
            raise UserError(_(
                "Falta la URL del webhook de n8n. Configúrala en Ajustes → Técnico → "
                "Parámetros del sistema, clave 'acathi_viajes.n8n_webhook_url'."
            ))
        token = self.env["ir.config_parameter"].sudo().get_param(
            "acathi_viajes.n8n_webhook_token"
        )
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = token
        try:
            resp = requests.post(
                url, data=json.dumps(self._n8n_payload()),
                headers=headers, timeout=30,
            )
            resp.raise_for_status()
        except Exception as e:  # noqa: BLE001
            _logger.exception("Error llamando a n8n para %s", self.name)
            self.estado = "error"
            raise UserError(_("No se pudo contactar con n8n: %s") % e)
        self.estado = "enviado"
        self.message_post(body=_("Solicitud enviada al motor n8n (request_id %s).") % self.name)
        return True

    def action_ver_informe(self):
        self.ensure_one()
        if not self.informe_url:
            raise UserError(_("Aún no hay informe para esta solicitud."))
        return {
            "type": "ir.actions.act_url",
            "url": self.informe_url,
            "target": "new",
        }
