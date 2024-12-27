from tabnanny import verbose
from django.db import models
from django.utils import timezone


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

    class Meta:
        verbose_name = 'Plan'
        verbose_name_plural = 'Planes'

    def __str__(self):
        return self.nombre


class Membresia(models.Model):
    ESTADOS = [
        ('ACTIVA', 'Activa'),
        ('VENCIDA', 'Vencida'),
        ('CANCELADA', 'Cancelada'),
    ]

    socio = models.ForeignKey(
        Socio, on_delete=models.CASCADE)
    plan = models.ForeignKey(
        Plan, on_delete=models.PROTECT)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVA')
    fecha_alta = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Membresia'
        verbose_name_plural = 'Membresias'

    def __str__(self):
        return f"{self.socio} - {self.plan}"


class Pago(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('VENCIDO', 'Vencido'),
    ]

    socio = models.ForeignKey(Socio, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(blank=True, null=True)
    fecha_vencimiento = models.DateField()
    estado = models.CharField(
        max_length=10, choices=ESTADOS, default='PENDIENTE')
    metodo_pago = models.CharField(max_length=50, blank=True, null=True)
    comprobante_nro = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
