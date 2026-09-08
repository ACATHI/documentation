# -*- coding: utf-8 -*-
import base64
import json
import logging
from io import BytesIO
from datetime import datetime

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

TEXTS = {
    'ca': {
        'title': 'Firma digital',
        'intro': 'Llegiu el document i signeu a baix amb el dit.',
        'sign_here': 'Signeu aquí',
        'clear': 'Esborrar',
        'submit': 'Enviar firma',
        'submitting': 'Enviant...',
        'signed_title': 'Document firmat',
        'signed_msg': 'La vostra firma s\'ha registrat correctament. Gràcies.',
        'expired': 'Aquest enllaç ha caducat o ja ha estat utilitzat.',
        'error': 'S\'ha produït un error. Torneu-ho a intentar.',
        'empty_sig': 'Heu de signar abans d\'enviar.',
        'scroll': 'Desplaceu-vos per llegir el document',
        'lang_label': 'Idioma',
    },
    'es': {
        'title': 'Firma digital',
        'intro': 'Leed el documento y firmad abajo con el dedo.',
        'sign_here': 'Firmad aquí',
        'clear': 'Borrar',
        'submit': 'Enviar firma',
        'submitting': 'Enviando...',
        'signed_title': 'Documento firmado',
        'signed_msg': 'Vuestra firma se ha registrado correctamente. Gracias.',
        'expired': 'Este enlace ha caducado o ya ha sido utilizado.',
        'error': 'Se ha producido un error. Intentadlo de nuevo.',
        'empty_sig': 'Debéis firmar antes de enviar.',
        'scroll': 'Desplazaos para leer el documento',
        'lang_label': 'Idioma',
    },
    'en': {
        'title': 'Digital signature',
        'intro': 'Read the document and sign below with your finger.',
        'sign_here': 'Sign here',
        'clear': 'Clear',
        'submit': 'Submit signature',
        'submitting': 'Submitting...',
        'signed_title': 'Document signed',
        'signed_msg': 'Your signature has been recorded. Thank you.',
        'expired': 'This link has expired or has already been used.',
        'error': 'An error occurred. Please try again.',
        'empty_sig': 'Please sign before submitting.',
        'scroll': 'Scroll to read the document',
        'lang_label': 'Language',
    },
    'fr': {
        'title': 'Signature numérique',
        'intro': 'Lisez le document et signez ci-dessous avec le doigt.',
        'sign_here': 'Signez ici',
        'clear': 'Effacer',
        'submit': 'Envoyer la signature',
        'submitting': 'Envoi...',
        'signed_title': 'Document signé',
        'signed_msg': 'Votre signature a été enregistrée. Merci.',
        'expired': 'Ce lien a expiré ou a déjà été utilisé.',
        'error': 'Une erreur s\'est produite. Veuillez réessayer.',
        'empty_sig': 'Veuillez signer avant d\'envoyer.',
        'scroll': 'Faites défiler pour lire le document',
        'lang_label': 'Langue',
    },
    'ar': {
        'title': 'التوقيع الرقمي',
        'intro': 'اقرأ الوثيقة ووقّع أدناه بإصبعك.',
        'sign_here': 'وقّع هنا',
        'clear': 'مسح',
        'submit': 'إرسال التوقيع',
        'submitting': 'جارٍ الإرسال...',
        'signed_title': 'تم التوقيع على الوثيقة',
        'signed_msg': 'تم تسجيل توقيعك بنجاح. شكراً.',
        'expired': 'انتهت صلاحية هذا الرابط أو تم استخدامه بالفعل.',
        'error': 'حدث خطأ. يرجى المحاولة مرة أخرى.',
        'empty_sig': 'يجب التوقيع قبل الإرسال.',
        'scroll': 'اسحب للأسفل لقراءة الوثيقة',
        'lang_label': 'اللغة',
    },
    'ru': {
        'title': 'Цифровая подпись',
        'intro': 'Прочитайте документ и подпишите пальцем внизу.',
        'sign_here': 'Подпишите здесь',
        'clear': 'Очистить',
        'submit': 'Отправить подпись',
        'submitting': 'Отправка...',
        'signed_title': 'Документ подписан',
        'signed_msg': 'Ваша подпись зарегистрирована. Спасибо.',
        'expired': 'Ссылка устарела или уже была использована.',
        'error': 'Произошла ошибка. Попробуйте ещё раз.',
        'empty_sig': 'Пожалуйста, подпишите перед отправкой.',
        'scroll': 'Прокрутите, чтобы прочитать документ',
        'lang_label': 'Язык',
    },
    'uk': {
        'title': 'Цифровий підпис',
        'intro': 'Прочитайте документ і підпишіть пальцем внизу.',
        'sign_here': 'Підпишіть тут',
        'clear': 'Очистити',
        'submit': 'Надіслати підпис',
        'submitting': 'Надсилання...',
        'signed_title': 'Документ підписано',
        'signed_msg': 'Ваш підпис зареєстровано. Дякуємо.',
        'expired': 'Це посилання застаріло або вже було використано.',
        'error': 'Виникла помилка. Спробуйте ще раз.',
        'empty_sig': 'Будь ласка, підпишіть перед надсиланням.',
        'scroll': 'Прокрутіть, щоб прочитати документ',
        'lang_label': 'Мова',
    },
}

