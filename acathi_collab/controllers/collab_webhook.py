# -*- coding: utf-8 -*-
"""Endpoint de entrada para colaboraciones (voluntariado/empleo/prácticas/empresa).

n8n recibe el mensaje del widget/formulario web y llama aquí para materializar
contacto (res.partner) + solicitud de colaboración. Datos ORDINARIOS.

Seguridad: cabecera 'X-Acathi-Token'. Reutiliza el mismo secreto que acathi_intake
('acathi_intake.inbound_token') para que n8n use un único token; si se define
'acathi_collab.inbound_token', ese tiene prioridad.
"""
import logging

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.acathi_collab.models.collab_request import DEFAULT_TEAM_MAP

_logger = logging.getLogger(__name__)


class AcathiCollabWebhook(http.Controller):

    def _check_token(self):
        Param = request.env["ir.config_parameter"].sudo()
        expected = Param.get_param("acathi_collab.inbound_token") \
            or Param.get_param("acathi_intake.inbound_token")
        got = request.httprequest.headers.get("X-Acathi-Token")
        return bool(expected) and got == expected

    def _person_name_vals(self, Partner, display_name):
        """Nombre de PERSONA compatible con y sin partner_firstname (OCA)."""
        name = (display_name or "").strip() or _("Contacto de colaboración")
        if "firstname" in Partner._fields:
            parts = name.split()
            if len(parts) > 1:
                return {"firstname": " ".join(parts[:-1]), "lastname": parts[-1]}
            return {"lastname": name}
        return {"name": name}

    def _company_name_vals(self, Partner, company_name):
        """Nombre de EMPRESA compatible con partner_firstname (name calculado)."""
        cname = (company_name or "").strip() or _("Empresa")
        if "firstname" in Partner._fields:
            return {"lastname": cname}  # name = lastname para is_company
        return {"name": cname}

    def _find_or_create_partner(self, env, data):
        Partner = env["res.partner"].sudo()
        is_company = data.get("collab_type") == "empresa"
        email = (data.get("email") or "").strip()
        phone = (data.get("phone") or "").strip()

        domain = []
        if email:
            domain = [("email", "=", email)]
        elif phone:
            domain = [("phone", "=", phone)]
        partner = Partner.search(domain, limit=1) if domain else Partner.browse()

        vals = {}
        if email:
            vals["email"] = email
        if phone:
            vals["phone"] = phone
        if partner:
            partner.write(vals)  # no tocamos el nombre de un contacto existente
        else:
            vals["is_company"] = is_company
            if is_company:
                vals.update(self._company_name_vals(
                    Partner, data.get("company_name") or data.get("display_name")))
            else:
                vals.update(self._person_name_vals(Partner, data.get("display_name")))
            partner = Partner.create(vals)
        return partner

    @http.route("/acathi_collab/inbound", type="json", auth="public",
                methods=["POST"], csrf=False)
    def inbound(self, **_kw):
        if not self._check_token():
            _logger.warning("acathi_collab inbound: token inválido")
            return {"ok": False, "error": "unauthorized"}
        data = request.get_json_data() if hasattr(request, "get_json_data") else request.jsonrequest
        env = request.env
        Collab = env["acathi.collab.request"].sudo()

        try:
            ctype = data.get("collab_type")
            if ctype not in dict(
                    env["acathi.collab.request"]._fields["collab_type"].selection):
                return {"ok": False, "error": "invalid_collab_type"}

            partner = self._find_or_create_partner(env, data)

            vals = {
                "collab_type": ctype,
                "partner_id": partner.id,
                "contact_name": data.get("display_name") or False,
                "email": (data.get("email") or "").strip() or False,
                "phone": (data.get("phone") or "").strip() or False,
                "has_whatsapp": bool(data.get("whatsapp")),
                "language": data.get("language") or "unknown",
                "company_name": data.get("company_name") or False,
                "study_center": data.get("study_center") or False,
                "area": data.get("area") or False,
                "availability": data.get("availability") or False,
                "collaboration_kind": data.get("collaboration_kind") or False,
                "event_subtype": data.get("event_subtype") or False,
                "message": data.get("message") or False,
                "source_channel": data.get("source_channel") or "web_chat",
                "channel_external_id": data.get("external_thread_id") or False,
                "consent_ok": bool(data.get("consent")),
                "consent_text_version": data.get("consent_text_version") or False,
                "state": "new",
            }
            if data.get("consent"):
                vals["consent_date"] = fields.Datetime.now()
            if ctype in DEFAULT_TEAM_MAP:
                vals["team"] = DEFAULT_TEAM_MAP[ctype]

            # event_subtype: sólo si es un valor válido del catálogo.
            valid_subtypes = dict(Collab._fields["event_subtype"].selection)
            if vals.get("event_subtype") not in valid_subtypes:
                vals["event_subtype"] = False
            # event_date: parseo defensivo (un formato raro NO debe tumbar el alta).
            raw_date = data.get("event_date")
            if raw_date:
                try:
                    vals["event_date"] = fields.Date.to_date(raw_date)
                except Exception:  # noqa: BLE001
                    vals["event_date"] = False
                    vals["message"] = ((vals.get("message") or "") +
                                        _("\n[Fecha indicada: %s]") % raw_date).strip()

            collab = Collab.create(vals)
            collab.message_post(body=_("Alta desde %s.") % (vals["source_channel"]))
            return {"ok": True, "request_ref": collab.name, "partner_id": partner.id}
        except Exception as e:  # noqa: BLE001
            _logger.exception("acathi_collab inbound: error procesando payload")
            return {"ok": False, "error": str(e)}
