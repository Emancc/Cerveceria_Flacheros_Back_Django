"""Carga datos de demostración para la Cervecería Los Flacheros."""

from datetime import date, datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.catalogo.models import (
    Cerveza,
    Estilo,
    Ingrediente,
    Lote,
    Proveedor,
    Receta,
    RecetaIngrediente,
)
from apps.cuentas.models import PerfilUsuario, Usuario
from apps.ventas.models import Cliente, DetallePedido, Pedido, Resena

IMAGEN_UNSPLASH = (
    "https://images.unsplash.com/photo-1518099074172-2e47eeec7d3e"
    "?auto=format&fit=crop&w=800&q=80"
)

ESTILOS = [
    {
        "slug": "pilsner",
        "nombre": "Pilsner",
        "color": "#f0d67a",
        "descripcion": "Dorada, ligera y refrescante, de final seco.",
    },
    {
        "slug": "red_ale",
        "nombre": "Red Ale",
        "color": "#b5541f",
        "descripcion": "Maltosa y tostada, con notas de caramelo.",
    },
    {
        "slug": "ipa",
        "nombre": "IPA",
        "color": "#e0a53c",
        "descripcion": "Intensa, cítrica y con amargor largo.",
    },
    {
        "slug": "stout",
        "nombre": "Stout",
        "color": "#2b1d16",
        "descripcion": "Oscura, cremosa y con recuerdos de cacao y café.",
    },
    {
        "slug": "weissbier",
        "nombre": "Weissbier",
        "color": "#f5e3b0",
        "descripcion": "Turbia y sedosa, con banana y clavo de olor.",
    },
    {
        "slug": "honey_ale",
        "nombre": "Honey Ale",
        "color": "#e8b84b",
        "descripcion": "Redonda y perfumada, con miel local.",
    },
]

CERVEZAS = [
    {
        "nombre": "Flacheros Pils",
        "estilo": "pilsner",
        "graduacion": Decimal("4.80"),
        "amargor": 22,
        "descripcion": (
            "Ligera, dorada y refrescante, con un final seco que invita a "
            "otra ronda."
        ),
        "precio": Decimal("2800.00"),
        "stock": 24,
        "imagen": IMAGEN_UNSPLASH,
        "color": "#f0d67a",
    },
    {
        "nombre": "Roja del Sendero",
        "estilo": "red_ale",
        "graduacion": Decimal("5.50"),
        "amargor": 28,
        "descripcion": (
            "Maltas tostadas con notas de caramelo y un amargor equilibrado "
            "de bosque."
        ),
        "precio": Decimal("3200.00"),
        "stock": 18,
        "imagen": (
            "https://images.unsplash.com/photo-1535958636474-b021ee887b13"
            "?auto=format&fit=crop&w=800&q=80"
        ),
        "color": "#b5541f",
    },
    {
        "nombre": "Bosque Negro",
        "estilo": "stout",
        "graduacion": Decimal("6.20"),
        "amargor": 42,
        "descripcion": (
            "Intensa y cremosa, con aromas de cacao, café y un suave "
            "recuerdo a tierra húmeda."
        ),
        "precio": Decimal("3600.00"),
        "stock": 12,
        "imagen": (
            "https://images.unsplash.com/photo-1571613316887-6f8d5cbf7ef7"
            "?auto=format&fit=crop&w=800&q=80"
        ),
        "color": "#2b1d16",
    },
    {
        "nombre": "Lúpulo del Valle",
        "estilo": "ipa",
        "graduacion": Decimal("6.50"),
        "amargor": 55,
        "descripcion": (
            "Explosión de lúpulo fresco con destellos cítricos y un amargor "
            "largo y limpio."
        ),
        "precio": Decimal("3800.00"),
        "stock": 20,
        "imagen": (
            "https://images.unsplash.com/photo-1608270586620-248524c67de9"
            "?auto=format&fit=crop&w=800&q=80"
        ),
        "color": "#e0a53c",
    },
    {
        "nombre": "Miel de Romero",
        "estilo": "honey_ale",
        "graduacion": Decimal("5.00"),
        "amargor": 20,
        "descripcion": (
            "Redonda y perfumada, endulzada con miel de romero de "
            "productores locales."
        ),
        "precio": Decimal("3400.00"),
        "stock": 15,
        "imagen": IMAGEN_UNSPLASH,
        "color": "#e8b84b",
    },
    {
        "nombre": "Trigo de la Casa",
        "estilo": "weissbier",
        "graduacion": Decimal("4.90"),
        "amargor": 14,
        "descripcion": (
            "Turbia y sedosa, con banana y clavo de olor sobre una base de "
            "trigo suave."
        ),
        "precio": Decimal("3100.00"),
        "stock": 9,
        "imagen": IMAGEN_UNSPLASH,
        "color": "#f5e3b0",
    },
    {
        "nombre": "Doble Malta",
        "estilo": "red_ale",
        "graduacion": Decimal("7.10"),
        "amargor": 38,
        "descripcion": (
            "Cuerpo generoso y maltoso, con recuerdos de pan tostado y "
            "frutos secos."
        ),
        "precio": Decimal("4100.00"),
        "stock": 6,
        "imagen": IMAGEN_UNSPLASH,
        "color": "#8a3b16",
    },
    {
        "nombre": "Cosecha Dorada",
        "estilo": "honey_ale",
        "graduacion": Decimal("4.60"),
        "amargor": 18,
        "descripcion": (
            "Suave y luminosa, con miel de campo y un cierre fresco de "
            "hierba recién cortada."
        ),
        "precio": Decimal("3000.00"),
        "stock": 0,
        "imagen": IMAGEN_UNSPLASH,
        "color": "#d9a441",
    },
]

