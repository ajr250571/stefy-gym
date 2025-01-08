from ast import arg
from datetime import timedelta
import datetime
from tabnanny import verbose
import time
from typing import Iterable
from venv import create
from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import pywhatkit
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.conf import settings


class Socio(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    dni = models.CharField(max_length=20, unique=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_alta = models.DateField(default=timezone.now)

    class Meta:
        verbose_name = 'Socio'
        verbose_name_plural = 'Socios'
        ordering = ['apellido', 'nombre']

    def nombre_completo(self):
        return f"{self.apellido}, {self.nombre}"

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"


class Plan(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion = models.IntegerField(verbose_name='Duración (meses)')
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def calcular_fecha_fin(self, fecha_inicio):
        """Calcula la fecha de finalización basada en la duración del plan"""
        return fecha_inicio + relativedelta(months=self.duracion)

    class Meta:
        verbose_name = 'Plan'
        verbose_name_plural = 'Planes'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Membresia(models.Model):
    ESTADOS = [
        ('ACTIVA', 'Activa'),
        ('VENCIDA', 'Vencida'),
        ('CANCELADA', 'Cancelada'),
    ]

    socio = models.OneToOneField(
        Socio, on_delete=models.PROTECT, blank=False, null=False
    )
    plan = models.ForeignKey(
        Plan, on_delete=models.PROTECT, blank=False, null=False)
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVA')
    fecha_alta = models.DateTimeField(auto_now_add=True)

    @classmethod
    def enviar_email(cls, membresia_id):
        print(settings.EMAIL_HOST_USER)
        membresia = cls.objects.select_related(
            'socio', 'plan').get(id=membresia_id)
        if membresia.socio.email:
            # Limpiamos el correo electrónico (asumiendo formato email)
            correo = membresia.socio.email
            if membresia.fecha_fin < timezone.now().date():
                titulo = 'Membresía vencida'
                mensaje = (
                    f"Hola {membresia.socio.nombre}!\n"
                    f"Te informamos que tu membresía del plan "
                    f"{membresia.plan.nombre} se encuentra vencida desde el "
                    f"{membresia.fecha_fin.strftime('%d/%m/%Y')}.\n"
                    "Por favor, contacta con nosotros para renovarla."
                )
            else:
                titulo = 'Membresía a vencer'
                mensaje = (
                    f"Hola {membresia.socio.nombre}!\n"
                    f"Te informamos que tu membresía del plan "
                    f"{membresia.plan.nombre} vencerá en el dia "
                    f"{membresia.fecha_fin.strftime('%d/%m/%Y')}.\n"
                    "Por favor, contacta con nosotros para renovarla."
                )

            try:
                email = EmailMessage(
                    subject=titulo,
                    body=mensaje,
                    to=[correo],
                    from_email=settings.EMAIL_HOST_USER
                )
                email.send()
                return True
            except Exception as e:
                print(f"Error al enviar correo electrónico: {str(e)}")
                return False

    @classmethod
    def enviar_whatsapp(cls, membresia_id):
        """
        Envía una notificación por WhatsApp al socio de una membresía específica
        Args:
            membresia_id: ID de la membresía a notificar
        Returns:
            bool: True si el mensaje se envió correctamente, False en caso contrario
        """
        try:
            membresia = cls.objects.select_related(
                'socio', 'plan').get(id=membresia_id)

            if membresia.estado == 'VENCIDA' and membresia.socio.telefono:
                # Limpiamos el número de teléfono (asumiendo formato +549xxxxxxxxxx)
                telefono = membresia.socio.telefono
                mensaje = (
                    f"Hola {membresia.socio.nombre}!\n"
                    f"Te informamos que tu membresía del plan {
                        membresia.plan.nombre} "
                    f"se encuentra vencida desde el {
                        membresia.fecha_fin.strftime('%d/%m/%Y')}.\n"
                    "Por favor, contacta con nosotros para renovarla."
                )

                try:
                    # pywhatkit.sendwhatmsg_instantly envía el mensaje inmediatamente
                    # pywhatkit.sendwhatmsg_instantly(  # type: ignore
                    #     phone_no=telefono,
                    #     message=mensaje,
                    #     wait_time=10,  # Segundos de espera para enviar el mensaje
                    #     tab_close=True,  # Cierra la pestaña después de enviar
                    #     close_time=5  # Segundos de espera para cerrar la pestaña
                    # )
                    hora = datetime.datetime.now()
                    hora_send = hora.hour
                    minutos_send = hora.minute + 1
                    pywhatkit.sendwhatmsg(
                        telefono, mensaje, hora_send, minutos_send, 10, True, 2)

                    return True
                except Exception as e:
                    print(f"Error al enviar WhatsApp: {str(e)}")
                    return False
            return False
        except cls.DoesNotExist:
            print(f"No se encontró la membresía con ID: {membresia_id}")
            return False
        except Exception as e:
            print(f"Error al procesar la membresía: {str(e)}")
            return False

    def dias_restantes(self):
        """Retorna los días restantes de la membresía"""
        if self.estado == 'CANCELADA':
            return 0
        return (self.fecha_fin - timezone.now().date()).days

    def vigente(self):
        """Verifica si la membresía está vigente"""
        if self.estado == 'ACTIVA':
            if self.fecha_fin < timezone.now().date():
                self.estado = 'VENCIDA'
                self.save()

        return self.estado == 'ACTIVA'

    def actualizar_estado(self):
        """Actualiza el estado de la membresía según la fecha"""
        if self.fecha_fin < timezone.now().date():
            self.estado = 'VENCIDA'

    def inicializar_fecha_fin(self):
        """Actualiza la fecha de finalización de la membresía"""
        # self.fecha_fin = self.plan.calcular_fecha_fin(self.fecha_inicio)
        self.fecha_fin = self.fecha_inicio  # el pago es el inicio de la membresia

    def actualizar_fecha_fin(self, nueva_fecha_fin):
        """Actualiza la fecha de finalización de la membresía"""
        self.fecha_fin = nueva_fecha_fin
        self.save()

    def save(self, *args, **kwargs):
        if not self.pk:  # Si es una nueva membresia
            self.inicializar_fecha_fin()

        self.actualizar_estado()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Membresia'
        verbose_name_plural = 'Membresias'
        ordering = ['socio']

    def __str__(self):
        return f"{self.socio} ({self.plan})"


class Pago(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('VENCIDO', 'Vencido'),
    ]
    METODO_PAGO = [
        ('EFECTIVO', 'Efectivo'),
        ('DEBITO', 'Débito'),
        ('CREDITO', 'Crédito'),
        ('TRANSFERENCIA', 'Transferencia'),
    ]
    membresia = models.ForeignKey(Membresia, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField()
    estado = models.CharField(
        max_length=10, choices=ESTADOS, default='PENDIENTE')
    metodo_pago = models.CharField(
        max_length=50, blank=True, null=True, choices=METODO_PAGO, default='EFECTIVO')
    comprobante_nro = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # si en un nuevo pago
            self.fecha_vencimiento = self.membresia.fecha_fin
            fecha_vencimiento = self.membresia.plan.calcular_fecha_fin(
                self.fecha_vencimiento)
            self.membresia.actualizar_fecha_fin(fecha_vencimiento)

        if self.monto > 0:
            self.estado = 'PAGADO'

        # if self.fecha_pago > self.fecha_vencimiento:
        #     self.estado = 'VENCIDO'

        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.membresia} - Pagó: {self.monto}"

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['membresia', '-fecha_pago']


@receiver(post_save, sender=Membresia)
def crear_pago_inicial_signal(sender, instance, created, **kwargs):
    if created:
        PagoService.crear_pago_inicial(instance)


class PagoService:
    @staticmethod
    def crear_pago_inicial(membresia):

        return Pago.objects.create(
            membresia=membresia,
            monto=membresia.plan.precio,
            fecha_pago=membresia.fecha_inicio,
            fecha_vencimiento=membresia.fecha_fin,
            estado='PAGADO'
        )
