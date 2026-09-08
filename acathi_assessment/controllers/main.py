# -*- coding: utf-8 -*-
import json
from odoo import http, fields
from odoo.http import request

# ─── Dades dels instruments (7 idiomes × 6 instruments) ──────────────────────

LANG_LABELS = {
    'ca': {'name': 'Català',    'dir': 'ltr', 'flag': '🏳️‍🌈'},
    'es': {'name': 'Castellà',  'dir': 'ltr', 'flag': '🇪🇸'},
    'en': {'name': 'English',   'dir': 'ltr', 'flag': '🇬🇧'},
    'fr': {'name': 'Français',  'dir': 'ltr', 'flag': '🇫🇷'},
    'ar': {'name': 'عربي',      'dir': 'rtl', 'flag': '🌍'},
    'ru': {'name': 'Русский',   'dir': 'ltr', 'flag': '🇷🇺'},
    'uk': {'name': 'Українська','dir': 'ltr', 'flag': '🇺🇦'},
}

INSTRUMENTS = {

    # ── PHQ-9 ──────────────────────────────────────────────────────────────────
    'phq9': {
        'title': {
            'ca': 'PHQ-9 — Qüestionari de Salut del Pacient',
            'es': 'PHQ-9 — Cuestionario sobre la Salud del Paciente',
            'en': 'PHQ-9 — Patient Health Questionnaire',
            'fr': 'PHQ-9 — Questionnaire sur la Santé du Patient',
            'ar': 'PHQ-9 — استبيان صحة المريض',
            'ru': 'PHQ-9 — Опросник здоровья пациента',
            'uk': 'PHQ-9 — Опитувальник здоров\'я пацієнта',
        },
        'instructions': {
            'ca': 'Durant les darreres 2 setmanes, amb quina freqüència t\'han molestat els problemes següents?',
            'es': 'Durante las últimas 2 semanas, ¿con qué frecuencia le han molestado los siguientes problemas?',
            'en': 'Over the last 2 weeks, how often have you been bothered by any of the following problems?',
            'fr': 'Au cours des 2 dernières semaines, à quelle fréquence avez-vous été gêné(e) par les problèmes suivants?',
            'ar': 'خلال الأسبوعين الماضيين، كم مرة أزعجتك المشاكل التالية؟',
            'ru': 'За последние 2 недели, как часто вас беспокоили следующие проблемы?',
            'uk': 'За останні 2 тижні, як часто вас турбували такі проблеми?',
        },
        'scale': {
            'ca': ['Mai', 'Alguns dies', 'Més de la meitat dels dies', 'Quasi cada dia'],
            'es': ['Para nada', 'Varios días', 'Más de la mitad de los días', 'Casi todos los días'],
            'en': ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
            'fr': ['Jamais', 'Plusieurs jours', 'Plus de la moitié du temps', 'Presque tous les jours'],
            'ar': ['إطلاقاً', 'عدة أيام', 'أكثر من نصف الأيام', 'تقريباً كل يوم'],
            'ru': ['Совсем нет', 'Несколько дней', 'Больше половины дней', 'Почти каждый день'],
            'uk': ['Зовсім ні', 'Кілька днів', 'Більше половини днів', 'Майже щодня'],
        },
        'scale_values': [0, 1, 2, 3],
        'questions': {
            'ca': [
                'Tenir poc interès o plaer en fer les coses',
                'Sentir-se desanimat/ada, deprimit/ida o sense esperança',
                'Dificultats per adormir-se, continuar dormint o dormir massa',
                'Sentir-se cansat/ada o tenir poca energia',
                'Poc apetit o menjar en excés',
                'Sentir-se malament amb vostè mateix/a, o pensar que és un fracàs o que ha decepcionat la família',
                'Dificultats per concentrar-se (llegir, mirar la televisió, etc.)',
                "Moure's o parlar tan lentament que la gent ho hagi notat, o estar tan inquiet/a que no pot quedar-se quiet/a",
                'Pensaments que seria millor estar mort/a, o de fer-se mal',
            ],
            'es': [
                'Tener poco interés o placer en hacer las cosas',
                'Sentirse decaído/a, deprimido/a o sin esperanza',
                'Dificultades para dormir o para despertarse, o dormir demasiado',
                'Sentirse cansado/a o con poca energía',
                'Tener poco apetito o comer en exceso',
                'Sentirse mal consigo mismo/a, o que es un fracaso o que ha decepcionado a su familia',
                'Dificultades para concentrarse (leer, ver televisión, etc.)',
                'Moverse o hablar tan lento que la gente lo ha notado, o estar tan inquieto/a que no puede quedarse quieto/a',
                'Pensamientos de que estaría mejor muerto/a, o de hacerse daño',
            ],
            'en': [
                'Little interest or pleasure in doing things',
                'Feeling down, depressed, or hopeless',
                'Trouble falling or staying asleep, or sleeping too much',
                'Feeling tired or having little energy',
                'Poor appetite or overeating',
                'Feeling bad about yourself — or that you are a failure or have let yourself or your family down',
                'Trouble concentrating on things, such as reading the newspaper or watching television',
                'Moving or speaking so slowly that other people could have noticed, or the opposite — being so fidgety or restless that you have been moving around a lot more than usual',
                'Thoughts that you would be better off dead, or of hurting yourself in some way',
            ],
            'fr': [
                'Peu d\'intérêt ou de plaisir à faire les choses',
                'Se sentir triste, déprimé(e) ou sans espoir',
                'Difficulté à s\'endormir ou à rester endormi(e), ou dormir trop',
                'Se sentir fatigué(e) ou manquer d\'énergie',
                'Avoir peu d\'appétit ou manger trop',
                'Se sentir mal dans sa peau, ou penser que l\'on est un(e) raté(e), ou s\'être déçu(e) soi-même ou avoir déçu sa famille',
                'Avoir du mal à se concentrer (lire le journal ou regarder la télévision)',
                'Bouger ou parler si lentement que les autres l\'auraient remarqué, ou au contraire être si agité(e) que l\'on bouge beaucoup plus que d\'habitude',
                'Penser qu\'il vaudrait mieux mourir ou se blesser d\'une façon ou d\'une autre',
            ],
            'ar': [
                'الشعور بالفتور أو قلة الاهتمام في أداء الأشياء',
                'الشعور باليأس أو الاكتئاب أو الإحباط',
                'صعوبة النوم أو الاستمرار في النوم أو النوم الزائد',
                'الشعور بالتعب أو نقص الطاقة',
                'ضعف الشهية أو الإفراط في الأكل',
                'الشعور بالفشل أو أنك خذلت نفسك أو عائلتك',
                'صعوبة التركيز في الأشياء مثل القراءة أو مشاهدة التلفاز',
                'التحرك أو الكلام ببطء شديد لدرجة أن الآخرين لاحظوا، أو العكس — الشعور بالقلق الشديد وعدم الثبات',
                'أفكار بأن الموت أفضل أو إيذاء النفس',
            ],
            'ru': [
                'Отсутствие интереса или удовольствия от занятий',
                'Подавленность, депрессия или безнадёжность',
                'Трудности с засыпанием, пробуждением или чрезмерный сон',
                'Усталость или недостаток энергии',
                'Плохой аппетит или переедание',
                'Плохое самоощущение, ощущение себя неудачником или что подвёл семью',
                'Трудности с концентрацией внимания (чтение, просмотр телевизора и т.д.)',
                'Замедленные движения или речь, замеченные окружающими, или наоборот — сильное беспокойство',
                'Мысли о том, что лучше было бы умереть, или желание причинить себе вред',
            ],
            'uk': [
                'Відсутність інтересу або задоволення від справ',
                'Пригніченість, депресія або безнадійність',
                'Труднощі із засипанням, пробудженням або надмірний сон',
                'Втома або брак енергії',
                'Поганий апетит або переїдання',
                'Погане ставлення до себе, відчуття невдачі або що підвів/ла сім\'ю',
                'Труднощі з концентрацією уваги (читання, перегляд телевізора тощо)',
                'Сповільнені рухи або мова, помічені оточуючими, або навпаки — сильне занепокоєння',
                'Думки про те, що краще було б померти, або бажання заподіяти собі шкоду',
            ],
        },
    },

    # ── GAD-7 ──────────────────────────────────────────────────────────────────
    'gad7': {
        'title': {
            'ca': 'GAD-7 — Escala d\'Ansietat Generalitzada',
            'es': 'GAD-7 — Escala de Trastorno de Ansiedad Generalizada',
            'en': 'GAD-7 — Generalized Anxiety Disorder Scale',
            'fr': 'GAD-7 — Échelle du Trouble d\'Anxiété Généralisée',
            'ar': 'GAD-7 — مقياس اضطراب القلق العام',
            'ru': 'GAD-7 — Шкала генерализованного тревожного расстройства',
            'uk': 'GAD-7 — Шкала генералізованого тривожного розладу',
        },
        'instructions': {
            'ca': 'Durant les darreres 2 setmanes, amb quina freqüència t\'han molestat els problemes següents?',
            'es': 'Durante las últimas 2 semanas, ¿con qué frecuencia le han molestado los siguientes problemas?',
            'en': 'Over the last 2 weeks, how often have you been bothered by the following problems?',
            'fr': 'Au cours des 2 dernières semaines, à quelle fréquence avez-vous été gêné(e) par les problèmes suivants?',
            'ar': 'خلال الأسبوعين الماضيين، كم مرة أزعجتك المشاكل التالية؟',
            'ru': 'За последние 2 недели, как часто вас беспокоили следующие проблемы?',
            'uk': 'За останні 2 тижні, як часто вас турбували такі проблеми?',
        },
        'scale': {
            'ca': ['Mai', 'Alguns dies', 'Més de la meitat dels dies', 'Quasi cada dia'],
            'es': ['Para nada', 'Varios días', 'Más de la mitad de los días', 'Casi todos los días'],
            'en': ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
            'fr': ['Jamais', 'Plusieurs jours', 'Plus de la moitié du temps', 'Presque tous les jours'],
            'ar': ['إطلاقاً', 'عدة أيام', 'أكثر من نصف الأيام', 'تقريباً كل يوم'],
            'ru': ['Совсем нет', 'Несколько дней', 'Больше половины дней', 'Почти каждый день'],
            'uk': ['Зовсім ні', 'Кілька днів', 'Більше половини днів', 'Майже щодня'],
        },
        'scale_values': [0, 1, 2, 3],
        'questions': {
            'ca': [
                'Sentir-se nerviós/osa, ansiós/osa o molt tens/a',
                'No poder aturar o controlar la preocupació',
                'Preocupar-se massa per coses diverses',
                'Dificultats per relaxar-se',
                'Estar tan inquiet/a que és difícil quedar-se assegut/ada tranquil·lament',
                'Irritar-se o enfadar-se fàcilment',
                'Sentir por com si pogués passar alguna cosa terrible',
            ],
            'es': [
                'Sentirse nervioso/a, ansioso/a o muy tenso/a',
                'No poder dejar de preocuparse o no poder controlar la preocupación',
                'Preocuparse demasiado por distintas cosas',
                'Dificultad para relajarse',
                'Estar tan inquieto/a que es difícil permanecer sentado/a tranquilamente',
                'Molestarse o ponerse irritable fácilmente',
                'Sentir miedo, como si algo terrible fuera a pasar',
            ],
            'en': [
                'Feeling nervous, anxious, or on edge',
                'Not being able to stop or control worrying',
                'Worrying too much about different things',
                'Trouble relaxing',
                'Being so restless that it is hard to sit still',
                'Becoming easily annoyed or irritable',
                'Feeling afraid as if something awful might happen',
            ],
            'fr': [
                'Être nerveux/euse, anxieux/euse ou très tendu(e)',
                'Ne pas pouvoir arrêter de vous inquiéter ni contrôler vos inquiétudes',
                'Vous inquiéter trop de différentes choses',
                'Du mal à vous détendre',
                'Être si agité(e) qu\'il est difficile de rester assis(e) tranquillement',
                'Vous énerver ou vous irriter facilement',
                'Avoir peur que quelque chose de terrible puisse se produire',
            ],
            'ar': [
                'الشعور بالتوتر أو القلق أو الانزعاج',
                'عدم القدرة على التوقف عن القلق أو السيطرة عليه',
                'القلق الزائد بشأن أشياء مختلفة',
                'صعوبة الاسترخاء',
                'الشعور بالقلق الشديد لدرجة يصعب معها الجلوس ساكناً',
                'التهيج أو الانفعال بسهولة',
                'الشعور بالخوف كأن شيئاً سيئاً سيحدث',
            ],
            'ru': [
                'Чувство нервозности, тревоги или напряжённости',
                'Невозможность остановить или контролировать беспокойство',
                'Чрезмерное беспокойство по разным поводам',
                'Трудности с расслаблением',
                'Такое беспокойство, что трудно оставаться на месте',
                'Раздражительность',
                'Ощущение страха, что может случиться что-то ужасное',
            ],
            'uk': [
                'Відчуття нервозності, тривоги або напруженості',
                'Неможливість зупинити або контролювати хвилювання',
                'Надмірне хвилювання через різні речі',
                'Труднощі з розслабленням',
                'Таке занепокоєння, що важко сидіти нерухомо',
                'Дратівливість',
                'Відчуття страху, що може статися щось жахливе',
            ],
        },
    },

    # ── PCL-5 ──────────────────────────────────────────────────────────────────
    'pcl5': {
        'title': {
            'ca': 'PCL-5 — Llista de Verificació del TEPT (DSM-5)',
            'es': 'PCL-5 — Lista de Verificación del TEPT (DSM-5)',
            'en': 'PCL-5 — PTSD Checklist for DSM-5',
            'fr': 'PCL-5 — Liste de contrôle du TSPT (DSM-5)',
            'ar': 'PCL-5 — قائمة اضطراب ما بعد الصدمة (DSM-5)',
            'ru': 'PCL-5 — Контрольный список симптомов ПТСР (DSM-5)',
            'uk': 'PCL-5 — Контрольний список симптомів ПТСР (DSM-5)',
        },
        'instructions': {
            'ca': 'Durant el darrer mes, fins a quin punt t\'han molestat els problemes següents?',
            'es': 'Durante el último mes, ¿en qué medida le han molestado los siguientes problemas?',
            'en': 'In the past month, how much were you bothered by the following problems?',
            'fr': 'Au cours du mois dernier, à quel point avez-vous été gêné(e) par les problèmes suivants?',
            'ar': 'خلال الشهر الماضي، كم أزعجتك المشاكل التالية؟',
            'ru': 'В прошлом месяце насколько вас беспокоили следующие проблемы?',
            'uk': 'Протягом минулого місяця наскільки вас турбували такі проблеми?',
        },
        'scale': {
            'ca': ['Gens', 'Una mica', 'Moderadament', 'Bastant', 'Extremadament'],
            'es': ['En absoluto', 'Un poco', 'Moderadamente', 'Bastante', 'Extremadamente'],
            'en': ['Not at all', 'A little bit', 'Moderately', 'Quite a bit', 'Extremely'],
            'fr': ['Pas du tout', 'Un peu', 'Modérément', 'Beaucoup', 'Extrêmement'],
            'ar': ['إطلاقاً', 'قليلاً', 'إلى حد ما', 'كثيراً', 'بشدة'],
            'ru': ['Совсем нет', 'Немного', 'Умеренно', 'Значительно', 'Крайне'],
            'uk': ['Зовсім ні', 'Трохи', 'Помірно', 'Значно', 'Дуже сильно'],
        },
        'scale_values': [0, 1, 2, 3, 4],
        'questions': {
            'ca': [
                'Records repetits i pertorbadors de l\'experiència estressant',
                'Somnis repetits i pertorbadors de l\'experiència estressant',
                'Sentir o actuar com si l\'experiència tornés a succeir (reviure-la)',
                'Sentir-se molt alterat/ada quan alguna cosa et recorda l\'experiència',
                'Reaccions físiques fortes quan alguna cosa et recorda l\'experiència (cor accelerat, dificultat per respirar, suor)',
                'Evitar records, pensaments o sentiments relacionats amb l\'experiència',
                'Evitar coses externes que recorden l\'experiència (llocs, persones, converses, activitats)',
                'Dificultats per recordar parts importants de l\'experiència',
                'Creences negatives fortes sobre tu mateix/a, els altres o el món',
                'Culpar-se a un/a mateix/a o a una altra persona per l\'experiència',
                'Sentiments negatius intensos (por, horror, ràbia, culpa, vergonya)',
                'Pèrdua d\'interès per activitats que gaudia',
                'Sentir-se distant o desconnectat/ada de les persones',
                'Dificultats per experimentar sentiments positius',
                'Comportament irritable, esclats d\'ira o actuar agressivament',
                'Assumir massa riscos o fer coses que podrien fer mal',
                'Estar en alerta màxima o molt vigilant',
                'Estar molt nerviós/osa o sobresaltar-se fàcilment',
                'Dificultats per concentrar-se',
                'Dificultats per adormir-se o continuar dormint',
            ],
            'es': [
                'Recuerdos repetidos y perturbadores de la experiencia estresante',
                'Sueños repetidos y perturbadores de la experiencia estresante',
                'Sentir o actuar como si la experiencia estuviera ocurriendo de nuevo',
                'Sentirse muy alterado/a cuando algo le recuerda la experiencia',
                'Reacciones físicas intensas al recordar la experiencia (corazón acelerado, dificultad para respirar, sudoración)',
                'Evitar recuerdos, pensamientos o sentimientos relacionados con la experiencia',
                'Evitar cosas externas que le recuerdan la experiencia (lugares, personas, conversaciones, actividades)',
                'Dificultades para recordar partes importantes de la experiencia',
                'Creencias negativas fuertes sobre usted mismo/a, los demás o el mundo',
                'Culparse a sí mismo/a o a otra persona por la experiencia',
                'Sentimientos negativos intensos (miedo, horror, ira, culpa, vergüenza)',
                'Pérdida de interés en actividades que disfrutaba',
                'Sentirse distante o desconectado/a de las personas',
                'Dificultades para experimentar sentimientos positivos',
                'Comportamiento irritable, explosiones de ira o actuar agresivamente',
                'Asumir demasiados riesgos o hacer cosas que podrían hacerle daño',
                'Estar en estado de alerta máxima o muy vigilante',
                'Estar muy nervioso/a o asustarse fácilmente',
                'Dificultades para concentrarse',
                'Dificultades para dormirse o seguir durmiendo',
            ],
            'en': [
                'Repeated, disturbing, and unwanted memories of the stressful experience',
                'Repeated, disturbing dreams of the stressful experience',
                'Suddenly feeling or acting as if the stressful experience were actually happening again',
                'Feeling very upset when something reminded you of the stressful experience',
                'Having strong physical reactions when something reminded you of the stressful experience',
                'Avoiding memories, thoughts, or feelings related to the stressful experience',
                'Avoiding external reminders of the stressful experience (people, places, conversations, activities)',
                'Trouble remembering important parts of the stressful experience',
                'Having strong negative beliefs about yourself, other people, or the world',
                'Blaming yourself or someone else for the stressful experience',
                'Having strong negative feelings such as fear, horror, anger, guilt, or shame',
                'Loss of interest in activities that you used to enjoy',
                'Feeling distant or cut off from other people',
                'Trouble experiencing positive feelings',
                'Irritable behavior, angry outbursts, or acting aggressively',
                'Taking too many risks or doing things that could cause you harm',
                'Being "superalert" or watchful or on guard',
                'Feeling jumpy or easily startled',
                'Having difficulty concentrating',
                'Trouble falling or staying asleep',
            ],
            'fr': [
                'Souvenirs répétés et perturbants de l\'expérience stressante',
                'Rêves répétés et perturbants de l\'expérience stressante',
                'Avoir soudainement le sentiment ou agir comme si l\'expérience se reproduisait',
                'Se sentir très bouleversé(e) quand quelque chose vous rappelle l\'expérience',
                'Réactions physiques intenses quand quelque chose vous rappelle l\'expérience',
                'Éviter les souvenirs, pensées ou sentiments liés à l\'expérience',
                'Éviter les rappels externes de l\'expérience (lieux, personnes, conversations)',
                'Difficulté à se souvenir de parties importantes de l\'expérience',
                'Croyances négatives fortes sur vous-même, les autres ou le monde',
                'Se blâmer ou blâmer quelqu\'un d\'autre pour l\'expérience',
                'Sentiments négatifs intenses (peur, horreur, colère, culpabilité, honte)',
                'Perte d\'intérêt pour des activités que vous appréciez',
                'Se sentir distant(e) ou coupé(e) des autres',
                'Difficulté à éprouver des sentiments positifs',
                'Comportement irritable, accès de colère ou comportement agressif',
                'Prendre trop de risques ou faire des choses pouvant vous nuire',
                'Être en état d\'alerte maximale ou très vigilant(e)',
                'Être très nerveux/euse ou sursauter facilement',
                'Difficulté à se concentrer',
                'Difficulté à s\'endormir ou à rester endormi(e)',
            ],
            'ar': [
                'ذكريات متكررة ومزعجة للتجربة المؤلمة',
                'أحلام متكررة ومزعجة للتجربة المؤلمة',
                'الشعور المفاجئ أو التصرف كأن التجربة تحدث مجدداً',
                'الشعور بضيق شديد عند تذكر التجربة',
                'ردود فعل جسدية قوية عند تذكر التجربة',
                'تجنب الذكريات والأفكار والمشاعر المتعلقة بالتجربة',
                'تجنب الأشياء الخارجية التي تذكرك بالتجربة',
                'صعوبة تذكر أجزاء مهمة من التجربة',
                'معتقدات سلبية قوية عن نفسك أو الآخرين أو العالم',
                'إلقاء اللوم على نفسك أو شخص آخر بسبب التجربة',
                'مشاعر سلبية شديدة كالخوف والغضب والذنب والخزي',
                'فقدان الاهتمام بالأنشطة التي كنت تستمتع بها',
                'الشعور بالبعد أو الانفصال عن الناس',
                'صعوبة تجربة المشاعر الإيجابية',
                'السلوك الانفعالي أو نوبات الغضب أو العدوانية',
                'المبالغة في المخاطرة أو القيام بأشياء قد تضرك',
                'الحذر الشديد والتيقظ الدائم',
                'التوتر الشديد أو التفزع بسهولة',
                'صعوبة التركيز',
                'صعوبة النوم أو الاستمرار في النوم',
            ],
            'ru': [
                'Повторяющиеся, тревожные воспоминания о стрессовом событии',
                'Повторяющиеся тревожные сны о стрессовом событии',
                'Внезапное ощущение или поведение, как будто событие повторяется',
                'Сильное расстройство при напоминании о стрессовом событии',
                'Сильные физические реакции при напоминании о событии',
                'Избегание воспоминаний, мыслей или чувств, связанных с событием',
                'Избегание внешних напоминаний о событии (мест, людей, разговоров)',
                'Трудности с припоминанием важных частей события',
                'Устойчивые негативные убеждения о себе, других или мире',
                'Обвинение себя или кого-то другого в произошедшем',
                'Устойчивые негативные чувства: страх, ужас, гнев, вина, стыд',
                'Потеря интереса к занятиям, которые раньше нравились',
                'Чувство отчуждённости от людей',
                'Трудности с переживанием положительных эмоций',
                'Раздражительность, вспышки гнева, агрессивное поведение',
                'Рискованное поведение или действия, которые могут причинить вред',
                'Постоянная бдительность или настороженность',
                'Нервозность или лёгкая пугливость',
                'Трудности с концентрацией',
                'Проблемы со сном',
            ],
            'uk': [
                'Повторювані тривожні спогади про стресову подію',
                'Повторювані тривожні сни про стресову подію',
                'Раптове відчуття або поведінка, ніби подія відбувається знову',
                'Сильне хвилювання при нагадуванні про стресову подію',
                'Сильні фізичні реакції при нагадуванні про подію',
                'Уникнення спогадів, думок або почуттів, пов\'язаних з подією',
                'Уникнення зовнішніх нагадувань про подію (місця, люди, розмови)',
                'Труднощі з пригадуванням важливих частин події',
                'Стійкі негативні переконання про себе, інших або світ',
                'Звинувачення себе або когось іншого у тому, що сталося',
                'Стійкі негативні почуття: страх, жах, гнів, провина, сором',
                'Втрата інтересу до занять, які раніше подобалися',
                'Відчуття відчуженості від людей',
                'Труднощі з переживанням позитивних емоцій',
                'Дратівливість, спалахи гніву, агресивна поведінка',
                'Ризикована поведінка або дії, що можуть завдати шкоди',
                'Постійна пильність або настороженість',
                'Нервозність або легке переляк',
                'Труднощі з концентрацією',
                'Проблеми зі сном',
            ],
        },
    },

    # ── HSCL-25 ────────────────────────────────────────────────────────────────
    'hscl25': {
        'title': {
            'ca': 'HSCL-25 — Llista de Símptomes de Hopkins',
            'es': 'HSCL-25 — Lista de Síntomas de Hopkins',
            'en': 'HSCL-25 — Hopkins Symptom Checklist',
            'fr': 'HSCL-25 — Liste de Symptômes de Hopkins',
            'ar': 'HSCL-25 — قائمة أعراض هوبكنز',
            'ru': 'HSCL-25 — Контрольный список симптомов Хопкинса',
            'uk': 'HSCL-25 — Контрольний список симптомів Хопкінса',
        },
        'instructions': {
            'ca': 'A continuació trobaràs una llista de problemes i molèsties que la gent pot tenir. Indica fins a quin punt t\'ha molestat cada problema durant les darreres setmanes.',
            'es': 'A continuación encontrará una lista de problemas y molestias que la gente puede tener. Indique en qué medida le ha molestado cada problema durante las últimas semanas.',
            'en': 'Below is a list of problems and complaints that people sometimes have. Please read each one carefully and indicate how much it has bothered you during the past week.',
            'fr': 'Vous trouverez ci-dessous une liste de problèmes et plaintes que les gens peuvent avoir. Indiquez dans quelle mesure chaque problème vous a dérangé(e) durant les dernières semaines.',
            'ar': 'فيما يلي قائمة بالمشاكل والشكاوى التي قد يعاني منها الناس. يُرجى الإشارة إلى مدى إزعاج كل مشكلة لك خلال الأسابيع الماضية.',
            'ru': 'Ниже приведён список проблем и жалоб, которые могут возникать у людей. Укажите, насколько каждая проблема беспокоила вас в течение прошлой недели.',
            'uk': 'Нижче наведено список проблем і скарг, які можуть виникати у людей. Вкажіть, наскільки кожна проблема турбувала вас протягом минулого тижня.',
        },
        'scale': {
            'ca': ['Gens', 'Una mica', 'Bastant', 'Molt'],
            'es': ['En absoluto', 'Un poco', 'Bastante', 'Mucho'],
            'en': ['Not at all', 'A little', 'Quite a bit', 'Extremely'],
            'fr': ['Pas du tout', 'Un peu', 'Beaucoup', 'Extrêmement'],
            'ar': ['إطلاقاً', 'قليلاً', 'كثيراً', 'بشدة'],
            'ru': ['Совсем нет', 'Немного', 'Довольно', 'Очень'],
            'uk': ['Зовсім ні', 'Трохи', 'Досить', 'Дуже'],
        },
        'scale_values': [1, 2, 3, 4],
        'questions': {
            'ca': [
                'Tremolors', 'Sentir-se nerviós/osa o tensa', 'De sobte tenir por sense raó',
                'Sentir-se atemorida', 'Desmais, mareig', 'Cor accelerat o palpitacions',
                'Tremolors', 'Sensació de terror o pànic', 'Sentir-se inquiet/a', 'Tenir por als espais oberts',
                'Sentir-se sense energia o cansat/ada', 'Culpar-se de les coses',
                'Plorar fàcilment', 'Sentir-se atrapat/ada', 'Sentir-se sol/a',
                'Sentir-se trist/a', 'Preocupar-se massa per les coses', 'No tenir interès per les coses',
                'Sentir-se sense esperança en el futur', 'Sentir que tot és un esforç',
                'Sentir-se sense valor', 'Pensaments de posar fi a la pròpia vida',
                'Sentir-se atrapat/ada sense sortida', 'Sentir massa responsabilitat',
                'Tenir por que passi alguna cosa greu',
            ],
            'es': [
                'Temblores', 'Nerviosismo o tensión', 'Miedos repentinos sin razón',
                'Sentirse atemorizado/a', 'Desmayos o mareos', 'Corazón acelerado o palpitaciones',
                'Temblores', 'Sensación de terror o pánico', 'Sentirse inquieto/a', 'Miedo a espacios abiertos',
                'Sentirse sin energía o cansado/a', 'Culparse de las cosas',
                'Llorar fácilmente', 'Sentirse atrapado/a', 'Sentirse solo/a',
                'Sentirse triste', 'Preocuparse demasiado por las cosas', 'No tener interés por las cosas',
                'Sentirse sin esperanza sobre el futuro', 'Sentir que todo es un esfuerzo',
                'Sentirse sin valor', 'Pensamientos de poner fin a su vida',
                'Sentirse atrapado/a sin salida', 'Sentir demasiada responsabilidad',
                'Tener miedo de que ocurra algo grave',
            ],
            'en': [
                'Trembling', 'Feeling nervous or tense', 'Suddenly scared for no reason',
                'Feeling fearful', 'Faintness or dizziness', 'Heart pounding or racing',
                'Trembling', 'Spells of terror or panic', 'Feeling restless', 'Fear of open spaces',
                'Feeling low in energy, slowed down', 'Blaming yourself for things',
                'Crying easily', 'Feeling of being trapped', 'Feeling lonely',
                'Feeling blue', 'Worrying too much about things', 'Feeling no interest in things',
                'Feeling hopeless about the future', 'Feeling everything is an effort',
                'Feelings of worthlessness', 'Thoughts of ending your life',
                'Feeling of being caught or trapped', 'Feeling too much responsibility',
                'Feeling afraid that something serious will happen',
            ],
            'fr': [
                'Tremblements', 'Se sentir nerveux/euse ou tendu(e)', 'Peur soudaine sans raison',
                'Se sentir effrayé(e)', 'Évanouissements ou vertiges', 'Cœur qui bat fort ou s\'emballe',
                'Tremblements', 'Accès de terreur ou panique', 'Se sentir agité(e)', 'Peur des espaces ouverts',
                'Se sentir sans énergie ou fatigué(e)', 'Se blâmer pour les choses',
                'Pleurer facilement', 'Sentiment d\'être piégé(e)', 'Se sentir seul(e)',
                'Se sentir déprimé(e)', 'S\'inquiéter trop des choses', 'Ne pas s\'intéresser aux choses',
                'Se sentir sans espoir pour l\'avenir', 'Sentir que tout demande un effort',
                'Se sentir sans valeur', 'Pensées de mettre fin à sa vie',
                'Sentiment d\'être piégé(e) sans issue', 'Trop de responsabilité',
                'Craindre qu\'il arrive quelque chose de grave',
            ],
            'ar': [
                'رعشة', 'التوتر أو الانزعاج', 'خوف مفاجئ بدون سبب',
                'الشعور بالخوف', 'الإغماء أو الدوار', 'تسارع دقات القلب',
                'رعشة', 'نوبات من الرعب أو الهلع', 'الشعور بالقلق', 'الخوف من الأماكن المفتوحة',
                'الشعور بانعدام الطاقة أو التعب', 'إلقاء اللوم على النفس',
                'البكاء بسهولة', 'الشعور بالفخ', 'الشعور بالوحدة',
                'الشعور بالحزن', 'القلق الزائد', 'فقدان الاهتمام بالأشياء',
                'الشعور باليأس من المستقبل', 'الشعور بأن كل شيء يتطلب جهداً',
                'الشعور بعدم القيمة', 'أفكار عن إنهاء الحياة',
                'الشعور بالاحتجاز بدون مخرج', 'الشعور بمسؤولية زائدة',
                'الخوف من حدوث شيء خطير',
            ],
            'ru': [
                'Дрожь', 'Нервозность или напряжение', 'Внезапный страх без причины',
                'Тревога', 'Обмороки или головокружение', 'Учащённое сердцебиение',
                'Дрожь', 'Приступы паники', 'Беспокойство', 'Боязнь открытых пространств',
                'Упадок сил или усталость', 'Самообвинение',
                'Плаксивость', 'Чувство ловушки', 'Одиночество',
                'Подавленность', 'Чрезмерное беспокойство', 'Безразличие к вещам',
                'Безнадёжность в отношении будущего', 'Ощущение, что всё даётся с трудом',
                'Чувство бесполезности', 'Мысли о том, чтобы покончить с жизнью',
                'Ощущение ловушки без выхода', 'Слишком большая ответственность',
                'Страх, что произойдёт что-то серьёзное',
            ],
            'uk': [
                'Тремтіння', 'Нервозність або напруженість', 'Раптовий страх без причини',
                'Тривога', 'Непритомність або запаморочення', 'Прискорене серцебиття',
                'Тремтіння', 'Напади паніки', 'Занепокоєння', 'Страх відкритих просторів',
                'Занепад сил або втома', 'Самозвинувачення',
                'Схильність до плачу', 'Відчуття пастки', 'Самотність',
                'Пригніченість', 'Надмірне хвилювання', 'Байдужість до речей',
                'Безнадійність щодо майбутнього', 'Відчуття, що все дається важко',
                'Відчуття нікчемності', 'Думки про те, щоб покінчити з життям',
                'Відчуття пастки без виходу', 'Занадто велика відповідальність',
                'Страх, що станеться щось серйозне',
            ],
        },
    },

    # ── IES-R ──────────────────────────────────────────────────────────────────
    'iesr': {
        'title': {
            'ca': 'IES-R — Escala d\'Impacte de l\'Esdeveniment (Revisada)',
            'es': 'IES-R — Escala de Impacto del Evento (Revisada)',
            'en': 'IES-R — Impact of Event Scale (Revised)',
            'fr': 'IES-R — Échelle de l\'Impact de l\'Événement (Révisée)',
            'ar': 'IES-R — مقياس تأثير الحدث (المُنقَّح)',
            'ru': 'IES-R — Шкала влияния события (пересмотренная)',
            'uk': 'IES-R — Шкала впливу події (переглянута)',
        },
        'instructions': {
            'ca': 'A continuació hi ha una llista de dificultats que la gent té de vegades després d\'esdeveniments estressants. Si us plau, llegeix cada element i indica fins a quin punt t\'ha molestat durant els darrers 7 dies en relació amb el teu esdeveniment més estressant.',
            'es': 'A continuación hay una lista de dificultades que la gente tiene a veces después de eventos estresantes. Por favor, lea cada elemento e indique cuánto le ha molestado durante los últimos 7 días en relación a su evento más estresante.',
            'en': 'Below is a list of difficulties people sometimes have after stressful life events. Please read each item and indicate how distressing each difficulty has been during the past 7 days with respect to your most stressful life event.',
            'fr': 'Voici une liste de difficultés que les gens ont parfois après des événements stressants. Veuillez lire chaque élément et indiquer à quel point chaque difficulté vous a perturbé(e) au cours des 7 derniers jours en rapport avec votre événement le plus stressant.',
            'ar': 'فيما يلي قائمة بالصعوبات التي يواجهها الناس أحياناً بعد الأحداث المجهدة. يُرجى قراءة كل بند والإشارة إلى مدى إزعاجه لك خلال الأيام السبعة الماضية.',
            'ru': 'Ниже приводится список трудностей, которые иногда возникают у людей после стрессовых событий. Прочитайте каждый пункт и укажите, насколько каждая трудность беспокоила вас в течение последних 7 дней.',
            'uk': 'Нижче наведено список труднощів, які іноді виникають у людей після стресових подій. Прочитайте кожен пункт і вкажіть, наскільки кожна труднощ турбувала вас протягом останніх 7 днів.',
        },
        'scale': {
            'ca': ['Gens', 'Una mica', 'Moderadament', 'Bastant', 'Extremadament'],
            'es': ['En absoluto', 'Un poco', 'Moderadamente', 'Bastante', 'Extremadamente'],
            'en': ['Not at all', 'A little bit', 'Moderately', 'Quite a bit', 'Extremely'],
            'fr': ['Pas du tout', 'Un peu', 'Modérément', 'Beaucoup', 'Extrêmement'],
            'ar': ['إطلاقاً', 'قليلاً', 'إلى حد ما', 'كثيراً', 'بشدة'],
            'ru': ['Совсем нет', 'Немного', 'Умеренно', 'Значительно', 'Крайне'],
            'uk': ['Зовсім ні', 'Трохи', 'Помірно', 'Значно', 'Дуже сильно'],
        },
        'scale_values': [0, 1, 2, 3, 4],
        'questions': {
            'ca': [
                'Qualsevol record em portava de tornada sentiments sobre l\'esdeveniment',
                'Tenia dificultats per continuar dormint',
                'Altres coses em feien pensar en l\'esdeveniment',
                'Sentia irritació i ràbia',
                'Intentava no alterar-me quan pensava en l\'esdeveniment o me\'n recordaven',
                'Pensava en l\'esdeveniment sense voler',
                'Sentia com si no hagués passat o no fos real',
                'Em quedava lluny de les coses que me\'n recordaven',
                'Imatges de l\'esdeveniment em venien al cap',
                'Estava nerviós/osa i m\'espantava fàcilment',
                'Intentava no pensar-hi',
                'Era conscient que tenia molts sentiments però no els tractava',
                'Els meus sentiments sobre l\'esdeveniment estaven adormits',
                'Em trobava actuant o sentint com si tornés a aquell moment',
                'Tenia dificultats per adormir-me',
                'Tenia onades de sentiments intensos sobre l\'esdeveniment',
                'Intentava eliminar-lo de la memòria',
                'Tenia dificultats per concentrar-me',
                'Els records em causaven reaccions físiques (suor, dificultat per respirar, cor accelerat)',
                'Tenia somnis sobre l\'esdeveniment',
                'Em sentia vigilant i en guàrdia',
                'Intentava no parlar-ne',
            ],
            'es': [
                'Cualquier recordatorio me traía de vuelta los sentimientos del evento',
                'Tenía dificultades para permanecer dormido/a',
                'Otras cosas me hacían pensar en el evento',
                'Me sentía irritable e iracundo/a',
                'Intentaba no alterarme cuando pensaba en el evento o me lo recordaban',
                'Pensaba en el evento sin querer',
                'Sentía como si no hubiera ocurrido o no fuera real',
                'Me mantenía alejado/a de las cosas que me lo recordaban',
                'Imágenes del evento venían a mi mente',
                'Estaba nervioso/a y me asustaba fácilmente',
                'Intentaba no pensar en ello',
                'Era consciente de que tenía muchos sentimientos pero no los manejaba',
                'Mis sentimientos sobre el evento estaban adormecidos',
                'Me encontraba actuando o sintiendo como si volviera a ese momento',
                'Tenía dificultades para dormirme',
                'Tenía olas de sentimientos intensos sobre el evento',
                'Intentaba eliminar el evento de mi memoria',
                'Tenía dificultades para concentrarme',
                'Los recuerdos me causaban reacciones físicas (sudor, dificultad para respirar, corazón acelerado)',
                'Tenía sueños sobre el evento',
                'Me sentía vigilante y en guardia',
                'Intentaba no hablar de ello',
            ],
            'en': [
                'Any reminder brought back feelings about it',
                'I had trouble staying asleep',
                'Other things kept making me think about it',
                'I felt irritable and angry',
                'I avoided letting myself get upset when I thought about it or was reminded of it',
                'I thought about it when I didn\'t mean to',
                'I felt as if it hadn\'t happened or wasn\'t real',
                'I stayed away from reminders of it',
                'Pictures about it popped into my mind',
                'I was jumpy and easily startled',
                'I tried not to think about it',
                'I was aware that I still had a lot of feelings about it, but I didn\'t deal with them',
                'My feelings about it were kind of numb',
                'I found myself acting or feeling like I was back at that time',
                'I had trouble falling asleep',
                'I had waves of strong feelings about it',
                'I tried to remove it from my memory',
                'I had trouble concentrating',
                'Reminders of it caused me to have physical reactions',
                'I had dreams about it',
                'I felt watchful and on-guard',
                'I tried not to talk about it',
            ],
            'fr': [
                'Tout rappel me ramenait des sentiments à ce sujet',
                'J\'avais du mal à rester endormi(e)',
                'D\'autres choses me faisaient y penser',
                'Je me sentais irritable et en colère',
                'J\'évitais de me laisser bouleverser quand j\'y pensais',
                'J\'y pensais sans le vouloir',
                'J\'avais l\'impression que ça n\'avait pas eu lieu ou n\'était pas réel',
                'Je m\'éloignais de tout ce qui me le rappelait',
                'Des images à ce sujet surgissaient dans mon esprit',
                'J\'étais nerveux/euse et sursautais facilement',
                'J\'essayais de ne pas y penser',
                'J\'avais conscience d\'avoir encore beaucoup de sentiments mais je ne les traitais pas',
                'Mes sentiments à ce sujet étaient comme engourdis',
                'Je me retrouvais à agir ou ressentir comme si j\'étais revenu(e) à ce moment',
                'J\'avais du mal à m\'endormir',
                'J\'avais des vagues de sentiments intenses à ce sujet',
                'J\'essayais de l\'effacer de ma mémoire',
                'J\'avais du mal à me concentrer',
                'Les rappels me causaient des réactions physiques',
                'J\'avais des rêves à ce sujet',
                'Je me sentais vigilant(e) et sur mes gardes',
                'J\'essayais de ne pas en parler',
            ],
            'ar': [
                'أي تذكير كان يعيد إليّ المشاعر المتعلقة بالحدث',
                'واجهت صعوبة في الاستمرار بالنوم',
                'أشياء أخرى جعلتني أفكر فيه',
                'شعرت بالانفعال والغضب',
                'تجنبت الانزعاج عند التفكير فيه أو عند تذكيري به',
                'فكرت فيه دون قصد',
                'شعرت كأنه لم يحدث أو لم يكن حقيقياً',
                'ابتعدت عن كل ما يذكرني به',
                'صور عنه ترد إلى ذهني',
                'كنت متوتراً وأفزع بسهولة',
                'حاولت عدم التفكير فيه',
                'أدركت أن لديّ مشاعر كثيرة لكنني لم أتعامل معها',
                'كانت مشاعري حوله خدرة بعض الشيء',
                'وجدت نفسي أتصرف أو أشعر كأنني عدت إلى ذلك الوقت',
                'واجهت صعوبة في النوم',
                'كانت لديّ موجات من المشاعر القوية حوله',
                'حاولت محوه من ذاكرتي',
                'واجهت صعوبة في التركيز',
                'تسببت التذكيرات في ردود فعل جسدية لديّ',
                'حلمت به',
                'كنت متيقظاً وعلى حذر',
                'حاولت عدم الحديث عنه',
            ],
            'ru': [
                'Любое напоминание возвращало чувства, связанные с событием',
                'Трудности с тем, чтобы продолжать спать',
                'Другие вещи заставляли думать о произошедшем',
                'Раздражительность и злость',
                'Стараться не расстраиваться, думая об этом',
                'Думал(а) об этом, не желая того',
                'Ощущение, что этого не было или что это нереально',
                'Избегание напоминаний об этом',
                'Образы этого всплывали в уме',
                'Нервозность и лёгкая пугливость',
                'Стараться не думать об этом',
                'Осознание сильных чувств, но нежелание с ними разбираться',
                'Онемение чувств, связанных с событием',
                'Ощущение себя в том времени снова',
                'Трудности с засыпанием',
                'Волны сильных чувств об этом',
                'Попытки вычеркнуть это из памяти',
                'Трудности с концентрацией',
                'Физические реакции при напоминании об этом',
                'Сны об этом',
                'Бдительность и настороженность',
                'Попытки не говорить об этом',
            ],
            'uk': [
                'Будь-яке нагадування повертало почуття, пов\'язані з подією',
                'Труднощі з тим, щоб продовжувати спати',
                'Інші речі змушували думати про це',
                'Дратівливість і злість',
                'Намагання не хвилюватися, думаючи про це',
                'Думав(-ла) про це мимоволі',
                'Відчуття, що цього не було або що це нереально',
                'Уникнення нагадувань про це',
                'Образи цього виникали в думках',
                'Нервозність і легкий переляк',
                'Намагання не думати про це',
                'Усвідомлення сильних почуттів, але небажання з ними розбиратися',
                'Оніміння почуттів, пов\'язаних з подією',
                'Відчуття себе знову в тому часі',
                'Труднощі із засипанням',
                'Хвилі сильних почуттів щодо цього',
                'Спроби стерти це з пам\'яті',
                'Труднощі з концентрацією',
                'Фізичні реакції при нагадуванні про це',
                'Сни про це',
                'Пильність і настороженість',
                'Спроби не говорити про це',
            ],
        },
    },

    # ── WHODAS 2.0 ─────────────────────────────────────────────────────────────
    'whodas': {
        'title': {
            'ca': 'WHODAS 2.0 — Escala d\'Avaluació de la Discapacitat de l\'OMS',
            'es': 'WHODAS 2.0 — Escala de Evaluación de la Discapacidad de la OMS',
            'en': 'WHODAS 2.0 — WHO Disability Assessment Schedule',
            'fr': 'WHODAS 2.0 — Calendrier d\'évaluation du handicap de l\'OMS',
            'ar': 'WHODAS 2.0 — جدول تقييم الإعاقة لمنظمة الصحة العالمية',
            'ru': 'WHODAS 2.0 — Расписание оценки инвалидности ВОЗ',
            'uk': 'WHODAS 2.0 — Розклад оцінки інвалідності ВООЗ',
        },
        'instructions': {
            'ca': 'Durant els darrers 30 dies, quanta dificultat has tingut per...',
            'es': 'Durante los últimos 30 días, ¿cuánta dificultad ha tenido para...?',
            'en': 'In the last 30 days, how much difficulty did you have in...',
            'fr': 'Au cours des 30 derniers jours, combien de difficultés avez-vous eu pour...',
            'ar': 'خلال الثلاثين يوماً الماضية، كم كانت صعوبتك في...',
            'ru': 'В течение последних 30 дней, насколько трудно вам было...',
            'uk': 'Протягом останніх 30 днів, наскільки важко вам було...',
        },
        'scale': {
            'ca': ['Cap dificultat', 'Poca dificultat', 'Dificultat moderada', 'Dificultat severa', 'Dificultat extrema / No puc'],
            'es': ['Ninguna dificultad', 'Poca dificultad', 'Dificultad moderada', 'Dificultad severa', 'Dificultad extrema / No puedo'],
            'en': ['None', 'Mild', 'Moderate', 'Severe', 'Extreme or cannot do'],
            'fr': ['Aucune', 'Légère', 'Modérée', 'Sévère', 'Extrême ou impossible'],
            'ar': ['لا يوجد', 'خفيفة', 'متوسطة', 'شديدة', 'شديدة جداً / لا أستطيع'],
            'ru': ['Нет', 'Небольшая', 'Умеренная', 'Значительная', 'Крайняя / не могу'],
            'uk': ['Немає', 'Незначна', 'Помірна', 'Значна', 'Крайня / не можу'],
        },
        'scale_values': [0, 1, 2, 3, 4],
        'questions': {
            'ca': [
                'Estar dret/a durant un període llarg (p. ex. 30 minuts)',
                'Ocupar-se de les responsabilitats domèstiques',
                'Aprendre una tasca nova (p. ex., aprendre com arribar a un lloc nou)',
                'Participar en activitats comunitàries (festes, activitats religioses o altres)',
                'Fins a quin punt la teva salut t\'ha afectat emocionalment',
                'Concentrar-te durant 10 minuts',
                'Caminar una distància llarga (p. ex. un quilòmetre)',
                'Rentar-te tot el cos',
                'Vestir-te',
                'Relacionar-te amb persones que no coneixes',
                'Mantenir una amistat',
                'La teva feina o activitats diàries habituals',
            ],
            'es': [
                'Estar de pie durante un período largo (p. ej., 30 minutos)',
                'Ocuparse de las responsabilidades domésticas',
                'Aprender una nueva tarea (p. ej., aprender cómo llegar a un lugar nuevo)',
                'Participar en actividades comunitarias (fiestas, actividades religiosas u otras)',
                'En qué medida su salud le ha afectado emocionalmente',
                'Concentrarse durante 10 minutos',
                'Caminar una distancia larga (p. ej., un kilómetro)',
                'Lavarse todo el cuerpo',
                'Vestirse',
                'Relacionarse con personas que no conoce',
                'Mantener una amistad',
                'Su trabajo o actividades diarias habituales',
            ],
            'en': [
                'Standing for long periods such as 30 minutes',
                'Taking care of your household responsibilities',
                'Learning a new task, for example learning how to get to a new place',
                'Joining in community activities in the same way as anyone else can',
                'How much have you been emotionally affected by your health problems',
                'Concentrating on doing something for ten minutes',
                'Walking a long distance such as a kilometre',
                'Washing your whole body',
                'Getting dressed',
                'Dealing with people you do not know',
                'Maintaining a friendship',
                'Your day-to-day work',
            ],
            'fr': [
                'Rester debout pendant de longues périodes (p. ex., 30 minutes)',
                'Prendre soin de vos responsabilités ménagères',
                'Apprendre une nouvelle tâche (p. ex., comment se rendre dans un nouvel endroit)',
                'Participer aux activités communautaires (fêtes, activités religieuses ou autres)',
                'Dans quelle mesure votre santé vous a-t-elle affecté(e) émotionnellement',
                'Se concentrer sur quelque chose pendant dix minutes',
                'Marcher sur une longue distance, comme un kilomètre',
                'Vous laver tout le corps',
                'Vous habiller',
                'Traiter avec des personnes que vous ne connaissez pas',
                'Entretenir une amitié',
                'Votre travail au quotidien',
            ],
            'ar': [
                'الوقوف لفترات طويلة (مثلاً 30 دقيقة)',
                'الاعتناء بمسؤوليات المنزل',
                'تعلم مهمة جديدة (مثلاً تعلم كيفية الذهاب إلى مكان جديد)',
                'المشاركة في الأنشطة المجتمعية (مهرجانات أو أنشطة دينية وغيرها)',
                'مدى التأثير العاطفي لمشاكلك الصحية عليك',
                'التركيز على شيء لمدة عشر دقائق',
                'المشي لمسافة طويلة مثل كيلومتر',
                'الاستحمام الكامل',
                'ارتداء الملابس',
                'التعامل مع أشخاص لا تعرفهم',
                'الحفاظ على الصداقات',
                'عملك اليومي المعتاد',
            ],
            'ru': [
                'Стоять долго, например 30 минут',
                'Справляться с домашними обязанностями',
                'Учиться чему-то новому (например, как добраться до нового места)',
                'Участвовать в общественной жизни так же, как все остальные',
                'Насколько ваши проблемы со здоровьем повлияли на вас эмоционально',
                'Сосредотачиваться на чём-то в течение десяти минут',
                'Идти пешком далеко, например километр',
                'Мыться полностью',
                'Одеваться',
                'Общаться с незнакомыми людьми',
                'Поддерживать дружбу',
                'Ваша повседневная работа или занятия',
            ],
            'uk': [
                'Стояти довго, наприклад 30 хвилин',
                'Справлятися з домашніми обов\'язками',
                'Вчитися чомусь новому (наприклад, як дістатися до нового місця)',
                'Брати участь у громадському житті так само, як усі інші',
                'Наскільки ваші проблеми зі здоров\'ям вплинули на вас емоційно',
                'Зосереджуватися на чомусь протягом десяти хвилин',
                'Іти пішки далеко, наприклад кілометр',
                'Мити все тіло',
                'Одягатися',
                'Спілкуватися з незнайомими людьми',
                'Підтримувати дружбу',
                'Ваша повсякденна робота або заняття',
            ],
        },
    },
}

