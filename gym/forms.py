from os import read
import re
from django import forms

from gym.models import Membresia, Plan, Socio, Pago


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['socio'].queryset = Socio.objects.filter(  # type: ignore
            activo=True)
        self.fields['plan'].queryset = Plan.objects.filter(  # type: ignore
            activo=True)  # type: ignore


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['membresia', 'monto', 'fecha_pago',
                  'fecha_vencimiento', 'estado', 'metodo_pago', 'comprobante_nro']

    def __init__(self, *args, **kwargs):
        super(PagoForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['fecha_vencimiento'].widget.attrs['readonly'] = False
