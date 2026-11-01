"""Tests de autenticación y perfiles."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

Usuario = get_user_model()


class AutenticacionTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create_user(
            email="vecino@example.com",
            password="ClaveSegura123",
            first_name="Vecino",
            last_name="Flachero",
        )
        cls.otro = Usuario.objects.create_user(
            email="otro@example.com",
            password="ClaveSegura123",
        )
        cls.admin = Usuario.objects.create_superuser(
            email="admin-test@example.com",
            password="ClaveSegura123",
        )

    def _obtener_token(self, email="vecino@example.com", password="ClaveSegura123"):
        return self.client.post(
            reverse("token_obtain_pair"),
            {"email": email, "password": password},
            format="json",
        )

    def test_token_con_email_ok(self):
        respuesta = self._obtener_token()
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn("access", respuesta.data)
        self.assertIn("refresh", respuesta.data)

    def test_token_password_incorrecta(self):
        respuesta = self._obtener_token(password="incorrecta")
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_sin_token(self):
        respuesta = self.client.get(reverse("me"))
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_con_token(self):
        access = self._obtener_token().data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        respuesta = self.client.get(reverse("me"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(set(respuesta.data.keys()), {"usuario", "perfil"})
        self.assertEqual(respuesta.data["usuario"]["email"], self.usuario.email)
        self.assertEqual(
            respuesta.data["perfil"]["usuario"]["email"],
            self.usuario.email,
        )

    def test_usuario_comun_no_ve_perfiles_ajenos(self):
        self.client.force_authenticate(user=self.usuario)
        listado = self.client.get(reverse("perfil-list"))
        self.assertEqual(listado.status_code, status.HTTP_200_OK)
        self.assertEqual(listado.data["count"], 1)
        self.assertEqual(
            listado.data["results"][0]["usuario"]["email"],
            self.usuario.email,
        )
        detalle = self.client.get(
            reverse("perfil-detail", args=[self.otro.perfil.pk])
        )
        self.assertEqual(detalle.status_code, status.HTTP_404_NOT_FOUND)

    def test_staff_ve_todos_los_perfiles(self):
        self.client.force_authenticate(user=self.admin)
        listado = self.client.get(reverse("perfil-list"))
        self.assertEqual(listado.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(listado.data["count"], 3)
