# Generated by Django 5.1.4 on 2025-02-03 19:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0002_delete_historicalpago'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membresia',
            name='socio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gym.socio', verbose_name='Socio'),
        ),
        migrations.AlterField(
            model_name='pago',
            name='estado',
            field=models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('PAGADO', 'Pagado'), ('VENCIDO', 'Vencido')], default='PAGADO', max_length=10, verbose_name='Estado'),
        ),
    ]
