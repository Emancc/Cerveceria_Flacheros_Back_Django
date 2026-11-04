"""Tests del endpoint de cervezas."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Avg, Sum
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalogo.models import Cerveza, Estilo
from apps.cuentas.models import PerfilUsuario

Usuario = get_user_model()


class CervezaAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create_user(
            email="cervezas@example.com",
            password="ClaveSegura123",
        )
        PerfilUsuario.objects.update_or_create(
            usuario=cls.usuario,
            defaults={"rol": PerfilUsuario.Rol.CERVECERO},
        )
        cls.ipa = Estilo.objects.create(
            nombre="IPA",
            slug="ipa",
            descripcion="Lúpulo intenso",
            color="#e0a53c",
        )
        cls.pilsner = Estilo.objects.create(
            nombre="Pilsner",
            slug="pilsner",
            descripcion="Dorada y suave",
            color="#f0d67a",
        )
        cls.cerveza_ipa = Cerveza.objects.create(
            nombre="Lúpulo del Valle",
            estilo=cls.ipa,
            graduacion=Decimal("6.50"),
            amargor=55,
            descripcion="Explosión cítrica",
            precio=Decimal("3800.00"),
            stock=20,
            imagen="https://example.com/ipa.jpg",
            color="#e0a53c",
        )
        cls.cerveza_ipa_2 = Cerveza.objects.create(
            nombre="IPA de la Casa",
            estilo=cls.ipa,
            graduacion=Decimal("5.80"),
            amargor=45,
            descripcion="IPA equilibrada",
            precio=Decimal("3200.00"),
            stock=3,
            color="#e0a53c",
        )
        cls.cerveza_pils = Cerveza.objects.create(
            nombre="Pilsner Clásica",
            estilo=cls.pilsner,
            graduacion=Decimal("4.80"),
            amargor=22,
            descripcion="Ligera y refrescante",
            precio=Decimal("2800.00"),
            stock=0,
            color="#f0d67a",
        )
        cls.cerveza_pils_2 = Cerveza.objects.create(
            nombre="Pilsner del Sur",
            estilo=cls.pilsner,
            graduacion=Decimal("4.60"),
            amargor=20,
            descripcion="Final seco",
            precio=Decimal("2600.00"),
            stock=12,
            color="#f0d67a",
        )

    def _autenticar(self):
        self.client.force_authenticate(user=self.usuario)

    def test_list_anonimo_paginado(self):
        respuesta = self.client.get(reverse("cerveza-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(respuesta.data.keys()),
            {"count", "next", "previous", "results"},
        )
        self.assertEqual(respuesta.data["count"], 4)

    def test_list_estilo_string_y_detalle_anidado(self):
        respuesta = self.client.get(reverse("cerveza-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        cerveza = respuesta.data["results"][0]
        self.assertIsInstance(cerveza["estilo"], str)
        self.assertIsInstance(cerveza["estilo_detalle"], dict)
        self.assertEqual(cerveza["estilo"], cerveza["estilo_detalle"]["slug"])
        self.assertIn("slug", cerveza["estilo_detalle"])
        self.assertIn("nombre", cerveza["estilo_detalle"])

    def test_detail_estilo_string(self):
        respuesta = self.client.get(
            reverse("cerveza-detail", args=[self.cerveza_ipa.pk])
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["estilo"], "ipa")
        self.assertIsInstance(respuesta.data["estilo"], str)

    def test_post_anonimo_401(self):
        respuesta = self.client.post(
            reverse("cerveza-list"),
            {
                "nombre": "Nueva IPA",
                "estilo": "ipa",
                "graduacion": "6.00",
                "amargor": 50,
                "descripcion": "Prueba",
                "precio": "3500.00",
                "stock": 10,
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_autenticado_201(self):
        self._autenticar()
        respuesta = self.client.post(
            reverse("cerveza-list"),
            {
                "nombre": "Nueva IPA",
                "estilo": "ipa",
                "graduacion": "6.00",
                "amargor": 50,
                "descripcion": "Prueba",
                "precio": "3500.00",
                "stock": 10,
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data["estilo"], "ipa")
        self.assertTrue(Cerveza.objects.filter(nombre="Nueva IPA").exists())

    def test_post_y_patch_con_color_vacio_del_front(self):
        self._autenticar()
        crear = self.client.post(
            reverse("cerveza-list"),
            {
                "nombre": "Cerveza del Front",
                "estilo": "pilsner",
                "graduacion": "4.50",
                "amargor": 18,
                "descripcion": "Payload real del frontend",
                "precio": "2900.00",
                "stock": 8,
                "imagen": "",
                "color": "",
            },
            format="json",
        )
        self.assertEqual(crear.status_code, status.HTTP_201_CREATED)
        self.assertEqual(crear.data["color"], "")
        self.assertEqual(crear.data["imagen"], "")

        actualizar = self.client.patch(
            reverse("cerveza-detail", args=[crear.data["id"]]),
            {"color": ""},
            format="json",
        )
        self.assertEqual(actualizar.status_code, status.HTTP_200_OK)
        self.assertEqual(actualizar.data["color"], "")

    def test_patch_200(self):
        self._autenticar()
        respuesta = self.client.patch(
            reverse("cerveza-detail", args=[self.cerveza_ipa.pk]),
            {"precio": "4100.00"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.cerveza_ipa.refresh_from_db()
        self.assertEqual(self.cerveza_ipa.precio, Decimal("4100.00"))

    def test_delete_204(self):
        self._autenticar()
        respuesta = self.client.delete(
            reverse("cerveza-detail", args=[self.cerveza_pils_2.pk])
        )
        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Cerveza.objects.filter(pk=self.cerveza_pils_2.pk).exists())

    def test_search(self):
        respuesta = self.client.get(reverse("cerveza-list"), {"search": "Valle"})
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 1)
        self.assertEqual(respuesta.data["results"][0]["nombre"], "Lúpulo del Valle")

    def test_filtro_estilo(self):
        respuesta = self.client.get(reverse("cerveza-list"), {"estilo": "ipa"})
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 2)
        for cerveza in respuesta.data["results"]:
            self.assertEqual(cerveza["estilo"], "ipa")

    def test_ordering_precio(self):
        respuesta = self.client.get(reverse("cerveza-list"), {"ordering": "-precio"})
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        precios = [Decimal(cerveza["precio"]) for cerveza in respuesta.data["results"]]
        self.assertEqual(precios, sorted(precios, reverse=True))

    def test_page_size(self):
        respuesta = self.client.get(reverse("cerveza-list"), {"page_size": 2})
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 4)
        self.assertEqual(len(respuesta.data["results"]), 2)
        self.assertIsNotNone(respuesta.data["next"])

    def test_estadisticas_requiere_auth(self):
        respuesta = self.client.get(reverse("cerveza-estadisticas"))
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_estadisticas_valores(self):
        self._autenticar()
        respuesta = self.client.get(reverse("cerveza-estadisticas"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(respuesta.data.keys()),
            {"total", "estilos", "stockTotal", "precioPromedio"},
        )
        total = Cerveza.objects.count()
        estilos = Cerveza.objects.values("estilo").distinct().count()
        stock = Cerveza.objects.aggregate(total=Sum("stock"))["total"] or 0
        promedio = round(
            float(Cerveza.objects.aggregate(p=Avg("precio"))["p"] or 0),
            2,
        )
        self.assertEqual(respuesta.data["total"], total)
        self.assertEqual(respuesta.data["estilos"], estilos)
        self.assertEqual(respuesta.data["stockTotal"], stock)
        self.assertAlmostEqual(respuesta.data["precioPromedio"], promedio, places=2)

    def test_bajo_stock_filtra_y_pagina(self):
        self._autenticar()
        respuesta = self.client.get(
            reverse("cerveza-bajo-stock"),
            {"umbral": 5, "page_size": 1},
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 2)
        self.assertEqual(len(respuesta.data["results"]), 1)
        for cerveza in respuesta.data["results"]:
            self.assertLess(cerveza["stock"], 5)

    def test_bajo_stock_umbral_invalido(self):
        self._autenticar()
        respuesta = self.client.get(
            reverse("cerveza-bajo-stock"),
            {"umbral": "abc"},
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("umbral", respuesta.data)
