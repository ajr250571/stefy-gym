from ast import In
from datetime import date
from os import error
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.urls import reverse_lazy
from gym.models import Membresia, Plan, Socio, Pago
from .forms import PlanForm, SocioForm, MembresiaForm, PagoForm
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


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


class planListView(LoginRequiredMixin, ListView):
    model = Plan
    template_name = 'plan/plan_list.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Listado de Planes'
        kwargs['create_url'] = reverse_lazy('plan_create')
        kwargs['crumb_url'] = reverse_lazy('plan_list')
        kwargs['crumb_name'] = 'Planes'
        return super().get_context_data(**kwargs)


class planCreateView(LoginRequiredMixin, CreateView):
    model = Plan
    form_class = PlanForm
    template_name = 'plan/plan_create.html'
    success_url = reverse_lazy('plan_list')
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Crear Plan'
        kwargs['crumb_url'] = reverse_lazy('plan_list')
        kwargs['crumb_name'] = 'Planes'
        return super().get_context_data(**kwargs)


class planUpdateView(LoginRequiredMixin, UpdateView):
    model = Plan
    form_class = PlanForm
    template_name = 'plan/plan_create.html'
    success_url = reverse_lazy('plan_list')
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Editar Plan'
        kwargs['crumb_url'] = reverse_lazy('plan_list')
        kwargs['crumb_name'] = 'Planes'
        return super().get_context_data(**kwargs)


class planDeleteView(LoginRequiredMixin, DeleteView):
    model = Plan
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('plan_list')
    login_url = '/login/'


# Socios

class socioListView(LoginRequiredMixin, ListView):
    model = Socio
    template_name = 'socio/socio_list.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Listado de Socios'
        kwargs['create_url'] = reverse_lazy('socio_create')
        kwargs['crumb_url'] = reverse_lazy('socio_list')
        kwargs['crumb_name'] = 'Socios'
        return super().get_context_data(**kwargs)


class socioCreateView(LoginRequiredMixin, CreateView):
    model = Socio
    form_class = SocioForm
    template_name = 'socio/socio_create.html'
    success_url = reverse_lazy('socio_list')
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Crear Socio'
        kwargs['crumb_url'] = reverse_lazy('socio_list')
        kwargs['crumb_name'] = 'Socios'
        return super().get_context_data(**kwargs)


class socioUpdateView(LoginRequiredMixin, UpdateView):
    model = Socio
    form_class = SocioForm
    template_name = 'socio/socio_create.html'
    success_url = reverse_lazy('socio_list')
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Editar Socio'
        kwargs['crumb_url'] = reverse_lazy('socio_list')
        kwargs['crumb_name'] = 'Socios'
        return super().get_context_data(**kwargs)


class socioDeleteView(LoginRequiredMixin, DeleteView):
    model = Socio
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('socio_list')
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        kwargs['cancel_url'] = reverse_lazy('socio_list')
        return super().get_context_data(**kwargs)

# Membresias


class membresiaListView(LoginRequiredMixin, ListView):
    model = Membresia
    template_name = 'membresia/membresia_list.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Listado de Membresias'
        kwargs['create_url'] = reverse_lazy('membresia_create')
        kwargs['crumb_url'] = reverse_lazy('membresia_list')
        kwargs['crumb_name'] = 'Membresias'
        return super().get_context_data(**kwargs)


class membresiaCreateView(LoginRequiredMixin, CreateView):
    model = Membresia
    form_class = MembresiaForm
    template_name = 'membresia/membresia_create.html'
    success_url = reverse_lazy('membresia_list')
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Crear Membresia'
        kwargs['crumb_url'] = reverse_lazy('membresia_list')
        kwargs['crumb_name'] = 'Membresias'
        return super().get_context_data(**kwargs)


class membresiaUpdateView(LoginRequiredMixin, UpdateView):
    model = Membresia
    form_class = MembresiaForm
    template_name = 'membresia/membresia_create.html'
    success_url = reverse_lazy('membresia_list')
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Editar Membresia'
        kwargs['crumb_url'] = reverse_lazy('membresia_list')
        kwargs['crumb_name'] = 'Membresias'
        return super().get_context_data(**kwargs)


class membresiaDeleteView(LoginRequiredMixin, DeleteView):
    model = Membresia
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('membresia_list')
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        kwargs['cancel_url'] = reverse_lazy('membresia_list')
        return super().get_context_data(**kwargs)


# Pagos

class pagoListView(LoginRequiredMixin, ListView):
    model = Pago
    template_name = 'pago/pago_list.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Listado de Pagos'
        kwargs['create_url'] = reverse_lazy('pago_create')
        kwargs['crumb_url'] = reverse_lazy('pago_list')
        kwargs['crumb_name'] = 'Pagos'
        return super().get_context_data(**kwargs)


class pagoCreateView(LoginRequiredMixin, CreateView):
    model = Pago
    form_class = PagoForm
    template_name = 'pago/pago_create.html'
    success_url = reverse_lazy('pago_list')
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Crear Pago'
        kwargs['crumb_url'] = reverse_lazy('pago_list')
        kwargs['crumb_name'] = 'Pagos'
        return super().get_context_data(**kwargs)


class pagoMembresiaCreateView(LoginRequiredMixin, CreateView):
    model = Pago
    form_class = PagoForm
    template_name = 'pago/pago_create.html'
    success_url = reverse_lazy('pago_list')
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Crear Pago'
        kwargs['crumb_url'] = reverse_lazy('pago_list')
        kwargs['crumb_name'] = 'Pagos'
        return super().get_context_data(**kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['membresia'] = self.kwargs['pk']
        membresia = Membresia.objects.get(pk=self.kwargs['pk'])
        initial['monto'] = membresia.plan.precio
        initial['fecha_vencimiento'] = membresia.fecha_fin
        initial['fecha_pago'] = date.today()
        initial['estado'] = 'PAGADO'
        return initial


class pagoUpdateView(LoginRequiredMixin, UpdateView):
    model = Pago
    form_class = PagoForm
    template_name = 'pago/pago_create.html'
    success_url = reverse_lazy('pago_list')
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Editar Pago'
        kwargs['crumb_url'] = reverse_lazy('pago_list')
        kwargs['crumb_name'] = 'Pagos'
        return super().get_context_data(**kwargs)


class pagoDeleteView(LoginRequiredMixin, DeleteView):
    model = Pago
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('pago_list')
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        kwargs['cancel_url'] = reverse_lazy('pago_list')
        return super().get_context_data(**kwargs)

# Listar membresias vencidas


class membresiaVencidaListView(LoginRequiredMixin, ListView):
    model = Membresia
    template_name = 'membresia/membresia_list.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Listado de Membresias Vencidas'
        kwargs['crumb_url'] = reverse_lazy('membresia_list')
        kwargs['crumb_name'] = 'Membresias'
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return Membresia.objects.filter(estado='VENCIDA')


class membresiaDetailView(DetailView):
    model = Membresia
    template_name = 'membresia/membresia_detail.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Detalle de Membresia'
        kwargs['crumb_url'] = reverse_lazy('home')
        kwargs['crumb_name'] = ''
        return super().get_context_data(**kwargs)

    def get_object(self, queryset=None):
        dni = self.kwargs['dni']
        membresia = Membresia.objects.get(socio__dni=dni)

        return membresia
