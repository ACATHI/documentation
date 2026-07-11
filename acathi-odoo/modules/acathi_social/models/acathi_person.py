# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class AcathiPerson(models.Model):
    _name = 'acathi.person'
    _description = 'Persona Atendida ACATHI'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'

    # ── IDENTIFICACIÓN ────────────────────────────────────────────
    name = fields.Char('Nombre completo', required=True, tracking=True)
    preferred_name = fields.Char('Nombre preferido', tracking=True,
        help='Nombre con el que prefiere ser llamada/o')
    partner_id = fields.Many2one('res.partner', string='Contacto',
        help='Contacto vinculado en la agenda')
    category_ids = fields.Many2many(
        'res.partner.category', string='Categorías',
        help='Categorías para agrupar personas atendidas')
    reference = fields.Char('Referencia', readonly=True, copy=False, default='Nueva')
    active = fields.Boolean('Activo', default=True)
    photo = fields.Image('Foto', max_width=256, max_height=256)
    state = fields.Selection([
        ('active', 'Activa/o'),
        ('followup', 'En seguimiento'),
        ('closed', 'Cerrada/o'),
        ('referred', 'Derivada/o'),
    ], string='Estado', default='active', tracking=True)

    # ── DATOS PERSONALES ──────────────────────────────────────────
    birth_date = fields.Date('Fecha de nacimiento')
    age = fields.Integer('Edad', compute='_compute_age', store=False)
    gender_identity = fields.Selection([
        ('trans_woman', 'Mujer trans'),
        ('trans_man', 'Hombre trans'),
        ('non_binary', 'No binario/a'),
        ('gender_fluid', 'Género fluido'),
        ('cis_woman', 'Mujer cisgénero'),
        ('cis_man', 'Hombre cisgénero'),
        ('other', 'Otro'),
        ('no_info', 'Prefiere no indicar'),
    ], string='Identidad de género', tracking=True)
    sexual_orientation = fields.Selection([
        ('homosexual', 'Gay/Lesbiana'),
        ('bisexual', 'Bisexual'),
        ('heterosexual', 'Heterosexual'),
        ('pansexual', 'Pansexual'),
        ('asexual', 'Asexual'),
        ('other', 'Otra'),
        ('no_info', 'Prefiere no indicar'),
    ], string='Orientación sexual',
        groups='acathi_social.group_acathi_professional')
    phone = fields.Char('Teléfono')
    mobile = fields.Char('Móvil')
    email = fields.Char('Email')
    emergency_contact = fields.Char('Contacto de emergencia')
    emergency_phone = fields.Char('Teléfono de emergencia')

    # ── ORIGEN Y MIGRACIÓN ────────────────────────────────────────
    nationality_id = fields.Many2one('res.country', string='Nacionalidad')
    origin_country_id = fields.Many2one('res.country', string='País de origen')
    transit_countries = fields.Text('Países de tránsito')
    migration_reason = fields.Selection([
        ('persecution_sexual', 'Persecución por orientación sexual/identidad de género'),
        ('persecution_political', 'Persecución política'),
        ('persecution_religious', 'Persecución religiosa'),
        ('violence', 'Violencia o conflicto armado'),
        ('economic', 'Motivos económicos'),
        ('family', 'Reunificación familiar'),
        ('other', 'Otros motivos'),
    ], string='Motivo de migración')
    arrival_date = fields.Date('Fecha llegada a España')
    arrival_city = fields.Char('Ciudad de llegada')

    # ── SITUACIÓN LEGAL ───────────────────────────────────────────
    legal_status = fields.Selection([
        ('regular', 'Situación regular'),
        ('irregular', 'Situación irregular'),
        ('asylum_seeker', 'Solicitante de asilo'),
        ('refugee', 'Refugiada/o reconocida/o'),
        ('stateless', 'Apátrida'),
        ('subsidiary_protection', 'Protección subsidiaria'),
        ('humanitarian', 'Razones humanitarias'),
    ], string='Situación legal', tracking=True)
    asylum_number = fields.Char('Nº expediente asilo')
    asylum_date = fields.Date('Fecha solicitud asilo')
    nie_number = fields.Char('NIE/TIE', groups='acathi_social.group_acathi_professional')
    nie_expiry = fields.Date('Caducidad NIE/TIE')
    passport_number = fields.Char('Nº Pasaporte', groups='acathi_social.group_acathi_professional')
    passport_expiry = fields.Date('Caducidad Pasaporte')

    # ── IDIOMAS ───────────────────────────────────────────────────
    language_ids = fields.One2many('acathi.person.language', 'person_id', string='Idiomas')
    spanish_level = fields.Selection([
        ('none', 'Sin conocimiento'),
        ('basic', 'Básico (A1-A2)'),
        ('intermediate', 'Intermedio (B1-B2)'),
        ('advanced', 'Avanzado (C1-C2)'),
        ('native', 'Nativo'),
    ], string='Nivel de español')

    # ── ESTUDIOS Y FORMACIÓN ──────────────────────────────────────
    education_level = fields.Selection([
        ('none', 'Sin estudios'),
        ('primary', 'Educación primaria'),
        ('secondary', 'Educación secundaria'),
        ('vocational', 'Formación profesional'),
        ('university', 'Universidad'),
        ('postgraduate', 'Posgrado/Máster/Doctorado'),
    ], string='Nivel de estudios máximo')
    education_homologated = fields.Boolean('Título homologado en España')
    education_homologation_state = fields.Selection([
        ('not_started', 'No iniciado'),
        ('in_progress', 'En trámite'),
        ('completed', 'Completado'),
    ], string='Estado homologación')
    education_ids = fields.One2many('acathi.person.education', 'person_id', string='Historial formativo')

    # ── SITUACIÓN LABORAL ─────────────────────────────────────────
    employment_status = fields.Selection([
        ('employed', 'Empleada/o'),
        ('unemployed', 'Desempleada/o'),
        ('searching', 'En búsqueda activa'),
        ('unable', 'No puede trabajar'),
        ('student', 'Estudiante'),
        ('volunteer', 'Voluntaria/o'),
    ], string='Situación laboral', tracking=True)
    work_permit = fields.Boolean('Permiso de trabajo')
    work_permit_expiry = fields.Date('Caducidad permiso trabajo')
    profession = fields.Char('Profesión/Oficio')
    employment_ids = fields.One2many('acathi.person.employment', 'person_id', string='Historial laboral')

    # ── SITUACIÓN FAMILIAR ────────────────────────────────────────
    family_status = fields.Selection([
        ('single', 'Soltera/o'),
        ('couple', 'En pareja'),
        ('married', 'Casada/o'),
        ('separated', 'Separada/o'),
        ('widowed', 'Viuda/o'),
    ], string='Estado civil')
    children_count = fields.Integer('Número de hijos/as')
    children_in_spain = fields.Integer('Hijos/as en España')
    children_origin = fields.Integer('Hijos/as en país de origen')
    family_reunification = fields.Boolean('Proceso reagrupación familiar')
    family_reunification_state = fields.Text('Estado reagrupación')
    family_notes = fields.Text('Notas situación familiar')

    # ── ALOJAMIENTO ───────────────────────────────────────────────
    housing_type = fields.Selection([
        ('acathi_house', 'Piso ACATHI'),
        ('own', 'Vivienda propia/alquilada'),
        ('shared', 'Piso compartido'),
        ('family', 'Con familia/amigos'),
        ('shelter', 'Centro de acogida'),
        ('homeless', 'Sin techo'),
        ('other', 'Otro'),
    ], string='Tipo de alojamiento', tracking=True)
    housing_id = fields.Many2one('acathi.housing', string='Piso ACATHI asignado')
    housing_address = fields.Char('Dirección actual')

    # ── SALUD ─────────────────────────────────────────────────────
    health_card = fields.Boolean('Tiene tarjeta sanitaria')
    health_card_pending = fields.Boolean('Gestión tarjeta sanitaria pendiente')
    health_notes = fields.Text('Notas de salud general',
        groups='acathi_social.group_acathi_professional')
    hiv_status = fields.Selection([
        ('positive', 'Positivo'),
        ('negative', 'Negativo'),
        ('unknown', 'Desconocido'),
        ('no_info', 'Prefiere no indicar'),
    ], string='Estado serológico VIH',
        groups='acathi_social.group_acathi_professional')
    hiv_treatment = fields.Boolean('En tratamiento antirretroviral (TAR)',
        groups='acathi_social.group_acathi_professional')
    hiv_followup_center = fields.Char('Centro de seguimiento VIH',
        groups='acathi_social.group_acathi_professional')
    last_hiv_test = fields.Date('Última prueba VIH',
        groups='acathi_social.group_acathi_professional')
    mental_health_followup = fields.Boolean('Seguimiento salud mental')
    mental_health_type = fields.Selection([
        ('internal', 'Interno ACATHI'),
        ('external', 'Derivado externo'),
        ('both', 'Ambos'),
    ], string='Tipo seguimiento salud mental',
        groups='acathi_social.group_acathi_professional')
    mental_health_center = fields.Char('Centro salud mental',
        groups='acathi_social.group_acathi_professional')
    mental_health_notes = fields.Text('Notas salud mental',
        groups='acathi_social.group_acathi_professional')
    trafficking_risk = fields.Boolean('Riesgo/víctima de trata',
        groups='acathi_social.group_acathi_professional')
    exploitation_risk = fields.Boolean('Riesgo/víctima de explotación',
        groups='acathi_social.group_acathi_professional')
    violence_risk = fields.Boolean('Situación de violencia',
        groups='acathi_social.group_acathi_professional')
    risk_notes = fields.Text('Notas situación de riesgo',
        groups='acathi_social.group_acathi_professional')

    # ── SITUACIÓN ECONÓMICA ───────────────────────────────────────
    income_source = fields.Selection([
        ('employment', 'Empleo'),
        ('rmi', 'RMI/Renta mínima'),
        ('rai', 'RAI'),
        ('family', 'Apoyo familiar'),
        ('ngo', 'Ayuda ONG'),
        ('none', 'Sin ingresos'),
        ('other', 'Otros'),
    ], string='Fuente de ingresos')
    monthly_income = fields.Float('Ingresos mensuales aprox. (€)',
        groups='acathi_social.group_acathi_professional')
    economic_aids = fields.Text('Ayudas económicas recibidas')

    # ── PRISIÓN ───────────────────────────────────────────────────
    prison_followup = fields.Boolean('Seguimiento en prisión')
    prison_name = fields.Char('Centro penitenciario')
    prison_entry_date = fields.Date('Fecha entrada prisión')
    prison_exit_date = fields.Date('Fecha salida/prevista')
    prison_notes = fields.Text('Notas seguimiento prisión',
        groups='acathi_social.group_acathi_professional')

    # ── GESTIÓN ACATHI ────────────────────────────────────────────
    responsible_id = fields.Many2one('hr.employee', string='Profesional responsable', tracking=True)
    entry_date = fields.Date('Fecha de alta', default=fields.Date.today)
    exit_date = fields.Date('Fecha de baja')
    exit_reason = fields.Selection([
        ('resolved', 'Situación resuelta'),
        ('referred', 'Derivada/o a otra entidad'),
        ('abandoned', 'Abandono voluntario'),
        ('lost_contact', 'Pérdida de contacto'),
        ('deceased', 'Fallecimiento'),
        ('other', 'Otros'),
    ], string='Motivo de baja')
    referral_entity = fields.Char('Entidad de derivación')
    gdpr_consent = fields.Boolean('Consentimiento RGPD firmado', tracking=True)
    gdpr_consent_date = fields.Date('Fecha consentimiento RGPD')
    confidential_notes = fields.Text('Notas confidenciales',
        groups='acathi_social.group_acathi_professional')

    # ── RELACIONES ────────────────────────────────────────────────
    case_ids = fields.One2many('acathi.case', 'person_id', string='Casos')
    case_count = fields.Integer('Nº Casos', compute='_compute_case_count')

    # ── COMPUTE ───────────────────────────────────────────────────
    @api.depends('birth_date')
    def _compute_age(self):
        for rec in self:
            if rec.birth_date:
                today = date.today()
                rec.age = today.year - rec.birth_date.year - (
                    (today.month, today.day) < (rec.birth_date.month, rec.birth_date.day)
                )
            else:
                rec.age = 0

    @api.depends('case_ids')
    def _compute_case_count(self):
        for rec in self:
            rec.case_count = len(rec.case_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'Nueva') == 'Nueva':
                vals['reference'] = self.env['ir.sequence'].next_by_code('acathi.person') or 'Nueva'
            if not vals.get('partner_id'):
                partner_name = (vals.get('preferred_name') or '').strip() or \
                               (vals.get('name') or '').strip()
                if partner_name:
                    partner = self.env['res.partner'].create({
                        'name': partner_name,
                        'phone': vals.get('phone') or False,
                        'mobile': vals.get('mobile') or False,
                        'email': vals.get('email') or False,
                        'comment': 'Persona atendida ACATHI',
                    })
                    vals['partner_id'] = partner.id
        return super().create(vals_list)

    def action_view_cases(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Casos',
            'res_model': 'acathi.case',
            'view_mode': 'list,form',
            'domain': [('person_id', '=', self.id)],
            'context': {'default_person_id': self.id},
        }


