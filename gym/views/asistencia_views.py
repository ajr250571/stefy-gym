from multiprocessing import Value
from django.utils import timezone
from django.db.models.base import Model as Model
from django.shortcuts import get_object_or_404, redirect, render
from gym.models import Asistencia, Membresia
from django.views.generic import View
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
from django.db.models import Count, F, Value
from django.db.models.functions import Concat
from ..filters import AsistenciaFilter, AsistenciaRangeFilter
from django_filters.views import FilterView
from django.contrib.auth.decorators import permission_required


class AsistenciaListView(PermissionRequiredMixin, FilterView):
    model = Asistencia
    template_name = 'asistencia/asistencia_list.html'
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.view_asistencia'
    filterset_class = AsistenciaFilter

    def get_filterset(self, filterset_class):
        # Si no hay parámetros en la URL, establecemos el valor inicial
        if not self.request.GET:
            return filterset_class(
                data={'fecha_at': 'month'},
                # cuenta asistencias por socio
                queryset=self.get_queryset().values('socio').annotate(nombre_completo=Concat(
                    'socio__apellido',  Value(', '), 'socio__nombre'),
                    cantidad=Count('id')).order_by('nombre_completo'),
                request=self.request
            )
        # si hay parametros en la URL, cuenta asistencias por socio
        return filterset_class(
            data=self.request.GET,
            queryset=self.get_queryset().values('socio').annotate(nombre_completo=Concat(
                'socio__apellido',  Value(', '), 'socio__nombre'),
                cantidad=Count('id')).order_by('nombre_completo'),
            request=self.request
        )

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Listado de Asistencias'
        # kwargs['filter_form'] = FechaFilterForm()
        kwargs['filter'] = self.filterset
        return super().get_context_data(**kwargs)


# type: ignore
@permission_required('gym.view_asistencia', login_url='/login/')
def lista_asistencias(request):

    if request.GET:
        # Si hay filtros, aplicar el filtro de Django Filter
        asistencia_filter = AsistenciaRangeFilter(
            request.GET, queryset=Asistencia.objects.all())
    else:
        # Si no hay filtros, no cargar ninguna asistencia
        asistencia_filter = AsistenciaRangeFilter(
            queryset=Asistencia.objects.none())

    # asistencias = Asistencia.objects.all()
    # asistencia_filter = AsistenciaRangeFilter(
    #     request.GET, queryset=asistencias)

    content = {'filter': asistencia_filter,
               'title': 'Listado de Asistencias'}

    return render(request, 'asistencia/asistencia_range_list.html', content)
