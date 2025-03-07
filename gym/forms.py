from datetime import date, timezone
from os import read
import re
from django import forms
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.utils.dateformat import format
from django.db.models import Q, BooleanField
from functools import reduce
import operator
from gym.models import Membresia, Plan, Socio, Pago


class DynamicFilterForm(forms.Form):
    CONDITION_CHOICES = (
        ('exact', 'Igual a'),
        ('icontains', 'Contiene (insensible a mayúsculas)'),
        ('gt', 'Mayor que'),
        ('lt', 'Menor que'),
        ('gte', 'Mayor o igual que'),
        ('lte', 'Menor o igual que'),
        ('startswith', 'Comienza con'),
        ('endswith', 'Termina con'),
    )

    BOOLEAN_CHOICES = (
        ('', '---------'),
        ('true', 'Sí'),
        ('false', 'No'),
    )

    field_name = forms.ChoiceField(label='Campo')
    condition = forms.ChoiceField(label='Condición', choices=CONDITION_CHOICES)
    value = forms.CharField(label='Valor', required=False)

    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Generar opciones de campos basadas en el modelo
        field_choices = [
            (field.name, field.verbose_name or field.name)
            for field in model._meta.fields
            if field.concrete and not field.many_to_many
        ]
        self.fields['field_name'].choices = field_choices

        # Obtener el modelo para inspeccionar los tipos de campos
        self.model = model
        self.adjust_fields_for_boolean()

    def adjust_fields_for_boolean(self):
        """Ajustar el campo 'value' según el tipo de campo seleccionado"""
        if 'field_name' in self.data:
            field_name = self.data['field_name']
            field = self.model._meta.get_field(field_name)
            if isinstance(field, BooleanField):
                self.fields['value'] = forms.ChoiceField(
                    choices=self.BOOLEAN_CHOICES,
                    label='Valor',
                    required=False,
                    widget=forms.Select
                )
                # Limitar las condiciones para booleanos
                self.fields['condition'].choices = [
                    ('exact', 'Igual a'),
                    ('isnull', 'Es nulo'),
                ]

    def clean(self):
        cleaned_data = super().clean()
        field_name = cleaned_data.get('field_name')
        condition = cleaned_data.get('condition')
        value = cleaned_data.get('value')

        if field_name and condition:
            field = self.model._meta.get_field(field_name)
            if isinstance(field, BooleanField):
                if value == 'true':
                    cleaned_data['value'] = True
                elif value == 'false':
                    cleaned_data['value'] = False
                elif value == '':
                    cleaned_data['value'] = None

        if condition and not value and condition != 'isnull':
            raise forms.ValidationError(
                "El valor es requerido para esta condición.")
        return cleaned_data

    def get_filter(self):
        if self.is_valid():
            field = self.cleaned_data['field_name']
            condition = self.cleaned_data['condition']
            value = self.cleaned_data['value']
            model_field = self.model._meta.get_field(field)

            if isinstance(model_field, BooleanField):
                if condition == 'exact' and value is not None:
                    return Q(**{field: value})
                elif condition == 'isnull':
                    return Q(**{f"{field}__isnull": True if value is None else False})
            elif value:
                filter_key = f"{field}__{condition}"
                return Q(**{filter_key: value})
        return Q()


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
        if self.instance and not self.instance.pk:
            # format(timezone.now().date(), 'Y-m-d')
            self.initial['fecha_pago'] = format(timezone.now().date(), 'Y-m-d')
        else:
            self.initial['fecha_pago'] = format(
                self.instance.fecha_pago, 'Y-m-d')
        # Inicializar el campo monto como oculto
        if self.instance:
            self.fields['estado'].initial = 'PAGADO'
            self.fields['monto'] = forms.DecimalField(
                widget=forms.HiddenInput(), required=False)
            # Si hay una instancia (edición), establecer el monto inicial
        if self.instance and self.instance.pk:
            # self.fields['estado'].initial = 'PAGADO'
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
