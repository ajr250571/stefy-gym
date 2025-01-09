from core.wsgi import *

from gym.models import Plan

# Poblar tabla plan con datos iniciales
Plan.objects.create(nombre='Mensual', precio=15000, duracion=1,
                    descripcion='Plan Mensual', activo=True)
