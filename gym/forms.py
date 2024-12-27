from django import forms

from gym.models import Membresia, Plan, Socio


class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['nombre', 'precio',
                  'duracion', 'descripcion', 'activo']


class SocioForm(forms.ModelForm):
    class Meta:
        model = Socio
        fields = ['nombre', 'apellido', 'email', 'telefono',
                  'fecha_nacimiento', 'dni', 'direccion', 'activo']


class MembresiaForm(forms.ModelForm):
    class Meta:
        model = Membresia
        fields = ['socio', 'plan', 'fecha_inicio', 'fecha_fin', 'estado']
