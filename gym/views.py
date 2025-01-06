from ast import In
from datetime import date, timedelta
from django.utils import timezone
from os import error
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.urls import reverse, reverse_lazy
from gym.models import Membresia, Plan, Socio, Pago
from .forms import PlanForm, SocioForm, MembresiaForm, PagoForm
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from dateutil.relativedelta import relativedelta
import pywhatkit
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


def home(request):
    return render(request, 'home.html')


# Usuarios
@login_required
def signup(request):
    form = UserCreationForm()
    content = {
        'title': 'Registrarse',
        'form': form,
        'error': ''
    }
    if request.method == 'POST':
        try:
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                login(request, authenticate(
                    username=request.POST['username'], password=request.POST['password1']))
                return redirect('home')
            else:
                content['error'] = 'Los datos ingresados no son válidos'

        except IntegrityError as e:
            content['error'] = 'El usuario ya existe'

    return render(request, 'signup.html', content)


def signout(request):
    logout(request)
    return redirect('login')


def signin(request):
    error = ''
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
        else:
            error = 'Los datos ingresados no son válidos'

    return render(request, 'signin.html', {
        'title': 'Iniciar Sesión',
        'form': AuthenticationForm(),
        'error': error
    })

# Planes


class planListView(PermissionRequiredMixin, ListView):
    model = Plan
    template_name = 'plan/plan_list.html'
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.view_plan'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Listado de Planes'
        kwargs['create_url'] = reverse_lazy('plan_create')
        kwargs['crumb_url'] = reverse_lazy('plan_list')
        kwargs['crumb_name'] = 'Planes'
        return super().get_context_data(**kwargs)


class planCreateView(PermissionRequiredMixin, CreateView):
    model = Plan
    form_class = PlanForm
    template_name = 'plan/plan_create.html'
    success_url = reverse_lazy('plan_list')
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.add_plan'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Crear Plan'
        kwargs['crumb_url'] = reverse_lazy('plan_list')
        kwargs['crumb_name'] = 'Planes'
        return super().get_context_data(**kwargs)


class planUpdateView(PermissionRequiredMixin, UpdateView):
    model = Plan
    form_class = PlanForm
    template_name = 'plan/plan_create.html'
    success_url = reverse_lazy('plan_list')
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.change_plan'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Editar Plan'
        kwargs['crumb_url'] = reverse_lazy('plan_list')
        kwargs['crumb_name'] = 'Planes'
        return super().get_context_data(**kwargs)


class planDeleteView(PermissionRequiredMixin, DeleteView):
    model = Plan
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('plan_list')
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.delete_plan'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)


# Socios

class socioListView(PermissionRequiredMixin, ListView):
    model = Socio
    template_name = 'socio/socio_list.html'
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.view_socio'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Listado de Socios'
        kwargs['create_url'] = reverse_lazy('socio_create')
        kwargs['crumb_url'] = reverse_lazy('socio_list')
        kwargs['crumb_name'] = 'Socios'
        return super().get_context_data(**kwargs)


class socioCreateView(PermissionRequiredMixin, CreateView):
    model = Socio
    form_class = SocioForm
    template_name = 'socio/socio_create.html'
    # success_url = reverse_lazy('socio_list')
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.add_socio'

    def get_success_url(self) -> str:
        # Redirigir a crete Membresia si el socio fue creado exitosamente
        return reverse('membresia_socio_create',
                       kwargs={'pk': self.object.pk})  # type: ignore

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Crear Socio'
        kwargs['crumb_url'] = reverse_lazy('socio_list')
        kwargs['crumb_name'] = 'Socios'
        return super().get_context_data(**kwargs)


class socioUpdateView(PermissionRequiredMixin, UpdateView):
    model = Socio
    form_class = SocioForm
    template_name = 'socio/socio_create.html'
    success_url = reverse_lazy('socio_list')
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.change_socio'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Editar Socio'
        kwargs['crumb_url'] = reverse_lazy('socio_list')
        kwargs['crumb_name'] = 'Socios'
        return super().get_context_data(**kwargs)


