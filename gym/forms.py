from datetime import date, timezone
from os import read
import re
from django import forms
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.utils.dateformat import format


from gym.models import Membresia, Plan, Socio, Pago


class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['nombre', 'precio',
                  'duracion', 'descripcion', 'activo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['duracion'].widget = forms.NumberInput(
            attrs={'type': 'number'})
        self.fields['descripcion'].widget = forms.Textarea(
            attrs={'rows': 3})


class SocioForm(forms.ModelForm):
    class Meta:
        model = Socio
        fields = ['nombre', 'apellido', 'email', 'telefono',
                  'fecha_nacimiento', 'dni', 'direccion', 'activo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_nacimiento'].widget = forms.DateInput(
            attrs={'type': 'text'})


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
        fields = ['membresia', 'monto', 'estado',  'fecha_pago',
                  'fecha_vencimiento', 'metodo_pago', 'comprobante_nro']
        readonly_fields = ['estado', 'monto']
        widgets = {
            'fecha_pago': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
            'fecha_vencimiento': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
            'monto': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'readonly': True
                }
            ),

            'comprobante_nro': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'metodo_pago': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'estado': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'readonly': True
                }
            ),
            'membresia': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super(PagoForm, self).__init__(*args, **kwargs)
        # Si es una nueva instancia (no es edición)
        if not self.instance.pk:
            self.initial['fecha_pago'] = format(timezone.now().date(), 'Y-m-d')
        # Inicializar el campo monto como oculto
        if self.instance:
            self.fields['estado'].initial = 'PAGADO'
            self.fields['monto'] = forms.DecimalField(
                widget=forms.HiddenInput(), required=False)
            # Si hay una instancia (edición), establecer el monto inicial
        if self.instance and self.instance.pk:
            self.fields['estado'].initial = 'PAGADO'
            self.fields['monto'].initial = self.instance.monto

    def clean(self):
        cleaned_data = super().clean()
        membresia = cleaned_data.get('membresia')

        if membresia:
            # Actualizar el monto basado en el plan de la membresía
            cleaned_data['monto'] = membresia.plan.precio
            # La fecha de vencimiento se calculará en el modelo

        return cleaned_data


class FechaFilterForm(forms.Form):
    fecha_desde = forms.DateField()
    fecha_hasta = forms.DateField()

    def __init__(self, *args, **kwargs):
        super(FechaFilterForm, self).__init__(*args, **kwargs)

        # Asignar fechas por defecto
        # self.fields['fecha_pago_desde'].initial = date.today() - \
        #     relativedelta(months=1)
        # self.fields['fecha_pago_hasta'].initial = date.today()
        # Asigna texto para mostrar

        self.fields['fecha_desde'].label = 'Desde'
        self.fields['fecha_hasta'].label = 'Hasta'
        # Asigna formato de fecha
        self.fields['fecha_desde'].widget = forms.DateInput(
            attrs={'type': 'date'})
        self.fields['fecha_hasta'].widget = forms.DateInput(
            attrs={'type': 'date'})
