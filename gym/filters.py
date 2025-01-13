import django_filters
from .models import Membresia, Pago, Asistencia


class MembresiaFilter(django_filters.FilterSet):
    class Meta:
        model = Membresia
        fields = ['socio', 'plan', 'estado']


class PagoFilter(django_filters.FilterSet):
    fecha_at = django_filters.DateRangeFilter(
        field_name='fecha_pago',
        label='F.Pago',
        initial='week',)

    class Meta:
        model = Pago
        fields = ['membresia', 'fecha_at']


class AsistenciaFilter(django_filters.FilterSet):
    fecha_at = django_filters.DateRangeFilter(
        field_name='fecha',
        label='Fecha',
        initial='week',)

    class Meta:
        model = Asistencia
        fields = ['socio', 'fecha_at']
