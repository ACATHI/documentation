# -*- coding: utf-8 -*-
from odoo import fields, models


class ViajeOpcion(models.Model):
    _name = "acathi.viaje.opcion"
    _description = "Opción de viaje puntuada (resultado del Radar)"
    _order = "score_total desc, coste_total asc"

    solicitud_id = fields.Many2one(
        "acathi.viaje.solicitud", string="Solicitud",
        required=True, ondelete="cascade", index=True,
    )
    combo_id = fields.Char(string="ID combinación")
    aerolinea = fields.Char(string="Aerolínea / vuelo")
    nombre_alojamiento = fields.Char(string="Alojamiento")
    coste_vuelo = fields.Float(string="Coste vuelo (EUR)")
    coste_estadia = fields.Float(string="Coste estadía (EUR)")
    coste_total = fields.Float(string="Coste total (EUR)")
    score_total = fields.Float(string="Puntuación")
    categoria = fields.Selection(
        [
            ("recomendada", "Recomendada"),
            ("aceptable", "Aceptable"),
            ("comparada", "Comparada"),
            ("fuera_presupuesto", "Fuera de presupuesto"),
            ("descartada", "Descartada"),
        ],
        string="Categoría",
    )
    recomendacion = fields.Text(string="Motivo / recomendación")
    aviso_factura = fields.Boolean(string="Aviso factura")
    link_reserva_vuelo = fields.Char(string="Enlace vuelo")
    link_reserva_estadia = fields.Char(string="Enlace alojamiento")
    seleccionada = fields.Boolean(string="Seleccionada")
