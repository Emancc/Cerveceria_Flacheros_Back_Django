# syntax=docker/dockerfile:1

FROM python:3.12-slim

# uv desde la imagen oficial.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

# Primero las dependencias para aprovechar la caché de capas.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev

ENV PATH="/opt/venv/bin:$PATH"

COPY . .

ENV DJANGO_SETTINGS_MODULE=config.settings.prod

RUN chmod +x /app/docker/entrypoint.sh

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
