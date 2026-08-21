import json
import os
import base64
import logging
from datetime import datetime

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

_FORM_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'src', 'consent_form.html')

_CONSENT_LABELS = {
    'ca': {
        'basic': 'Dades personals bàsiques',
        'legal': 'Situació migratòria i legal',
        'identity': 'Identitat de gènere i orientació sexual',
        'health': 'Dades de salut',
        'economic': 'Situació econòmica i habitatge',
        'risk': 'Situació de vulnerabilitat i risc',
    },
    'es': {
        'basic': 'Datos personales básicos',
        'legal': 'Situación migratoria y legal',
        'identity': 'Identidad de género y orientación sexual',
        'health': 'Datos de salud',
        'economic': 'Situación económica y vivienda',
        'risk': 'Situación de vulnerabilidad y riesgo',
    },
    'fr': {
        'basic': 'Données personnelles de base',
        'legal': 'Situation migratoire et juridique',
        'identity': 'Identité de genre et orientation sexuelle',
        'health': 'Données de santé',
        'economic': 'Situation économique et logement',
        'risk': 'Situation de vulnérabilité et risque',
    },
    'en': {
        'basic': 'Basic personal data',
        'legal': 'Migration and legal status',
        'identity': 'Gender identity and sexual orientation',
        'health': 'Health data',
        'economic': 'Economic situation and housing',
        'risk': 'Vulnerability and risk situation',
    },
    'ar': {
        'basic': 'البيانات الشخصية الأساسية',
        'legal': 'الوضع الهجرة والقانوني',
        'identity': 'الهوية الجنسية والميل الجنسي',
        'health': 'البيانات الصحية',
        'economic': 'الوضع الاقتصادي والسكن',
        'risk': 'الضعف والخطر',
    },
    'ru': {
        'basic': 'Основные персональные данные',
        'legal': 'Миграционный и правовой статус',
        'identity': 'Гендерная идентичность и сексуальная ориентация',
        'health': 'Данные о здоровье',
        'economic': 'Экономическое положение и жильё',
        'risk': 'Уязвимость и риск',
    },
    'uk': {
        'basic': 'Основні персональні дані',
        'legal': 'Міграційний та правовий статус',
        'identity': 'Гендерна ідентичність та сексуальна орієнтація',
        'health': 'Дані про здоров\'я',
        'economic': 'Економічне становище та житло',
        'risk': 'Вразливість і ризик',
    },
}

