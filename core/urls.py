
from tkinter.font import names
from django.contrib import admin
from django.urls import include, path
from gym.views import home, signup


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gym.urls'), name='gym'),

]
