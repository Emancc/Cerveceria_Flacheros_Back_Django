"""Tests de ventas: pedidos, detalles y clientes."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalogo.models import Cerveza, Estilo
from apps.ventas.models import Cliente, DetallePedido, Pedido

Usuario = get_user_model()


class PedidoAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create_user(
            email="ventas@example.com",
            password="ClaveSegura123",
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
            precio=Decimal("3800.00"),
            stock=20,
            color="#e0a53c",
        )
        cls.cerveza_2 = Cerveza.objects.create(
            nombre="Pilsner Clásica",
            estilo=cls.estilo,
            graduacion=Decimal("4.80"),
            amargor=22,
            descripcion="Suave",
            precio=Decimal("2800.00"),
            stock=15,
            color="#f0d67a",
        )
        cls.cliente = Cliente.objects.create(
            nombre="Bar El Lúpulo",
            email="bar@example.com",
            tipo=Cliente.Tipo.BAR,
        )
        cls.pedido = Pedido.objects.create(
            cliente=cls.cliente,
            estado=Pedido.Estado.PENDIENTE,
            canal=Pedido.Canal.WEB,
            notas="Pedido de prueba",
        )
        DetallePedido.objects.create(
            pedido=cls.pedido,
            cerveza=cls.cerveza,
            cantidad=2,
        )
        DetallePedido.objects.create(
            pedido=cls.pedido,
            cerveza=cls.cerveza_2,
            cantidad=3,
        )
        cls.pedido.refresh_from_db()

    def _autenticar(self):
        self.client.force_authenticate(user=self.usuario)

    def test_pedidos_list_anidado(self):
        self._autenticar()
        respuesta = self.client.get(reverse("pedido-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        pedido = respuesta.data["results"][0]
        self.assertIsInstance(pedido["cliente"], dict)
        self.assertIsInstance(pedido["detalles"], list)
        self.assertEqual(len(pedido["detalles"]), 2)

    def test_pedido_detail_plano(self):
        self._autenticar()
        respuesta = self.client.get(
            reverse("pedido-detail", args=[self.pedido.pk])
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIsInstance(respuesta.data["cliente"], int)
        self.assertNotIn("detalles", respuesta.data)
        self.assertEqual(respuesta.data["detalles_count"], 2)

    def test_cambiar_estado_valido(self):
        self._autenticar()
        respuesta = self.client.post(
            reverse("pedido-cambiar-estado", args=[self.pedido.pk]),
            {"estado": "confirmado"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["estado"], "confirmado")
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, Pedido.Estado.CONFIRMADO)

    def test_cambiar_estado_invalido(self):
        self._autenticar()
        respuesta = self.client.post(
            reverse("pedido-cambiar-estado", args=[self.pedido.pk]),
            {"estado": "inventado"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(respuesta.data, {"estado": ["Estado inválido."]})

    def test_total_se_recalcula_al_crear_detalle(self):
        pedido = Pedido.objects.create(cliente=self.cliente)
        pedido.refresh_from_db()
        self.assertEqual(pedido.total, Decimal("0.00"))

        self._autenticar()
        respuesta = self.client.post(
            reverse("detalle-pedido-list"),
            {
                "pedido": pedido.pk,
                "cerveza": self.cerveza.pk,
                "cantidad": 4,
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

        pedido.refresh_from_db()
        self.assertEqual(pedido.total, Decimal("4") * self.cerveza.precio)
        self.assertEqual(pedido.cantidad_items, 4)

    def test_clientes_sin_token_401(self):
        respuesta = self.client.get(reverse("cliente-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_clientes_con_token_200(self):
        self._autenticar()
        respuesta = self.client.get(reverse("cliente-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 1)
