import os
import sys
from datetime import datetime, time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django

django.setup()

# CORREGIDO: Se eliminan Estilista y HorarioEstilista (modelos eliminados).
# Horario reemplaza a HorarioEstilista.
# Los estilistas ahora son registros de Usuario con rol='estilista'.
from core.models import Cita, Horario, Peluqueria, Servicio, Usuario

print('Creando datos de ejemplo...')

# --- Limpieza (orden importa por las FK) ---
Cita.objects.all().delete()
Horario.objects.all().delete()
Servicio.objects.all().delete()
Usuario.objects.all().delete()
Peluqueria.objects.all().delete()

# =============================================================================
# PELUQUERIA
# =============================================================================
peluqueria = Peluqueria.objects.create(
    nombre='Bella Estetica',
    telefono='987654321',
    direccion='Calle Principal 123',
    descripcion='Centro de belleza profesional',
)
print(f'Peluqueria: {peluqueria}')

# =============================================================================
# USUARIOS
# =============================================================================
# CORREGIDO: Se usa create_user() en lugar de create() para que AbstractUser
# haga el hashing correcto de la contrasena. NO se usa el campo inventado
# 'contrasena' ni 'nombre'. Se usan 'first_name', 'last_name' y 'password'.
# Para el estado activo/inactivo se usa 'is_active' (Regla #7), no 'status'.

admin = Usuario.objects.create_user(
    username='admin_bella',
    first_name='Admin',
    last_name='Sistema',
    email='admin@bellaestetica.com',
    password='admin123',
    rol='administrador',
    is_active=True,
)
print(f'Usuario Admin: {admin}')

cliente1 = Usuario.objects.create_user(
    username='maria_garcia',
    first_name='Maria',
    last_name='Garcia',
    email='maria@email.com',
    password='pass123',
    telefono='987111111',
    rol='cliente',
    is_active=True,
)
print(f'Cliente: {cliente1}')

cliente2 = Usuario.objects.create_user(
    username='juan_perez',
    first_name='Juan',
    last_name='Perez',
    email='juan@email.com',
    password='pass123',
    telefono='987222222',
    rol='cliente',
    is_active=True,
)
print(f'Cliente: {cliente2}')

# CORREGIDO: Los estilistas ya NO se crean con Estilista.objects.create().
# Ahora son Usuarios con rol='estilista', con peluqueria y especialidad asignadas.
# Se usa create_user() para el hashing de contrasena.

estilista1 = Usuario.objects.create_user(
    username='ana_lopez',
    first_name='Ana',
    last_name='Lopez',
    email='ana@bellaestetica.com',
    password='pass123',
    telefono='987123456',
    rol='estilista',
    is_active=True,
    peluqueria=peluqueria,       # FK antes en Estilista.hair_salon
    especialidad='Cortes y Tintes',
)
print(f'Estilista: {estilista1}')

estilista2 = Usuario.objects.create_user(
    username='rosa_martinez',
    first_name='Rosa',
    last_name='Martinez',
    email='rosa@bellaestetica.com',
    password='pass123',
    telefono='987654000',
    rol='estilista',
    is_active=True,
    peluqueria=peluqueria,
    especialidad='Peinados y Tratamientos',
)
print(f'Estilista: {estilista2}')

# =============================================================================
# SERVICIOS
# =============================================================================
servicio1 = Servicio.objects.create(
    nombre='Corte de cabello',
    descripcion='Corte profesional personalizado',
    precio=50.00,
    duracion_minutos=30,
    hair_salon=peluqueria,
)
print(f'Servicio: {servicio1}')

servicio2 = Servicio.objects.create(
    nombre='Tintura',
    descripcion='Tintura profesional de calidad',
    precio=80.00,
    duracion_minutos=60,
    hair_salon=peluqueria,
)
print(f'Servicio: {servicio2}')

servicio3 = Servicio.objects.create(
    nombre='Peinado',
    descripcion='Peinado de ocasion',
    precio=35.00,
    duracion_minutos=20,
    hair_salon=peluqueria,
)
print(f'Servicio: {servicio3}')

# =============================================================================
# HORARIOS (antes HorarioEstilista)
# =============================================================================
# CORREGIDO: Se usa Horario en lugar de HorarioEstilista.
# 'stylist' fue renombrado a 'estilista' (FK a Usuario con rol='estilista').

Horario.objects.create(
    estilista=estilista1,
    dia_semana='lunes',
    hora_inicio=time(9, 0),
    hora_fin=time(18, 0),
    activo=True,
)
print('Horario: Ana Lopez - Lunes 09:00-18:00')

Horario.objects.create(
    estilista=estilista1,
    dia_semana='martes',
    hora_inicio=time(9, 0),
    hora_fin=time(18, 0),
    activo=True,
)
print('Horario: Ana Lopez - Martes 09:00-18:00')

Horario.objects.create(
    estilista=estilista2,
    dia_semana='lunes',
    hora_inicio=time(10, 0),
    hora_fin=time(19, 0),
    activo=True,
)
print('Horario: Rosa Martinez - Lunes 10:00-19:00')

# =============================================================================
# CITAS
# =============================================================================
# CORREGIDO: Los campos de FK cambiaron:
#   'user'     → 'cliente'    (related_name='citas_como_cliente')
#   'stylist'  → 'estilista'  (related_name='citas_como_estilista')
#   'service'  → 'servicio'   (related_name='citas')
#
# Las validaciones en Cita.clean() verifican que:
#   1. hora_fin > hora_inicio
#   2. duracion_real == servicio.duracion_minutos
#   3. estilista.peluqueria == servicio.hair_salon
#   4. No solapamientos de horario para el mismo estilista
# Los datos de prueba cumplen todas estas reglas.

cita1 = Cita.objects.create(
    cliente=cliente1,
    estilista=estilista1,
    servicio=servicio1,
    fecha=datetime.now().date(),
    hora_inicio=time(10, 0),
    hora_fin=time(10, 30),     # 30 min = duracion_minutos de servicio1
    estado='confirmada',
)
print(f'Cita 1: {cita1} (estado={cita1.estado})')

cita2 = Cita.objects.create(
    cliente=cliente2,
    estilista=estilista2,
    servicio=servicio2,
    fecha=datetime.now().date(),
    hora_inicio=time(11, 0),
    hora_fin=time(12, 0),     # 60 min = duracion_minutos de servicio2
    estado='cancelada',
)
print(f'Cita 2: {cita2} (estado={cita2.estado})')

print('\nDatos de ejemplo creados exitosamente!')
print('Total: 1 peluqueria, 4 usuarios (1 admin + 2 clientes + 2 estilistas), 3 servicios, 3 horarios, 2 citas')