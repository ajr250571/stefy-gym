from datetime import date
from colorama import init
from django import forms
import django_filters
from .models import Membresia, Pago, Asistencia, Socio, Plan
from dateutil.relativedelta import relativedelta

# filters.py
from django_filters import FilterSet, CharFilter, NumberFilter, BooleanFilter, DateFilter, ChoiceFilter
from django.db.models import fields, CharField, DateField, DateTimeField, BooleanField, IntegerField, FloatField, DecimalField, TextField

from gym import models


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, ButtonHolder, Submit


import django_filters
from django import forms
from django.db import models


class DynamicModelFilter(django_filters.FilterSet):
    # Condiciones por tipo de campo
    NUMBER_CONDITIONS = [
        ('exact', 'Igual a'),
        ('gt', 'Mayor que'),
        ('lt', 'Menor que'),
        ('gte', 'Mayor o igual'),
        ('lte', 'Menor o igual'),
    ]

    TEXT_CONDITIONS = [
        ('exact', 'Igual a'),
        ('contains', 'Contiene'),
        ('startswith', 'Comienza con'),
        ('endswith', 'Termina con'),
    ]

    BOOL_CONDITIONS = [
        ('exact', 'Verdadero', True),
        ('exact', 'Falso', False),
    ]

    DATE_CONDITIONS = [
        ('exact', 'Igual a'),
        ('lt', 'Antes de'),
        ('gt', 'Después de'),
        ('range', 'Entre'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dynamic_filters = self.build_dynamic_filters()

    def build_dynamic_filters(self):
        filters = {}
        # Obtener parámetros del formulario
        fields = self.data.getlist('field') if self.data else []
        conditions = self.data.getlist('condition') if self.data else []
        values = self.data.getlist('value') if self.data else []

        for i, field_name in enumerate(fields):
            if not field_name:
                continue

            field = self.queryset.model._meta.get_field(field_name)
            condition = conditions[i] if i < len(conditions) else 'exact'
            filter_name = f"{field_name}__{condition}"

            # Seleccionar widget y opciones según tipo de campo
            if isinstance(field, (models.IntegerField, models.FloatField)):
                filters[filter_name] = django_filters.NumberFilter(
                    field_name=field_name, lookup_expr=condition
                )
            elif isinstance(field, (models.CharField, models.TextField)):
                filters[filter_name] = django_filters.CharFilter(
                    field_name=field_name, lookup_expr=condition
                )
            elif isinstance(field, models.BooleanField):
                filters[filter_name] = django_filters.BooleanFilter(
                    field_name=field_name, lookup_expr='exact'
                )
            elif isinstance(field, (models.DateField, models.DateTimeField)):
                if condition == 'range':
                    filters[f"{field_name}__gte"] = django_filters.DateFilter(
                        field_name=field_name, lookup_expr='gte'
                    )
                    filters[f"{field_name}__lte"] = django_filters.DateFilter(
                        field_name=field_name, lookup_expr='lte'
                    )
                else:
                    filters[filter_name] = django_filters.DateFilter(
                        field_name=field_name, lookup_expr=condition
                    )

        self.filters.update(filters)
        return filters

    class Meta:
        fields = []


class DynamicFilterSet(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configurar filtros dinámicos según tipo de campo
        for field_name, field in self.form.fields.items():
            model_field = self._meta.model._meta.get_field(field_name)

            # Campos numéricos
            if isinstance(model_field, (IntegerField, FloatField, DecimalField)):
                self.filters[field_name] = django_filters.NumberFilter(
                    field_name=field_name,
                    widget=forms.NumberInput(attrs={'class': 'form-control'}),
                    lookup_expr='exact'
                )
                self.filters[f'{field_name}__gt'] = django_filters.NumberFilter(
                    field_name=field_name,
                    lookup_expr='gt',
                    label=f'{field_name} mayor que'
                )
                self.filters[f'{field_name}__lt'] = django_filters.NumberFilter(
                    field_name=field_name,
                    lookup_expr='lt',
                    label=f'{field_name} menor que'
                )

            # Campos de texto
            elif isinstance(model_field, (CharField, TextField)):
                self.filters[field_name] = django_filters.CharFilter(
                    field_name=field_name,
                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                    lookup_expr='icontains',
                    label=f'{field_name} contiene'
                )

            # Campos booleanos
            elif isinstance(model_field, BooleanField):
                self.filters[field_name] = django_filters.BooleanFilter(
                    field_name=field_name,
                    widget=forms.Select(
                        choices=[('', 'Cualquiera'),
                                 (True, 'Sí'), (False, 'No')],
                        attrs={'class': 'form-control'}
                    )
                )

            # Campos de fecha
            elif isinstance(model_field, (DateField, DateTimeField)):
                self.filters[field_name] = django_filters.DateFilter(
                    field_name=field_name,
                    widget=forms.DateInput(
                        attrs={'class': 'form-control', 'type': 'date'}),
                    lookup_expr='exact'
                )
                self.filters[f'{field_name}__gte'] = django_filters.DateFilter(
                    field_name=field_name,
                    lookup_expr='gte',
                    label=f'{field_name} desde'
                )
                self.filters[f'{field_name}__lte'] = django_filters.DateFilter(
                    field_name=field_name,
                    lookup_expr='lte',
                    label=f'{field_name} hasta'
                )

    class Meta:
        model = Plan  # Reemplaza con tu modelo
        fields = ['nombre']  # Especifica tus campos


class MembresiaFilter(django_filters.FilterSet):
    class Meta:
        model = Membresia
        fields = ['socio', 'plan', 'estado']


class SocioFilter(django_filters.FilterSet):
    class Meta:
        model = Socio
        fields = ['apellido', 'nombre', 'activo']


class PagoFilter(django_filters.FilterSet):
    fecha_at = django_filters.DateRangeFilter(
        field_name='fecha_pago',
        label='F.Pago',
        initial='week',)

    class Meta:
        model = Pago
        fields = ['membresia', 'fecha_at']


class PagoRangeFilter(django_filters.FilterSet):
    fecha_pago_desde = django_filters.DateFilter(
        field_name='fecha_pago',
        lookup_expr='gte',
        label='Fecha Desde',
        # initial igual al primer dia del mes actual
        initial=date.today().replace(day=1)
        # initial=date.today() - relativedelta(months=1)


    )
    fecha_pago_hasta = django_filters.DateFilter(
        field_name='fecha_pago',
        lookup_expr='lte',
        label='Fecha Hasta',
        initial=date.today()
    )

    def __init__(self, *args, **kwargs):
        super(PagoRangeFilter, self).__init__(*args, **kwargs)
        self.filters['fecha_pago_desde'].initial = date.today() - \
            relativedelta(months=1)
        self.filters['fecha_pago_hasta'].initial = date.today()

    class Meta:
        model = Pago
        fields = ['fecha_pago_desde', 'fecha_pago_hasta']


class AsistenciaFilter(django_filters.FilterSet):
    fecha_at = django_filters.DateRangeFilter(
        field_name='fecha',
        label='Fecha',
        initial='week',)

    class Meta:
        model = Asistencia
        fields = ['socio', 'fecha_at']


class AsistenciaRangeFilter(django_filters.FilterSet):
    fecha = django_filters.DateFromToRangeFilter()
    socio = django_filters.ModelChoiceFilter(
        queryset=Socio.objects.all().order_by('apellido', 'nombre'))

    # Inicializar fecha a hoy
    # def __init__(self, *args, **kwargs):
    #     super(AsistenciaRangeFilter, self).__init__(*args, **kwargs)
    #     self.filters['fecha'].initial = date

    class Meta:
        model = Asistencia
        fields = ['socio', 'fecha']