_DOCUMENT_STRINGS = {
    'ca': {
        'dir': 'ltr', 'lang': 'ca',
        'title': 'ACATHI — Consentiment Informat per al Tractament de Dades Personals',
        'org': "Associació Catalana per la Integració d'Homosexuals, Bisexuals i Transsexuals Immigrants",
        'signed_on': 'Document signat el', 'at': 'a',
        'sec_responsible': 'Responsable del tractament',
        'sec_person': 'Dades de la persona',
        'sec_categories': 'Categories de dades consentides',
        'sec_legal': 'Base legal i finalitat',
        'sec_rights': 'Els teus drets',
        'sec_signature': 'Signatura de la persona',
        'lbl_name': 'Nom complet', 'lbl_doc': 'Document (NIE / Passaport)',
        'lbl_dob': 'Data de naixement', 'lbl_email': 'Correu electrònic',
        'no_sig': '(signatura no capturada)',
        'not_consented': 'No consentit',
        'responsible_text': "ACATHI és una organització sense ànim de lucre que treballa per la integració social de persones LGBTIQ+ migrades i refugiades. Contacte: info@acathi.org · acathi.org",
        'legal_text': "El tractament de les dades bàsiques es basa en el consentiment explícit (art. 6.1.a RGPD). Les dades especialment sensibles (salut, orientació sexual, identitat de gènere, vulnerabilitat) es tracten per l'art. 9.2.a RGPD. Les dades es conservaran 5 anys posteriors al tancament de l'expedient.",
        'rights_text': "Pots exercir els drets d'accés, rectificació, supressió, portabilitat, oposició i limitació a info@acathi.org. Pots reclamar davant l'Agència Catalana de Protecció de Dades (apdcat.cat) o l'AEPD (aepd.es).",
        'footer': 'Base legal: art. 6.1.a i art. 9.2.a Reglament (UE) 2016/679 (RGPD) + LOPDGDD 3/2018 · acathi.org',
    },
    'es': {
        'dir': 'ltr', 'lang': 'es',
        'title': 'ACATHI — Consentimiento Informado para el Tratamiento de Datos Personales',
        'org': 'Asociación Catalana para la Integración de Homosexuales, Bisexuales y Transexuales Inmigrantes',
        'signed_on': 'Documento firmado el', 'at': 'en',
        'sec_responsible': 'Responsable del tratamiento',
        'sec_person': 'Tus datos',
        'sec_categories': 'Categorías de datos consentidas',
        'sec_legal': 'Base legal y finalidad',
        'sec_rights': 'Tus derechos',
        'sec_signature': 'Firma de la persona',
        'lbl_name': 'Nombre completo', 'lbl_doc': 'Documento (NIE / Pasaporte)',
        'lbl_dob': 'Fecha de nacimiento', 'lbl_email': 'Correo electrónico',
        'no_sig': '(firma no capturada)',
        'not_consented': 'No consentido',
        'responsible_text': 'ACATHI es una organización sin ánimo de lucro que trabaja por la integración social de personas LGBTIQ+ migradas y refugiadas. Contacto: info@acathi.org · acathi.org',
        'legal_text': 'El tratamiento de los datos básicos se basa en el consentimiento explícito (art. 6.1.a RGPD). Los datos especialmente sensibles (salud, orientación sexual, identidad de género, vulnerabilidad) se tratan por el art. 9.2.a RGPD. Los datos se conservarán 5 años tras el cierre del expediente.',
        'rights_text': 'Puedes ejercer los derechos de acceso, rectificación, supresión, portabilidad, oposición y limitación en info@acathi.org. Puedes reclamar ante la Agencia Española de Protección de Datos (aepd.es).',
        'footer': 'Base legal: art. 6.1.a y art. 9.2.a Reglamento (UE) 2016/679 (RGPD) + LOPDGDD 3/2018 · acathi.org',
    },
    'fr': {
        'dir': 'ltr', 'lang': 'fr',
        'title': 'ACATHI — Consentement éclairé au traitement des données personnelles',
        'org': "Association Catalane pour l'Intégration des Homosexuels, Bisexuels et Transsexuels Immigrants",
        'signed_on': 'Document signé le', 'at': 'à',
        'sec_responsible': 'Responsable du traitement',
        'sec_person': 'Vos données',
        'sec_categories': 'Catégories de données consenties',
        'sec_legal': 'Base légale et finalité',
        'sec_rights': 'Vos droits',
        'sec_signature': 'Signature de la personne',
        'lbl_name': 'Nom complet', 'lbl_doc': 'Document (NIE / Passeport)',
        'lbl_dob': 'Date de naissance', 'lbl_email': 'Adresse e-mail',
        'no_sig': '(signature non capturée)',
        'not_consented': 'Non consenti',
        'responsible_text': "ACATHI est une organisation à but non lucratif qui œuvre pour l'intégration sociale des personnes LGBTIQ+ migrantes et réfugiées. Contact: info@acathi.org · acathi.org",
        'legal_text': "Le traitement des données de base repose sur le consentement explicite (art. 6.1.a RGPD). Les données sensibles (santé, orientation sexuelle, identité de genre, vulnérabilité) sont traitées en vertu de l'art. 9.2.a RGPD. Les données seront conservées 5 ans après la clôture du dossier.",
        'rights_text': "Vous pouvez exercer vos droits d'accès, de rectification, d'effacement, de portabilité, d'opposition et de limitation à info@acathi.org. Vous pouvez vous adresser à l'autorité de contrôle compétente.",
        'footer': 'Base légale: art. 6.1.a et art. 9.2.a Règlement (UE) 2016/679 (RGPD) · acathi.org',
    },
    'en': {
        'dir': 'ltr', 'lang': 'en',
        'title': 'ACATHI — Informed Consent for Personal Data Processing',
        'org': 'Catalan Association for the Integration of Homosexual, Bisexual and Transgender Immigrants',
        'signed_on': 'Document signed on', 'at': 'in',
        'sec_responsible': 'Data Controller',
        'sec_person': 'Your data',
        'sec_categories': 'Consented data categories',
        'sec_legal': 'Legal basis and purpose',
        'sec_rights': 'Your rights',
        'sec_signature': 'Signature',
        'lbl_name': 'Full name', 'lbl_doc': 'Document (NIE / Passport)',
        'lbl_dob': 'Date of birth', 'lbl_email': 'Email address',
        'no_sig': '(signature not captured)',
        'not_consented': 'Not consented',
        'responsible_text': 'ACATHI is a non-profit organization working for the social integration of LGBTIQ+ migrants and refugees. Contact: info@acathi.org · acathi.org',
        'legal_text': 'Processing of basic data is based on explicit consent (art. 6.1.a GDPR). Sensitive data (health, sexual orientation, gender identity, vulnerability) is processed under art. 9.2.a GDPR. Data will be retained for 5 years after case closure.',
        'rights_text': 'You may exercise your rights of access, rectification, erasure, portability, objection and restriction at info@acathi.org. You may lodge a complaint with the competent supervisory authority.',
        'footer': 'Legal basis: art. 6.1.a and art. 9.2.a Regulation (EU) 2016/679 (GDPR) · acathi.org',
    },
    'ar': {
        'dir': 'rtl', 'lang': 'ar',
        'title': 'ACATHI — موافقة مستنيرة على معالجة البيانات الشخصية',
        'org': 'الجمعية الكتالونية لدمج المهاجرين من مجتمع الميم',
        'signed_on': 'وثيقة موقعة بتاريخ', 'at': 'في',
        'sec_responsible': 'المسؤول عن المعالجة',
        'sec_person': 'بياناتك',
        'sec_categories': 'فئات البيانات الموافق عليها',
        'sec_legal': 'الأساس القانوني والغرض',
        'sec_rights': 'حقوقك',
        'sec_signature': 'توقيع الشخص',
        'lbl_name': 'الاسم الكامل', 'lbl_doc': 'وثيقة الهوية (NIE / جواز السفر)',
        'lbl_dob': 'تاريخ الميلاد', 'lbl_email': 'البريد الإلكتروني',
        'no_sig': '(لم يتم التقاط التوقيع)',
        'not_consented': 'غير موافق عليه',
        'responsible_text': 'ACATHI منظمة غير ربحية تعمل على الاندماج الاجتماعي للمهاجرين واللاجئين من مجتمع الميم. للتواصل: info@acathi.org · acathi.org',
        'legal_text': 'تستند معالجة البيانات الأساسية إلى الموافقة الصريحة (المادة 6.1.أ من اللائحة الأوروبية). تُعالج البيانات الحساسة (الصحة، التوجه الجنسي، الهوية الجنسية، الضعف) وفق المادة 9.2.أ. يتم الاحتفاظ بالبيانات 5 سنوات بعد إغلاق الملف.',
        'rights_text': 'يحق لك ممارسة حقوق الوصول والتصحيح والحذف والنقل والاعتراض والتقييد على info@acathi.org.',
        'footer': 'الأساس القانوني: المادة 6.1.أ و9.2.أ من اللائحة الأوروبية RGPD · acathi.org',
    },
    'ru': {
        'dir': 'ltr', 'lang': 'ru',
        'title': 'ACATHI — Информированное согласие на обработку персональных данных',
        'org': 'Каталонская ассоциация по интеграции ЛГБТИК+ мигрантов и беженцев',
        'signed_on': 'Документ подписан', 'at': 'в',
        'sec_responsible': 'Ответственный за обработку',
        'sec_person': 'Ваши данные',
        'sec_categories': 'Категории данных, на которые дано согласие',
        'sec_legal': 'Правовая основа и цель',
        'sec_rights': 'Ваши права',
        'sec_signature': 'Подпись',
        'lbl_name': 'Полное имя', 'lbl_doc': 'Документ (NIE / Паспорт)',
        'lbl_dob': 'Дата рождения', 'lbl_email': 'Электронная почта',
        'no_sig': '(подпись не получена)',
        'not_consented': 'Не согласовано',
        'responsible_text': 'ACATHI — некоммерческая организация по социальной интеграции ЛГБТИК+ мигрантов и беженцев. Контакт: info@acathi.org · acathi.org',
        'legal_text': 'Обработка базовых данных основана на явном согласии (ст. 6.1.а GDPR). Чувствительные данные (здоровье, сексуальная ориентация, гендерная идентичность, уязвимость) обрабатываются по ст. 9.2.а GDPR. Данные хранятся 5 лет после закрытия дела.',
        'rights_text': 'Вы можете воспользоваться правами доступа, исправления, удаления, переносимости, возражения и ограничения по адресу info@acathi.org.',
        'footer': 'Правовая основа: ст. 6.1.а и ст. 9.2.а Регламент (ЕС) 2016/679 (GDPR) · acathi.org',
    },
    'uk': {
        'dir': 'ltr', 'lang': 'uk',
        'title': 'ACATHI — Інформована згода на обробку персональних даних',
        'org': 'Каталонська асоціація з інтеграції ЛГБТІК+ мігрантів та біженців',
        'signed_on': 'Документ підписано', 'at': 'у',
        'sec_responsible': 'Відповідальний за обробку',
        'sec_person': 'Ваші дані',
        'sec_categories': 'Категорії даних, на які надано згоду',
        'sec_legal': 'Правова підстава та мета',
        'sec_rights': 'Ваші права',
        'sec_signature': 'Підпис',
        'lbl_name': "Повне ім'я", 'lbl_doc': 'Документ (NIE / Паспорт)',
        'lbl_dob': 'Дата народження', 'lbl_email': 'Електронна пошта',
        'no_sig': '(підпис не отримано)',
        'not_consented': 'Не погоджено',
        'responsible_text': 'ACATHI — некомерційна організація із соціальної інтеграції ЛГБТІК+ мігрантів та біженців. Контакт: info@acathi.org · acathi.org',
        'legal_text': "Обробка базових даних ґрунтується на явній згоді (ст. 6.1.а GDPR). Чутливі дані (здоров'я, сексуальна орієнтація, гендерна ідентичність, вразливість) обробляються за ст. 9.2.а GDPR. Дані зберігаються 5 років після закриття справи.",
        'rights_text': 'Ви можете скористатися правами доступу, виправлення, видалення, переносимості, заперечення та обмеження за адресою info@acathi.org.',
        'footer': 'Правова підстава: ст. 6.1.а та ст. 9.2.а Регламент (ЄС) 2016/679 (GDPR) · acathi.org',
    },
}


