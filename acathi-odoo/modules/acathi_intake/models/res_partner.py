# -*- coding: utf-8 -*-
from odoo import api, fields, models

from .intake_request import SOURCE_CHANNELS, LANGUAGES


class ResPartner(models.Model):
    _inherit = "res.partner"

    whatsapp_number = fields.Char(string="Número WhatsApp")
    telegram_user_id = fields.Char(string="ID de usuario Telegram", index=True)
    preferred_channel = fields.Selection(SOURCE_CHANNELS, string="Canal preferido")
    preferred_language = fields.Selection(LANGUAGES, string="Idioma preferido")
    needs_interpreter = fields.Boolean(string="Necesita interpretación")
    # Marca sensible: indica que es persona beneficiaria (revela condición LGTBIQ+/asilo).
    is_beneficiary_lgtbi = fields.Boolean(
        string="Beneficiario/a (acogida)", groups="acathi_intake.group_acathi_sensitive",
    )
    intake_request_ids = fields.One2many("acathi.intake.request", "partner_id", string="Solicitudes de acogida")
    intake_request_count = fields.Integer(compute="_compute_intake_request_count", string="Nº solicitudes")

    @api.depends("intake_request_ids")
    def _compute_intake_request_count(self):
        for partner in self:
            partner.intake_request_count = len(partner.intake_request_ids)
