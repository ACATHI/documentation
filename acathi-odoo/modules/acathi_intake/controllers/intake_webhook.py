# -*- coding: utf-8 -*-
"""Endpoint de entrada para n8n.

n8n (orquestador) recibe el mensaje del canal (Telegram/WhatsApp/web), aplica
reglas y menú, y llama aquí para materializar contacto + solicitud + mensaje.
La clasificación llega YA resuelta desde n8n (menú determinista); Odoo no
interpreta texto libre en el MVP.

Seguridad: cabecera 'X-Acathi-Token' verificada contra el parámetro del sistema
'acathi_intake.inbound_token'. auth='public' + operaciones con sudo() tras validar.
"""
import logging

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.acathi_intake.models.intake_request import DEFAULT_TEAM_MAP

_logger = logging.getLogger(__name__)


class AcathiIntakeWebhook(http.Controller):

    def _check_token(self):
        expected = request.env["ir.config_parameter"].sudo().get_param(
            "acathi_intake.inbound_token")
        got = request.httprequest.headers.get("X-Acathi-Token")
        return bool(expected) and got == expected

    def _partner_name_vals(self, Partner, display_name):
        """Nombre compatible CON y SIN el módulo partner_firstname (OCA).

        Con partner_firstname instalado, res.partner.name es un campo calculado a
        partir de firstname/lastname; crear pasando solo 'name' puede dejar name
        vacío y disparar el check res_partner_check_name ("el contacto requiere un
        nombre"). Si el campo firstname existe, pasamos firstname/lastname.
        """
        name = (display_name or "").strip() or _("Contacto de acogida")
        if "firstname" in Partner._fields:
            parts = name.split()
            if len(parts) > 1:
                return {"firstname": " ".join(parts[:-1]), "lastname": parts[-1]}
            return {"lastname": name}
        return {"name": name}

    def _find_or_create_partner(self, env, data):
        Partner = env["res.partner"].sudo()
        tg = data.get("external_user_id")
        phone = data.get("phone")
        email = data.get("email")
        # Antiduplicados: por id de canal, luego teléfono/whatsapp, luego email.
        domain = []
        if data.get("source_channel") == "telegram" and tg:
            domain = [("telegram_user_id", "=", tg)]
        elif phone:
            domain = ["|", ("phone", "=", phone), ("whatsapp_number", "=", phone)]
        elif email:
            domain = [("email", "=", email)]
        partner = Partner.search(domain, limit=1) if domain else Partner.browse()

        vals = {
            "preferred_channel": data.get("source_channel"),
            "preferred_language": data.get("language") or "unknown",
        }
        if data.get("source_channel") == "telegram" and tg:
            vals["telegram_user_id"] = tg
        if phone:
            vals["phone"] = phone
            if data.get("source_channel") == "whatsapp":
                vals["whatsapp_number"] = phone
        if email:
            vals["email"] = email

        if partner:
            partner.write(vals)  # no tocamos el nombre de un contacto ya existente
        else:
            vals.update(self._partner_name_vals(Partner, data.get("display_name")))
            partner = Partner.create(vals)
        return partner

    @http.route("/acathi_intake/inbound", type="json", auth="public",
                methods=["POST"], csrf=False)
    def inbound(self, **_kw):
        if not self._check_token():
            _logger.warning("acathi_intake inbound: token inválido")
            return {"ok": False, "error": "unauthorized"}
        data = request.get_json_data() if hasattr(request, "get_json_data") else request.jsonrequest
        env = request.env
        Req = env["acathi.intake.request"].sudo()
        Msg = env["acathi.intake.message"].sudo()

        try:
            partner = self._find_or_create_partner(env, data)

            # Contacto indicado por la persona (teléfono o email) → a la ficha, si aún no lo tiene.
            contact = (data.get("contact") or "").strip()
            if contact and contact.lower() not in ("no", "omitir", "ometre", "-", "skip"):
                if "@" in contact and not partner.email:
                    partner.write({"email": contact})
                elif any(ch.isdigit() for ch in contact) and not partner.phone:
                    partner.write({"phone": contact})

            # Reutiliza la solicitud abierta del mismo hilo si existe.
            ext_id = data.get("external_thread_id") or data.get("external_user_id")
            req = Req.browse()
            if ext_id:
                req = Req.search([
                    ("channel_external_id", "=", ext_id),
                    ("state", "not in", ["closed", "cancelled"]),
                ], limit=1)

            rtype = data.get("request_type") or False
            req_vals = {
                "partner_id": partner.id,
                "source_channel": data.get("source_channel"),
                "channel_external_id": ext_id,
                "request_type": rtype,
                "request_subtype": data.get("request_subtype") or False,
                "language": data.get("language") or "unknown",
                "priority": data.get("priority") or "normal",
                "risk_level": data.get("risk_level") or False,
                "risk_flags": data.get("risk_flags") or False,
                "consent_ok": bool(data.get("consent")),
                "consent_source": data.get("source_channel"),
                "consent_text_version": data.get("consent_text_version") or False,
                "summary": (data.get("message_text") or "")[:120],
                "description": data.get("message_text") or False,
                "needs_human_review": bool(data.get("needs_human_review")),
                "state": "triage",
            }
            if data.get("consent"):
                req_vals["consent_date"] = fields.Datetime.now()
            # Coherencia tipo↔equipo/cita también al ACTUALIZAR (no solo al crear).
            if rtype in DEFAULT_TEAM_MAP:
                team, appt = DEFAULT_TEAM_MAP[rtype]
                req_vals["team"] = team or False
                req_vals["suggested_appointment_type"] = appt or False
            # Alto riesgo: menores/trata siempre rojo/urgente + revisión humana.
            if rtype in ("menores", "trata"):
                req_vals["risk_level"] = "red"
                req_vals["priority"] = "urgent"
                req_vals["needs_human_review"] = True

            if req:
                if req.assigned_user_id:
                    # Ya la gestiona una persona del equipo: NO re-clasificar ni
                    # reasignar (no pisar decisiones humanas). Solo escalar si procede.
                    minimal = {"needs_human_review": req.needs_human_review or req_vals["needs_human_review"]}
                    if req_vals.get("risk_level") == "red":
                        minimal.update(risk_level="red", priority="urgent")
                    req.write(minimal)
                else:
                    req.write(req_vals)
            else:
                req = Req.create(req_vals)

            # Registra el mensaje entrante en el hilo del canal.
            Msg.create({
                "request_id": req.id,
                "partner_id": partner.id,
                "direction": "inbound",
                "body": data.get("message_text") or False,
                "external_message_id": data.get("external_message_id") or False,
                "timestamp": fields.Datetime.now(),
                "raw_payload": data.get("raw_payload") or False,
                "processed_by_bot": True,
            })
            req.last_inbound_message_date = fields.Datetime.now()

            # Urgencia detectada por reglas en n8n → derivación inmediata.
            if data.get("risk_level") == "red" or data.get("priority") == "urgent":
                req.action_handoff_human()

            return {"ok": True, "request_ref": req.name, "partner_id": partner.id}
        except Exception as e:  # noqa: BLE001
            _logger.exception("acathi_intake inbound: error procesando payload")
            return {"ok": False, "error": str(e)}
