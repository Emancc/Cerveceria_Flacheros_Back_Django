"""Modelos de ventas: clientes, pedidos, detalles y reseñas."""

from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q, Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.catalogo.models import Cerveza
from apps.core.models import ModeloConFechas


class Cliente(ModeloConFechas):
    """Cliente que compra cerveza."""

    class Tipo(models.TextChoices):
        MINORISTA = "minorista", _("Minorista")
        MAYORISTA = "mayorista", _("Mayorista")
        BAR = "bar", _("Bar")
        EVENTO = "evento", _("Evento")

    nombre = models.CharField(_("nombre"), max_length=100)
    email = models.EmailField(_("correo electrónico"), unique=True)
    telefono = models.CharField(_("teléfono"), max_length=30, blank=True)
    tipo = models.CharField(
        _("tipo"),
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.MINORISTA,
    )
    direccion = models.CharField(_("dirección"), max_length=200, blank=True)
    activo = models.BooleanField(_("activo"), default=True)

    class Meta:
        verbose_name = _("cliente")
        verbose_name_plural = _("clientes")
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Pedido(ModeloConFechas):
    """Pedido de un cliente."""

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", _("Pendiente")
        CONFIRMADO = "confirmado", _("Confirmado")
        ENTREGADO = "entregado", _("Entregado")
        CANCELADO = "cancelado", _("Cancelado")

    class Canal(models.TextChoices):
        WEB = "web", _("Web")
        LOCAL = "local", _("Local")
        TELEFONO = "telefono", _("Teléfono")

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="pedidos",
        verbose_name=_("cliente"),
    )
    fecha_pedido = models.DateTimeField(
        _("fecha del pedido"),
        default=timezone.now,
    )
    estado = models.CharField(
        _("estado"),
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    canal = models.CharField(
        _("canal"),
        max_length=10,
        choices=Canal.choices,
        default=Canal.WEB,
    )
    notas = models.TextField(_("notas"), blank=True)
    total = models.DecimalField(
        _("total"),
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0"))],
    )

    class Meta:
        verbose_name = _("pedido")
        verbose_name_plural = _("pedidos")
        ordering = ["-fecha_pedido"]

    def __str__(self):
        return f"Pedido #{self.pk or 'nuevo'} - {self.cliente.nombre}"

    def recalcular_total(self, guardar=True):
        """Recalcula el total a partir de los detalles del pedido."""
        total = sum(
            (detalle.subtotal for detalle in self.detalles.all()),
            Decimal("0"),
        )
        self.total = total
        if guardar:
            # `auto_now` solo se actualiza si el campo va en update_fields.
            self.save(update_fields=["total", "actualizado_en"])
        return total

    @property
    def cantidad_items(self):
        """Cantidad total de unidades pedidas."""
        if self.pk is None:
            return 0
        return self.detalles.aggregate(total=Sum("cantidad"))["total"] or 0


class DetallePedido(models.Model):
    """Línea de un pedido: cerveza, cantidad y precio unitario."""

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="detalles",
        verbose_name=_("pedido"),
    )
    cerveza = models.ForeignKey(
        Cerveza,
        on_delete=models.PROTECT,
        related_name="detalles_pedido",
        verbose_name=_("cerveza"),
    )
    cantidad = models.PositiveIntegerField(
        _("cantidad"),
        validators=[MinValueValidator(1)],
    )
    precio_unitario = models.DecimalField(
        _("precio unitario"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )

    class Meta:
        verbose_name = _("detalle de pedido")
        verbose_name_plural = _("detalles de pedido")
        ordering = ["pedido", "cerveza__nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["pedido", "cerveza"],
                name="detalle_unico_por_pedido",
            ),
        ]

    def __str__(self):
        return f"{self.cantidad} x {self.cerveza.nombre}"

    @property
    def subtotal(self):
        if self.cantidad is None:
            return Decimal("0")
        return self.cantidad * (self.precio_unitario or Decimal("0"))

    def save(self, *args, **kwargs):
        if self.precio_unitario is None:
            self.precio_unitario = self.cerveza.precio
        super().save(*args, **kwargs)
        self.pedido.recalcular_total()

    def delete(self, *args, **kwargs):
        pedido = self.pedido
        resultado = super().delete(*args, **kwargs)
        pedido.recalcular_total()
        return resultado


class Resena(ModeloConFechas):
    """Opinión de un cliente sobre una cerveza."""

    cerveza = models.ForeignKey(
        Cerveza,
        on_delete=models.CASCADE,
        related_name="resenas",
        verbose_name=_("cerveza"),
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="resenas",
        verbose_name=_("cliente"),
    )
    puntuacion = models.PositiveSmallIntegerField(
        _("puntuación"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comentario = models.TextField(_("comentario"), blank=True)

    class Meta:
        verbose_name = _("reseña")
        verbose_name_plural = _("reseñas")
        ordering = ["-creado_en"]
        constraints = [
            models.UniqueConstraint(
                fields=["cerveza", "cliente"],
                name="resena_unica_por_cliente",
            ),
            models.CheckConstraint(
                condition=Q(puntuacion__gte=1, puntuacion__lte=5),
                name="resena_puntuacion_valida",
            ),
        ]

    def __str__(self):
        return f"{self.cerveza.nombre} - {self.cliente.nombre}: {self.puntuacion}/5"