PROVEEDORES = [
    {
        "nombre": "Maltería del Sur",
        "contacto": "Lucía Fernández",
        "email": "ventas@malteriadelsur.com.ar",
        "telefono": "0351-455-1200",
        "cuit": "30-71234567-8",
        "direccion": "Av. Industrial 1200, Córdoba",
    },
    {
        "nombre": "Lúpulos del Valle",
        "contacto": "Martín Quiroga",
        "email": "pedidos@lupulosdelvalle.com.ar",
        "telefono": "0299-442-8890",
        "cuit": "30-70987654-3",
        "direccion": "Ruta 22 Km 8, Neuquén",
    },
    {
        "nombre": "Levaduras Andinas",
        "contacto": "Sofía Ríos",
        "email": "contacto@levadurasandinas.com.ar",
        "telefono": "0261-430-7711",
        "cuit": "30-70811223-4",
        "direccion": "Parque Industrial, Mendoza",
    },
    {
        "nombre": "Envases Córdoba",
        "contacto": "Diego Paz",
        "email": "comercial@envasescordoba.com.ar",
        "telefono": "0351-477-3300",
        "cuit": "30-71555666-9",
        "direccion": "Bv. de los Granaderos 450, Córdoba",
    },
]

INGREDIENTES = [
    {
        "nombre": "Malta Pilsner",
        "tipo": "malta",
        "unidad": "kg",
        "stock": Decimal("120.00"),
        "stock_minimo": Decimal("50.00"),
        "proveedor": "Maltería del Sur",
    },
    {
        "nombre": "Malta Caramelo",
        "tipo": "malta",
        "unidad": "kg",
        "stock": Decimal("35.00"),
        "stock_minimo": Decimal("40.00"),
        "proveedor": "Maltería del Sur",
    },
    {
        "nombre": "Malta Chocolate",
        "tipo": "malta",
        "unidad": "kg",
        "stock": Decimal("18.00"),
        "stock_minimo": Decimal("20.00"),
        "proveedor": "Maltería del Sur",
    },
    {
        "nombre": "Trigo malteado",
        "tipo": "malta",
        "unidad": "kg",
        "stock": Decimal("60.00"),
        "stock_minimo": Decimal("30.00"),
        "proveedor": "Maltería del Sur",
    },
    {
        "nombre": "Lúpulo Cascade",
        "tipo": "lupulo",
        "unidad": "g",
        "stock": Decimal("900.00"),
        "stock_minimo": Decimal("500.00"),
        "proveedor": "Lúpulos del Valle",
    },
    {
        "nombre": "Lúpulo Citra",
        "tipo": "lupulo",
        "unidad": "g",
        "stock": Decimal("250.00"),
        "stock_minimo": Decimal("400.00"),
        "proveedor": "Lúpulos del Valle",
    },
    {
        "nombre": "Levadura Ale",
        "tipo": "levadura",
        "unidad": "g",
        "stock": Decimal("600.00"),
        "stock_minimo": Decimal("300.00"),
        "proveedor": "Levaduras Andinas",
    },
    {
        "nombre": "Levadura Lager",
        "tipo": "levadura",
        "unidad": "g",
        "stock": Decimal("150.00"),
        "stock_minimo": Decimal("200.00"),
        "proveedor": "Levaduras Andinas",
    },
    {
        "nombre": "Agua de manantial",
        "tipo": "agua",
        "unidad": "l",
        "stock": Decimal("2000.00"),
        "stock_minimo": Decimal("500.00"),
        "proveedor": None,
    },
    {
        "nombre": "Miel de romero",
        "tipo": "adjunto",
        "unidad": "kg",
        "stock": Decimal("25.00"),
        "stock_minimo": Decimal("10.00"),
        "proveedor": None,
    },
    {
        "nombre": "Azúcar de caña",
        "tipo": "adjunto",
        "unidad": "kg",
        "stock": Decimal("8.00"),
        "stock_minimo": Decimal("15.00"),
        "proveedor": None,
    },
]

