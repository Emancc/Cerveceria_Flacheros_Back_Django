# Cervecería Los Flacheros — Backend Django

Backend del sistema de gestión de **Cervecería Los Flacheros**, una cervecería artesanal de Córdoba. Expone una API REST para el catálogo público y para la administración de producción, ventas, clientes y usuarios.

La API está preparada para integrarse con el frontend desarrollado en Next.js e incluye autenticación JWT y por sesión, paginación, filtros, búsqueda, ordenamiento y documentación OpenAPI.

## Integrantes

- Emanuel Cepeda Caceres
- Federico Ezequiel Arballo

## Proyecto publicado

El backend se encuentra desplegado en Render. Desde la instancia publicada se puede acceder a la API y a sus herramientas de documentación.

- **Backend:** https://cerveceria-flacheros-back-django-1.onrender.com/
- **API:** https://cerveceria-flacheros-back-django-1.onrender.com/api/
- **Swagger UI:** https://cerveceria-flacheros-back-django-1.onrender.com/api/docs/
- **OpenAPI:** https://cerveceria-flacheros-back-django-1.onrender.com/api/schema/
- **ReDoc:** https://cerveceria-flacheros-back-django-1.onrender.com/api/redoc/
- **Panel de administración:** https://cerveceria-flacheros-back-django-1.onrender.com/admin/
- **Frontend:** https://cervecerialf.vercel.app/
- **Repositorio:** https://github.com/Emancc/Cerveceria_Flacheros_Back_Django


## Tecnologías

| Tecnología | Versión | Uso |
|---|---:|---|
| Python | 3.12 | Lenguaje |
| Django | 6.1.2 | Framework web |
| Django REST Framework | 3.18.3 | API REST |
| SimpleJWT | 5.5.1 | Autenticación JWT |
| drf-spectacular | 0.30.0 | Esquema OpenAPI, Swagger y ReDoc |
| django-filter | 26.2 | Filtros de consulta |
| django-cors-headers | 4.9.0 | Configuración CORS |
| django-environ | 0.14.0 | Variables de entorno |
| Pillow | 13.0.0 | Validación y procesamiento de imágenes |
| psycopg | 3.3.6 | Conexión con PostgreSQL |
| Gunicorn | 26.2.0 | Servidor WSGI |
| WhiteNoise | 6.12.0 | Archivos estáticos en producción |
| uv | — | Gestión de dependencias y entorno |
| SQLite | — | Base de datos local y de tests por defecto |
| PostgreSQL | 16 | Base de datos para Docker y despliegue |
| Docker Compose | — | Orquestación de contenedores |

Las dependencias se encuentran declaradas en `pyproject.toml` y `uv.lock`. También se incluye `requirements.txt` para instalaciones mediante pip.

## Arquitectura

El backend está organizado en aplicaciones Django:

| Aplicación | Responsabilidad |
|---|---|
| `apps/cuentas` | Usuario personalizado autenticado por email, perfiles y roles. |
| `apps/catalogo` | Estilos, cervezas, proveedores, ingredientes, recetas y lotes de producción. |
| `apps/ventas` | Clientes, pedidos, detalles de pedidos y reseñas. |
| `apps/core` | Modelo abstracto con fechas, paginación y comando de carga de datos de demostración. |
| `config` | Rutas, router de la API y configuración por entorno. |

## Modelo de datos

El sistema contiene 13 entidades: 11 modelos de dominio, `Usuario` y `PerfilUsuario`. Las recetas se relacionan con los ingredientes mediante el modelo intermedio `RecetaIngrediente`.

