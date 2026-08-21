#!/usr/bin/env python3
"""
Script de exportación de datos Odoo 19 → CSV
Para ACATHI - Migración a Odoo 16
"""

import xmlrpc.client
import csv
import os
from datetime import datetime

# ── CONFIGURACIÓN ──────────────────────────────────────────────
URL      = "https://o.acathi.org"
DB       = "db"
USER     = "admin"           # cambia si tu usuario es otro
PASSWORD = "Bcnrav7103?"     # contraseña del usuario admin
OUTPUT   = "/srv/odoo/exports"
# ───────────────────────────────────────────────────────────────

os.makedirs(OUTPUT, exist_ok=True)

# Conexión
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid    = common.authenticate(DB, USER, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

if not uid:
    print("❌ Error de autenticación. Verifica usuario y contraseña.")
    exit(1)

print(f"✅ Conectado como UID {uid}")

def exportar(modelo, campos, nombre_archivo, dominio=[]):
    """Exporta un modelo Odoo a CSV"""
    print(f"📦 Exportando {modelo}...")
    try:
        ids = models.execute_kw(DB, uid, PASSWORD, modelo, 'search', [dominio])
        if not ids:
            print(f"   ⚠️  Sin registros en {modelo}")
            return
        registros = models.execute_kw(DB, uid, PASSWORD, modelo, 'read', [ids], {'fields': campos})
        ruta = os.path.join(OUTPUT, f"{nombre_archivo}_{datetime.now().strftime('%Y%m%d')}.csv")
        with open(ruta, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=campos, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(registros)
        print(f"   ✅ {len(registros)} registros → {ruta}")
    except Exception as e:
        print(f"   ❌ Error en {modelo}: {e}")

# ── EXPORTACIONES ──────────────────────────────────────────────

# 1. Empresas
exportar(
    'res.partner',
    ['name', 'email', 'phone', 'mobile', 'street', 'city', 'zip',
     'country_id', 'website', 'vat', 'comment', 'active'],
    'empresas',
    [['is_company', '=', True]]
)

# 2. Contactos (personas)
exportar(
    'res.partner',
    ['name', 'email', 'phone', 'mobile', 'street', 'city', 'zip',
     'country_id', 'function', 'company_id', 'comment', 'active'],
    'contactos',
    [['is_company', '=', False], ['type', '=', 'contact']]
)

# 3. Empleados
exportar(
    'hr.employee',
    ['name', 'job_title', 'job_id', 'department_id', 'work_email',
     'work_phone', 'mobile_phone', 'gender', 'birthday',
     'identification_id', 'country_id', 'active'],
    'empleados'
)

# 4. Ausencias (tipos)
exportar(
    'hr.leave.type',
    ['name', 'time_type', 'request_unit', 'leave_validation_type',
     'active'],
    'tipos_ausencia'
)

# 5. Ausencias (solicitudes)
exportar(
    'hr.leave.allocation',
    ['name', 'employee_id', 'holiday_status_id', 'number_of_days',
     'state', 'date_from', 'date_to'],
    'asignaciones_vacaciones'
)

# 6. Solicitudes de ausencia
exportar(
    'hr.leave',
    ['name', 'employee_id', 'holiday_status_id', 'number_of_days',
     'state', 'date_from', 'date_to'],
    'ausencias'
)

# 7. Departamentos
exportar(
    'hr.department',
    ['name', 'manager_id', 'active'],
    'departamentos'
)

# 8. Puestos de trabajo
exportar(
    'hr.job',
    ['name', 'department_id', 'no_of_recruitment', 'active'],
    'puestos'
)

print(f"\n✅ Exportación completada en {OUTPUT}")
print("📁 Archivos generados:")
for f in os.listdir(OUTPUT):
    ruta = os.path.join(OUTPUT, f)
    size = os.path.getsize(ruta)
    print(f"   {f} ({size/1024:.1f} KB)")