RECETAS = [
    {
        "cerveza": "Flacheros Pils",
        "volumen": Decimal("30.00"),
        "ingredientes": [
            ("Malta Pilsner", Decimal("4.50"), "kg"),
            ("Lúpulo Cascade", Decimal("120.00"), "g"),
            ("Levadura Lager", Decimal("20.00"), "g"),
        ],
    },
    {
        "cerveza": "Roja del Sendero",
        "volumen": Decimal("25.00"),
        "ingredientes": [
            ("Malta Caramelo", Decimal("3.00"), "kg"),
            ("Malta Pilsner", Decimal("2.00"), "kg"),
            ("Lúpulo Cascade", Decimal("90.00"), "g"),
        ],
    },
    {
        "cerveza": "Bosque Negro",
        "volumen": Decimal("28.00"),
        "ingredientes": [
            ("Malta Chocolate", Decimal("2.50"), "kg"),
            ("Malta Pilsner", Decimal("3.00"), "kg"),
            ("Lúpulo Cascade", Decimal("80.00"), "g"),
        ],
    },
    {
        "cerveza": "Lúpulo del Valle",
        "volumen": Decimal("40.00"),
        "ingredientes": [
            ("Malta Pilsner", Decimal("5.00"), "kg"),
            ("Lúpulo Citra", Decimal("180.00"), "g"),
            ("Levadura Ale", Decimal("25.00"), "g"),
        ],
    },
    {
        "cerveza": "Miel de Romero",
        "volumen": Decimal("30.00"),
        "ingredientes": [
            ("Malta Pilsner", Decimal("4.00"), "kg"),
            ("Miel de romero", Decimal("1.20"), "kg"),
            ("Levadura Ale", Decimal("20.00"), "g"),
        ],
    },
    {
        "cerveza": "Trigo de la Casa",
        "volumen": Decimal("25.00"),
        "ingredientes": [
            ("Trigo malteado", Decimal("3.50"), "kg"),
            ("Malta Pilsner", Decimal("2.00"), "kg"),
            ("Levadura Ale", Decimal("22.00"), "g"),
        ],
    },
    {
        "cerveza": "Doble Malta",
        "volumen": Decimal("35.00"),
        "ingredientes": [
            ("Malta Pilsner", Decimal("4.00"), "kg"),
            ("Malta Caramelo", Decimal("2.50"), "kg"),
            ("Malta Chocolate", Decimal("0.80"), "kg"),
        ],
    },
    {
        "cerveza": "Cosecha Dorada",
        "volumen": Decimal("30.00"),
        "ingredientes": [
            ("Malta Pilsner", Decimal("3.50"), "kg"),
            ("Miel de romero", Decimal("0.80"), "kg"),
            ("Lúpulo Cascade", Decimal("60.00"), "g"),
        ],
    },
]

