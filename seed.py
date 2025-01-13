from core.wsgi import *

from gym.models import Plan
from django.utils import timezone
import time
from time import mktime
from datetime import timedelta, datetime

# Poblar tabla plan con datos iniciales
Plan.objects.create(nombre='Mensual', precio=15000, duracion=1,
    descripcion='Plan Mensual', activo=True)
Plan.objects.create(nombre='Semestral', precio=60000, duracion=6,
    descripcion='Plan Semestral', activo=True)
Plan.objects.create(nombre='Anual', precio=120000, duracion=12,
    descripcion='Plan Anual', activo=True)
