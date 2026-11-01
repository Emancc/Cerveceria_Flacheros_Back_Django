"""Tests de subida y uso de imágenes de cerveza."""

import shutil
import tempfile
from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalogo.models import Cerveza, Estilo

Usuario = get_user_model()


def _imagen_bytes(ancho=300, alto=300, formato="PNG"):
    """Genera una imagen real en memoria."""
    buffer = BytesIO()
    Image.new("RGB", (ancho, alto), (200, 120, 40)).save(buffer, format=formato)
    return buffer.getvalue()


class ImagenesCervezaAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create_user(
            email="imagenes@example.com",
            password="ClaveSegura123",
        )
        cls.staff = Usuario.objects.create_user(
            email="staff-imagenes@example.com",
            password="ClaveSegura123",
            is_staff=True,
        )
        cls.estilo = Estilo.objects.create(
            nombre="IPA",
            slug="ipa",
            descripcion="Lúpulo intenso",
            color="#e0a53c",
        )
        cls.cerveza_externa = Cerveza.objects.create(
            nombre="Cerveza con URL",
            estilo=cls.estilo,
            graduacion=Decimal("6.50"),
            amargor=55,
            descripcion="Imagen externa",
            precio=Decimal("3800.00"),
            stock=20,
            imagen="https://example.com/ipa.jpg",
            color="#e0a53c",
        )

    def setUp(self):
        self.media_root = tempfile.mkdtemp(prefix="cervezas-test-media-")
        self._override = override_settings(MEDIA_ROOT=self.media_root)
        self._override.enable()
        self.addCleanup(self._override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, ignore_errors=True)

    def _autenticar(self, usuario=None):
        self.client.force_authenticate(user=usuario or self.usuario)

    def _subir_png(self, ancho=300, alto=300):
        self._autenticar(self.staff)
        archivo = SimpleUploadedFile(
            "cerveza.png",
            _imagen_bytes(ancho, alto),
            content_type="image/png",
        )
        return self.client.post(
            reverse("cerveza-imagenes"),
            {"imagen": archivo},
            format="multipart",
        )

    def _crear_archivo(self, nombre="cervezas/2026/11/prueba.png"):
        return default_storage.save(nombre, ContentFile(_imagen_bytes()))

    def test_subida_valida_201_y_archivo_en_storage(self):
        respuesta = self._subir_png()

        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertIn("ruta", respuesta.data)
        self.assertIn("url", respuesta.data)
        self.assertTrue(respuesta.data["ruta"].startswith("cervezas/"))
        self.assertTrue(respuesta.data["ruta"].endswith(".png"))
        self.assertTrue(default_storage.exists(respuesta.data["ruta"]))
        self.assertIn("/media/", respuesta.data["url"])

    def test_rechazo_formato_gif(self):
        self._autenticar(self.staff)
        archivo = SimpleUploadedFile(
            "animacion.gif",
            _imagen_bytes(formato="GIF"),
            content_type="image/gif",
        )
        respuesta = self.client.post(
            reverse("cerveza-imagenes"),
            {"imagen": archivo},
            format="multipart",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("imagen", respuesta.data)

    def test_rechazo_archivo_que_no_es_imagen(self):
        self._autenticar(self.staff)
        archivo = SimpleUploadedFile(
            "texto.png",
            b"esto no es una imagen",
            content_type="image/png",
        )
        respuesta = self.client.post(
            reverse("cerveza-imagenes"),
            {"imagen": archivo},
            format="multipart",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("imagen", respuesta.data)

    def test_rechazo_por_peso_mayor_a_5_mb(self):
        self._autenticar(self.staff)
        archivo = SimpleUploadedFile(
            "grande.png",
            b"0" * (5 * 1024 * 1024 + 1),
            content_type="image/png",
        )
        respuesta = self.client.post(
            reverse("cerveza-imagenes"),
            {"imagen": archivo},
            format="multipart",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("imagen", respuesta.data)
        self.assertIn("5 MB", respuesta.data["imagen"][0])

    def test_rechazo_por_dimensiones_menores_a_200(self):
        respuesta = self._subir_png(ancho=100, alto=100)

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("imagen", respuesta.data)

    def test_subida_sin_token_401(self):
        archivo = SimpleUploadedFile(
            "cerveza.png",
            _imagen_bytes(),
            content_type="image/png",
        )
        respuesta = self.client.post(
            reverse("cerveza-imagenes"),
            {"imagen": archivo},
            format="multipart",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subida_usuario_no_staff_403(self):
        self._autenticar(self.usuario)
        archivo = SimpleUploadedFile(
            "cerveza.png",
            _imagen_bytes(),
            content_type="image/png",
        )
        respuesta = self.client.post(
            reverse("cerveza-imagenes"),
            {"imagen": archivo},
            format="multipart",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            respuesta.data["detail"],
            "No tenés permisos para subir imágenes.",
        )

    def test_imagen_url_en_detalle_y_listado(self):
        ruta = self._crear_archivo()
        self.cerveza_externa.imagen_archivo = ruta
        self.cerveza_externa.save(update_fields=["imagen_archivo"])

        detalle = self.client.get(
            reverse("cerveza-detail", args=[self.cerveza_externa.pk])
        )
        self.assertEqual(detalle.status_code, status.HTTP_200_OK)
        self.assertTrue(detalle.data["imagen_url"].startswith("http://testserver/"))
        self.assertIn(ruta, detalle.data["imagen_url"])

        listado = self.client.get(reverse("cerveza-list"))
        self.assertEqual(listado.status_code, status.HTTP_200_OK)
        cerveza = next(
            item
            for item in listado.data["results"]
            if item["id"] == self.cerveza_externa.pk
        )
        self.assertIn(ruta, cerveza["imagen_url"])

    def test_imagen_url_usa_url_externa_sin_archivo(self):
        respuesta = self.client.get(
            reverse("cerveza-detail", args=[self.cerveza_externa.pk])
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(
            respuesta.data["imagen_url"],
            "https://example.com/ipa.jpg",
        )

        listado = self.client.get(reverse("cerveza-list"))
        self.assertEqual(listado.status_code, status.HTTP_200_OK)
        cerveza = next(
            item
            for item in listado.data["results"]
            if item["id"] == self.cerveza_externa.pk
        )
        self.assertEqual(cerveza["imagen_url"], "https://example.com/ipa.jpg")

    def test_detalle_devuelve_imagen_archivo_relativa_y_url_absoluta(self):
        ruta = self._crear_archivo()
        self.cerveza_externa.imagen_archivo = ruta
        self.cerveza_externa.save(update_fields=["imagen_archivo"])

        respuesta = self.client.get(
            reverse("cerveza-detail", args=[self.cerveza_externa.pk])
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["imagen_archivo"], ruta)
        self.assertTrue(respuesta.data["imagen_url"].startswith("http://testserver/"))
        self.assertIn(ruta, respuesta.data["imagen_url"])

    def test_patch_reenviando_imagen_archivo_conserva_imagen(self):
        ruta = self._crear_archivo()
        self.cerveza_externa.imagen_archivo = ruta
        self.cerveza_externa.save(update_fields=["imagen_archivo"])
        self.assertTrue(default_storage.exists(ruta))

        detalle = self.client.get(
            reverse("cerveza-detail", args=[self.cerveza_externa.pk])
        )
        self.assertEqual(detalle.status_code, status.HTTP_200_OK)
        imagen_url_original = detalle.data["imagen_url"]

        self._autenticar()
        respuesta = self.client.patch(
            reverse("cerveza-detail", args=[self.cerveza_externa.pk]),
            {
                "nombre": self.cerveza_externa.nombre,
                "imagen_archivo": detalle.data["imagen_archivo"],
            },
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["imagen_archivo"], ruta)
        self.assertEqual(respuesta.data["imagen_url"], imagen_url_original)
        self.assertTrue(default_storage.exists(ruta))
        self.cerveza_externa.refresh_from_db()
        self.assertEqual(self.cerveza_externa.imagen_archivo.name, ruta)

    def test_patch_con_imagen_archivo_vacio_borra_imagen(self):
        ruta = self._crear_archivo()
        self.cerveza_externa.imagen_archivo = ruta
        self.cerveza_externa.save(update_fields=["imagen_archivo"])
        self.assertTrue(default_storage.exists(ruta))

        self._autenticar()
        respuesta = self.client.patch(
            reverse("cerveza-detail", args=[self.cerveza_externa.pk]),
            {"imagen_archivo": ""},
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["imagen_archivo"], "")
        self.cerveza_externa.refresh_from_db()
        self.assertFalse(self.cerveza_externa.imagen_archivo)
        self.assertFalse(default_storage.exists(ruta))
        self.assertEqual(
            respuesta.data["imagen_url"],
            "https://example.com/ipa.jpg",
        )

    def test_crear_cerveza_con_ruta_existente(self):
        subida = self._subir_png()
        self.assertEqual(subida.status_code, status.HTTP_201_CREATED)
        ruta = subida.data["ruta"]

        respuesta = self.client.post(
            reverse("cerveza-list"),
            {
                "nombre": "Cerveza con archivo",
                "estilo": "ipa",
                "graduacion": "5.50",
                "amargor": 40,
                "descripcion": "Con imagen subida",
                "precio": "3000.00",
                "stock": 5,
                "imagen_archivo": ruta,
            },
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        cerveza = Cerveza.objects.get(nombre="Cerveza con archivo")
        self.assertEqual(cerveza.imagen_archivo.name, ruta)
        self.assertIn(ruta, respuesta.data["imagen_url"])

    def test_crear_cerveza_con_ruta_inexistente_400(self):
        self._autenticar()
        respuesta = self.client.post(
            reverse("cerveza-list"),
            {
                "nombre": "Cerveza sin archivo",
                "estilo": "ipa",
                "graduacion": "5.50",
                "amargor": 40,
                "descripcion": "Ruta inválida",
                "precio": "3000.00",
                "stock": 5,
                "imagen_archivo": "cervezas/2026/11/no-existe.png",
            },
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("imagen_archivo", respuesta.data)
        self.assertFalse(Cerveza.objects.filter(nombre="Cerveza sin archivo").exists())

    def test_eliminar_cerveza_borra_archivo_fisico(self):
        ruta = self._crear_archivo()
        self.cerveza_externa.imagen_archivo = ruta
        self.cerveza_externa.save(update_fields=["imagen_archivo"])
        self.assertTrue(default_storage.exists(ruta))

        self._autenticar()
        respuesta = self.client.delete(
            reverse("cerveza-detail", args=[self.cerveza_externa.pk])
        )

        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(default_storage.exists(ruta))

    def test_actualizar_imagen_borra_archivo_anterior(self):
        ruta_anterior = self._crear_archivo("cervezas/2026/11/anterior.png")
        ruta_nueva = self._crear_archivo("cervezas/2026/11/nueva.png")
        self.cerveza_externa.imagen_archivo = ruta_anterior
        self.cerveza_externa.save(update_fields=["imagen_archivo"])

        self._autenticar()
        respuesta = self.client.patch(
            reverse("cerveza-detail", args=[self.cerveza_externa.pk]),
            {"imagen_archivo": ruta_nueva},
            format="json",
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertFalse(default_storage.exists(ruta_anterior))
        self.assertTrue(default_storage.exists(ruta_nueva))
