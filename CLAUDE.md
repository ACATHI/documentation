# ACATHI Odoo — Regles de projecte

## Entorn
- Odoo 17 Community · Docker container `odoo17` · DB: `db17`
- Servidor: `root@mail` · Custom-addons: `/srv/odoo17/custom-addons/`
- Còpia local: `C:\Users\PresidentACATHI\Documents\odoo\`
- SCP: `scp -i ~/.ssh/id_rsa_acathi` (clau bcrypt, demana passphrase)
- Log del servidor: `tail -20 /srv/odoo17/data/odoo.log` (no stdout)

## Desplegament — ordre obligatori

```bash
ODOO_IMAGE=$(docker inspect odoo17 --format '{{.Image}}')
docker stop odoo17
docker run --rm --network acathi-net \
  -v /srv/odoo17/custom-addons:/mnt/extra-addons \
  -v /srv/odoo17/data:/var/lib/odoo \
  -v /srv/odoo17/config/odoo.conf:/etc/odoo/odoo.conf \
  $ODOO_IMAGE odoo -c /etc/odoo/odoo.conf -d db17 \
  --update NOM_MODUL --stop-after-init
tail -20 /srv/odoo17/data/odoo.log
docker start odoo17
```

Executar `ruff check` i `ruff format` **abans** de fer scp.

## Regles Odoo 17 — errors freqüents

| Regla | Correcte | Incorrecte |
|-------|----------|------------|
| Vistes llista | `<tree>` | `<list>` |
| view_mode | `'tree,form'` | `'list,form'` |
| decoration-* | a l'element `<tree>` | als `<field>` fills |
| _inherit com a llista | cal `_name` explícit | sense `_name` falla |
| partner_firstname instal·lat | `firstname` + `lastname` | sol `name` → error |

## Seguretat — mai al repositori
- Contrasenyes de servidor (root, db_password, admin_passwd)
- Tokens, claus d'API, credencials de qualsevol servei

## Mòduls del projecte

| Mòdul | Descripció | Estat |
|-------|-----------|-------|
| `acathi_social` | Gestió social: persones, casos, intervencions, habitatge | Producció |
| `grant_management` | Cicle de vida de subvencions | Producció |
| `acathi_consent` | Consentiment RGPD signable | Pendent desplegar |
| `acathi_collab` | Canal web: formulari + col·laboracions | Desenvolupament |
| `acathi_documents` | Gestió documental | Desenvolupament |
| `acathi_viajes` | Radar de viajes (integrat amb n8n) | Desenvolupament |
| `acathi_intake` | Formulari d'entrada de sol·licituds | Desenvolupament |

## Qualitat de codi

```bash
# Abans de qualsevol scp al servidor:
ruff check acathi_social_v17/
ruff format acathi_social_v17/
pylint --rcfile=.pylintrc acathi_social_v17/models/

# Activar entorn virtual (Windows):
.venv\Scripts\Activate.ps1
```

## Context ACATHI
- ONG LGBTIQ+ migrants i refugiats — dades molt sensibles (RGPD crític)
- Dades restringides: VIH, tràfic de persones, orientació sexual, NIE/passaport
- Finançadors: Ajuntament BCN, Diputació BCN, Generalitat DS, COSIFE, SMPRAV
- Idiomes de treball: català (normatiu institucional) i castellà
