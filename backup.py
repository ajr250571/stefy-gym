# Backup regular de base de datos
# py manage.py dumpdata --indent 4 gym auth > db.json
# python manage.py loaddata db.json
# py backup.py

import os
from datetime import datetime
from core.wsgi import *
from django.core import management
from pathlib import Path
import environ
import time

env = environ.Env()
environ.Env.read_env()


def backup_db():
    # Ruta para guardar el backup

    backup_path = 'backups'
    if not os.path.exists(backup_path):
        os.makedirs(backup_path)

    backup_file = f'{backup_path}/backup_{
        datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

    # Código que deseas medir
    start_time = time.time()
    # ... tu código aquí ...

    # Comando para ejecutar dumpdata
    management.call_command('dumpdata',
                            'gym',
                            'auth',
                            '--output', backup_file,
                            '--indent', '4',
                            # '--all',  # Para realizar un backup de todos los modelos
                            # Agrega aquí otras opciones según tus necesidades
                            # --natural-foreign, --exclude, etc.
                            )

    max_backup = env.int('MAX_BACKUP')
    print(f"Backup creado: {backup_file}"
          f"\nMáximo de backups: {max_backup}")
    # Mantener solo los últimos 7 backups
    backup_files = sorted(Path(backup_path).glob('backup_*.json'))
    if len(backup_files) > max_backup:
        for old_file in backup_files[:-max_backup]:
            os.remove(old_file)
            print(f"Backup antiguo eliminado: {old_file}")

    end_time = time.time()
    print("Tiempo de ejecución:", (end_time - start_time), "segundos")


# Llama a la función para realizar el backup
backup_db()