# ─── Textos de la UI en cada idioma ──────────────────────────────────────────
UI_TEXTS = {
    'submit': {
        'ca': 'Enviar respostes', 'es': 'Enviar respuestas', 'en': 'Submit answers',
        'fr': 'Envoyer les réponses', 'ar': 'إرسال الإجابات',
        'ru': 'Отправить ответы', 'uk': 'Надіслати відповіді',
    },
    'required': {
        'ca': 'Si us plau, respon totes les preguntes abans d\'enviar.',
        'es': 'Por favor, responde todas las preguntas antes de enviar.',
        'en': 'Please answer all questions before submitting.',
        'fr': 'Veuillez répondre à toutes les questions avant d\'envoyer.',
        'ar': 'يُرجى الإجابة على جميع الأسئلة قبل الإرسال.',
        'ru': 'Пожалуйста, ответьте на все вопросы перед отправкой.',
        'uk': 'Будь ласка, дайте відповідь на всі запитання перед надсиланням.',
    },
    'thanks_title': {
        'ca': 'Gràcies per completar el qüestionari',
        'es': 'Gracias por completar el cuestionario',
        'en': 'Thank you for completing the questionnaire',
        'fr': 'Merci d\'avoir complété le questionnaire',
        'ar': 'شكراً لإكمالك الاستبيان',
        'ru': 'Спасибо за заполнение анкеты',
        'uk': 'Дякуємо за заповнення анкети',
    },
    'thanks_body': {
        'ca': 'Les teves respostes han estat enviades al professional que t\'ha assignat el qüestionari. Pots tancar aquesta finestra.',
        'es': 'Tus respuestas han sido enviadas al profesional que te asignó el cuestionario. Puedes cerrar esta ventana.',
        'en': 'Your answers have been sent to the professional who assigned you this questionnaire. You can close this window.',
        'fr': 'Vos réponses ont été envoyées au professionnel qui vous a assigné ce questionnaire. Vous pouvez fermer cette fenêtre.',
        'ar': 'تم إرسال إجاباتك إلى المختص الذي أرسل لك الاستبيان. يمكنك إغلاق هذه النافذة.',
        'ru': 'Ваши ответы отправлены специалисту, назначившему вам эту анкету. Вы можете закрыть это окно.',
        'uk': 'Ваші відповіді надіслано фахівцю, який призначив вам цю анкету. Ви можете закрити це вікно.',
    },
    'expired': {
        'ca': 'Aquest formulari ha caducat o ja ha estat completat. Posa\'t en contacte amb el professional per si cal un nou formulari.',
        'es': 'Este formulario ha caducado o ya ha sido completado. Contacta con el profesional si necesitas un nuevo formulario.',
        'en': 'This form has expired or has already been completed. Please contact the professional if you need a new form.',
        'fr': 'Ce formulaire a expiré ou a déjà été complété. Contactez le professionnel si vous avez besoin d\'un nouveau formulaire.',
        'ar': 'انتهت صلاحية هذا النموذج أو تم إكماله بالفعل. تواصل مع المختص إذا احتجت نموذجاً جديداً.',
        'ru': 'Срок действия формы истёк или она уже заполнена. Обратитесь к специалисту, если вам нужна новая форма.',
        'uk': 'Термін дії форми закінчився або вона вже заповнена. Зверніться до фахівця, якщо вам потрібна нова форма.',
    },
    'progress': {
        'ca': 'Pregunta {current} de {total}',
        'es': 'Pregunta {current} de {total}',
        'en': 'Question {current} of {total}',
        'fr': 'Question {current} sur {total}',
        'ar': 'سؤال {current} من {total}',
        'ru': 'Вопрос {current} из {total}',
        'uk': 'Запитання {current} з {total}',
    },
}