```mermaid
erDiagram
    USUARIO ||--|| PERFIL_USUARIO : tiene
    ESTILO ||--o{ CERVEZA : clasifica
    CERVEZA ||--o{ RECETA : tiene
    RECETA ||--o{ RECETA_INGREDIENTE : contiene
    INGREDIENTE ||--o{ RECETA_INGREDIENTE : participa
    CERVEZA ||--o{ LOTE : produce
    RECETA ||--o{ LOTE : utiliza
    PROVEEDOR ||--o{ INGREDIENTE : provee
    CLIENTE ||--o{ PEDIDO : realiza
    PEDIDO ||--o{ DETALLE_PEDIDO : contiene
    CERVEZA ||--o{ DETALLE_PEDIDO : incluye
    CLIENTE ||--o{ RESENA : escribe
    CERVEZA ||--o{ RESENA : recibe

    USUARIO {
        int id PK
        string email UK
        string first_name
        string last_name
        bool is_staff
        bool is_superuser
        bool is_active
    }
    PERFIL_USUARIO {
        int id PK
        int usuario_id FK
        string telefono
        string rol
        string bio
        string avatar
    }
    ESTILO {
        int id PK
        string nombre UK
        string slug UK
        string descripcion
        string color
    }
    CERVEZA {
        int id PK
        string nombre UK
        int estilo_id FK
        decimal graduacion
        int amargor
        string descripcion
        decimal precio
        int stock
        string imagen
        string imagen_archivo
        string color
        bool activo
    }
    PROVEEDOR {
        int id PK
        string nombre UK
        string contacto
        string email
        string telefono
        string cuit
        string direccion
        bool activo
    }
    INGREDIENTE {
        int id PK
        string nombre UK
        string tipo
        string unidad
        decimal stock
        decimal stock_minimo
        int proveedor_id FK
    }
    RECETA {
        int id PK
        int cerveza_id FK
        string nombre
        int version
        decimal volumen_litros
        string notas
        bool activa
    }
    RECETA_INGREDIENTE {
        int id PK
        int receta_id FK
        int ingrediente_id FK
        decimal cantidad
        string unidad
    }
    LOTE {
        int id PK
        int cerveza_id FK
        int receta_id FK
        string codigo UK
        date fecha_elaboracion
        date fecha_vencimiento
        decimal volumen_litros
        string estado
        string observaciones
    }
    CLIENTE {
        int id PK
        string nombre
        string email UK
        string telefono
        string tipo
        string direccion
        bool activo
    }
    PEDIDO {
        int id PK
        int cliente_id FK
        datetime fecha_pedido
        string estado
        string canal
        string notas
        decimal total
    }
    DETALLE_PEDIDO {
        int id PK
        int pedido_id FK
        int cerveza_id FK
        int cantidad
        decimal precio_unitario
    }
    RESENA {
        int id PK
        int cerveza_id FK
        int cliente_id FK
        int puntuacion
        string comentario
        datetime creado_en
    }
```

## API REST

La URL base local es `http://localhost:8000`. Los recursos de la API se encuentran bajo `/api/`.

### Autenticación y perfiles

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| POST | `/api/token/` | Público | Obtiene los tokens `access` y `refresh` mediante email y contraseña. |
| POST | `/api/token/refresh/` | Público | Renueva el token de acceso. |
| GET | `/api/auth/me/` | Autenticado | Devuelve los datos del usuario y su perfil. |
| GET | `/api/perfiles/` | Autenticado | Lista perfiles. El personal staff puede consultar todos; los demás usuarios solo el propio. |
| GET | `/api/perfiles/{id}/` | Autenticado | Devuelve un perfil respetando la misma restricción de acceso. |

