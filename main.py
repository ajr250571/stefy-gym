# main.py
# pyinstaller pyinstaller_build.spec
from django.core.management import execute_from_command_line
import django
import os
import sys
from pathlib import Path

# Agregar el directorio raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django.setup()


if __name__ == '__main__':
    execute_from_command_line(sys.argv)