# ─── Controlador ─────────────────────────────────────────────────────────────

class AssessmentPortalController(http.Controller):

    @http.route('/avaluacio/<string:token>', type='http', auth='public', website=False, csrf=False)
    def portal_form(self, token, **kwargs):
        Session = request.env['acathi.assessment.session'].sudo()
        session = Session.search([('token', '=', token)], limit=1)

        lang = kwargs.get('lang', session.language if session else 'ca')
        if lang not in LANG_LABELS:
            lang = 'ca'

        if not session or session.state in ('completed', 'expired') or \
                session.expiry_date < fields.Datetime.now():
            if session and session.state == 'pending' and session.expiry_date < fields.Datetime.now():
                session.state = 'expired'
            msg = UI_TEXTS['expired'].get(lang, UI_TEXTS['expired']['ca'])
            return request.make_response(self._render_error(msg, lang),
                                         headers=[('Content-Type', 'text/html; charset=utf-8')])

        instrument_key = session.instrument
        if instrument_key not in INSTRUMENTS:
            return request.make_response(self._render_error('Instrument no disponible', lang),
                                         headers=[('Content-Type', 'text/html; charset=utf-8')])

        instrument_data = INSTRUMENTS[instrument_key]
        html = self._render_form(session, instrument_data, lang)
        return request.make_response(html,
                                     headers=[('Content-Type', 'text/html; charset=utf-8')])

    @http.route('/avaluacio/<string:token>/qr', type='http', auth='public', website=False, csrf=False)
    def portal_qr(self, token, **kwargs):
        """Retorna una pàgina HTML amb el QR de la sessió per imprimir o escanejar."""
        Session = request.env['acathi.assessment.session'].sudo()
        session = Session.search([('token', '=', token)], limit=1)
        if not session:
            return request.make_response(self._render_error('Sessió no trobada', 'ca'),
                                         headers=[('Content-Type', 'text/html; charset=utf-8')])

        base = request.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        url = f'{base}/avaluacio/{token}'
        instrument_name = dict(session._fields['instrument'].selection).get(session.instrument, '')

        # Genera QR via biblioteca Python (si disponible) o mostra URL gran
        qr_html = ''
        try:
            import qrcode
            import base64
            import io
            qr = qrcode.QRCode(version=1, box_size=8, border=4)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            b64 = base64.b64encode(buf.getvalue()).decode()
            qr_html = f'<img src="data:image/png;base64,{b64}" style="width:240px;height:240px" alt="QR Code"/>'
        except ImportError:
            qr_html = f'<div style="font-size:.8rem;word-break:break-all;color:#555;max-width:300px">{url}</div>'

        html = f'''<!DOCTYPE html>
<html lang="ca"><head><meta charset="utf-8">
<title>QR — {instrument_name} — ACATHI</title>
<style>
body{{font-family:system-ui,sans-serif;display:flex;align-items:center;
  justify-content:center;min-height:100vh;margin:0;background:#fff}}
.card{{text-align:center;padding:2rem;max-width:340px}}
.logo{{font-weight:700;font-size:1.2rem;color:#6a3fa0;margin-bottom:.5rem}}
.instr{{font-size:.9rem;color:#666;margin-bottom:1rem}}
.url{{font-size:.75rem;color:#999;word-break:break-all;margin-top:1rem}}
@media print{{button{{display:none}}}}
</style></head>
<body><div class="card">
<div class="logo">ACATHI</div>
<div class="instr">{instrument_name}</div>
{qr_html}
<div class="url">{url}</div>
<br>
<button onclick="window.print()" style="margin-top:1rem;padding:.5rem 1.5rem;
  background:#6a3fa0;color:#fff;border:none;border-radius:8px;cursor:pointer">
  🖨️ Imprimir
</button>
</div></body></html>'''

        return request.make_response(html,
                                     headers=[('Content-Type', 'text/html; charset=utf-8')])

    @http.route('/avaluacio/<string:token>/submit', type='json', auth='public', csrf=False)
    def portal_submit(self, token, answers=None, lang='ca', **kwargs):
        if not answers:
            return {'ok': False, 'error': 'no_data'}

        Session = request.env['acathi.assessment.session'].sudo()
        session = Session.search([('token', '=', token)], limit=1)

        if not session or session.state != 'pending' or session.expiry_date < fields.Datetime.now():
            return {'ok': False, 'error': 'invalid_session'}

        instrument = session.instrument
        if instrument not in INSTRUMENTS:
            return {'ok': False, 'error': 'unknown_instrument'}

        try:
            result = self._save_answers(session, instrument, answers, lang)
        except Exception as exc:
            return {'ok': False, 'error': str(exc)}

        session.state = 'completed'
        return {'ok': True, 'thanks_title': UI_TEXTS['thanks_title'].get(lang, ''),
                'thanks_body': UI_TEXTS['thanks_body'].get(lang, '')}

    def _save_answers(self, session, instrument, answers, lang):
        """Desa les respostes al model d'Odoo corresponent."""
        env = request.env
        common = {
            'person_id': session.person_id.id,
            'case_id': session.case_id.id if session.case_id else False,
            'professional_id': session.professional_id.id,
            'date': fields.Date.today(),
            'notes': f'[Portal mòbil — idioma: {lang}]',
        }

        def q(key):
            return str(answers.get(key, '0'))

        if instrument == 'phq9':
            rec = env['acathi.phq9'].sudo().create({
                **common,
                'q1': q('q1'), 'q2': q('q2'), 'q3': q('q3'),
                'q4': q('q4'), 'q5': q('q5'), 'q6': q('q6'),
                'q7': q('q7'), 'q8': q('q8'), 'q9': q('q9'),
            })
            session.result_phq9_id = rec.id

        elif instrument == 'gad7':
            rec = env['acathi.gad7'].sudo().create({
                **common,
                'q1': q('q1'), 'q2': q('q2'), 'q3': q('q3'),
                'q4': q('q4'), 'q5': q('q5'), 'q6': q('q6'), 'q7': q('q7'),
            })
            session.result_gad7_id = rec.id

        elif instrument == 'pcl5':
            vals = {**common}
            for i in range(1, 21):
                vals[f'q{i}'] = q(f'q{i}')
            rec = env['acathi.pcl5'].sudo().create(vals)
            session.result_pcl5_id = rec.id

        elif instrument == 'hscl25':
            vals = {**common}
            for i in range(1, 26):
                vals[f'q{i}'] = q(f'q{i}')
            rec = env['acathi.hscl25'].sudo().create(vals)
            session.result_hscl25_id = rec.id

        elif instrument == 'iesr':
            vals = {**common}
            for i in range(1, 23):
                vals[f'q{i}'] = q(f'q{i}')
            rec = env['acathi.iesr'].sudo().create(vals)
            session.result_iesr_id = rec.id

        elif instrument == 'whodas':
            vals = {**common}
            for i in range(1, 13):
                vals[f'q{i}'] = q(f'q{i}')
            rec = env['acathi.whodas'].sudo().create(vals)
            session.result_whodas_id = rec.id

        return True

    def _render_error(self, message, lang='ca'):
        dir_attr = 'rtl' if lang == 'ar' else 'ltr'
        return f'''<!DOCTYPE html><html lang="{lang}" dir="{dir_attr}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ACATHI</title>
<style>
body{{font-family:system-ui,sans-serif;background:#f5f5f5;display:flex;align-items:center;
justify-content:center;min-height:100vh;margin:0;padding:1rem}}
.card{{background:#fff;border-radius:12px;padding:2rem;max-width:480px;text-align:center;
box-shadow:0 2px 8px rgba(0,0,0,.1)}}
.logo{{font-size:1.5rem;font-weight:700;color:#6a3fa0;margin-bottom:1rem}}
p{{color:#555;line-height:1.6}}
</style></head>
<body><div class="card">
<div class="logo">ACATHI</div>
<p>{message}</p>
</div></body></html>'''

    def _render_form(self, session, instrument_data, lang):
        questions = instrument_data['questions'].get(lang, instrument_data['questions']['ca'])
        scale = instrument_data['scale'].get(lang, instrument_data['scale']['ca'])
        scale_values = instrument_data['scale_values']
        title = instrument_data['title'].get(lang, instrument_data['title']['ca'])
        instructions = instrument_data['instructions'].get(lang, instrument_data['instructions']['ca'])

        dir_attr = 'rtl' if lang == 'ar' else 'ltr'

        # Language switcher
        lang_buttons = ''.join(
            f'<a href="/avaluacio/{session.token}?lang={lk}" '
            f'class="lang-btn{"  active" if lk == lang else ""}">'
            f'{lv["name"]}</a>'
            for lk, lv in LANG_LABELS.items()
        )

        # Questions HTML
        q_html = ''
        for idx, q_text in enumerate(questions, 1):
            q_key = f'q{idx}'
            options = ''.join(
                f'<label class="option-label">'
                f'<input type="radio" name="{q_key}" value="{sv}" required>'
                f'<span class="option-text">{sv_label}</span>'
                f'</label>'
                for sv, sv_label in zip(scale_values, scale)
            )
            q_html += f'''<div class="question-card" id="qc-{idx}">
<div class="q-num">{idx}</div>
<div class="q-body">
  <p class="q-text">{q_text}</p>
  <div class="options">{options}</div>
</div></div>'''

        total = len(questions)
        submit_text = UI_TEXTS['submit'].get(lang, 'Enviar')
        required_text = UI_TEXTS['required'].get(lang, '')
        progress_tpl = UI_TEXTS['progress'].get(lang, 'Question {current} of {total}')

        # Serialize data for JS
        session_js = json.dumps({
            'token': session.token,
            'lang': lang,
            'total': total,
            'thanks_title': UI_TEXTS['thanks_title'].get(lang, ''),
            'thanks_body': UI_TEXTS['thanks_body'].get(lang, ''),
            'required_msg': required_text,
            'progress_tpl': progress_tpl,
        })

        return f'''<!DOCTYPE html>
<html lang="{lang}" dir="{dir_attr}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#6a3fa0">
<title>{title} — ACATHI</title>
<style>
:root{{
  --purple:#6a3fa0;--purple-light:#ede9f8;--purple-dark:#4e2e7a;
  --green:#2ecc71;--text:#1a1a2e;--muted:#666;--border:#e0e0e0;
  --radius:12px;--shadow:0 2px 8px rgba(0,0,0,.08);
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:system-ui,-apple-system,sans-serif;background:#f7f5fb;
  color:var(--text);min-height:100vh}}
header{{background:var(--purple);color:#fff;padding:.75rem 1rem;
  display:flex;align-items:center;gap:.75rem;position:sticky;top:0;z-index:10}}
.logo{{font-weight:700;font-size:1.1rem;letter-spacing:.02em}}
.lang-switcher{{display:flex;flex-wrap:wrap;gap:.25rem;padding:.5rem 1rem;
  background:#fff;border-bottom:1px solid var(--border)}}
.lang-btn{{padding:.25rem .6rem;border-radius:6px;font-size:.8rem;
  text-decoration:none;color:var(--purple);border:1px solid var(--border)}}
.lang-btn.active{{background:var(--purple);color:#fff;border-color:var(--purple)}}
.progress-bar{{height:4px;background:var(--border);position:sticky;top:48px;z-index:9}}
.progress-fill{{height:100%;background:var(--purple);transition:width .3s;width:0%}}
main{{max-width:680px;margin:0 auto;padding:1rem 1rem 6rem}}
.instrument-header{{background:#fff;border-radius:var(--radius);padding:1.25rem;
  margin-bottom:1rem;box-shadow:var(--shadow)}}
.instrument-title{{font-size:1.1rem;font-weight:700;color:var(--purple);margin-bottom:.5rem}}
.instrument-instructions{{font-size:.9rem;color:var(--muted);line-height:1.5}}
.question-card{{background:#fff;border-radius:var(--radius);padding:1rem;
  margin-bottom:.75rem;box-shadow:var(--shadow);display:flex;gap:.75rem;
  border-left:4px solid var(--border);transition:border-color .2s}}
.question-card.answered{{border-left-color:var(--green)}}
.q-num{{font-weight:700;color:var(--purple);font-size:1.1rem;
  min-width:1.75rem;padding-top:.1rem}}
.q-body{{flex:1}}
.q-text{{font-size:.95rem;line-height:1.4;margin-bottom:.75rem}}
.options{{display:flex;flex-direction:column;gap:.5rem}}
.option-label{{display:flex;align-items:center;gap:.6rem;cursor:pointer;
  padding:.5rem .75rem;border-radius:8px;border:1px solid var(--border);
  transition:background .15s,border-color .15s}}
.option-label:has(input:checked){{background:var(--purple-light);
  border-color:var(--purple)}}
.option-label input[type="radio"]{{width:18px;height:18px;accent-color:var(--purple);
  flex-shrink:0}}
.option-text{{font-size:.9rem}}
[dir="rtl"] .question-card{{border-left:none;border-right:4px solid var(--border)}}
[dir="rtl"] .question-card.answered{{border-right-color:var(--green)}}
.sticky-submit{{position:fixed;bottom:0;left:0;right:0;padding:1rem;
  background:#fff;border-top:1px solid var(--border);
  display:flex;flex-direction:column;align-items:center;gap:.5rem}}
.btn-submit{{background:var(--purple);color:#fff;border:none;
  padding:.9rem 2rem;border-radius:10px;font-size:1rem;font-weight:600;
  width:100%;max-width:400px;cursor:pointer;transition:background .2s}}
.btn-submit:hover{{background:var(--purple-dark)}}
.btn-submit:disabled{{background:#aaa;cursor:not-allowed}}
.progress-text{{font-size:.8rem;color:var(--muted)}}
.error-msg{{color:#c0392b;font-size:.85rem;display:none}}
.thanks-screen{{display:none;text-align:center;padding:3rem 1rem}}
.thanks-icon{{font-size:4rem;margin-bottom:1rem}}
.thanks-title{{font-size:1.3rem;font-weight:700;color:var(--purple);margin-bottom:.75rem}}
.thanks-body{{font-size:.95rem;color:var(--muted);line-height:1.6}}
</style>
</head>
<body>
<header>
  <div class="logo">ACATHI</div>
  <div style="font-size:.85rem;opacity:.85">{title}</div>
</header>

<div class="lang-switcher">{lang_buttons}</div>
<div class="progress-bar"><div class="progress-fill" id="progress-fill"></div></div>

<main>
  <div class="instrument-header">
    <div class="instrument-title">{title}</div>
    <div class="instrument-instructions">{instructions}</div>
  </div>

  <form id="assessment-form" novalidate>
    {q_html}
  </form>

  <div class="thanks-screen" id="thanks-screen">
    <div class="thanks-icon">✅</div>
    <div class="thanks-title" id="thanks-title"></div>
    <div class="thanks-body" id="thanks-body"></div>
  </div>
</main>

<div class="sticky-submit" id="sticky-submit">
  <div class="progress-text" id="progress-text"></div>
  <div class="error-msg" id="error-msg"></div>
  <button class="btn-submit" id="btn-submit" type="button">{submit_text}</button>
</div>

<script>
const S = {session_js};
let answered = 0;

function updateProgress() {{
  const total = S.total;
  const cards = document.querySelectorAll('.question-card');
  let done = 0;
  cards.forEach((card, i) => {{
    const checked = card.querySelector('input[type="radio"]:checked');
    if (checked) {{ done++; card.classList.add('answered'); }}
    else {{ card.classList.remove('answered'); }}
  }});
  answered = done;
  document.getElementById('progress-fill').style.width = (done / total * 100) + '%';
  const tpl = S.progress_tpl;
  document.getElementById('progress-text').textContent =
    tpl.replace('{{current}}', done).replace('{{total}}', total);
}}

document.getElementById('assessment-form').addEventListener('change', updateProgress);
updateProgress();

document.getElementById('btn-submit').addEventListener('click', async () => {{
  const form = document.getElementById('assessment-form');
  const total = S.total;
  const errorEl = document.getElementById('error-msg');

  // check all answered
  let allAnswered = true;
  for (let i = 1; i <= total; i++) {{
    if (!form.querySelector(`input[name="q${{i}}"]:checked`)) {{
      allAnswered = false;
      const card = document.getElementById(`qc-${{i}}`);
      if (card) card.scrollIntoView({{behavior:'smooth',block:'center'}});
      break;
    }}
  }}
  if (!allAnswered) {{
    errorEl.textContent = S.required_msg;
    errorEl.style.display = 'block';
    return;
  }}
  errorEl.style.display = 'none';

  const answers = {{}};
  for (let i = 1; i <= total; i++) {{
    const el = form.querySelector(`input[name="q${{i}}"]:checked`);
    if (el) answers[`q${{i}}`] = el.value;
  }}

  const btn = document.getElementById('btn-submit');
  btn.disabled = true;
  btn.textContent = '...';

  try {{
    const res = await fetch('/avaluacio/' + S.token + '/submit', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{jsonrpc:'2.0',method:'call',id:1,
        params:{{answers, lang: S.lang}}}})
    }});
    const data = await res.json();
    const result = data.result;
    if (result && result.ok) {{
      document.getElementById('assessment-form').style.display = 'none';
      document.getElementById('sticky-submit').style.display = 'none';
      const thanks = document.getElementById('thanks-screen');
      document.getElementById('thanks-title').textContent = result.thanks_title || S.thanks_title;
      document.getElementById('thanks-body').textContent = result.thanks_body || S.thanks_body;
      thanks.style.display = 'block';
    }} else {{
      btn.disabled = false;
      btn.textContent = '{submit_text}';
      errorEl.textContent = 'Error: ' + (result && result.error ? result.error : 'unknown');
      errorEl.style.display = 'block';
    }}
  }} catch(e) {{
    btn.disabled = false;
    btn.textContent = '{submit_text}';
    errorEl.textContent = 'Error de xarxa. Torna-ho a intentar.';
    errorEl.style.display = 'block';
  }}
}});
</script>
</body>
</html>'''
