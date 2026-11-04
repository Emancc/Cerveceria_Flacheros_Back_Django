"""Tests de subida de imágenes de cerveza a Cloudinary."""

from io import BytesIO
from unittest.mock import patch

import cloudinary
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalogo.imagenes import configurar_cloudinary
from apps.catalogo.models import Cerveza, Estilo

Usuario = get_user_model()

URL_CLOUDINARY = (
    "https://res.cloudinary.com/demo/image/upload/v123/"
    "cervezas/2026/11/foto.png"
)


def _imagen_bytes():
    """Genera una imagen PNG real en memoria."""
    buffer = BytesIO()
    Image.new("RGB", (300, 300), (200, 120, 40)).save(buffer, format="PNG")
    return buffer.getvalue()


class ConfiguracionCloudinaryTests(SimpleTestCase):
    def tearDown(self):
        cloudinary.reset_config()

    @override_settings(CLOUDINARY_URL="cloudinary://123456789:secreto@demo")
    def test_configura_credenciales_desde_url(self):
        configurar_cloudinary()

        config = cloudinary.config()
        self.assertEqual(config.cloud_name, "demo")
        self.assertEqual(config.api_key, "123456789")
        self.assertEqual(config.api_secret, "secreto")
        self.assertTrue(config.secure)

    @override_settings(CLOUDINARY_URL="https://demo")
    def test_url_invalida_falla(self):
        with self.assertRaises(ImproperlyConfigured):
            configurar_cloudinary()


@override_settings(
    USE_CLOUDINARY=True,
    CLOUDINARY_URL="cloudinary://123456789:secreto@demo",
)
class ImagenesCloudinaryAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = Usuario.objects.create_user(
            email="staff-cloudinary@example.com",
            password="ClaveSegura123",
            is_staff=True,
        )
        cls.estilo = Estilo.objects.create(
            nombre="IPA",
            slug="ipa",
            descripcion="Lúpulo intenso",
            color="#e0a53c",
        )

    def _subir_png(self):
        self.client.force_authenticate(user=self.staff)
        archivo = SimpleUploadedFile(
            "cerveza.png",
            _imagen_bytes(),
            content_type="image/png",
        )
        return self.client.post(
            reverse("cerveza-imagenes"),
            {"imagen": archivo},
            format="multipart",
        )

    @patch("apps.catalogo.views.subir_imagen")
    def test_subida_usa_cloudinary_y_devuelve_url(self, subir_mock):
        subir_mock.return_value = {"secure_url": URL_CLOUDINARY}

        respuesta = self._subir_png()

        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data["ruta"], "")
        self.assertEqual(respuesta.data["url"], URL_CLOUDINARY)
        subir_mock.assert_called_once()
        _, carpeta = subir_mock.call_args.args
        self.assertTrue(carpeta.startswith("cervezas/"))

    @patch("apps.catalogo.views.subir_imagen")
    def test_error_de_cloudinary_devuelve_502(self, subir_mock):
        subir_mock.side_effect = RuntimeError("Cloudinary caído")

        with self.assertLogs("apps.catalogo.views", level="ERROR"):
            respuesta = self._subir_png()

        self.assertEqual(respuesta.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("imagen", respuesta.data)

    def test_crear_cerveza_con_url_de_cloudinary(self):
        self.client.force_authenticate(user=self.staff)
        respuesta = self.client.post(
            reverse("cerveza-list"),
            {
                "nombre": "Cerveza Cloudinary",
                "estilo": "ipa",
                "graduacion": "6.50",
                "amargor": 55,
                "descripcion": "Imagen persistida en Cloudinary",
                "precio": "3800.00",
                "stock": 12,
                "imagen": URL_CLOUDINARY,
            },
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        cerveza = Cerveza.objects.get(nombre="Cerveza Cloudinary")
        self.assertEqual(cerveza.imagen, URL_CLOUDINARY)
        self.assertFalse(cerveza.imagen_archivo)
        self.assertEqual(respuesta.data["imagen_url"], URL_CLOUDINARY)
