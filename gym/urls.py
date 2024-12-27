from os import name
from tkinter.font import names
from django.urls import path
from .views import *


app_namespace = 'gym'

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('logout/', signout, name='logout'),
    path('login/', signin, name='login'),


    path('plan/list/', planListView.as_view(), name='plan_list'),
    path('plan/create/', planCreateView.as_view(), name='plan_create'),
    path('plan/update/<int:pk>', planUpdateView.as_view(), name='plan_update'),
    path('plan/delete/<int:pk>', planDeleteView.as_view(), name='plan_delete'),

    path('socio/list/', socioListView.as_view(), name='socio_list'),
    path('socio/create/', socioCreateView.as_view(), name='socio_create'),
    path('socio/update/<int:pk>', socioUpdateView.as_view(), name='socio_update'),
    path('socio/delete/<int:pk>', socioDeleteView.as_view(), name='socio_delete'),

    path('membresia/list/', membresiaListView.as_view(), name='membresia_list'),
    path('membresia/create/', membresiaCreateView.as_view(),
         name='membresia_create'),
    path('membresia/update/<int:pk>',
         membresiaUpdateView.as_view(), name='membresia_update'),
    path('membresia/delete/<int:pk>',
         membresiaDeleteView.as_view(), name='membresia_delete'),
]