LOTES = [
    {
        "codigo": "LF-2026-001",
        "cerveza": "Flacheros Pils",
        "fecha": date(2026, 1, 15),
        "volumen": Decimal("30.00"),
        "estado": "planificado",
        "vencimiento": None,
    },
    {
        "codigo": "LF-2026-002",
        "cerveza": "Roja del Sendero",
        "fecha": date(2026, 2, 3),
        "volumen": Decimal("25.00"),
        "estado": "fermentando",
        "vencimiento": None,
    },
    {
        "codigo": "LF-2026-003",
        "cerveza": "Bosque Negro",
        "fecha": date(2026, 3, 12),
        "volumen": Decimal("28.00"),
        "estado": "madurando",
        "vencimiento": date(2026, 6, 10),
    },
    {
        "codigo": "LF-2026-004",
        "cerveza": "Lúpulo del Valle",
        "fecha": date(2026, 4, 20),
        "volumen": Decimal("40.00"),
        "estado": "envasado",
        "vencimiento": date(2026, 7, 19),
    },
    {
        "codigo": "LF-2026-005",
        "cerveza": "Miel de Romero",
        "fecha": date(2026, 5, 18),
        "volumen": Decimal("30.00"),
        "estado": "envasado",
        "vencimiento": date(2026, 8, 16),
    },
    {
        "codigo": "LF-2026-006",
        "cerveza": "Trigo de la Casa",
        "fecha": date(2026, 6, 25),
        "volumen": Decimal("25.00"),
        "estado": "descartado",
        "vencimiento": None,
    },
    {
        "codigo": "LF-2026-007",
        "cerveza": "Doble Malta",
        "fecha": date(2026, 8, 7),
        "volumen": Decimal("35.00"),
        "estado": "fermentando",
        "vencimiento": None,
    },
    {
        "codigo": "LF-2026-008",
        "cerveza": "Cosecha Dorada",
        "fecha": date(2026, 9, 14),
        "volumen": Decimal("30.00"),
        "estado": "madurando",
        "vencimiento": date(2026, 12, 13),
    },
]

CLIENTES = [
    {
        "nombre": "Almacén Don Pedro",
        "email": "pedro@example.com",
        "telefono": "0351-411-2233",
        "tipo": "minorista",
        "direccion": "Av. Colón 1200, Córdoba",
    },
    {
        "nombre": "Distribuidora Cuyo",
        "email": "compras@distribuidoracuyo.com.ar",
        "telefono": "0261-422-3344",
        "tipo": "mayorista",
        "direccion": "Ruta 40 Km 12, Mendoza",
    },
    {
        "nombre": "Bar El Lúpulo",
        "email": "bar@ellupulo.com.ar",
        "telefono": "0351-466-7788",
        "tipo": "bar",
        "direccion": "Belgrano 450, Córdoba",
    },
    {
        "nombre": "Eventos La Cosecha",
        "email": "eventos@lacosecha.com.ar",
        "telefono": "0351-499-1122",
        "tipo": "evento",
        "direccion": "Av. Del Prado 800, Córdoba",
    },
    {
        "nombre": "Kiosco La Esquina",
        "email": "kiosco@example.com",
        "telefono": "0351-433-5566",
        "tipo": "minorista",
        "direccion": "San Martín 230, Córdoba",
    },
    {
        "nombre": "Cervecería del Parque",
        "email": "contacto@cerveceriadelparque.com.ar",
        "telefono": "0351-477-9900",
        "tipo": "bar",
        "direccion": "Parque Sarmiento, Córdoba",
    },
]

