from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import *

@admin.register(Plan)
class PlanAdmin(SimpleHistoryAdmin):
    list_display = ('nombre', 'descripcion', 'precio',
                    'duracion', 'activo')
    ordering = ('duracion',)

@admin.register(Socio)
class SocioAdmin(SimpleHistoryAdmin):
    list_display = ('nombre_completo', 'email', 'telefono',
                    'fecha_nacimiento', 'dni', 'direccion', 'activo', 'fecha_alta')
    ordering = ('apellido', 'nombre')


@admin.register(Membresia)
class MembresiaAdmin(SimpleHistoryAdmin):
    list_display = ('socio', 'plan', 'fecha_inicio',
                    'fecha_fin', 'estado', 'vigente')
    ordering = ('socio',)


@admin.register(Pago)
class PagoAdmin(SimpleHistoryAdmin):
    list_display = ('membresia', 'monto', 'fecha_pago',
                    'fecha_vencimiento', 'estado', 'metodo_pago')

    ordering = ('membresia',)


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('socio', 'fecha')
    list_filter = ('socio', 'fecha',)

    ordering = ('socio', '-fecha')
