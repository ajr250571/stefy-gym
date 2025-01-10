# hook-django.py
# Este archivo ayuda a PyInstaller a encontrar todos los módulos necesarios de Django
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('django')
datas = collect_data_files('django')
