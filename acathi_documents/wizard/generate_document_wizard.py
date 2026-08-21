import base64
import io
import logging
import re
import secrets
import string
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def _replace_vars(text, variables):
    """Replace {{key}} placeholders in a string."""
    def replacer(m):
        return str(variables.get(m.group(1), m.group(0)))
    return re.sub(r'\{\{(\w+)\}\}', replacer, text)


def _set_run_with_breaks(run, text):
    """Set run text inserting <w:br/> for each \n character."""
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    r_elem = run._r
    # Remove existing w:t and w:br children
    for tag in (qn('w:t'), qn('w:br')):
        for child in r_elem.findall(tag):
            r_elem.remove(child)
    parts = text.split('\n')
    for i, part in enumerate(parts):
        if i > 0:
            br = OxmlElement('w:br')
            r_elem.append(br)
        t = OxmlElement('w:t')
        t.text = part
        if part != part.strip():
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        r_elem.append(t)


def _fill_docx(template_bytes, variables):
    """Fill a .docx template with variable substitution. Returns bytes."""
    try:
        from docx import Document
        from docx.oxml.ns import qn
    except ImportError:
        raise UserError(
            "Cal instal·lar python-docx al servidor:\n"
            "docker exec odoo17 pip install python-docx"
        )

    doc = Document(io.BytesIO(template_bytes))

    def process_paragraph(para):
        full = ''.join(r.text for r in para.runs)
        filled = _replace_vars(full, variables)
        if filled != full:
            if '\n' in filled:
                # Use first run with line-break elements, clear the rest
                if para.runs:
                    _set_run_with_breaks(para.runs[0], filled)
                    for run in para.runs[1:]:
                        run.text = ''
            else:
                for i, run in enumerate(para.runs):
                    run.text = filled if i == 0 else ''

    for para in doc.paragraphs:
        process_paragraph(para)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    process_paragraph(para)

    # Headers and footers
    for section in doc.sections:
        for hf in [section.header, section.footer]:
            if hf:
                for para in hf.paragraphs:
                    process_paragraph(para)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