### Catálogo y producción

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| GET, POST | `/api/estilos/` | GET público; POST autenticado | Lista y crea estilos. |
| GET, PUT, PATCH, DELETE | `/api/estilos/{id}/` | GET público; escritura autenticada | Consulta, modifica o elimina un estilo. |
| GET, POST | `/api/cervezas/` | GET público; POST autenticado | Lista y crea cervezas. |
| GET, PUT, PATCH, DELETE | `/api/cervezas/{id}/` | GET público; escritura autenticada | Consulta, modifica o elimina una cerveza. |
| GET | `/api/cervezas/estadisticas/` | Autenticado | Devuelve totales, cantidad de estilos, stock total y precio promedio. |
| GET | `/api/cervezas/bajo-stock/?umbral=10` | Autenticado | Lista cervezas con stock inferior al umbral indicado. El valor predeterminado es 10. |
| POST | `/api/cervezas/imagenes/` | Staff autenticado | Recibe y valida una imagen de cerveza. |
| GET, POST | `/api/proveedores/` | Autenticado | Lista y crea proveedores. |
| GET, PUT, PATCH, DELETE | `/api/proveedores/{id}/` | Autenticado | Consulta, modifica o elimina un proveedor. |
| GET, POST | `/api/ingredientes/` | Autenticado | Lista y crea ingredientes. |
| GET, PUT, PATCH, DELETE | `/api/ingredientes/{id}/` | Autenticado | Consulta, modifica o elimina un ingrediente. |
| GET, POST | `/api/recetas/` | Autenticado | Lista y crea recetas. |
| GET, PUT, PATCH, DELETE | `/api/recetas/{id}/` | Autenticado | Consulta, modifica o elimina una receta. |
| GET, POST | `/api/lotes/` | Autenticado | Lista y crea lotes de producción. |
| GET, PUT, PATCH, DELETE | `/api/lotes/{id}/` | Autenticado | Consulta, modifica o elimina un lote. |
| POST | `/api/lotes/{id}/finalizar/` | Autenticado | Cambia el lote al estado `envasado` y asigna vencimiento a 30 días si todavía no tiene uno. |

### Ventas y clientes

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| GET, POST | `/api/clientes/` | Autenticado | Lista y crea clientes. |
| GET, PUT, PATCH, DELETE | `/api/clientes/{id}/` | Autenticado | Consulta, modifica o elimina un cliente. |
| GET, POST | `/api/pedidos/` | Autenticado | Lista y crea pedidos. |
| GET, PUT, PATCH, DELETE | `/api/pedidos/{id}/` | Autenticado | Consulta, modifica o elimina un pedido. |
| POST | `/api/pedidos/{id}/cambiar-estado/` | Autenticado | Cambia el estado del pedido validando los valores permitidos. |
| GET, POST | `/api/detalles-pedido/` | Autenticado | Lista y crea detalles de pedidos. |
| GET, PUT, PATCH, DELETE | `/api/detalles-pedido/{id}/` | Autenticado | Consulta, modifica o elimina un detalle. |
| GET, POST | `/api/resenas/` | Autenticado | Lista y crea reseñas. |
| GET, PUT, PATCH, DELETE | `/api/resenas/{id}/` | Autenticado | Consulta, modifica o elimina una reseña. |

### Documentación y vistas

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| GET | `/` | Público | Página de bienvenida. |
| GET | `/api/` | Según permisos de los recursos | API navegable de Django REST Framework. |
| GET | `/api/schema/` | Público | Esquema OpenAPI en YAML. |
| GET | `/api/docs/` | Público | Interfaz Swagger UI. |
| GET | `/api/redoc/` | Público | Documentación ReDoc. |
| GET | `/admin/` | Sesión | Panel de administración de Django. |

### Formato de respuesta paginada

La paginación utiliza `page` y `page_size`. El tamaño predeterminado es 10 registros y el máximo permitido es 100.

```json
{
  "count": 8,
  "next": "http://localhost:8000/api/cervezas/?page=2",
  "previous": null,
  "results": []
}
```

### Serialización de listados y detalles

Algunos recursos utilizan serializers específicos para los listados. En esos casos, la respuesta de listado puede incluir relaciones anidadas, mientras que el detalle y las operaciones de escritura utilizan una representación más simple.

- **Cervezas:** `estilo` se representa mediante el slug. En el listado también se incluye `estilo_detalle`.
- **Ingredientes:** el listado incluye el proveedor anidado.
- **Recetas:** el listado incluye la cerveza y los ingredientes asociados.
- **Lotes:** el listado incluye información relacionada de cerveza y receta.
- **Pedidos:** el listado incluye cliente y detalles del pedido.
- **Reseñas:** el listado incluye cerveza y cliente.