LANG_NAMES = {
    'ca': 'Català', 'es': 'Español', 'en': 'English',
    'fr': 'Français', 'ar': 'العربية', 'ru': 'Русский', 'uk': 'Українська',
}


def _embed_signature(pdf_bytes, signature_data, sig_x_pct=55.0, sig_y_pct=8.0, sig_page=0):
    """Embed a signature PNG onto a page of the PDF at the given position."""
    from PyPDF2 import PdfFileReader, PdfFileWriter
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.utils import ImageReader

    if ',' in signature_data:
        signature_data = signature_data.split(',')[1]
    sig_bytes = base64.b64decode(signature_data)

    pdf_reader = PdfFileReader(BytesIO(pdf_bytes))
    num_pages = pdf_reader.numPages

    # sig_page=0 means last page; otherwise 1-based index
    target_idx = num_pages - 1 if sig_page == 0 else max(0, min(int(sig_page) - 1, num_pages - 1))
    target = pdf_reader.getPage(target_idx)

    mb = target.mediaBox
    page_w = float(mb[2]) - float(mb[0])
    page_h = float(mb[3]) - float(mb[1])

    sig_w = page_w * 0.30
    sig_h = sig_w * 0.28
    sig_x = page_w * (sig_x_pct / 100.0)
    sig_y = page_h * (sig_y_pct / 100.0)

    # Keep signature within page bounds
    sig_x = min(sig_x, page_w - sig_w - 4)
    sig_y = max(sig_y, sig_h + 12)

    overlay_buf = BytesIO()
    c = rl_canvas.Canvas(overlay_buf, pagesize=(page_w, page_h))
    c.drawImage(ImageReader(BytesIO(sig_bytes)),
                sig_x, sig_y, width=sig_w, height=sig_h, mask='auto')
    c.setFont('Helvetica', 7)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(sig_x, sig_y - 10,
                 f"Signat digitalment: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    c.save()

    overlay_reader = PdfFileReader(overlay_buf)
    writer = PdfFileWriter()
    for i in range(num_pages):
        page = pdf_reader.getPage(i)
        if i == target_idx:
            page.mergePage(overlay_reader.getPage(0))
        writer.addPage(page)

    out = BytesIO()
    writer.write(out)
    return out.getvalue()


def _render_position_picker(session):
    doc = session.document_id
    cur = ''
    if session.sig_x_pct or session.sig_y_pct:
        pg = session.sig_page or 'última'
        cur = f"Actual: pàg. {pg}, X={session.sig_x_pct:.1f}%, Y={session.sig_y_pct:.1f}%"
    html = f'''<!DOCTYPE html>
<html lang="ca">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Posicionar firma — {session.signatory_name}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:system-ui,sans-serif;background:#f5f3ff;color:#1e1b4b;min-height:100vh;display:flex;flex-direction:column}}
header{{background:#5b21b6;color:#fff;padding:1rem 1.5rem}}
header h2{{font-size:1.05rem;margin-bottom:.2rem}}
header p{{font-size:.8rem;opacity:.85}}
.bar{{display:flex;align-items:center;gap:.75rem;padding:.6rem 1.5rem;background:#fff;border-bottom:1px solid #e0d7f7;flex-wrap:wrap}}
.btn{{padding:.4rem .9rem;border-radius:6px;border:none;cursor:pointer;font-size:.85rem;font-weight:600}}
.nav{{background:#ede9fe;color:#5b21b6}}.nav:disabled{{opacity:.4;cursor:not-allowed}}
.save{{background:#5b21b6;color:#fff}}.save:disabled{{background:#c4b5fd;cursor:not-allowed}}
.close{{background:#f3f4f6;color:#374151}}
#pg{{font-size:.85rem;color:#6b7280;flex:1;text-align:center}}
.scroll{{overflow:auto;flex:1;padding:1rem 1.5rem}}
.wrap{{position:relative;display:inline-block}}
#pdfCanvas{{display:block}}
#hit{{position:absolute;top:0;left:0;cursor:crosshair}}
.info{{padding:.5rem 1.5rem;font-size:.8rem;color:#5b21b6;background:#f5f3ff;border-top:1px solid #e0d7f7;min-height:1.8rem}}
footer{{display:flex;align-items:center;gap:.75rem;padding:.75rem 1.5rem;background:#fff;border-top:1px solid #e0d7f7;flex-wrap:wrap}}
.cur{{font-size:.78rem;color:#6b7280;flex:1}}
</style>
</head>
<body>
<header>
  <h2>Posicionar firma: {session.signatory_name}</h2>
  <p>Document: {doc.name} — Clica al PDF per marcar on ha d'anar la firma</p>
</header>
<div class="bar">
  <button class="btn nav" id="bPrev" onclick="go(-1)" disabled>◀</button>
  <span id="pg">Carregant…</span>
  <button class="btn nav" id="bNext" onclick="go(1)" disabled>▶</button>
</div>
<div class="scroll">
  <div class="wrap" id="wrap">
    <canvas id="pdfCanvas"></canvas>
    <canvas id="hit"></canvas>
  </div>
</div>
<div class="info" id="info">Clica sobre el PDF per marcar la posició de la firma</div>
<footer>
  <div class="cur" id="cur">{cur}</div>
  <button class="btn save" id="bSave" onclick="save()" disabled>Guardar posició</button>
  <button class="btn close" onclick="window.close()">Tancar</button>
</footer>
<script>
pdfjsLib.GlobalWorkerOptions.workerSrc='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
const PDF_URL='/firma/{session.token}/pdf',SAVE_URL='/firma-pos/{session.id}/save';
let pdf,cur=1,total=0,mk=null;
async function init(){{
  pdf=await pdfjsLib.getDocument(PDF_URL).promise;
  total=pdf.numPages;
  document.getElementById('bNext').disabled=total<=1;
  render(1);
}}
async function render(n){{
  cur=n;
  const pg=await pdf.getPage(n),vp=pg.getViewport({{scale:1.5}});
  const pc=document.getElementById('pdfCanvas'),hit=document.getElementById('hit');
  pc.width=hit.width=vp.width; pc.height=hit.height=vp.height;
  await pg.render({{canvasContext:pc.getContext('2d'),viewport:vp}}).promise;
  document.getElementById('pg').textContent=`Pàgina ${{n}} / ${{total}}`;
  document.getElementById('bPrev').disabled=n<=1;
  document.getElementById('bNext').disabled=n>=total;
  if(mk&&mk.p===n) drawMk(mk.xp,mk.yt); else clearMk();
}}
function drawMk(xp,yt){{
  const h=document.getElementById('hit'),ctx=h.getContext('2d');
  ctx.clearRect(0,0,h.width,h.height);
  const x=h.width*xp/100,y=h.height*yt/100,sw=h.width*.30,sh=sw*.28;
  ctx.strokeStyle='rgba(91,33,182,.35)';ctx.lineWidth=1;ctx.setLineDash([4,4]);
  ctx.strokeRect(x,y-sh,sw,sh);ctx.setLineDash([]);
  ctx.strokeStyle='#dc2626';ctx.lineWidth=2.5;
  ctx.beginPath();ctx.moveTo(x-10,y-10);ctx.lineTo(x+10,y+10);
  ctx.moveTo(x+10,y-10);ctx.lineTo(x-10,y+10);ctx.stroke();
}}
function clearMk(){{document.getElementById('hit').getContext('2d').clearRect(0,0,9999,9999);}}
document.getElementById('hit').addEventListener('click',function(e){{
  const r=this.getBoundingClientRect(),sx=this.width/r.width,sy=this.height/r.height;
  const cx=(e.clientX-r.left)*sx,cy=(e.clientY-r.top)*sy;
  const xp=cx/this.width*100,yt=cy/this.height*100,yb=100-yt;
  mk={{p:cur,xp,yt,yb}};
  drawMk(xp,yt);
  document.getElementById('info').textContent=`Pàgina ${{cur}}, X: ${{xp.toFixed(1)}}%, Y: ${{yb.toFixed(1)}}% des de baix`;
  document.getElementById('bSave').disabled=false;
}});
async function save(){{
  if(!mk)return;
  const btn=document.getElementById('bSave');
  btn.textContent='Guardant…';btn.disabled=true;
  try{{
    const r=await fetch(SAVE_URL,{{method:'POST',headers:{{'Content-Type':'application/json'}},
      body:JSON.stringify({{page:mk.p,x_pct:mk.xp,y_pct:mk.yb}})}});
    const d=await r.json();
    if(d.ok){{
      document.getElementById('cur').textContent=`✓ Guardat: pàg.${{mk.p}}, X=${{mk.xp.toFixed(1)}}%, Y=${{mk.yb.toFixed(1)}}%`;
      btn.textContent='✓ Guardat';
      setTimeout(()=>window.close(),1800);
    }}else{{btn.textContent='Guardar posició';btn.disabled=false;alert(d.error||'Error');}}
  }}catch(e){{btn.textContent='Guardar posició';btn.disabled=false;alert('Error de connexió');}}
}}
function go(d){{render(cur+d);}}
init();
</script>
</body>
</html>'''
    return html


def _render_portal(session, lang='ca', error=None):
    t = TEXTS.get(lang, TEXTS['ca'])
    doc = session.document_id
    is_rtl = lang == 'ar'

    lang_options = ''.join(
        f'<option value="{k}" {"selected" if k == lang else ""}>{v}</option>'
        for k, v in LANG_NAMES.items()
    )

    if session.state == 'signed':
        return f"""<!DOCTYPE html><html lang="{lang}" {"dir='rtl'" if is_rtl else ""}>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ACATHI — {t['signed_title']}</title>
<style>
:root{{--purple:#6b21a8;--green:#16a34a;}}
body{{margin:0;font-family:system-ui,sans-serif;background:#f5f3ff;display:flex;
  align-items:center;justify-content:center;min-height:100vh;padding:1rem;box-sizing:border-box;}}
.card{{background:#fff;border-radius:16px;padding:2rem;max-width:400px;width:100%;
  text-align:center;box-shadow:0 4px 24px rgba(0,0,0,.08);}}
.icon{{font-size:3rem;margin-bottom:1rem;}}
h1{{color:var(--green);font-size:1.4rem;margin:.5rem 0;}}
p{{color:#555;margin:.5rem 0;}}
</style></head>
<body><div class="card">
<div class="icon">✅</div>
<h1>{t['signed_title']}</h1>
<p>{t['signed_msg']}</p>
<p style="margin-top:1.5rem;font-size:.8rem;color:#999;">ACATHI</p>
</div></body></html>"""

    if session.state in ('expired',):
        return f"""<!DOCTYPE html><html lang="{lang}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ACATHI — Caducat</title>
<style>
body{{margin:0;font-family:system-ui,sans-serif;background:#fef2f2;display:flex;
  align-items:center;justify-content:center;min-height:100vh;padding:1rem;}}
.card{{background:#fff;border-radius:16px;padding:2rem;max-width:400px;width:100%;
  text-align:center;box-shadow:0 4px 24px rgba(0,0,0,.08);}}
</style></head>
<body><div class="card">
<div style="font-size:3rem">⏰</div>
<h1 style="color:#dc2626">{t['expired']}</h1>
</div></body></html>"""

    error_html = f'<div class="error">{error}</div>' if error else ''

    return f"""<!DOCTYPE html>
<html lang="{lang}" {"dir='rtl'" if is_rtl else ""}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>ACATHI — {t['title']}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/signature_pad/4.1.7/signature_pad.umd.min.js"></script>
<style>
:root{{
  --purple:#6b21a8;--purple-light:#f5f3ff;--purple-dark:#4c1d95;
  --border:#e5e7eb;--text:#1f2937;--muted:#6b7280;
}}
*{{box-sizing:border-box;}}
body{{margin:0;font-family:system-ui,-apple-system,sans-serif;
  background:var(--purple-light);color:var(--text);}}
header{{background:var(--purple);color:#fff;padding:.75rem 1rem;
  display:flex;align-items:center;gap:.75rem;position:sticky;top:0;z-index:10;}}
header img{{height:32px;}}
header h1{{margin:0;font-size:1rem;font-weight:600;flex:1;}}
.lang-select{{background:rgba(255,255,255,.15);border:none;color:#fff;
  border-radius:6px;padding:.25rem .5rem;font-size:.8rem;cursor:pointer;}}
.lang-select option{{background:#4c1d95;color:#fff;}}
main{{max-width:600px;margin:0 auto;padding:1rem;}}
.card{{background:#fff;border-radius:12px;padding:1.25rem;margin-bottom:1rem;
  box-shadow:0 2px 8px rgba(0,0,0,.06);}}
.doc-name{{font-weight:700;font-size:1.1rem;color:var(--purple-dark);margin-bottom:.25rem;}}
.intro{{color:var(--muted);font-size:.9rem;}}
.pdf-container{{background:#e5e7eb;border-radius:8px;overflow-y:auto;
  max-height:60vh;padding:.5rem;display:flex;flex-direction:column;gap:.5rem;}}
.pdf-container canvas{{width:100%!important;height:auto!important;
  border-radius:4px;box-shadow:0 1px 4px rgba(0,0,0,.15);}}
.scroll-hint{{text-align:center;color:var(--muted);font-size:.8rem;
  padding:.5rem;}}
.sig-wrapper{{border:2px dashed var(--border);border-radius:8px;
  background:#fafafa;overflow:hidden;position:relative;}}
.sig-wrapper canvas{{display:block;width:100%;touch-action:none;}}
.sig-label{{color:var(--muted);font-size:.85rem;margin-bottom:.5rem;}}
.btn-row{{display:flex;gap:.75rem;margin-top:.75rem;}}
.btn{{flex:1;padding:.75rem;border-radius:8px;font-size:1rem;
  font-weight:600;cursor:pointer;border:none;transition:.15s;}}
.btn-clear{{background:#f3f4f6;color:var(--text);}}
.btn-submit{{background:var(--purple);color:#fff;}}
.btn-submit:disabled{{background:#c4b5fd;cursor:not-allowed;}}
.error{{background:#fef2f2;border:1px solid #fca5a5;color:#dc2626;
  padding:.75rem;border-radius:8px;font-size:.9rem;margin-bottom:1rem;}}
.loading{{display:none;text-align:center;padding:2rem;color:var(--muted);}}
</style>
</head>
<body>
<header>
  <h1>ACATHI — {t['title']}</h1>
  <select class="lang-select" onchange="changeLang(this.value)">
    {lang_options}
  </select>
</header>
<main>
  {error_html}
  <div class="card">
    <div class="doc-name">{doc.name}</div>
    <div class="intro">{doc.description or t['intro']}</div>
  </div>

  <div class="card">
    <div class="scroll-hint">⬇ {t['scroll']}</div>
    <div class="pdf-container" id="pdfContainer">
      <div class="loading" id="pdfLoading">📄 Carregant...</div>
    </div>
  </div>

  <div class="card">
    <div class="sig-label">{t['sign_here']}</div>
    <div class="sig-wrapper">
      <canvas id="sigCanvas" height="180"></canvas>
    </div>
    <div class="btn-row">
      <button class="btn btn-clear" onclick="clearSig()">{t['clear']}</button>
      <button class="btn btn-submit" id="btnSubmit" onclick="submitSig()">
        {t['submit']}
      </button>
    </div>
  </div>
</main>

<script>
const TOKEN = "{session.token}";
const PDF_URL = "/firma/{session.token}/pdf";
const SUBMIT_URL = "/firma/{session.token}/submit";
const EMPTY_MSG = "{t['empty_sig']}";
const ERROR_MSG = "{t['error']}";
const SUBMITTING = "{t['submitting']}";

// PDF.js
pdfjsLib.GlobalWorkerOptions.workerSrc =
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

async function loadPdf() {{
  const container = document.getElementById('pdfContainer');
  try {{
    const pdf = await pdfjsLib.getDocument(PDF_URL).promise;
    for (let i = 1; i <= pdf.numPages; i++) {{
      const page = await pdf.getPage(i);
      const scale = container.clientWidth / page.getViewport({{scale:1}}).width * 0.96;
      const vp = page.getViewport({{scale}});
      const canvas = document.createElement('canvas');
      canvas.height = vp.height;
      canvas.width = vp.width;
      container.appendChild(canvas);
      await page.render({{canvasContext: canvas.getContext('2d'), viewport: vp}}).promise;
    }}
  }} catch(e) {{
    container.innerHTML = '<p style="color:#dc2626;text-align:center">Error carregant el PDF.</p>';
  }}
}}
loadPdf();

// SignaturePad
const sigCanvas = document.getElementById('sigCanvas');
sigCanvas.width = sigCanvas.parentElement.clientWidth;
const pad = new SignaturePad(sigCanvas, {{
  penColor: '#1e1b4b',
  backgroundColor: 'rgba(255,255,255,0)',
}});

window.addEventListener('resize', () => {{
  const ratio = window.devicePixelRatio || 1;
  const data = pad.toData();
  sigCanvas.width = sigCanvas.parentElement.clientWidth * ratio;
  sigCanvas.height = 180 * ratio;
  sigCanvas.getContext('2d').scale(ratio, ratio);
  pad.fromData(data);
}});

function clearSig() {{ pad.clear(); }}

function changeLang(lang) {{
  window.location.href = "/firma/{session.token}?lang=" + lang;
}}

async function submitSig() {{
  if (pad.isEmpty()) {{ alert(EMPTY_MSG); return; }}
  const btn = document.getElementById('btnSubmit');
  btn.disabled = true;
  btn.textContent = SUBMITTING;

  const sigData = pad.toDataURL('image/png');

  try {{
    const resp = await fetch(SUBMIT_URL, {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{signature: sigData, lang: "{lang}"}})
    }});
    const data = await resp.json();
    if (data.ok) {{
      window.location.href = "/firma/{session.token}?lang={lang}";
    }} else {{
      alert(data.error || ERROR_MSG);
      btn.disabled = false;
      btn.textContent = "{t['submit']}";
    }}
  }} catch(e) {{
    alert(ERROR_MSG);
    btn.disabled = false;
    btn.textContent = "{t['submit']}";
  }}
}}
</script>
</body>
</html>"""


class AcathiFirmaController(http.Controller):

    @http.route('/firma/<string:token>', type='http', auth='public', website=False)
    def firma_portal(self, token, lang='ca', **kwargs):
        session = request.env['acathi.firma.session'].sudo().search(
            [('token', '=', token)], limit=1)
        if not session:
            return request.make_response(
                '<h1>Enllaç no vàlid</h1>', headers=[('Content-Type', 'text/html')])
        if lang not in TEXTS:
            lang = 'ca'
        html = _render_portal(session, lang)
        return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])

    @http.route('/firma/<string:token>/pdf', type='http', auth='public')
    def firma_pdf(self, token, **kwargs):
        session = request.env['acathi.firma.session'].sudo().search(
            [('token', '=', token)], limit=1)
        if not session or session.state not in ('pending',):
            return request.make_response('', status=404)
        doc = session.document_id
        if not doc.document_file:
            return request.make_response('', status=404)
        pdf_bytes = base64.b64decode(doc.document_file)
        return request.make_response(
            pdf_bytes,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'inline; filename="{doc.document_filename or "document.pdf"}"'),
            ]
        )

    @http.route('/firma/<string:token>/qr', type='http', auth='public')
    def firma_qr(self, token, **kwargs):
        session = request.env['acathi.firma.session'].sudo().search(
            [('token', '=', token)], limit=1)
        if not session:
            return request.make_response('', status=404)
        url = session.portal_url
        try:
            import qrcode
            from PIL import Image
            qr = qrcode.QRCode(box_size=8, border=2)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color='#4c1d95', back_color='white')
            buf = BytesIO()
            img.save(buf, format='PNG')
            return request.make_response(
                buf.getvalue(), headers=[('Content-Type', 'image/png')])
        except ImportError:
            html = (f'<html><body style="font-family:monospace;padding:2rem">'
                    f'<h2>QR — {session.document_id.name}</h2>'
                    f'<p>{url}</p></body></html>')
            return request.make_response(
                html, headers=[('Content-Type', 'text/html')])

    @http.route('/firma/<string:token>/submit', type='http', auth='public',
                csrf=False, methods=['POST'])
    def firma_submit(self, token, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
        except (ValueError, TypeError):
            return request.make_response(
                json.dumps({'ok': False, 'error': 'Invalid request'}),
                headers=[('Content-Type', 'application/json')])

        signature = data.get('signature')
        lang = data.get('lang', 'ca')

        if not signature:
            return request.make_response(
                json.dumps({'ok': False, 'error': 'Firma no rebuda'}),
                headers=[('Content-Type', 'application/json')])

        session = request.env['acathi.firma.session'].sudo().search(
            [('token', '=', token)], limit=1)
        if not session:
            return request.make_response(
                json.dumps({'ok': False, 'error': 'Sessió no trobada'}),
                headers=[('Content-Type', 'application/json')])
        if session.state != 'pending':
            return request.make_response(
                json.dumps({'ok': False, 'error': 'Sessió ja completada o caducada'}),
                headers=[('Content-Type', 'application/json')])

        doc = session.document_id
        if not doc.document_file:
            return request.make_response(
                json.dumps({'ok': False, 'error': 'Document no disponible'}),
                headers=[('Content-Type', 'application/json')])

        try:
            # Use signed_master as base if previous signatures exist
            base_b64 = doc.signed_master or doc.document_file
            pdf_bytes = base64.b64decode(base_b64)
            signed_bytes = _embed_signature(
                pdf_bytes, signature,
                sig_x_pct=session.sig_x_pct,
                sig_y_pct=session.sig_y_pct,
                sig_page=session.sig_page,
            )
            sig_b64 = signature.split(',')[1] if ',' in signature else signature
            orig_name = doc.document_filename or 'document.pdf'
            signed_name = orig_name.replace('.pdf', '_firmat.pdf')
            master_name = orig_name.replace('.pdf', '_totes_firmes.pdf')

            session.write({
                'state': 'signed',
                'signed_document': base64.b64encode(signed_bytes),
                'signed_document_filename': signed_name,
                'signature_image': sig_b64,
                'signed_date': datetime.now(),
            })
            doc.write({
                'signed_master': base64.b64encode(signed_bytes),
                'signed_master_filename': master_name,
            })
            if doc.session_ids and all(s.state == 'signed' for s in doc.session_ids):
                doc.write({'state': 'completed'})
            session.message_post(
                body=f'Document firmat digitalment ({lang})',
                message_type='comment')
            return request.make_response(
                json.dumps({'ok': True}),
                headers=[('Content-Type', 'application/json')])
        except Exception as e:
            _logger.exception('Error embedding signature for token %s', token)
            return request.make_response(
                json.dumps({'ok': False, 'error': str(e)}),
                headers=[('Content-Type', 'application/json')])

    @http.route('/firma-pos/<int:session_id>', type='http', auth='user')
    def firma_pos_picker(self, session_id, **kwargs):
        session = request.env['acathi.firma.session'].browse(session_id)
        if not session.exists():
            return request.not_found()
        html = _render_position_picker(session)
        return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])

    @http.route('/firma-pos/<int:session_id>/save', type='http', auth='user',
                csrf=False, methods=['POST'])
    def firma_pos_save(self, session_id, **kwargs):
        session = request.env['acathi.firma.session'].browse(session_id)
        if not session.exists():
            return request.make_response(
                json.dumps({'ok': False, 'error': 'Sessió no trobada'}),
                headers=[('Content-Type', 'application/json')])
        try:
            data = json.loads(request.httprequest.data)
            session.write({
                'sig_x_pct': float(data.get('x_pct', 55.0)),
                'sig_y_pct': float(data.get('y_pct', 8.0)),
                'sig_page': int(data.get('page', 0)),
            })
            return request.make_response(
                json.dumps({'ok': True}),
                headers=[('Content-Type', 'application/json')])
        except Exception as e:
            return request.make_response(
                json.dumps({'ok': False, 'error': str(e)}),
                headers=[('Content-Type', 'application/json')])