def _render_consent_document(data, lang='ca'):
    consents = data.get('consents', {})
    labels = _CONSENT_LABELS.get(lang, _CONSENT_LABELS['ca'])
    s = _DOCUMENT_STRINGS.get(lang, _DOCUMENT_STRINGS['ca'])

    consented = [labels[k] for k, v in consents.items() if v and k in labels]
    not_consented = [labels[k] for k, v in consents.items() if not v and k in labels]

    sig = data.get('signature', '')
    values = {
        's': s,
        'lang': lang,
        'signer_name': f"{data.get('firstName', '')} {data.get('lastName', '')}".strip(),
        'signer_doc': data.get('docNum', '') or '',
        'dob': data.get('dob', '') or '',
        'email': data.get('email', '') or '',
        'consent_date': data.get('consentDate', ''),
        'consent_place': data.get('consentPlace', 'Barcelona'),
        'consented_categories': consented,
        'not_consented_categories': not_consented,
        'signature_image': sig if (sig and sig.startswith('data:image')) else None,
    }
    try:
        html_bytes = request.env['ir.qweb'].sudo()._render('acathi_consent.consent_document', values)
        return html_bytes.decode('utf-8') if isinstance(html_bytes, bytes) else html_bytes
    except Exception:
        _logger.exception("QWeb render failed for lang=%s", lang)
        return _build_consent_document_fallback(data, s, consented, not_consented, sig)


