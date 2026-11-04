"""Migra imágenes locales de cervezas a Cloudinary."""

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from apps.catalogo.imagenes import cloudinary_activo, subir_imagen
from apps.catalogo.models import Cerveza


class Command(BaseCommand):
    help = (
        "Sube a Cloudinary las imágenes locales de las cervezas y limpia las "
        "referencias a archivos que ya no existen. Sin --apply solo muestra "
        "lo que haría."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Aplica los cambios. Sin esta opción el comando es un dry-run.",
        )

    def handle(self, *args, **options):
        if not cloudinary_activo():
            raise CommandError(
                "Cloudinary no está habilitado. Configurá USE_CLOUDINARY=true "
                "y CLOUDINARY_URL antes de ejecutar este comando."
            )
        if not getattr(settings, "CLOUDINARY_URL", ""):
            raise CommandError("Falta la variable de entorno CLOUDINARY_URL.")

        aplicar = options["apply"]
        cervezas = Cerveza.objects.exclude(imagen_archivo="").order_by("pk")
        por_subir = 0
        por_limpiar = 0
        subidas = 0
        limpiadas = 0
        errores = 0

        for cerveza in cervezas:
            nombre = cerveza.imagen_archivo.name
            if not default_storage.exists(nombre):
                por_limpiar += 1
                self.stdout.write(
                    f"[limpiar] {cerveza.pk} {cerveza.nombre}: "
                    f"{nombre} no existe"
                )
                if aplicar:
                    cerveza.imagen_archivo = ""
                    cerveza.save(
                        update_fields=["imagen_archivo", "actualizado_en"]
                    )
                    limpiadas += 1
                continue

            por_subir += 1
            self.stdout.write(
                f"[subir] {cerveza.pk} {cerveza.nombre}: {nombre}"
            )
            if not aplicar:
                continue

            try:
                with default_storage.open(nombre, "rb") as archivo:
                    resultado = subir_imagen(archivo, "cervezas/migradas")
            except Exception as exc:  # noqa: BLE001
                errores += 1
                self.stderr.write(
                    f"[error] {cerveza.pk} {cerveza.nombre}: {exc}"
                )
                continue

            cerveza.imagen = resultado["secure_url"]
            cerveza.imagen_archivo = ""
            cerveza.save(
                update_fields=["imagen", "imagen_archivo", "actualizado_en"]
            )
            subidas += 1

        if aplicar:
            resumen = (
                f"Aplicado: {subidas} imágenes subidas, "
                f"{limpiadas} referencias limpiadas, {errores} errores."
            )
        else:
            resumen = (
                f"Dry-run: {por_subir} imágenes para subir, "
                f"{por_limpiar} referencias para limpiar. "
                "Ejecutá con --apply para aplicar los cambios."
            )
        self.stdout.write(self.style.SUCCESS(resumen))
