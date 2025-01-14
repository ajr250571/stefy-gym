import time
from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import pywhatkit
import pyautogui
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.conf import settings
from simple_history.models import HistoricalRecords
import environ


env = environ.Env()
environ.Env.read_env()


class Socio(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    apellido = models.CharField(max_length=100, verbose_name='Apellido')
    email = models.EmailField(unique=True, verbose_name='Email')
    telefono = models.CharField(
        max_length=20, blank=True, null=True, verbose_name='Teléfono')
    fecha_nacimiento = models.DateField(
        blank=True, null=True, verbose_name='Fecha de Nacimiento')
    dni = models.CharField(max_length=20, unique=True, verbose_name='DNI')
    direccion = models.CharField(
        max_length=100, blank=True, null=True, verbose_name='Direccion')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_alta = models.DateField(default=timezone.now)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Socio'
        verbose_name_plural = 'Socios'
        ordering = ['apellido', 'nombre']

    def nombre_completo(self):
        return f"{self.apellido}, {self.nombre}"

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"


class Plan(models.Model):
    nombre = models.CharField(
        max_length=100, unique=True, verbose_name='Nombre')
    precio = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Precio')
    duracion = models.IntegerField(verbose_name='Duración (meses)')
    descripcion = models.TextField(
        blank=True, null=True, verbose_name='Descripción')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    history = HistoricalRecords()

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
        Socio, on_delete=models.PROTECT, blank=False, null=False, verbose_name='Socio'
    )
    plan = models.ForeignKey(
        Plan, on_delete=models.PROTECT, blank=False, null=False, verbose_name='Plan')
    fecha_inicio = models.DateField(
        default=timezone.now, verbose_name='Fecha de Inicio')
    fecha_fin = models.DateField(verbose_name='Fecha de Finalización')
    estado = models.CharField(
        max_length=10, choices=ESTADOS, default='ACTIVA', verbose_name='Estado')
    fecha_alta = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha de Alta')
    history = HistoricalRecords()

    @classmethod
    def enviar_email(cls, membresia_id):
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
                    f"'{membresia.plan.nombre}' se encuentra vencida desde el "
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

            if membresia.socio.telefono:
                telefono = membresia.socio.telefono
                if membresia.fecha_fin < timezone.now().date():
                    titulo = 'Membresía vencida'
                    mensaje = (
                        f"Hola {membresia.socio.nombre}!\n"
                        f"Te informamos que tu membresía del plan "
                        f"'{membresia.plan.nombre}' se encuentra vencida desde el "
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

                # Limpiamos el número de teléfono (asumiendo formato +549xxxxxxxxxx)

                try:
                    pywhatkit.sendwhatmsg_instantly(  # type: ignore
                        phone_no=telefono,
                        message=mensaje,
                        tab_close=False,
                        # Segundos antes de cerrar la pestaña
                        wait_time=env.int('WAIT_TIME_WHATSAPP')
                    )
                    # Esperar a que WhatsApp Web se cargue
                    time.sleep(env.int('TIMEOUT_WHATSAPP'))  # type: ignore
                    # Asegurar que el foco esté en el campo de mensaje
                    # Click en el centro
                    pyautogui.click(pyautogui.size()[
                                    0] // 2, pyautogui.size()[1] // 2)
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

                    # hora = datetime.datetime.now()
                    # hora_send = hora.hour
                    # minutos_send = hora.minute + 2
                    # pywhatkit.sendwhatmsg(  # type: ignore
                    #     telefono, mensaje, hora_send, minutos_send, 10, True, 3)

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
            if self.fecha_fin <= timezone.now().date():
                self.estado = 'VENCIDA'
                self.save()
        return self.estado == 'ACTIVA'

    def actualizar_estado(self):
        """Actualiza el estado de la membresía según la fecha"""
        if self.estado != 'CANCELADA':
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
    membresia = models.ForeignKey(
        Membresia, on_delete=models.CASCADE, verbose_name='Membresia')
    monto = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Monto')
    fecha_pago = models.DateField(
        default=timezone.now, verbose_name='Fecha de Pago')
    fecha_vencimiento = models.DateField(verbose_name='Fecha de Vencimiento')
    estado = models.CharField(
        max_length=10, choices=ESTADOS, default='PAGADO', verbose_name='Estado')
    metodo_pago = models.CharField(
        max_length=50, blank=True, null=True, choices=METODO_PAGO, default='EFECTIVO', verbose_name='Metodo de Pago')
    comprobante_nro = models.CharField(
        max_length=50, blank=True, null=True, verbose_name='Nro. de Comprobante')

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


class Asistencia(models.Model):
    socio = models.ForeignKey(
        Socio, on_delete=models.CASCADE, verbose_name='Socio')
    fecha = models.DateField(default=timezone.now, verbose_name='Fecha')

    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        ordering = ['socio', '-fecha']

    def __str__(self):
        return f"{self.socio} - {self.fecha}"

    @classmethod
    def registrar_asistencia(cls, socio_dni):
        socio = Socio.objects.get(dni=socio_dni)
        # Si no existe asistencia para el socio y fecha, crear una nueva
        if not cls.objects.filter(socio=socio, fecha=timezone.now().date()).exists():
            return cls.objects.create(socio=socio, fecha=timezone.now().date())