PEDIDOS = [
    {
        "cliente": "Almacén Don Pedro",
        "fecha": datetime(2026, 1, 20, 10, 0),
        "estado": "pendiente",
        "canal": "web",
        "notas": "Reposición de fin de semana",
        "detalles": [("Flacheros Pils", 6), ("Lúpulo del Valle", 4)],
    },
    {
        "cliente": "Distribuidora Cuyo",
        "fecha": datetime(2026, 2, 14, 11, 30),
        "estado": "confirmado",
        "canal": "local",
        "notas": "Pedido mayorista",
        "detalles": [
            ("Flacheros Pils", 24),
            ("Roja del Sendero", 12),
            ("Bosque Negro", 6),
        ],
    },
    {
        "cliente": "Bar El Lúpulo",
        "fecha": datetime(2026, 3, 8, 18, 0),
        "estado": "entregado",
        "canal": "telefono",
        "notas": "Entrega en barra",
        "detalles": [("Lúpulo del Valle", 12), ("Trigo de la Casa", 8)],
    },
    {
        "cliente": "Eventos La Cosecha",
        "fecha": datetime(2026, 4, 22, 9, 0),
        "estado": "confirmado",
        "canal": "web",
        "notas": "Evento corporativo",
        "detalles": [
            ("Miel de Romero", 20),
            ("Flacheros Pils", 20),
            ("Roja del Sendero", 10),
        ],
    },
    {
        "cliente": "Kiosco La Esquina",
        "fecha": datetime(2026, 5, 30, 16, 45),
        "estado": "cancelado",
        "canal": "web",
        "notas": "Cancelado por el cliente",
        "detalles": [("Bosque Negro", 3)],
    },
    {
        "cliente": "Cervecería del Parque",
        "fecha": datetime(2026, 6, 18, 20, 0),
        "estado": "entregado",
        "canal": "local",
        "notas": "Pedido de barra",
        "detalles": [("Doble Malta", 6), ("Cosecha Dorada", 6)],
    },
]

RESENAS = [
    ("Flacheros Pils", "Almacén Don Pedro", 5, "Muy fresca, ideal para el verano."),
    ("Flacheros Pils", "Distribuidora Cuyo", 4, "Buena rotación entre los clientes."),
    ("Flacheros Pils", "Bar El Lúpulo", 5, "La más pedida de la barra."),
    ("Lúpulo del Valle", "Eventos La Cosecha", 5, "Un éxito en el evento."),
    ("Lúpulo del Valle", "Kiosco La Esquina", 4, "Amargor justo."),
    ("Roja del Sendero", "Cervecería del Parque", 4, "Maltosa y equilibrada."),
    ("Bosque Negro", "Almacén Don Pedro", 5, "Cremosa, con buen café."),
    ("Bosque Negro", "Distribuidora Cuyo", 3, "Un poco intensa para algunos."),
    ("Miel de Romero", "Bar El Lúpulo", 4, "Perfumada y distinta."),
    ("Trigo de la Casa", "Eventos La Cosecha", 5, "Muy refrescante."),
    ("Doble Malta", "Kiosco La Esquina", 4, "Cuerpo generoso."),
    ("Cosecha Dorada", "Cervecería del Parque", 3, "Suave, para empezar."),
]


