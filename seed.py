from core.wsgi import *

from gym.models import Plan
from django.utils import timezone
import time
from datetime import timedelta

# Poblar tabla plan con datos iniciales
# Plan.objects.create(nombre='Mensual', precio=15000, duracion=1,
#                     descripcion='Plan Mensual', activo=True)
ahora = timezone.now()
print(ahora)
una_hora_despues = ahora + timedelta(hours=1)
print(una_hora_despues)
print("--------------------------------------")

print(timezone.now().date())
print(timezone.now())
print(time.strftime('%Y-%m-%d %H:%M:%S'))

print(time.localtime())
print(time.ctime())
print(timezone.now()-timezone.timedelta(days=1))
print(timezone.get_current_timezone_name())
print(timezone.now().tzinfo)