class AcathiPersonLanguage(models.Model):
    _name = 'acathi.person.language'
    _description = 'Idioma de persona atendida'

    person_id = fields.Many2one('acathi.person', string='Persona', required=True, ondelete='cascade')
    language = fields.Char('Idioma', required=True)
    level = fields.Selection([
        ('basic', 'Básico (A1-A2)'),
        ('intermediate', 'Intermedio (B1-B2)'),
        ('advanced', 'Avanzado (C1-C2)'),
        ('native', 'Nativo'),
    ], string='Nivel', required=True)
    can_read = fields.Boolean('Lee', default=True)
    can_write = fields.Boolean('Escribe', default=True)
    can_speak = fields.Boolean('Habla', default=True)


class AcathiPersonEducation(models.Model):
    _name = 'acathi.person.education'
    _description = 'Formación de persona atendida'

    person_id = fields.Many2one('acathi.person', string='Persona', required=True, ondelete='cascade')
    title = fields.Char('Título/Formación', required=True)
    institution = fields.Char('Centro/Institución')
    country_id = fields.Many2one('res.country', string='País')
    year_start = fields.Integer('Año inicio')
    year_end = fields.Integer('Año fin')
    completed = fields.Boolean('Completado', default=True)
    homologated = fields.Boolean('Homologado en España')
    homologation_state = fields.Selection([
        ('not_started', 'No iniciado'),
        ('in_progress', 'En trámite'),
        ('completed', 'Completado'),
    ], string='Estado homologación')
    notes = fields.Text('Observaciones')


class AcathiPersonEmployment(models.Model):
    _name = 'acathi.person.employment'
    _description = 'Historial laboral de persona atendida'

    person_id = fields.Many2one('acathi.person', string='Persona', required=True, ondelete='cascade')
    company = fields.Char('Empresa/Empleador')
    position = fields.Char('Puesto/Cargo', required=True)
    sector = fields.Char('Sector')
    country_id = fields.Many2one('res.country', string='País')
    date_start = fields.Date('Fecha inicio')
    date_end = fields.Date('Fecha fin')
    current = fields.Boolean('Trabajo actual')
    notes = fields.Text('Observaciones')