class Command(BaseCommand):
    help = "Carga datos de demostración idempotentes para la Cervecería Los Flacheros."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Borra los datos de dominio antes de cargar los datos demo.",
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            if options["reset"]:
                self._reset()
            self._crear_admin()
            estilos = self._crear_estilos()
            cervezas = self._crear_cervezas(estilos)
            proveedores = self._crear_proveedores()
            ingredientes = self._crear_ingredientes(proveedores)
            recetas = self._crear_recetas(cervezas, ingredientes)
            self._crear_lotes(cervezas, recetas)
            clientes = self._crear_clientes()
            self._crear_pedidos(clientes, cervezas)
            self._crear_resenas(clientes, cervezas)
        self._resumen()

    def _reset(self):
        modelos = [
            Resena,
            DetallePedido,
            Pedido,
            Cliente,
            Lote,
            RecetaIngrediente,
            Receta,
            Ingrediente,
            Proveedor,
            Cerveza,
            Estilo,
        ]
        for modelo in modelos:
            modelo.objects.all().delete()
        self.stdout.write(
            self.style.WARNING("Datos de dominio eliminados (--reset).")
        )

    def _crear_admin(self):
        usuario, _ = Usuario.objects.update_or_create(
            email="admin@flacheros.com",
            defaults={
                "first_name": "Admin",
                "last_name": "Flacheros",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        usuario.set_password("admin12345")
        usuario.save()
        PerfilUsuario.objects.update_or_create(
            usuario=usuario,
            defaults={
                "rol": PerfilUsuario.Rol.ADMIN,
                "telefono": "+54 351 555-0100",
                "bio": "Administrador de demostración de la Cervecería Los Flacheros.",
            },
        )

    def _crear_estilos(self):
        estilos = {}
        for datos in ESTILOS:
            estilo, _ = Estilo.objects.update_or_create(
                slug=datos["slug"],
                defaults={
                    "nombre": datos["nombre"],
                    "descripcion": datos["descripcion"],
                    "color": datos["color"],
                },
            )
            estilos[datos["slug"]] = estilo
        return estilos

    def _crear_cervezas(self, estilos):
        cervezas = {}
        for datos in CERVEZAS:
            cerveza, _ = Cerveza.objects.update_or_create(
                nombre=datos["nombre"],
                defaults={
                    "estilo": estilos[datos["estilo"]],
                    "graduacion": datos["graduacion"],
                    "amargor": datos["amargor"],
                    "descripcion": datos["descripcion"],
                    "precio": datos["precio"],
                    "stock": datos["stock"],
                    "imagen": datos["imagen"],
                    "color": datos["color"],
                    "activo": True,
                },
            )
            cervezas[datos["nombre"]] = cerveza
        return cervezas

    def _crear_proveedores(self):
        proveedores = {}
        for datos in PROVEEDORES:
            proveedor, _ = Proveedor.objects.update_or_create(
                nombre=datos["nombre"],
                defaults={
                    "contacto": datos["contacto"],
                    "email": datos["email"],
                    "telefono": datos["telefono"],
                    "cuit": datos["cuit"],
                    "direccion": datos["direccion"],
                    "activo": True,
                },
            )
            proveedores[datos["nombre"]] = proveedor
        return proveedores

    def _crear_ingredientes(self, proveedores):
        ingredientes = {}
        for datos in INGREDIENTES:
            proveedor = (
                proveedores.get(datos["proveedor"])
                if datos["proveedor"]
                else None
            )
            ingrediente, _ = Ingrediente.objects.update_or_create(
                nombre=datos["nombre"],
                defaults={
                    "tipo": datos["tipo"],
                    "unidad": datos["unidad"],
                    "stock": datos["stock"],
                    "stock_minimo": datos["stock_minimo"],
                    "proveedor": proveedor,
                },
            )
            ingredientes[datos["nombre"]] = ingrediente
        return ingredientes

    def _crear_recetas(self, cervezas, ingredientes):
        recetas = {}
        for datos in RECETAS:
            cerveza = cervezas[datos["cerveza"]]
            receta, _ = Receta.objects.update_or_create(
                cerveza=cerveza,
                version=1,
                defaults={
                    "nombre": f"Receta {cerveza.nombre}",
                    "volumen_litros": datos["volumen"],
                    "notas": "Receta base de la casa para demostración.",
                    "activa": True,
                },
            )
            nombres = [nombre for nombre, _, _ in datos["ingredientes"]]
            receta.ingredientes.exclude(
                ingrediente__nombre__in=nombres
            ).delete()
            for nombre, cantidad, unidad in datos["ingredientes"]:
                RecetaIngrediente.objects.update_or_create(
                    receta=receta,
                    ingrediente=ingredientes[nombre],
                    defaults={"cantidad": cantidad, "unidad": unidad},
                )
            recetas[datos["cerveza"]] = receta
        return recetas

    def _crear_lotes(self, cervezas, recetas):
        for datos in LOTES:
            Lote.objects.update_or_create(
                codigo=datos["codigo"],
                defaults={
                    "cerveza": cervezas[datos["cerveza"]],
                    "receta": recetas.get(datos["cerveza"]),
                    "fecha_elaboracion": datos["fecha"],
                    "fecha_vencimiento": datos["vencimiento"],
                    "volumen_litros": datos["volumen"],
                    "estado": datos["estado"],
                    "observaciones": (
                        f"Lote de demostración {datos['codigo']}."
                    ),
                },
            )

    def _crear_clientes(self):
        clientes = {}
        for datos in CLIENTES:
            cliente, _ = Cliente.objects.update_or_create(
                email=datos["email"],
                defaults={
                    "nombre": datos["nombre"],
                    "telefono": datos["telefono"],
                    "tipo": datos["tipo"],
                    "direccion": datos["direccion"],
                    "activo": True,
                },
            )
            clientes[datos["nombre"]] = cliente
        return clientes

    def _crear_pedidos(self, clientes, cervezas):
        for datos in PEDIDOS:
            cliente = clientes[datos["cliente"]]
            fecha = timezone.make_aware(datos["fecha"])
            pedido, _ = Pedido.objects.update_or_create(
                cliente=cliente,
                fecha_pedido=fecha,
                defaults={
                    "estado": datos["estado"],
                    "canal": datos["canal"],
                    "notas": datos["notas"],
                },
            )
            deseadas = [cervezas[nombre] for nombre, _ in datos["detalles"]]
            pedido.detalles.exclude(cerveza__in=deseadas).delete()
            for nombre, cantidad in datos["detalles"]:
                cerveza = cervezas[nombre]
                DetallePedido.objects.update_or_create(
                    pedido=pedido,
                    cerveza=cerveza,
                    defaults={
                        "cantidad": cantidad,
                        "precio_unitario": cerveza.precio,
                    },
                )
            pedido.recalcular_total()

    def _crear_resenas(self, clientes, cervezas):
        for cerveza_nombre, cliente_nombre, puntuacion, comentario in RESENAS:
            Resena.objects.update_or_create(
                cerveza=cervezas[cerveza_nombre],
                cliente=clientes[cliente_nombre],
                defaults={
                    "puntuacion": puntuacion,
                    "comentario": comentario,
                },
            )

    def _resumen(self):
        conteos = [
            ("Estilos", Estilo.objects.count()),
            ("Cervezas", Cerveza.objects.count()),
            ("Proveedores", Proveedor.objects.count()),
            ("Ingredientes", Ingrediente.objects.count()),
            ("Recetas", Receta.objects.count()),
            ("Ingredientes de receta", RecetaIngrediente.objects.count()),
            ("Lotes", Lote.objects.count()),
            ("Clientes", Cliente.objects.count()),
            ("Pedidos", Pedido.objects.count()),
            ("Detalles de pedido", DetallePedido.objects.count()),
            ("Reseñas", Resena.objects.count()),
        ]
        self.stdout.write(
            self.style.SUCCESS("Datos de demostración cargados correctamente.")
        )
        for etiqueta, cantidad in conteos:
            self.stdout.write(f"  {etiqueta}: {cantidad}")
