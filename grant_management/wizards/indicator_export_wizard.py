import base64
import csv
import io

from odoo import fields, models, _


class GrantIndicatorExportWizard(models.TransientModel):
    _name = 'grant.indicator.export.wizard'
    _description = 'Exportar indicadors a CSV'

    funder_id = fields.Many2one(
        comodel_name='grant.funder',
        string='Finançador',
        help='Deixeu en blanc per exportar tots els finançadors',
    )
    call_id = fields.Many2one(
        comodel_name='grant.call',
        string='Convocatòria',
        help='Deixeu en blanc per exportar totes les convocatòries',
    )
    only_with_results = fields.Boolean(
        string='Només indicadors amb resultats',
        default=False,
        help='Filtra els indicadors que ja tenen valor assolit informat',
    )
    include_historical = fields.Boolean(
        string="Incloure indicadors d'anys anteriors",
        default=False,
    )

    def action_export_csv(self):
        self.ensure_one()

        domain = []
        if self.funder_id:
            domain.append(('application_id.funder_id', '=', self.funder_id.id))
        if self.call_id:
            domain.append(('application_id.call_id', '=', self.call_id.id))
        if self.only_with_results:
            domain.append(('achieved_value_num', '>', 0))

        indicators = self.env['grant.indicator'].search(
            domain,
            order='application_id, sequence',
        )

        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        writer.writerow([
            'Expedient',
            'Finançador',
            'Convocatòria',
            'Any',
            'Indicador',
            'Tipus',
            'Valor esperat (text)',
            'Valor esperat (núm.)',
            'Valor assolit (text)',
            'Valor assolit (núm.)',
            '% assoliment',
            'Semàfor',
            'Font de verificació',
        ])

        indicator_type_labels = dict(
            self.env['grant.indicator']._fields['indicator_type'].selection
        )
        traffic_light_labels = dict(
            self.env['grant.indicator']._fields['traffic_light'].selection
        )

        for ind in indicators:
            app = ind.application_id
            writer.writerow([
                app.name or '',
                app.funder_id.name or '',
                app.call_id.name or '',
                app.call_id.year or '',
                ind.name or '',
                indicator_type_labels.get(ind.indicator_type, ''),
                ind.expected_value or '',
                ind.expected_value_num if ind.expected_value_num else '',
                ind.achieved_value or '',
                ind.achieved_value_num if ind.achieved_value_num else '',
                f'{ind.achievement_pct:.1f}' if ind.achievement_pct else '',
                traffic_light_labels.get(ind.traffic_light, ''),
                ind.source or '',
            ])

        if self.include_historical:
            hist_domain = []
            if self.funder_id:
                hist_domain.append(('application_id.funder_id', '=', self.funder_id.id))
            if self.call_id:
                hist_domain.append(('application_id.call_id', '=', self.call_id.id))
            historical = self.env['grant.historical.indicator'].search(
                hist_domain,
                order='application_id, id',
            )
            if historical:
                writer.writerow([])
                writer.writerow(['=== INDICADORS HISTÒRICS (evolució 4 anys) ==='])
                writer.writerow([
                    'Expedient', 'Finançador',
                    'Indicador', 'Any N-3', 'Any N-2', 'Any N-1', 'Any actual (previsió)',
                ])
                for h in historical:
                    app = h.application_id
                    writer.writerow([
                        app.name or '',
                        app.funder_id.name or '',
                        h.name or '',
                        h.value_y1 or '',
                        h.value_y2 or '',
                        h.value_y3 or '',
                        h.value_y4 or '',
                    ])

        # Codificació UTF-8 BOM per compatibilitat Excel
        content = output.getvalue().encode('utf-8-sig')
        filename = 'indicadors_subvencions.csv'
        if self.call_id:
            safe_name = self.call_id.name.replace('/', '-').replace(' ', '_')[:40]
            filename = f'indicadors_{safe_name}.csv'
        elif self.funder_id:
            safe_name = self.funder_id.name.replace('/', '-').replace(' ', '_')[:40]
            filename = f'indicadors_{safe_name}.csv'

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(content),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'text/csv',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
