from django.urls import path
from .views.general_views import enviar_whatsapp, whatsapp_vencidas, whatsapp_por_vencer, enviar_email, email_vencidas, email_por_vencer, AsistenciaListView
from .views.plan_views import planListView, planCreateView, planUpdateView, planDeleteView
from .views.socio_views import socioListView, socioCreateView, socioUpdateView, socioDeleteView
from .views.usuario_views import signup, signin, signout
from .views.membresia_views import membresiaListView, membresiaCreateView, membresiaUpdateView, membresiaDeleteView, membresiaVencidaListView, membresiaDetailView, membresiaSocioCreateView
from .views.pago_views import pagoListView, pagoCreateView, pagoUpdateView, pagoDeleteView, pagoMembresiaCreateView, MontosMensualesView, errorPermisosView, get_membresia_monto
from .views.home_views import home

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

    path('pago/list/', pagoListView.as_view(), name='pago_list'),
    path('pago/create/', pagoCreateView.as_view(), name='pago_create'),
    path('pago/update/<int:pk>', pagoUpdateView.as_view(), name='pago_update'),
    path('pago/delete/<int:pk>', pagoDeleteView.as_view(), name='pago_delete'),

    path('vencida/list/', membresiaVencidaListView.as_view(),
         name='membresia_vencida_list'),

    path('pago_membresia/<int:pk>',
         pagoMembresiaCreateView.as_view(), name='pago_membresia'),

    path('membresia/<str:dni>', membresiaDetailView.as_view(),
         name='membresia_detail'),

    path('error_permisos/', errorPermisosView.as_view(), name='error_permisos'),

    path('montos_mensuales/', MontosMensualesView.as_view(),
         name='montos_mensuales'),

    path('membresia_socio/create/<int:pk>', membresiaSocioCreateView.as_view(),
         name='membresia_socio_create'),

    path('enviar_whatsapp/<int:membresia_id>',
         enviar_whatsapp.as_view(), name='enviar_whatsapp'),

    path('whatsapp_vencidas/', whatsapp_vencidas.as_view(),
         name='whatsapp_vencidas'),
    path('whatsapp_por_vencer/', whatsapp_por_vencer.as_view(),
         name='whatsapp_por_vencer'),

    path('enviar_email/<int:membresia_id>',
         enviar_email.as_view(), name='enviar_email'),

    path('email_vencidas/', email_vencidas.as_view(),
         name='email_vencidas'),
    path('email_por_vencer/', email_por_vencer.as_view(),
         name='email_por_vencer'),

    path('asistencia_list/', AsistenciaListView.as_view(), name='asistencia_list'),

    path('pagos/get-membresia-monto/',
         get_membresia_monto, name='get_membresia_monto'),
]
