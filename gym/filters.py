from datetime import date
from colorama import init
import django_filters
from .models import Membresia, Pago, Asistencia, Socio
from dateutil.relativedelta import relativedelta


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
