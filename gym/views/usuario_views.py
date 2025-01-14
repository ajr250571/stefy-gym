from django.db.models.base import Model as Model
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect, render

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