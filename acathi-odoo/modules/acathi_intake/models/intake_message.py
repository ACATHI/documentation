# -*- coding: utf-8 -*-
from odoo import fields, models


class AcathiIntakeMessage(models.Model):
    _name = "acathi.intake.message"
    _description = "Mensaje de canal de acogida"
    _order = "timestamp asc, id asc"

    # Guarda el hilo de la PERSONA por el canal (entrante/saliente) con payload crudo.
    # Es distinto del chatter (mail.thread), que registra notas internas del equipo.
    request_id = fields.Many2one(
        "acathi.intake.request", string="Solicitud", required=True,
        ondelete="cascade", index=True,
    )
    partner_id = fields.Many2one("res.partner", string="Contacto")
    channel = fields.Selection(related="request_id.source_channel", store=True, string="Canal")
    direction = fields.Selection(
        [("inbound", "Entrante"), ("outbound", "Saliente")],
        string="Sentido", required=True,
    )
    body = fields.Text(string="Contenido", groups="acathi_intake.group_acathi_sensitive")
    external_message_id = fields.Char(string="ID externo del mensaje", index=True)
    timestamp = fields.Datetime(string="Marca de tiempo", required=True)
    raw_payload = fields.Text(string="Payload crudo (JSON)", groups="acathi_intake.group_acathi_sensitive")
    processed_by_bot = fields.Boolean(string="Procesado por bot")
