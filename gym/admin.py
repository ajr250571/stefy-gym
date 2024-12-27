from django.contrib import admin

from .models import *


@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'email', 'telefono',
                    'fecha_nacimiento', 'dni', 'direccion', 'activo', 'fecha_alta')
    ordering = ('apellido', 'nombre')


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'precio',
                    'duracion', 'activo')
    ordering = ('duracion',)


@admin.register(Membresia)
class MembresiaAdmin(admin.ModelAdmin):
    list_display = ('socio', 'plan', 'fecha_inicio', 'fecha_fin', 'estado')
    ordering = ('socio',)


admin.site.register(Pago)
