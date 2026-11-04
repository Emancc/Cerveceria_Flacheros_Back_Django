"""Tests de permisos por rol en la API."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalogo.models import Cerveza, Estilo
from apps.cuentas.models import PerfilUsuario
from apps.ventas.models import Cliente, Pedido

Usuario = get_user_model()


class PermisosPorRolTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = Usuario.objects.create_user(
            email="admin-permisos@example.com",
            password="ClaveSegura123",
            is_staff=True,
            is_superuser=True,
        )
        cls.cervecero = cls._crear_usuario(
            "cervecero-permisos@example.com", PerfilUsuario.Rol.CERVECERO
        )
        cls.ventas = cls._crear_usuario(
            "ventas-permisos@example.com", PerfilUsuario.Rol.VENTAS
        )
        cls.cliente = cls._crear_usuario(
            "cliente-permisos@example.com", PerfilUsuario.Rol.CLIENTE
        )
        cls.otro_cliente = cls._crear_usuario(
            "otro-cliente-permisos@example.com", PerfilUsuario.Rol.CLIENTE
        )

        cls.estilo = Estilo.objects.create(
            nombre="IPA",
            slug="ipa",
            descripcion="Lúpulo",
            color="#e0a53c",
        )
        cls.cerveza = Cerveza.objects.create(
            nombre="Lúpulo del Valle",
            estilo=cls.estilo,
            graduacion=Decimal("6.50"),
            amargor=55,
            descripcion="Cítrica",
            precio=Decimal("1800.00"),
            stock=10,
            color="#e0a53c",
        )

        cls.cliente_modelo = Cliente.objects.create(
            nombre="Cliente Permisos",
            email="cliente-permisos@example.com",
            tipo=Cliente.Tipo.MINORISTA,
        )
        cls.otro_cliente_modelo = Cliente.objects.create(
            nombre="Otro Cliente",
            email="otro-cliente-permisos@example.com",
            tipo=Cliente.Tipo.MINORISTA,
        )
        cls.pedido_propio = Pedido.objects.create(
            cliente=cls.cliente_modelo,
            estado=Pedido.Estado.PENDIENTE,
            canal=Pedido.Canal.WEB,
        )
        cls.pedido_ajeno = Pedido.objects.create(
            cliente=cls.otro_cliente_modelo,
            estado=Pedido.Estado.PENDIENTE,
            canal=Pedido.Canal.WEB,
        )

    @classmethod
    def _crear_usuario(cls, email, rol):
        usuario = Usuario.objects.create_user(
            email=email,
            password="ClaveSegura123",
        )
        PerfilUsuario.objects.update_or_create(
            usuario=usuario,
            defaults={"rol": rol},
        )
        return usuario

    def _autenticar(self, usuario):
        self.client.force_authenticate(user=usuario)

    # --- Cliente ---------------------------------------------------------

    def test_cliente_no_ve_proveedores(self):
        self._autenticar(self.cliente)
        respuesta = self.client.get(reverse("proveedor-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_cliente_no_ve_clientes(self):
        self._autenticar(self.cliente)
        respuesta = self.client.get(reverse("cliente-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_cliente_no_ve_ingredientes(self):
        self._autenticar(self.cliente)
        respuesta = self.client.get(reverse("ingrediente-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_cliente_lee_cervezas(self):
        self._autenticar(self.cliente)
        respuesta = self.client.get(reverse("cerveza-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_cliente_no_escribe_cervezas(self):
        self._autenticar(self.cliente)
        respuesta = self.client.post(
            reverse("cerveza-list"),
            {
                "nombre": "Nueva",
                "estilo": "ipa",
                "graduacion": "5.00",
                "amargor": 20,
                "descripcion": "Prueba",
                "precio": "1000.00",
                "stock": 5,
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_cliente_solo_ve_sus_pedidos(self):
        self._autenticar(self.cliente)
        respuesta = self.client.get(reverse("pedido-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 1)
        self.assertEqual(respuesta.data["results"][0]["id"], self.pedido_propio.pk)

    def test_cliente_no_ve_pedido_ajeno(self):
        self._autenticar(self.cliente)
        respuesta = self.client.get(
            reverse("pedido-detail", args=[self.pedido_ajeno.pk])
        )
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)

    def test_cliente_no_cambia_estado(self):
        self._autenticar(self.cliente)
        respuesta = self.client.post(
            reverse("pedido-cambiar-estado", args=[self.pedido_propio.pk]),
            {"estado": "confirmado"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_checkout_crea_pedido_con_precio_del_catalogo(self):
        self._autenticar(self.cliente)
        respuesta = self.client.post(
            reverse("pedido-checkout"),
            {
                "items": [{"cerveza": self.cerveza.pk, "cantidad": 3}],
                "notas": "Entregar por la tarde",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data["cliente"], self.cliente_modelo.pk)
        self.assertEqual(Decimal(str(respuesta.data["total"])), Decimal("5400.00"))
        self.assertEqual(respuesta.data["cantidad_items"], 3)

        pedido = Pedido.objects.get(pk=respuesta.data["id"])
        detalle = pedido.detalles.get()
        self.assertEqual(detalle.precio_unitario, self.cerveza.precio)

    def test_checkout_sin_stock_suficiente_400(self):
        self._autenticar(self.cliente)
        respuesta = self.client.post(
            reverse("pedido-checkout"),
            {"items": [{"cerveza": self.cerveza.pk, "cantidad": 99}]},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_solo_clientes(self):
        self._autenticar(self.ventas)
        respuesta = self.client.post(
            reverse("pedido-checkout"),
            {"items": [{"cerveza": self.cerveza.pk, "cantidad": 1}]},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_cliente_no_crea_pedidos_por_crud(self):
        self._autenticar(self.cliente)
        respuesta = self.client.post(
            reverse("pedido-list"),
            {"canal": "web"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_cliente_no_agrega_detalles_por_crud(self):
        self._autenticar(self.cliente)
        respuesta = self.client.post(
            reverse("detalle-pedido-list"),
            {
                "pedido": self.pedido_propio.pk,
                "cerveza": self.cerveza.pk,
                "cantidad": 1,
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    # --- Ventas ----------------------------------------------------------

    def test_ventas_gestiona_clientes_y_pedidos(self):
        self._autenticar(self.ventas)
        self.assertEqual(
            self.client.get(reverse("cliente-list")).status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            self.client.get(reverse("pedido-list")).status_code,
            status.HTTP_200_OK,
        )

    def test_ventas_no_ve_proveedores(self):
        self._autenticar(self.ventas)
        respuesta = self.client.get(reverse("proveedor-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_ventas_no_escribe_cervezas(self):
        self._autenticar(self.ventas)
        respuesta = self.client.patch(
            reverse("cerveza-detail", args=[self.cerveza.pk]),
            {"stock": 3},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    # --- Cervecero -------------------------------------------------------

    def test_cervecero_gestiona_catalogo(self):
        self._autenticar(self.cervecero)
        self.assertEqual(
            self.client.get(reverse("proveedor-list")).status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            self.client.get(reverse("ingrediente-list")).status_code,
            status.HTTP_200_OK,
        )
        respuesta = self.client.patch(
            reverse("cerveza-detail", args=[self.cerveza.pk]),
            {"stock": 7},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_cervecero_no_ve_clientes_ni_pedidos(self):
        self._autenticar(self.cervecero)
        self.assertEqual(
            self.client.get(reverse("cliente-list")).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.get(reverse("pedido-list")).status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # --- Admin y anónimo -------------------------------------------------

    def test_admin_accede_a_todo(self):
        self._autenticar(self.admin)
        for nombre in ("proveedor-list", "cliente-list", "pedido-list"):
            with self.subTest(recurso=nombre):
                self.assertEqual(
                    self.client.get(reverse(nombre)).status_code,
                    status.HTTP_200_OK,
                )

    def test_anonimo_lee_cervezas(self):
        respuesta = self.client.get(reverse("cerveza-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_anonimo_no_ve_proveedores(self):
        respuesta = self.client.get(reverse("proveedor-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)