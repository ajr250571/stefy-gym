# Comando para empaquetar
pyinstaller - -name = stefy - -onefile main.py ^
--add-data "gym/templates:gym/templates" ^
--add-data "gym/static:gym/static" ^
--add-data "db.sqlite3:." ^
--hidden-import = "django.template.loader_tags" ^
--hidden-import = "django.template.defaulttags" ^
--hidden-import = "django.template.defaultfilters"