En los detalles y operaciones de escritura se utilizan los serializers correspondientes a cada recurso, con referencias mediante identificadores o slugs según el campo.

## Autenticación y permisos

La API admite autenticación JWT y autenticación por sesión de Django.

### Obtener tokens

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@flacheros.com", "password": "admin12345"}'
```

La respuesta contiene los tokens `access` y `refresh`:

```json
{
  "access": "<token_de_acceso>",
  "refresh": "<token_de_refresco>"
}
```

La duración configurada es de **8 horas** para `access` y **1 día** para `refresh`.

### Enviar el token

```bash
curl http://localhost:8000/api/cervezas/ \
  -H "Authorization: Bearer <access>"
```

### Renovar el token

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<token_de_refresco>"}'
```

### Permisos

- Los endpoints de lectura de estilos y cervezas son públicos.
- La creación, modificación y eliminación de estilos y cervezas requieren autenticación.
- Los demás recursos requieren autenticación.
- La carga de imágenes requiere un usuario autenticado con `is_staff=True`.
- Los usuarios comunes solo pueden consultar su propio perfil; los usuarios staff pueden consultar todos los perfiles.
- El panel `/admin/` utiliza la sesión de Django.

## Paginación, filtros, búsqueda y ordenamiento

Los filtros se combinan mediante parámetros de query string. La búsqueda utiliza `search` y el ordenamiento utiliza `ordering`. Para ordenar en forma descendente se antepone `-` al campo.

| Recurso | Búsqueda (`search`) | Filtros | Ordenamiento (`ordering`) |
|---|---|---|---|
| Estilos | `nombre`, `slug` | — | `nombre` |
| Cervezas | `nombre`, `descripcion`, `estilo__nombre` | `estilo`, `activo`, `graduacion_min`, `graduacion_max`, `precio_min`, `precio_max` | `nombre`, `precio`, `stock`, `graduacion`, `amargor`, `creado_en` |
| Proveedores | `nombre`, `contacto`, `email`, `cuit` | `activo` | `nombre` |
| Ingredientes | `nombre`, `proveedor__nombre` | `tipo`, `unidad`, `proveedor`, `bajo_minimo` | `nombre`, `stock` |
| Recetas | `nombre`, `cerveza__nombre` | `cerveza`, `activa` | `nombre`, `version`, `creado_en` |
| Lotes | `codigo`, `cerveza__nombre` | `estado`, `cerveza`, `fecha_desde`, `fecha_hasta` | `codigo`, `fecha_elaboracion`, `volumen_litros`, `estado` |
| Clientes | `nombre`, `email`, `telefono` | `tipo`, `activo` | `nombre`, `email` |
| Pedidos | `cliente__nombre`, `cliente__email` | `estado`, `canal`, `cliente`, `fecha_desde`, `fecha_hasta` | `fecha_pedido`, `total`, `estado` |
| Detalles de pedido | `cerveza__nombre`, `pedido__cliente__nombre` | `pedido`, `cerveza` | `pedido`, `cantidad` |
| Reseñas | `cerveza__nombre`, `cliente__nombre`, `comentario` | `cerveza`, `cliente`, `puntuacion_min` | `puntuacion`, `creado_en` |

`bajo_minimo` acepta `true` o `false` y compara el stock del ingrediente con su stock mínimo. Los parámetros `fecha_desde` y `fecha_hasta` filtran por fecha de elaboración en lotes y por fecha del pedido en pedidos.

Ejemplo de consulta:

```bash
curl "http://localhost:8000/api/cervezas/?search=valle&estilo=ipa&ordering=-precio&page=1&page_size=10"
```

## Gestión de imágenes de cervezas

El modelo `Cerveza` admite dos alternativas para la imagen:

- `imagen`: URL de una imagen externa.
- `imagen_archivo`: ruta de un archivo almacenado por el backend.

El campo `imagen_url` devuelve la URL que debe utilizar el frontend. Si existe un archivo asociado, se utiliza ese archivo; en caso contrario, se utiliza la URL del campo `imagen`.