def _build_consent_document_fallback(data, s, consented, not_consented, sig):
    consented_li = ''.join(f'<li style="color:#1E7A4A">&#10003; {l}</li>' for l in consented)
    not_consented_li = ''.join(f'<li style="color:#999">&#10007; {l} ({s["not_consented"]})</li>' for l in not_consented)
    sig_html = f'<img src="{sig}" style="max-width:320px;border:1px solid #ccc;border-radius:6px;">' if sig and sig.startswith('data:image') else f'<p style="color:#999">{s["no_sig"]}</p>'
    return f"""<!DOCTYPE html><html lang="{s['lang']}" dir="{s['dir']}">
<head><meta charset="UTF-8"><title>{s['title']}</title>
<style>body{{font-family:Arial,sans-serif;max-width:720px;margin:40px auto;padding:20px;color:#222;line-height:1.6}}
h1{{color:#5B2D8E;border-bottom:2px solid #5B2D8E;padding-bottom:10px}}
.section{{margin:20px 0;padding:16px;border:1px solid #ddd;border-radius:6px}}
h2{{font-size:13px;text-transform:uppercase;color:#5B2D8E;margin:0 0 12px}}
.label{{font-weight:bold;color:#666;font-size:11px;text-transform:uppercase}}
.value{{font-size:15px;margin:3px 0 12px}}ul{{padding-left:20px}}li{{margin:4px 0;font-size:14px}}
.footer{{margin-top:40px;font-size:11px;color:#999;border-top:1px solid #eee;padding-top:16px}}</style>
</head><body>
<h1>{s['title']}</h1>
<p style="color:#888;font-size:13px">{s['org']}<br>{s['signed_on']} <strong>{data.get('consentDate','')}</strong> {s['at']} <strong>{data.get('consentPlace','')}</strong></p>
<div class="section"><h2>{s['sec_person']}</h2>
<div class="label">{s['lbl_name']}</div><div class="value">{data.get('firstName','')} {data.get('lastName','')}</div>
<div class="label">{s['lbl_doc']}</div><div class="value">{data.get('docNum','—') or '—'}</div>
<div class="label">{s['lbl_dob']}</div><div class="value">{data.get('dob','—') or '—'}</div>
<div class="label">{s['lbl_email']}</div><div class="value">{data.get('email','—') or '—'}</div></div>
<div class="section"><h2>{s['sec_categories']}</h2><ul>{consented_li}{not_consented_li}</ul></div>
<div class="section"><h2>{s['sec_signature']}</h2>{sig_html}</div>
<div class="footer">{s['footer']}</div></body></html>"""


