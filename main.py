# main.py
# pyinstaller pyinstaller_build.spec
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
    execute_from_command_line(sys.argv)