class socioDeleteView(PermissionRequiredMixin, DeleteView):
    model = Socio
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('socio_list')
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.delete_socio'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['cancel_url'] = reverse_lazy('socio_list')
        return super().get_context_data(**kwargs)

# Membresias


class membresiaListView(PermissionRequiredMixin, ListView):
    model = Membresia
    template_name = 'membresia/membresia_list.html'
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.view_membresia'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Listado de Membresias'
        kwargs['create_url'] = reverse_lazy('membresia_create')
        kwargs['crumb_url'] = reverse_lazy('membresia_list')
        kwargs['crumb_name'] = 'Membresias'
        return super().get_context_data(**kwargs)


class membresiaCreateView(PermissionRequiredMixin, CreateView):
    model = Membresia
    form_class = MembresiaForm
    template_name = 'membresia/membresia_create.html'
    success_url = reverse_lazy('membresia_list')
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.add_membresia'

    def get_initial(self):
        self.initial['fecha_fin'] = timezone.now().date() + \
            relativedelta(months=1)
        return super().get_initial()

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Crear Membresia'
        kwargs['crumb_url'] = reverse_lazy('membresia_list')
        kwargs['crumb_name'] = 'Membresias'
        return super().get_context_data(**kwargs)


class membresiaSocioCreateView(PermissionRequiredMixin, CreateView):
    model = Membresia
    form_class = MembresiaForm
    template_name = 'membresia/membresia_create.html'
    success_url = reverse_lazy('membresia_list')
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.add_membresia'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Crear Membresia'
        kwargs['crumb_url'] = reverse_lazy('membresia_list')
        kwargs['crumb_name'] = 'Membresias'
        return super().get_context_data(**kwargs)

    def get_initial(self):

        initial = super().get_initial()

        initial['socio'] = self.kwargs['pk']
        initial['fecha_fin'] = timezone.now().date() + \
            relativedelta(months=1)
        # Asigna plan por defecto al socio
        plan = Plan.objects.get(duracion=1)
        initial['plan'] = plan

        return initial


class membresiaUpdateView(PermissionRequiredMixin, UpdateView):
    model = Membresia
    form_class = MembresiaForm
    template_name = 'membresia/membresia_create.html'
    success_url = reverse_lazy('membresia_list')
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.change_membresia'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Editar Membresia'
        kwargs['crumb_url'] = reverse_lazy('membresia_list')
        kwargs['crumb_name'] = 'Membresias'
        return super().get_context_data(**kwargs)


class membresiaDeleteView(PermissionRequiredMixin, DeleteView):
    model = Membresia
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('membresia_list')
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.delete_membresia'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['cancel_url'] = reverse_lazy('membresia_list')
        return super().get_context_data(**kwargs)


# Pagos

class pagoListView(PermissionRequiredMixin, ListView):
    model = Pago
    template_name = 'pago/pago_list.html'
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.view_pago'

    def get_queryset(self):
        fecha_desde = timezone.now() - relativedelta(months=6)
        return Pago.objects.filter(fecha_pago__gte=fecha_desde).order_by('membresia', '-fecha_pago')

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Listado de Pagos'
        kwargs['create_url'] = reverse_lazy('pago_create')
        kwargs['crumb_url'] = reverse_lazy('pago_list')
        kwargs['crumb_name'] = 'Pagos'
        return super().get_context_data(**kwargs)


class pagoCreateView(PermissionRequiredMixin, CreateView):
    model = Pago
    form_class = PagoForm
    template_name = 'pago/pago_create.html'
    success_url = reverse_lazy('pago_list')
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.add_pago'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Crear Pago'
        kwargs['crumb_url'] = reverse_lazy('pago_list')
        kwargs['crumb_name'] = 'Pagos'
        return super().get_context_data(**kwargs)


