from datetime import date, timezone
from os import read
import re
from django import forms
from dateutil.relativedelta import relativedelta


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


class PagoFilterForm(forms.Form):
    fecha_pago_desde = forms.DateField()
    fecha_pago_hasta = forms.DateField()

    def __init__(self, *args, **kwargs):
        super(PagoFilterForm, self).__init__(*args, **kwargs)

        # Asignar fechas por defecto
        # self.fields['fecha_pago_desde'].initial = date.today() - \
        #     relativedelta(months=1)
        # self.fields['fecha_pago_hasta'].initial = date.today()
        # Asigna texto para mostrar

        self.fields['fecha_pago_desde'].label = 'Desde'
        self.fields['fecha_pago_hasta'].label = 'Hasta'
        # Asigna formato de fecha
        self.fields['fecha_pago_desde'].widget = forms.DateInput(
            attrs={'type': 'date'})
        self.fields['fecha_pago_hasta'].widget = forms.DateInput(
            attrs={'type': 'date'})