class AcathiConsentController(http.Controller):

    def _get_request_or_error(self, token):
        return request.env['acathi.consent.request'].sudo().search(
            [('token', '=', token)], limit=1
        ) or None

    @http.route('/acathi/consent/<string:token>', type='http', auth='public', website=False, csrf=False)
    def consent_form(self, token, **kwargs):
        consent_req = self._get_request_or_error(token)

        def html_page(content):
            return request.make_response(content, headers=[('Content-Type', 'text/html; charset=utf-8')])

        if not consent_req:
            return html_page('<html><body style="font-family:sans-serif;padding:40px;text-align:center"><h2>Enllaç no vàlid / Invalid link</h2><p>Contacte: info@acathi.org</p></body></html>')
        if consent_req.state == 'signed':
            return html_page('<html><body style="font-family:sans-serif;padding:40px;text-align:center"><h2 style="color:#1E7A4A">&#10003; Ja signat / Already signed</h2><p>Gràcies / Thank you</p></body></html>')
        if consent_req.state == 'expired':
            return html_page('<html><body style="font-family:sans-serif;padding:40px;text-align:center"><h2>Caducat / Expired</h2><p>Demana un nou formulari / Request a new form</p></body></html>')

        lang = consent_req.language or 'ca'
        try:
            with open(_FORM_PATH, 'r', encoding='utf-8') as f:
                html = f.read()
        except Exception:
            _logger.exception("Cannot read consent_form.html")
            return request.make_response('Error intern.', status=500)

        html = html.replace('__TOKEN__', token).replace('__LANG__', lang)
        return html_page(html)

    @http.route('/acathi/consent/<string:token>/submit', type='http', auth='public',
                methods=['POST'], csrf=False)
    def consent_submit(self, token, **kwargs):
        def json_response(data, status=200):
            return request.make_response(
                json.dumps(data),
                headers=[('Content-Type', 'application/json')],
                status=status,
            )

        consent_req = self._get_request_or_error(token)
        if not consent_req:
            return json_response({'success': False, 'error': 'Token no vàlid'}, 404)
        if consent_req.state != 'pending':
            return json_response({'success': False, 'error': 'Ja processat o caducat'}, 409)

        try:
            data = json.loads(request.httprequest.data or b'{}')
        except (ValueError, TypeError):
            return json_response({'success': False, 'error': 'Format incorrecte'}, 400)

        consents = data.get('consents', {})
        first = (data.get('firstName') or '').strip()
        last = (data.get('lastName') or '').strip()
        if not first or not last:
            return json_response({'success': False, 'error': 'Falten nom i cognoms'}, 400)
        if not consents.get('basic'):
            return json_response({'success': False, 'error': 'Cal acceptar les dades bàsiques'}, 400)

        lang = consent_req.language or 'ca'
        labels = _CONSENT_LABELS.get(lang, _CONSENT_LABELS['ca'])
        consented_labels = [v for k, v in labels.items() if consents.get(k)]

        html_doc = _render_consent_document(data, lang)
        date_str = data.get('consentDate') or datetime.now().strftime('%Y-%m-%d')
        filename = f"Consentiment_RGPD_{last}_{first}_{date_str}_{lang}.html"

        person = consent_req.person_id
        try:
            attachment = request.env['ir.attachment'].sudo().create({
                'name': filename,
                'type': 'binary',
                'datas': base64.b64encode(html_doc.encode('utf-8')).decode('ascii'),
                'res_model': 'acathi.person',
                'res_id': person.id,
                'mimetype': 'text/html',
            })

            consent_req.sudo().write({
                'state': 'signed',
                'signed_at': datetime.now(),
                'signer_name': f'{first} {last}',
                'signer_doc': data.get('docNum', ''),
                'consent_basic': bool(consents.get('basic')),
                'consent_legal': bool(consents.get('legal')),
                'consent_identity': bool(consents.get('identity')),
                'consent_health': bool(consents.get('health')),
                'consent_economic': bool(consents.get('economic')),
                'consent_risk': bool(consents.get('risk')),
                'attachment_id': attachment.id,
            })

            body = (
                f"<b>&#10003; Consentiment RGPD signat</b> [{lang.upper()}] el {date_str} "
                f"per <b>{first} {last}</b>"
                + (f" (Doc: {data.get('docNum')})" if data.get('docNum') else '')
                + f".<br/>Categories: {', '.join(consented_labels)}."
            )
            person.sudo().message_post(
                body=body,
                subtype_xmlid='mail.mt_note',
                attachment_ids=[attachment.id],
            )
        except Exception:
            _logger.exception("Error saving consent for token %s", token)
            return json_response({'success': False, 'error': 'Error intern'}, 500)

        return json_response({'success': True})