### Subir una imagen

El endpoint `POST /api/cervezas/imagenes/` recibe contenido `multipart/form-data` con el archivo en el campo `imagen`.

```bash
curl -X POST http://localhost:8000/api/cervezas/imagenes/ \
  -H "Authorization: Bearer <access>" \
  -F "imagen=@./cerveza.jpg"
```

La carga requiere un usuario staff autenticado. Se aplican las siguientes validaciones:

- Formatos permitidos: JPEG, PNG y WEBP.
- Tamaño máximo: 5 MB.
- Dimensiones mínimas: 200 × 200 píxeles.
- El archivo debe ser una imagen válida.

La respuesta incluye `ruta` y `url`. Para asociar el archivo a una cerveza, se envía el valor de `ruta` en el campo `imagen_archivo` al crear o actualizar el recurso.

## Instalación y ejecución local

### Requisitos

- Python 3.12 o superior.
- [uv](https://docs.astral.sh/uv/) para instalar las dependencias y administrar el entorno.
- Git para clonar el repositorio.
- Docker y Docker Compose, si se desea utilizar PostgreSQL en contenedores.

### Preparar el entorno

```bash
git clone https://github.com/Emancc/Cerveceria_Flacheros_Back_Django.git
cd Cerveceria_Flacheros_Back_Django

# Crear el archivo de variables de entorno
cp .env.example .env

# Instalar dependencias
uv sync

# Aplicar migraciones
uv run python manage.py migrate

# Cargar datos de demostración
uv run python manage.py seed_demo

# Iniciar el servidor
uv run python manage.py runserver
```

En Windows PowerShell, la copia del archivo de entorno se realiza con:

```powershell
Copy-Item .env.example .env
```

El servidor local queda disponible en `http://127.0.0.1:8000`.

### Instalación mediante pip

También se pueden instalar las dependencias desde `requirements.txt`:

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

### Variables de entorno

Las variables principales se definen en `.env` o en el entorno de ejecución:

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Django. Debe ser segura y mantenerse privada. |
| `DEBUG` | Activa o desactiva el modo de depuración. |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por coma. |
| `DJANGO_SETTINGS_MODULE` | Configuración a utilizar: `config.settings.dev` o `config.settings.prod`. |
| `DATABASE_URL` | Conexión a la base de datos. Por defecto utiliza `sqlite:///db.sqlite3`. |
| `POSTGRES_DB` | Nombre de la base de datos PostgreSQL utilizada por Docker Compose. |
| `POSTGRES_USER` | Usuario de PostgreSQL utilizado por Docker Compose. |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL utilizada por Docker Compose. |
| `CORS_ALLOWED_ORIGINS` | Orígenes autorizados para solicitudes CORS. |
| `CSRF_TRUSTED_ORIGINS` | Orígenes confiables para la protección CSRF. |

Para producción se debe utilizar `config.settings.prod`, establecer `DEBUG=False`, definir una `SECRET_KEY` segura y configurar correctamente los hosts y orígenes permitidos.

## Datos de demostración

El comando `seed_demo` carga registros de ejemplo para estilos, cervezas, proveedores, ingredientes, recetas, lotes, clientes, pedidos y reseñas. Es idempotente: puede ejecutarse más de una vez sin duplicar los registros de demostración.

```bash
uv run python manage.py seed_demo
```

Para eliminar los datos de dominio y volver a cargarlos:

```bash
uv run python manage.py seed_demo --reset
```

**`--reset` elimina los registros de dominio** (reseñas, detalles de pedidos, pedidos, clientes, lotes, recetas, ingredientes, proveedores, cervezas y estilos) antes de volver a cargar los datos. No elimina los usuarios.

El comando crea o actualiza el usuario administrador de demostración:

| Campo | Valor |
|---|---|
| Email | `admin@flacheros.com` |
| Contraseña | `admin12345` |
| Perfil | `admin` |

Estas credenciales son exclusivamente para demostración y deben cambiarse antes de utilizar el sistema en un entorno real.

## Docker

El proyecto incluye `Dockerfile` y `docker-compose.yml`. Docker Compose inicia PostgreSQL 16 y el backend Django.

Configurar las variables necesarias en `.env` y ejecutar:

```bash
docker compose up --build
```

El contenedor del backend realiza las migraciones, recopila los archivos estáticos y carga los datos de demostración antes de iniciar Gunicorn.

Servicios:

- Backend: `http://localhost:8000`
- Administración: `http://localhost:8000/admin/`
- Swagger: `http://localhost:8000/api/docs/`
- PostgreSQL: servicio interno `db`, puerto `5432`.

Los datos de PostgreSQL se conservan en el volumen `postgres_data` y los archivos estáticos en `staticfiles`.

## Despliegue en Render

El backend está publicado en [Render](https://cerveceria-flacheros-back-django-1.onrender.com/). El repositorio incluye `render.yaml` con la configuración de un servicio web Python y una base PostgreSQL. Los enlaces públicos a la API, Swagger, OpenAPI y ReDoc se encuentran en la sección [Proyecto publicado](#proyecto-publicado).

La configuración establece:

- `config.settings.prod` como módulo de configuración.
- `DEBUG=False`.
- Generación de `SECRET_KEY`.
- Conexión a PostgreSQL mediante `DATABASE_URL`.
- Instalación de dependencias desde `requirements.txt`.
- Ejecución de `bash bash.sh`, que aplica migraciones, ejecuta `collectstatic` e inicia Gunicorn.
- `/api/schema/` como ruta de verificación de estado.

Los dominios permitidos y los orígenes CORS/CSRF deben coincidir con los dominios reales del backend y del frontend.

## Pruebas automatizadas

El proyecto contiene **55 pruebas automatizadas** distribuidas en las aplicaciones `cuentas`, `catalogo` y `ventas`.

La cobertura incluye:

- Autenticación por email, emisión y renovación de tokens, consulta del usuario autenticado y permisos sobre perfiles.
- Operaciones CRUD, permisos, filtros, búsqueda, ordenamiento y paginación del catálogo.
- Estadísticas de cervezas, consulta de bajo stock y validación de imágenes.
- Proveedores, ingredientes, recetas y relaciones entre recetas e ingredientes.
- Lotes de producción y acción de finalización.
- Clientes, pedidos, detalles, recálculo de totales, cambios de estado y reseñas.

Ejecutar las pruebas con:

```bash
uv run python manage.py test -v 2
```

## Panel de administración

El panel de Django se encuentra en `/admin/`. Permite administrar los modelos del sistema y cuenta con filtros, búsqueda, ordenamiento y vistas de relaciones.

| Modelo | Funcionalidades de administración |
|---|---|
| Estilo | Filtro por fecha; búsqueda por nombre, slug y descripción. |
| Cerveza | Filtros por estilo y estado; búsqueda por nombre, estilo y descripción; edición en línea de precio, stock y estado. |
| Proveedor | Filtro por estado; búsqueda por nombre, contacto, email y CUIT. |
| Ingrediente | Filtros por tipo, unidad y proveedor; búsqueda por nombre y proveedor. |
| Receta | Filtros por estado y estilo de cerveza; incluye ingredientes relacionados. |
| RecetaIngrediente | Filtros por unidad y cerveza de la receta. |
| Lote | Filtros por estado y estilo de cerveza; búsqueda por código, cerveza y receta. |
| Cliente | Filtros por tipo y estado; búsqueda por nombre, email y teléfono. |
| Pedido | Filtros por estado, canal y fecha; búsqueda por cliente, email y notas. |
| DetallePedido | Filtro por estilo de cerveza; búsqueda por pedido y cerveza. |
| Reseña | Filtros por puntuación y estilo; búsqueda por cerveza, cliente y comentario. |
| Usuario | Búsqueda por email, nombre y apellido. |
| PerfilUsuario | Filtro por rol; búsqueda por email y teléfono. |

Los pedidos muestran el total y la cantidad de artículos como campos calculados de solo lectura. Las recetas y los pedidos permiten administrar sus relaciones mediante formularios inline.

## Integración con Next.js

En el archivo `.env.local` del frontend:

```env
NEXT_PUBLIC_USE_MOCK=false
NEXT_PUBLIC_API_URL=http://localhost:8000/api/
```

Para el entorno local, el backend contempla los orígenes de desarrollo:

```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Flujo de autenticación desde el frontend:

1. Enviar `POST /api/token/` con `email` y `password`.
2. Conservar los tokens `access` y `refresh`.
3. Enviar `Authorization: Bearer <access>` en las solicitudes privadas.
4. Cuando el token de acceso expire, solicitar uno nuevo mediante `POST /api/token/refresh/`.
5. Procesar la paginación mediante `count`, `next`, `previous` y `results`.

En el catálogo, el campo `estilo` se representa mediante el slug. En el listado de cervezas también se incluye `estilo_detalle` con la información del estilo. En el detalle de un pedido, `cliente` se representa mediante su identificador y no se incluye el arreglo `detalles`, que sí está disponible en el listado.

## Capturas

### Sitio público

![Portada del sitio](docs/capturas/portada.png)

### Documentación de la API

![Swagger UI](docs/capturas/swagger.png)

### Administración de Django

![Login del administrador](docs/capturas/admin.png)

![Panel de administración](docs/capturas/admin_panel.png)

### Administración de cervezas

![Listado de cervezas en el administrador](docs/capturas/admin_cervezas.png)

### API navegable

![Listado de cervezas en la API](docs/capturas/api_listado.png)

### Relaciones anidadas

![Recetas con cerveza e ingredientes relacionados](docs/capturas/api_recetas_nested.png)

## Estructura del proyecto

```text
.
├── apps/
│   ├── core/
│   │   ├── management/commands/seed_demo.py
│   │   ├── models.py
│   │   └── pagination.py
│   ├── cuentas/
│   │   ├── migrations/
│   │   ├── tests/test_auth.py
│   │   ├── admin.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── signals.py
│   │   └── views.py
│   ├── catalogo/
│   │   ├── migrations/
│   │   ├── tests/
│   │   ├── admin.py
│   │   ├── filters.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── signals.py
│   │   └── views.py
│   └── ventas/
│       ├── migrations/
│       ├── tests/test_pedidos.py
│       ├── admin.py
│       ├── filters.py
│       ├── models.py
│       ├── serializers.py
│       └── views.py
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── api_urls.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── docker/
│   └── entrypoint.sh
├── docs/capturas/
├── templates/
│   └── bienvenida.html
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── pyproject.toml
├── render.yaml
├── requirements.txt
└── uv.lock
```

## Decisiones técnicas

- **Usuario personalizado:** el modelo `Usuario` utiliza el email como identificador de autenticación y elimina el campo `username`.
- **Perfil asociado:** cada usuario dispone de un perfil relacionado mediante una relación uno a uno.
- **Estilo de cerveza:** la API utiliza el slug del estilo en el campo `estilo`; el listado agrega `estilo_detalle` para exponer la información relacionada.
- **Total de pedidos:** el total se calcula a partir de los detalles y se actualiza al crear, modificar o eliminar una línea del pedido. El campo `total` es de solo lectura en la API.
- **Imágenes:** las cervezas pueden utilizar una URL externa o una imagen almacenada por el backend.
- **Consultas:** los viewsets utilizan `select_related`, `prefetch_related` y anotaciones para recuperar relaciones y contadores.
- **Permisos:** estilos y cervezas permiten lectura pública; las operaciones de escritura requieren autenticación. Los demás recursos requieren autenticación.
- **Documentación API:** el esquema OpenAPI se genera con drf-spectacular.
- **Datos de demostración:** `seed_demo` utiliza operaciones de actualización o creación para mantener una carga idempotente.
