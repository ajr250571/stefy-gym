# Backup regular de base de datos
# py manage.py dumpdata --indent 4 gym auth > db.json
# python manage.py loaddata db.json
# py backup.py

import os
from datetime import datetime, timedelta
from core.wsgi import *
from django.core import management
from pathlib import Path
import environ
import time
from gym.models import Membresia
import pywhatkit
import pyautogui
from django.http import JsonResponse


env = environ.Env()
environ.Env.read_env()


def backup_db():
    print("-----------------------------------------------------------")
    print("-----------------------------------------------------------")
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


def correo_membresias_vencidas():
    start_time = time.time()
    print("-----------------------------------------------------------")
    print("-----------------------------------------------------------")
    print("Enviando correos de membresias vencidas...")
    print(f"Fecha de hoy: {datetime.now().date()}")
    maniana = datetime.now().date() - timedelta(days=-1)
    print(f"Fecha de manana: {maniana}")
    membresias_vencidas = Membresia.objects.filter(
        fecha_fin__exact=maniana)
    for membresia in membresias_vencidas:
        print("-----------------------------------------------------------")
        if membresia.enviar_email(membresia.id):  # type: ignore
            print(f"Correo enviado a {membresia.socio.nombre_completo()}")
        else:
            print(f"Error al enviar correo a {
                membresia.socio.nombre_completo()}")

    end_time = time.time()
    print("-----------------------------------------------------------")
    print("Tiempo de ejecución:", round(end_time - start_time, 6), "segundos")


def whatsapp_membresias_vencidas():
    start_time = time.time()
    print("-----------------------------------------------------------")
    print("-----------------------------------------------------------")
    print("Enviando whatsapp de membresias vencidas...")
    print(f"Fecha de hoy: {datetime.now().date()}")
    maniana = datetime.now().date() - timedelta(days=-1)
    membresias_vencidas = Membresia.objects.filter(
        fecha_fin__exact=maniana)
    for membresia in membresias_vencidas:
        print("-----------------------------------------------------------")
        mensaje = (
            f"Hola {membresia.socio.nombre}!\n"
            f"Te informamos que tu membresía del plan "
            f"{membresia.plan.nombre} vencerá en el dia "
            f"{membresia.fecha_fin.strftime('%d/%m/%Y')}.\n"
            "Por favor, contacta con nosotros para renovarla."
        )
        if send_whatsapp_message(membresia.socio.telefono, mensaje):  # type: ignore
            print(f"Whatsapp enviado a {membresia.socio.nombre_completo()}")
        else:
            print(f"Error al enviar whatsapp a {
                  membresia.socio.nombre_completo()}")

    end_time = time.time()
    print("-----------------------------------------------------------")
    print("Tiempo de ejecución:", round(end_time - start_time, 6), "segundos")


def send_whatsapp_message(phone_number, message):
    """
    Envía un mensaje de WhatsApp usando pywhatkit con manejo de errores
    y confirmación de envío mediante pyautogui.
    Args:
        phone_number (str): Número de teléfono incluyendo código de país (ej: '+34612345678')
        message (str): Mensaje a enviar
    Returns:
        dict: Resultado de la operación con estado y mensaje
    """
    try:
        # Remover el '+' si está presente en el número

        # Enviar el mensaje
        pywhatkit.sendwhatmsg_instantly(  # type: ignore
            phone_no=phone_number,
            message=message,
            tab_close=False,
            # Segundos antes de cerrar la pestaña
            wait_time=env.int('WAIT_TIME_WHATSAPP')
        )
        # Esperar a que WhatsApp Web se cargue
        time.sleep(env.int('TIMEOUT_WHATSAPP'))
        # Asegurar que el foco esté en el campo de mensaje
        # Click en el centro
        pyautogui.click(pyautogui.size()[0] // 2, pyautogui.size()[1] // 2)
        time.sleep(2)
        # Presionar Tab para mover el foco al campo de mensaje si es necesario
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        time.sleep(1)
        # Enviar el mensaje
        pyautogui.press('enter')
        time.sleep(1)
        # Cerrar la pestaña (opcional)
        pyautogui.hotkey('ctrl', 'w')

        return True
    except Exception as e:
        return False


enviar_email = env.bool('ENVIAR_EMAIL')
enviar_whatsapp = env.bool('ENVIAR_WHATSAPP')

# Llama a las funciónes
backup_db()
if enviar_email:
    correo_membresias_vencidas()
if enviar_whatsapp:
    whatsapp_membresias_vencidas()
