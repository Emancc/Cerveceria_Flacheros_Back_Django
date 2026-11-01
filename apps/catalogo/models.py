"""Modelos del catálogo: estilos, cervezas, proveedores, ingredientes y lotes."""

from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Q
from django.utils.translation import gettext_lazy as _

from apps.core.models import ModeloConFechas


class Estilo(ModeloConFechas):
    """Estilo de cerveza (pilsner, IPA, stout, etc.)."""

    nombre = models.CharField(_("nombre"), max_length=60, unique=True)
    slug = models.SlugField(_("slug"), max_length=60, unique=True)
    descripcion = models.TextField(_("descripción"), blank=True)
    color = models.CharField(
        _("color"),
        max_length=7,
        default="#C8A24A",
        blank=True,
    )

    class Meta:
        verbose_name = _("estilo")
        verbose_name_plural = _("estilos")
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Cerveza(ModeloConFechas):
    """Producto terminado que se ofrece a los clientes."""

    nombre = models.CharField(_("nombre"), max_length=80, unique=True)
    estilo = models.ForeignKey(
        Estilo,
        on_delete=models.PROTECT,
        related_name="cervezas",
        verbose_name=_("estilo"),
    )
    graduacion = models.DecimalField(
        _("graduación"),
        max_digits=4,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("15")),
        ],
    )
    amargor = models.PositiveSmallIntegerField(
        _("amargor (IBU)"),
        validators=[MaxValueValidator(120)],
    )
    descripcion = models.TextField(_("descripción"))
    precio = models.DecimalField(
        _("precio"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    stock = models.PositiveIntegerField(_("stock"), default=0)
    imagen = models.URLField(_("imagen"), max_length=500, blank=True)
    imagen_archivo = models.ImageField(
        _("archivo de imagen"),
        upload_to="cervezas/%Y/%m/",
        max_length=255,
        blank=True,
    )
    color = models.CharField(
        _("color"),
        max_length=7,
        default="#C8A24A",
        blank=True,
    )
    activo = models.BooleanField(_("activo"), default=True)

    class Meta:
        verbose_name = _("cerveza")
        verbose_name_plural = _("cervezas")
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["estilo", "activo"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(precio__gt=0),
                name="cerveza_precio_positivo",
            ),
            models.CheckConstraint(
                condition=Q(graduacion__gte=0, graduacion__lte=15),
                name="cerveza_graduacion_valida",
            ),
            models.CheckConstraint(
                condition=Q(amargor__lte=120),
                name="cerveza_amargor_valido",
            ),
        ]

    def __str__(self):
        return self.nombre

    @property
    def resenas_promedio(self):
        """Promedio de puntuaciones de las reseñas, o None si no hay."""
        promedio = self.resenas.aggregate(promedio=Avg("puntuacion"))["promedio"]
        if promedio is None:
            return None
        return round(promedio, 2)


class Proveedor(ModeloConFechas):
    """Proveedor de materias primas."""

    nombre = models.CharField(_("nombre"), max_length=100, unique=True)
    contacto = models.CharField(_("contacto"), max_length=100, blank=True)
    email = models.EmailField(_("correo electrónico"), blank=True)
    telefono = models.CharField(_("teléfono"), max_length=30, blank=True)
    cuit = models.CharField(_("CUIT"), max_length=13, blank=True)
    direccion = models.CharField(_("dirección"), max_length=200, blank=True)
    activo = models.BooleanField(_("activo"), default=True)

    class Meta:
        verbose_name = _("proveedor")
        verbose_name_plural = _("proveedores")
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Ingrediente(ModeloConFechas):
    """Materia prima usada en las recetas."""

    class Tipo(models.TextChoices):
        MALTA = "malta", _("Malta")
        LUPULO = "lupulo", _("Lúpulo")
        LEVADURA = "levadura", _("Levadura")
        AGUA = "agua", _("Agua")
        ADJUNTO = "adjunto", _("Adjunto")
        OTRO = "otro", _("Otro")

    class Unidad(models.TextChoices):
        KG = "kg", _("Kilogramo")
        G = "g", _("Gramo")
        L = "l", _("Litro")
        ML = "ml", _("Mililitro")
        UNIDAD = "unidad", _("Unidad")

    nombre = models.CharField(_("nombre"), max_length=80, unique=True)
    tipo = models.CharField(
        _("tipo"),
        max_length=20,
        choices=Tipo.choices,
    )
    unidad = models.CharField(
        _("unidad"),
        max_length=10,
        choices=Unidad.choices,
    )
    stock = models.DecimalField(
        _("stock"),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0"))],
    )
    stock_minimo = models.DecimalField(
        _("stock mínimo"),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0"))],
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        related_name="ingredientes",
        null=True,
        blank=True,
        verbose_name=_("proveedor"),
    )

    class Meta:
        verbose_name = _("ingrediente")
        verbose_name_plural = _("ingredientes")
        ordering = ["nombre"]
        constraints = [
            models.CheckConstraint(
                condition=Q(stock__gte=0),
                name="ingrediente_stock_no_negativo",
            ),
        ]

    def __str__(self):
        return self.nombre


class Receta(ModeloConFechas):
    """Fórmula de elaboración de una cerveza."""

    cerveza = models.ForeignKey(
        Cerveza,
        on_delete=models.CASCADE,
        related_name="recetas",
        verbose_name=_("cerveza"),
    )
    nombre = models.CharField(_("nombre"), max_length=80)
    version = models.PositiveSmallIntegerField(_("versión"), default=1)
    volumen_litros = models.DecimalField(
        _("volumen en litros"),
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    notas = models.TextField(_("notas"), blank=True)
    activa = models.BooleanField(_("activa"), default=True)

    class Meta:
        verbose_name = _("receta")
        verbose_name_plural = _("recetas")
        ordering = ["cerveza__nombre", "-version"]
        constraints = [
            models.UniqueConstraint(
                fields=["cerveza", "version"],
                name="receta_unica_por_version",
            ),
        ]

    def __str__(self):
        return f"{self.cerveza.nombre} v{self.version}"


class RecetaIngrediente(models.Model):
    """Cantidad de un ingrediente dentro de una receta."""

    receta = models.ForeignKey(
        Receta,
        on_delete=models.CASCADE,
        related_name="ingredientes",
        verbose_name=_("receta"),
    )
    ingrediente = models.ForeignKey(
        Ingrediente,
        on_delete=models.PROTECT,
        related_name="recetas",
        verbose_name=_("ingrediente"),
    )
    cantidad = models.DecimalField(
        _("cantidad"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    unidad = models.CharField(
        _("unidad"),
        max_length=10,
        choices=Ingrediente.Unidad.choices,
    )

    class Meta:
        verbose_name = _("ingrediente de receta")
        verbose_name_plural = _("ingredientes de receta")
        ordering = ["receta", "ingrediente__nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["receta", "ingrediente"],
                name="receta_ingrediente_unico",
            ),
        ]

    def __str__(self):
        return f"{self.receta} - {self.ingrediente}"


class Lote(ModeloConFechas):
    """Lote de producción de una cerveza."""

    class Estado(models.TextChoices):
        PLANIFICADO = "planificado", _("Planificado")
        FERMENTANDO = "fermentando", _("Fermentando")
        MADURANDO = "madurando", _("Madurando")
        ENVASADO = "envasado", _("Envasado")
        DESCARTADO = "descartado", _("Descartado")

    cerveza = models.ForeignKey(
        Cerveza,
        on_delete=models.PROTECT,
        related_name="lotes",
        verbose_name=_("cerveza"),
    )
    receta = models.ForeignKey(
        Receta,
        on_delete=models.SET_NULL,
        related_name="lotes",
        null=True,
        blank=True,
        verbose_name=_("receta"),
    )
    codigo = models.CharField(_("código"), max_length=20, unique=True)
    fecha_elaboracion = models.DateField(_("fecha de elaboración"))
    fecha_vencimiento = models.DateField(
        _("fecha de vencimiento"),
        null=True,
        blank=True,
    )
    volumen_litros = models.DecimalField(
        _("volumen en litros"),
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    estado = models.CharField(
        _("estado"),
        max_length=20,
        choices=Estado.choices,
        default=Estado.PLANIFICADO,
    )
    observaciones = models.TextField(_("observaciones"), blank=True)

    class Meta:
        verbose_name = _("lote")
        verbose_name_plural = _("lotes")
        ordering = ["-fecha_elaboracion"]
        constraints = [
            models.CheckConstraint(
                condition=Q(volumen_litros__gt=0),
                name="lote_volumen_positivo",
            ),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.cerveza.nombre}"