class AcathiGenerateDocumentWizard(models.TransientModel):
    _name = 'acathi.generate.document.wizard'
    _description = 'Generador de documents ACATHI'

    template_type = fields.Selection([
        ('certificate', 'Certificat de participació'),
        ('donation', 'Rebut / certificat de donació'),
        ('report', 'Informe'),
        ('other', 'Altre'),
    ], string='Tipus de document', required=True, default='certificate')

    template_id = fields.Many2one(
        'acathi.document.template',
        string='Plantilla',
        required=True,
        domain="[('template_type', '=', template_type)]",
    )

    person_id = fields.Many2one('acathi.person', string='Persona atesa')
    activity_id = fields.Many2one('acathi.activity', string='Activitat')
    donation_id = fields.Many2one('acathi.donation', string='Donació')

    # Result
    result_file = fields.Binary(string='Document generat', readonly=True)
    result_filename = fields.Char(readonly=True)
    state = fields.Selection([
        ('draft', 'Configurar'),
        ('done', 'Descarregar'),
    ], default='draft')

    @api.onchange('template_type')
    def _onchange_template_type(self):
        self.template_id = False

    def _generate_code(self, prefix='DOC'):
        """Generate a unique code like CERT-202608-A3F7K2."""
        today = date.today()
        alphabet = string.ascii_uppercase + string.digits
        suffix = ''.join(secrets.choice(alphabet) for _ in range(6))
        return f'{prefix}-{today.strftime("%Y%m")}-{suffix}'

    def _build_variables(self):
        today = date.today()
        prefix_map = {
            'certificate': 'CERT',
            'donation': 'DON',
            'report': 'INF',
            'other': 'DOC',
        }
        prefix = prefix_map.get(self.template_type, 'DOC')
        v = {
            'data_avui': today.strftime('%d/%m/%Y'),
            'any_actual': str(today.year),
            'num_ordre': self._generate_code(prefix),
        }

        if self.person_id:
            p = self.person_id
            firstname = getattr(p, 'firstname', '') or ''
            lastname = getattr(p, 'lastname', '') or ''
            nom_complet = f'{firstname} {lastname}'.strip() or getattr(p, 'name', '') or ''

            # data_primer_contacte
            entry = getattr(p, 'entry_date', None)
            data_primer = entry.strftime('%d/%m/%Y') if entry else ''

            # periode_vinculacio
            exit_d = getattr(p, 'exit_date', None)
            if entry:
                fi = exit_d.strftime('%d/%m/%Y') if exit_d else today.strftime('%d/%m/%Y')
                periode = f'{entry.strftime("%d/%m/%Y")} — {fi}'
            else:
                periode = ''

            # tipus_vinculacio: tipus de casos actius únics
            CASE_TYPE_LABELS = {
                'reception': 'Acollida', 'legal': 'Legal / Asil',
                'psychological': 'Psicològic', 'labor': 'Laboral',
                'social': 'Social', 'health': 'Salut',
                'prison': 'Presó', 'housing': 'Allotjament',
            }
            cases = p.case_ids if hasattr(p, 'case_ids') else []
            tipus_set = []
            seen = set()
            for c in cases:
                ct = getattr(c, 'case_type', None)
                if ct and ct not in seen:
                    seen.add(ct)
                    tipus_set.append(CASE_TYPE_LABELS.get(ct, ct))
            tipus_vinculacio = ', '.join(tipus_set) if tipus_set else 'Persona atesa'

            # activitats_realitzades / activitats_detall
            activitats = self.env['acathi.activity'].sudo().search(
                [('participant_ids', 'in', p.id)], order='date asc'
            )
            noms_activitats = ', '.join(a.name for a in activitats) if activitats else ''
            detall_lines = []
            for a in activitats:
                data = a.date.strftime('%d/%m/%Y') if getattr(a, 'date', None) else ''
                desc = getattr(a, 'description', '') or ''
                line = f'• {a.name}'
                if data:
                    line += f' ({data})'
                if desc:
                    line += f': {desc}'
                detall_lines.append(line)
            activitats_detall = '\n'.join(detall_lines) if detall_lines else ''

            # atencions_realitzades / atencions_detall
            INTERV_TYPE_LABELS = {
                'interview': 'Entrevista', 'phone': 'Trucada telefònica',
                'email': 'Email/Missatge', 'accompaniment': 'Acompanyament',
                'management': 'Gestió/Tràmit', 'coordination': 'Coordinació',
                'group': 'Activitat grupal', 'visit': 'Visita domiciliària',
                'other': 'Altres',
            }
            intervencions = self.env['acathi.intervention'].sudo().search(
                [('person_id', '=', p.id)], order='date asc'
            )
            noms_atencions = ', '.join(i.name for i in intervencions) if intervencions else ''
            atencions_lines = []
            for i in intervencions:
                data = i.date.strftime('%d/%m/%Y') if getattr(i, 'date', None) else ''
                tipus = INTERV_TYPE_LABELS.get(getattr(i, 'intervention_type', ''), '')
                desc = getattr(i, 'description', '') or ''
                line = f'• {i.name}'
                if data:
                    line += f' ({data}'
                    if tipus:
                        line += f' — {tipus}'
                    line += ')'
                if desc:
                    line += f': {desc}'
                atencions_lines.append(line)
            atencions_detall = '\n'.join(atencions_lines) if atencions_lines else ''

            # observacions_vinculacio
            observacions = getattr(p, 'confidential_notes', '') or ''

            v.update({
                'nom': firstname or (nom_complet.split()[0] if nom_complet else ''),
                'cognoms': lastname or (' '.join(nom_complet.split()[1:]) if nom_complet else ''),
                'nom_complet': nom_complet,
                'data_naixement': p.birth_date.strftime('%d/%m/%Y') if getattr(p, 'birth_date', None) else '',
                'email': getattr(p, 'email', '') or '',
                'telefon': getattr(p, 'phone', '') or getattr(p, 'mobile', '') or '',
                'document_identitat': (
                    getattr(p.sudo(), 'nie_number', '') or
                    getattr(p.sudo(), 'passport_number', '') or ''
                ),
                'pais_origen': getattr(p.origin_country_id, 'name', '') if getattr(p, 'origin_country_id', None) else '',
                'data_primer_contacte': data_primer,
                'tipus_vinculacio': tipus_vinculacio,
                'activitats_realitzades': noms_activitats,
                'activitats_detall': activitats_detall,
                'atencions_realitzades': noms_atencions,
                'atencions_detall': atencions_detall,
                'periode_vinculacio': periode,
                'observacions_vinculacio': observacions,
            })

        if self.activity_id:
            a = self.activity_id
            v.update({
                'nom_activitat': getattr(a, 'name', '') or '',
                'data_activitat': a.date.strftime('%d/%m/%Y') if getattr(a, 'date', None) else '',
                'lloc_activitat': getattr(a, 'location', '') or getattr(a, 'lloc', '') or '',
                'descripcio_activitat': getattr(a, 'description', '') or '',
            })

        if self.donation_id:
            d = self.donation_id
            v.update({
                'donant': d.donor_id.name or '',
                'import_donacio': f'{d.amount:,.2f} €'.replace(',', 'X').replace('.', ',').replace('X', '.'),
                'data_donacio': d.date_received.strftime('%d/%m/%Y') if d.date_received else '',
                'finalitat': d.purpose or '',
            })

        return v

    def action_generate(self):
        self.ensure_one()
        if not self.template_id.template_file:
            raise UserError('La plantilla no té cap fitxer .docx carregat.')

        template_bytes = base64.b64decode(self.template_id.template_file)
        variables = self._build_variables()

        try:
            result_bytes = _fill_docx(template_bytes, variables)
        except UserError:
            raise
        except Exception as e:
            _logger.exception("Error generating document")
            raise UserError(f'Error en generar el document: {e}')

        # Build filename
        parts = [self.template_id.name.replace(' ', '_')]
        if self.person_id:
            parts.append(variables.get('nom_complet', '').replace(' ', '_'))
        if self.activity_id:
            parts.append(variables.get('nom_activitat', '')[:20].replace(' ', '_'))
        if self.donation_id:
            parts.append(variables.get('donant', '')[:20].replace(' ', '_'))
        parts.append(variables['data_avui'].replace('/', '-'))
        filename = '_'.join(filter(None, parts)) + '.docx'

        self.write({
            'result_file': base64.b64encode(result_bytes).decode(),
            'result_filename': filename,
            'state': 'done',
        })

        # Save to donation if applicable
        if self.donation_id and self.template_type == 'donation':
            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': base64.b64encode(result_bytes).decode(),
                'res_model': 'acathi.donation',
                'res_id': self.donation_id.id,
                'mimetype': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            })
            self.donation_id.write({
                'certificate_attachment_id': attachment.id,
                'state': 'receipt_sent',
            })

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
