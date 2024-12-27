from ast import In
from os import error
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.urls import reverse_lazy
from gym.models import Membresia, Plan, Socio
from .forms import PlanForm, SocioForm, MembresiaForm
from django.views.generic import CreateView, UpdateView, DeleteView, ListView


def home(request):
    return render(request, 'home.html')


# Usuarios

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


class planListView(ListView):
    model = Plan
    template_name = 'plan/plan_list.html'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Listado de Planes'
        kwargs['create_url'] = reverse_lazy('plan_create')
        kwargs['crumb_url'] = reverse_lazy('plan_list')
        kwargs['crumb_name'] = 'Planes'
        return super().get_context_data(**kwargs)


class planCreateView(CreateView):
    model = Plan
    form_class = PlanForm
    template_name = 'plan/plan_create.html'
    success_url = reverse_lazy('plan_list')

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Crear Plan'
        kwargs['crumb_url'] = reverse_lazy('plan_list')
        kwargs['crumb_name'] = 'Planes'
        return super().get_context_data(**kwargs)


class planUpdateView(UpdateView):
    model = Plan
    form_class = PlanForm
    template_name = 'plan/plan_create.html'
    success_url = reverse_lazy('plan_list')

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Editar Plan'
        kwargs['crumb_url'] = reverse_lazy('plan_list')
        kwargs['crumb_name'] = 'Planes'
        return super().get_context_data(**kwargs)


class planDeleteView(DeleteView):
    model = Plan
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('plan_list')


# Socios

class socioListView(ListView):
    model = Socio
    template_name = 'socio/socio_list.html'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Listado de Socios'
        kwargs['create_url'] = reverse_lazy('socio_create')
        kwargs['crumb_url'] = reverse_lazy('socio_list')
        kwargs['crumb_name'] = 'Socios'
        return super().get_context_data(**kwargs)


class socioCreateView(CreateView):
    model = Socio
    form_class = SocioForm
    template_name = 'socio/socio_create.html'
    success_url = reverse_lazy('socio_list')

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Crear Socio'
        kwargs['crumb_url'] = reverse_lazy('socio_list')
        kwargs['crumb_name'] = 'Socios'
        return super().get_context_data(**kwargs)


class socioUpdateView(UpdateView):
    model = Socio
    form_class = SocioForm
    template_name = 'socio/socio_create.html'
    success_url = reverse_lazy('socio_list')

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Editar Socio'
        kwargs['crumb_url'] = reverse_lazy('socio_list')
        kwargs['crumb_name'] = 'Socios'
        return super().get_context_data(**kwargs)


class socioDeleteView(DeleteView):
    model = Socio
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('socio_list')

    def get_context_data(self, **kwargs):
        kwargs['cancel_url'] = reverse_lazy('socio_list')
        return super().get_context_data(**kwargs)

# Membresias


class membresiaListView(ListView):
    model = Membresia
    template_name = 'membresia/membresia_list.html'

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Listado de Membresias'
        kwargs['create_url'] = reverse_lazy('membresia_create')
        kwargs['crumb_url'] = reverse_lazy('membresia_list')
        kwargs['crumb_name'] = 'Membresias'
        return super().get_context_data(**kwargs)


class membresiaCreateView(CreateView):
    model = Membresia
    form_class = MembresiaForm
    template_name = 'membresia/membresia_create.html'
    success_url = reverse_lazy('membresia_list')

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Crear Membresia'
        kwargs['crumb_url'] = reverse_lazy('membresia_list')
        kwargs['crumb_name'] = 'Membresias'
        return super().get_context_data(**kwargs)


class membresiaUpdateView(UpdateView):
    model = Membresia
    form_class = MembresiaForm
    template_name = 'membresia/membresia_create.html'
    success_url = reverse_lazy('membresia_list')

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Editar Membresia'
        kwargs['crumb_url'] = reverse_lazy('membresia_list')
        kwargs['crumb_name'] = 'Membresias'
        return super().get_context_data(**kwargs)


class membresiaDeleteView(DeleteView):
    model = Membresia
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('membresia_list')

    def get_context_data(self, **kwargs):
        kwargs['cancel_url'] = reverse_lazy('membresia_list')
        return super().get_context_data(**kwargs)
