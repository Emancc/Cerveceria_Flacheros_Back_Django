"""Tests del catálogo y smoke tests del admin."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalogo.models import (
    Cerveza,
    Estilo,
    Ingrediente,
    Lote,
    Proveedor,
    Receta,
    RecetaIngrediente,
)
from apps.cuentas.models import PerfilUsuario
from apps.ventas.models import Cliente, Resena

Usuario = get_user_model()


class CatalogoAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create_user(
            email="catalogo@example.com",
            password="ClaveSegura123",
        )
        PerfilUsuario.objects.update_or_create(
            usuario=cls.usuario,
            defaults={"rol": PerfilUsuario.Rol.ADMIN},
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
        cls.proveedor = Proveedor.objects.create(
            nombre="Lúpulos del Valle",
            contacto="Martín Quiroga",
            email="pedidos@lupulosdelvalle.com.ar",
            telefono="0299-442-8890",
            cuit="30-70987654-3",
            direccion="Ruta 22 Km 8, Neuquén",
        )
        cls.ingrediente_bajo = Ingrediente.objects.create(
            nombre="Lúpulo Citra",
            tipo=Ingrediente.Tipo.LUPULO,
            unidad=Ingrediente.Unidad.G,
            stock=Decimal("250.00"),
            stock_minimo=Decimal("400.00"),
            proveedor=cls.proveedor,
        )
        cls.ingrediente_ok = Ingrediente.objects.create(
            nombre="Malta Pilsner",
            tipo=Ingrediente.Tipo.MALTA,
            unidad=Ingrediente.Unidad.KG,
            stock=Decimal("120.00"),
            stock_minimo=Decimal("50.00"),
            proveedor=cls.proveedor,
        )
        cls.receta = Receta.objects.create(
            cerveza=cls.cerveza,
            nombre="Receta Lúpulo del Valle",
            version=1,
            volumen_litros=Decimal("30.00"),
            notas="Receta base",
        )
        RecetaIngrediente.objects.create(
            receta=cls.receta,
            ingrediente=cls.ingrediente_ok,
            cantidad=Decimal("4.50"),
            unidad=Ingrediente.Unidad.KG,
        )
        RecetaIngrediente.objects.create(
            receta=cls.receta,
            ingrediente=cls.ingrediente_bajo,
            cantidad=Decimal("120.00"),
            unidad=Ingrediente.Unidad.G,
        )
        cls.lote = Lote.objects.create(
            cerveza=cls.cerveza,
            receta=cls.receta,
            codigo="LF-2026-001",
            fecha_elaboracion=date(2026, 1, 15),
            volumen_litros=Decimal("30.00"),
            estado=Lote.Estado.FERMENTANDO,
        )
        cls.cliente = Cliente.objects.create(
            nombre="Bar El Lúpulo",
            email="bar@example.com",
            tipo=Cliente.Tipo.BAR,
        )

    def _autenticar(self):
        self.client.force_authenticate(user=self.usuario)

    def test_estilos_publico(self):
        respuesta = self.client.get(reverse("estilo-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 1)

    def test_proveedores_sin_token_401(self):
        respuesta = self.client.get(reverse("proveedor-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_proveedores_con_token_200(self):
        self._autenticar()
        respuesta = self.client.get(reverse("proveedor-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 1)

    def test_ingredientes_filtro_bajo_minimo(self):
        self._autenticar()
        respuesta = self.client.get(
            reverse("ingrediente-list"),
            {"bajo_minimo": "true"},
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 1)
        self.assertEqual(
            respuesta.data["results"][0]["nombre"],
            "Lúpulo Citra",
        )
        self.assertTrue(respuesta.data["results"][0]["bajo_minimo"])

    def test_recetas_list_anidado(self):
        self._autenticar()
        respuesta = self.client.get(reverse("receta-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        receta = respuesta.data["results"][0]
        self.assertIsInstance(receta["cerveza"], dict)
        self.assertEqual(receta["cerveza"]["estilo"], "ipa")
        self.assertIsInstance(receta["ingredientes"], list)
        self.assertEqual(len(receta["ingredientes"]), 2)

    def test_receta_detail_plano(self):
        self._autenticar()
        respuesta = self.client.get(
            reverse("receta-detail", args=[self.receta.pk])
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIsInstance(respuesta.data["cerveza"], int)
        self.assertNotIn("ingredientes", respuesta.data)

    def test_lotes_list_anidado(self):
        self._autenticar()
        respuesta = self.client.get(reverse("lote-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        lote = respuesta.data["results"][0]
        self.assertIsInstance(lote["cerveza"], dict)
        self.assertIsInstance(lote["receta"], dict)
        self.assertEqual(lote["codigo"], "LF-2026-001")

    def test_finalizar_lote(self):
        self._autenticar()
        respuesta = self.client.post(
            reverse("lote-finalizar", args=[self.lote.pk])
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["estado"], "envasado")
        self.assertIsNotNone(respuesta.data["fecha_vencimiento"])
        self.lote.refresh_from_db()
        self.assertEqual(self.lote.estado, Lote.Estado.ENVASADO)
        self.assertIsNotNone(self.lote.fecha_vencimiento)

    def test_resenas_crud_basico(self):
        self._autenticar()
        crear = self.client.post(
            reverse("resena-list"),
            {
                "cerveza": self.cerveza.pk,
                "cliente": self.cliente.pk,
                "puntuacion": 5,
                "comentario": "Excelente",
            },
            format="json",
        )
        self.assertEqual(crear.status_code, status.HTTP_201_CREATED)
        resena_id = crear.data["id"]

        detalle = self.client.get(
            reverse("resena-detail", args=[resena_id])
        )
        self.assertEqual(detalle.status_code, status.HTTP_200_OK)
        self.assertEqual(detalle.data["puntuacion"], 5)

        actualizar = self.client.patch(
            reverse("resena-detail", args=[resena_id]),
            {"puntuacion": 4},
            format="json",
        )
        self.assertEqual(actualizar.status_code, status.HTTP_200_OK)
        self.assertEqual(actualizar.data["puntuacion"], 4)

        borrar = self.client.delete(
            reverse("resena-detail", args=[resena_id])
        )
        self.assertEqual(borrar.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Resena.objects.filter(pk=resena_id).exists())


class AdminSmokeTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = Usuario.objects.create_superuser(
            email="admin-smoke@example.com",
            password="ClaveSegura123",
        )

    def setUp(self):
        self.client.force_login(self.admin)

    def test_admin_index_y_changelists(self):
        urls = [
            reverse("admin:index"),
            reverse("admin:catalogo_estilo_changelist"),
            reverse("admin:catalogo_cerveza_changelist"),
            reverse("admin:catalogo_proveedor_changelist"),
            reverse("admin:catalogo_ingrediente_changelist"),
            reverse("admin:catalogo_receta_changelist"),
            reverse("admin:catalogo_recetaingrediente_changelist"),
            reverse("admin:catalogo_lote_changelist"),
            reverse("admin:ventas_cliente_changelist"),
            reverse("admin:ventas_pedido_changelist"),
            reverse("admin:ventas_detallepedido_changelist"),
            reverse("admin:ventas_resena_changelist"),
        ]
        for url in urls:
            with self.subTest(url=url):
                respuesta = self.client.get(url)
                self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
