 @echo off
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
echo Instalación completada
pause