@echo off
f:
cd stefy-gym
call venv\Scripts\activate
python manage.py runserver 0.0.0.0:3014