class pagoMembresiaCreateView(PermissionRequiredMixin, CreateView):
    model = Pago
    form_class = PagoForm
    template_name = 'pago/pago_create.html'
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.add_pago'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_success_url(self):
        # Obtener parámetros de la URL
        param = self.kwargs.get('pk')
        if param:
            # Si hay parámetro, redirigir a una URL específica
            return reverse('membresia_list')
        else:
            # Si no hay parámetro, redirigir a la URL por defecto
            return reverse('pago_list')

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Crear Pago'
        kwargs['crumb_url'] = reverse_lazy('pago_list')
        kwargs['crumb_name'] = 'Pagos'
        return super().get_context_data(**kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['membresia'] = self.kwargs['pk']
        membresia = Membresia.objects.get(pk=self.kwargs['pk'])
        if membresia.plan == None:
            initial['monto'] = 0
        else:
            initial['monto'] = membresia.plan.precio
            initial['fecha_vencimiento'] = membresia.fecha_fin

        initial['fecha_pago'] = date.today()
        initial['estado'] = 'PAGADO'
        return initial


class pagoUpdateView(PermissionRequiredMixin, UpdateView):
    model = Pago
    form_class = PagoForm
    template_name = 'pago/pago_create.html'
    success_url = reverse_lazy('pago_list')
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.change_pago'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Editar Pago'
        kwargs['crumb_url'] = reverse_lazy('pago_list')
        kwargs['crumb_name'] = 'Pagos'
        return super().get_context_data(**kwargs)


class pagoDeleteView(PermissionRequiredMixin, DeleteView):
    model = Pago
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('pago_list')
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.delete_pago'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['cancel_url'] = reverse_lazy('pago_list')
        return super().get_context_data(**kwargs)

# Listar membresias vencidas


class membresiaVencidaListView(PermissionRequiredMixin, ListView):
    model = Membresia
    template_name = 'membresia/membresia_list.html'
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.view_membresia'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Listado de Membresias Vencidas'
        kwargs['crumb_url'] = reverse_lazy('membresia_list')
        kwargs['crumb_name'] = 'Membresias'
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return Membresia.objects.filter(estado='VENCIDA')


class membresiaDetailView(PermissionRequiredMixin, DetailView):
    model = Membresia
    template_name = 'membresia/membresia_detail.html'
    login_url = '/login/'
    permisos_url = '/error_permisos/'
    permission_required = 'gym.view_membresia'

    def handle_no_permission(self):
        messages.error(
            self.request, 'No tienes permisos para realizar esta acción.')
        return redirect(self.permisos_url)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Detalle de Membresia'
        kwargs['crumb_url'] = reverse_lazy('home')
        kwargs['crumb_name'] = ''
        return super().get_context_data(**kwargs)

    def get_object(self, queryset=None):
        dni = self.kwargs['dni']
        membresia = Membresia.objects.get(socio__dni=dni)

        return membresia


class errorPermisosView(TemplateView):
    template_name = 'error_permisos.html'


def send_whatsapp_message(request):
    if request.method == 'POST':
        mensaje = request.POST.get('mensaje')
        telefono = request.POST.get('telefono')
        pywhatkit.sendwhatmsg(  # type: ignore
            '+543814755771', 'Prueba de envio', 10, 8, 15, True, 5)  # type: ignore

        return redirect('home')
    else:
        return render(request, 'error_permisos.html')


class MontosMensualesView(TemplateView):
    template_name = 'pago/montos_mensuales.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        montos_mensuales = Pago.objects.annotate(
            mes=TruncMonth('fecha_pago')
        ).values('mes').annotate(
            total=Sum('monto')
        ).order_by('-mes')

        context['montos_mensuales'] = montos_mensuales
        return context


class enviar_whatsapp(View):
    def get(self, request, membresia_id):
        Membresia.enviar_whatsapp(membresia_id)
        return redirect('membresia_list')


@require_http_methods(["POST"])
def enviar_whatsapp_nop(request, membresia_id):
    """
    Vista para manejar el envío de notificaciones WhatsApp
    """
    try:
        resultado = Membresia.enviar_whatsapp(membresia_id)
        if resultado:
            return JsonResponse({
                'status': 'success',
                'message': 'Notificación WhatsApp enviada correctamente'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'No se pudo enviar la notificación'
            }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
