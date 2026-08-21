from odoo import models, fields


VARIABLE_HELP = """Variables disponibles en les plantilles .docx (format {{variable}}):

── Persona atesa ─────────────────────────────
{{nom}}              Nom de la persona
{{cognoms}}          Cognoms
{{nom_complet}}      Nom i cognoms complets
{{data_naixement}}   Data de naixement
{{document_identitat}} NIE/TIE o Passaport
{{pais_origen}}      País d'origen
{{email}}            Correu electrònic
{{telefon}}          Telèfon
{{data_primer_contacte}}   Data d'alta / primer contacte
{{tipus_vinculacio}}        Tipus de serveis rebuts (acollida, legal…)
{{activitats_realitzades}}  Activitats en què ha participat (noms separats per comes)
{{activitats_detall}}       Llista detallada d'activitats: • Nom (data): descripció
{{atencions_realitzades}}   Atencions/intervencions rebudes (noms separats per comes)
{{atencions_detall}}        Llista detallada d'atencions: • Nom (data — tipus): descripció
{{periode_vinculacio}}      Període de vinculació (data alta — data baixa)
{{observacions_vinculacio}} Notes confidencials de la persona

── Activitat ─────────────────────────────────
{{nom_activitat}}    Nom de l'activitat
{{data_activitat}}   Data de l'activitat
{{lloc_activitat}}   Lloc de l'activitat
{{descripcio_activitat}}  Descripció

── Donació ───────────────────────────────────
{{donant}}           Nom del donant
{{import_donacio}}   Import (p.ex. 150,00 €)
{{data_donacio}}     Data de recepció
{{finalitat}}        Finalitat / destinació dels fons

── Genèriques ────────────────────────────────
{{data_avui}}        Data actual (dd/mm/aaaa)
{{any_actual}}       Any actual
{{num_ordre}}        Codi únic del document (p.ex. CERT-202608-A3F7K2)
"""


class AcathiDocumentTemplate(models.Model):
    _name = 'acathi.document.template'
    _description = 'Plantilla de document ACATHI'
    _order = 'template_type, name'

    name = fields.Char(string='Nom de la plantilla', required=True)
    template_type = fields.Selection([
        ('certificate', 'Certificat de participació'),
        ('donation', 'Rebut / certificat de donació'),
        ('report', 'Informe'),
        ('other', 'Altre'),
    ], string='Tipus', required=True, default='certificate')
    template_file = fields.Binary(string='Fitxer .docx', attachment=True)
    template_filename = fields.Char(string='Nom del fitxer')
    description = fields.Text(string='Notes internes')
    active = fields.Boolean(default=True)
    variable_help = fields.Text(
        string='Variables disponibles',
        default=VARIABLE_HELP,
        readonly=True,
    )
