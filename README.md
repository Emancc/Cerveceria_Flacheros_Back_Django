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
| Cloudinary | 1.46.3 | Persistencia de imágenes en producción |
| psycopg | 3.3.6 | Driver PostgreSQL |
| Gunicorn | 26.2.0 | Servidor WSGI de producción |
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
| `SECRET_KEY` | Clave secreta de Django. Obligatoria en producción. |
| `DEBUG` | `True` en desarrollo, `False` en producción. |
| `ALLOWED_HOSTS` | Hosts separados por coma. |
| `DJANGO_SETTINGS_MODULE` | `config.settings.dev` o `config.settings.prod`. |
| `DATABASE_URL` | `sqlite:///db.sqlite3` o URL de PostgreSQL. |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Credenciales del servicio `db`. |
| `CORS_ALLOWED_ORIGINS` | Orígenes permitidos del frontend. |
| `CSRF_TRUSTED_ORIGINS` | Orígenes confiables para CSRF. |
| `USE_CLOUDINARY` | `True` en producción para subir imágenes a Cloudinary; `False` en desarrollo/tests. |
| `CLOUDINARY_URL` | Credencial `cloudinary://API_KEY:API_SECRET@CLOUD_NAME`. Solo si `USE_CLOUDINARY=True`. |

### Imágenes en Cloudinary

En desarrollo y tests las imágenes se guardan en `media/` y se referencia la
ruta relativa en `imagen_archivo`. En producción, Render no tiene disco
persistente, así que con `USE_CLOUDINARY=True` el endpoint
`POST /api/cervezas/imagenes/` sube el archivo a Cloudinary y devuelve
`{ ruta: "", url: secure_url }`. El front guarda esa URL en `imagen`.

Configuración en Render:

1. Crear una cuenta en Cloudinary y copiar el **API environment variable**
   (`CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME`).
2. En Render → Environment agregar:
   - `USE_CLOUDINARY=true`
   - `CLOUDINARY_URL=<credencial>` (como secreto)
3. Redeploy. No hay migraciones nuevas.

Para migrar imágenes locales existentes o limpiar referencias a archivos que
ya no existen en Render:

```bash
uv run python manage.py migrar_imagenes_cloudinary          # dry-run
uv run python manage.py migrar_imagenes_cloudinary --apply  # aplica
```

El comando sube a Cloudinary los archivos locales que todavía existan, guarda
la URL en `imagen` y limpia `imagen_archivo`. Si el archivo ya no existe, solo
limpia la referencia para que se use la URL externa o el placeholder.

En Render, ejecutá el comando desde la **Shell** del servicio:

```bash
python manage.py migrar_imagenes_cloudinary          # dry-run
python manage.py migrar_imagenes_cloudinary --apply  # aplica
```

Las imágenes reemplazadas o eliminadas desde el panel no se borran
automáticamente de Cloudinary; se pueden administrar desde la consola de
Cloudinary.

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

La batería tiene **84 tests** con `APITestCase` y base de datos real (con mocks
puntuales para la subida a Cloudinary). Cubre:

- Autenticación: token por email, password incorrecta, `me` con/sin token,
  perfiles propios vs. ajenos y visibilidad para staff.
- Cervezas: listado paginado, `estilo` string en list/detalle y
  `estilo_detalle` anidado solo en list, payload del front con `color: ""` e
  `imagen: ""`, permisos de escritura, CRUD, búsqueda, filtro por estilo,
  ordering, `page_size`, estadísticas y bajo stock (incluido umbral inválido).
- Catálogo: estilos públicos, proveedores con/sin token, ingredientes bajo
  mínimo, recetas anidadas en list y planas en detalle, lotes anidados,
  `finalizar` y CRUD de reseñas.
- Ventas: pedidos anidados en list vs. planos en detalle, cambio de estado
  válido/inválido, recálculo del total al crear un detalle y clientes con/sin
  token.
- Admin: smoke test de `/admin/` y de los changelists de los 11 modelos de
  dominio con superusuario.
- Imágenes: subida local, validación de formato/peso/dimensiones, subida a
  Cloudinary mockeada y comando de migración `migrar_imagenes_cloudinary`.

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

1. `POST /api/token/` con `{email, password}`.
2. Guardar `access` y `refresh`.
3. Enviar `Authorization: Bearer <access>` en cada request privada.
4. Ante un `401`, renovar con `POST /api/token/refresh/`.
5. Respetar la paginación `{count, next, previous, results}` y los errores
   por campo de DRF (`{"campo": ["mensaje"]}`).

Contrato diferencial:

- `GET /api/cervezas/` → `estilo` es un **string slug** (`"pilsner"`, `"ipa"`,
  etc.) y `estilo_detalle` es el objeto anidado con `slug`, `nombre`, etc.
- `GET /api/cervezas/{id}/` → `estilo` es un **string slug**; no incluye
  `estilo_detalle`.
- `GET /api/pedidos/` → `cliente` y `detalles` anidados.
- `GET /api/pedidos/{id}/` → `cliente` es un **id** y no incluye `detalles`.

> **Compatibilidad con el front:** `estilo` siempre es string en el catálogo.
> Usar `estilo_detalle` solo si se necesita el objeto completo en el listado.

## Checklist de requisitos de la cátedra

| Requisito | Dónde se cumple |
|---|---|
| 10+ modelos | 11 modelos de dominio + `Usuario` y `PerfilUsuario`. |
| 8+ viewsets | 11 viewsets registrados en `config/api_urls.py`. |
| 2+ serializers anidados solo en list | Ingredientes, recetas, lotes, pedidos, reseñas y cervezas (`estilo_detalle`). |
| 2+ `@action` | `estadisticas`, `bajo-stock`, `finalizar` y `cambiar-estado`. |
| Auth por sesión y por token | `SessionAuthentication` + SimpleJWT; admin y API navegable. |
| Paginación | `PaginacionEstandar` con `page` y `page_size`. |
| Filtros | `django-filter` en catálogo y ventas. |
| Búsqueda y ordering | `SearchFilter` y `OrderingFilter` por recurso. |
| Documentación | `/api/schema/`, `/api/docs/` y `/api/redoc/`. |
| Vista template | `/` con `templates/bienvenida.html`. |
| Admin completo | 11 modelos de dominio + usuarios y perfiles, con filtros, búsqueda, orden e inlines. |
| uv | `pyproject.toml`, `uv.lock` y comandos con `uv run`. |
| CORS | `django-cors-headers` y orígenes configurables. |
| Docker | `Dockerfile`, `docker-compose.yml` y `docker/entrypoint.sh`. |
| Tests | 84 tests con `APITestCase` y base real. |
| Datos demo | `python manage.py seed_demo` idempotente. |

## Flujo de Git sugerido

El repositorio lo administra el grupo. Se sugiere:

- `main` estable y protegida; cada feature en una rama
  `feature/<tema>` (por ejemplo `feature/seed-demo`,
  `feature/tests-api`, `feature/readme`).
- Commits con convención: `feat:`, `fix:`, `test:`, `docs:`, `chore:`.
- Pull Request hacia `main` con descripción, checklist y revisión de al menos
  un integrante.
- Mantener `uv.lock` versionado y ejecutar `uv run python manage.py test`
  antes de abrir el PR.
- No commitear `.env`, `db.sqlite3`, `staticfiles/` ni `media/`.

> Esta entrega no ejecutó comandos git; los cambios quedan en el árbol de
> trabajo para que el grupo los revise y versione.

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
│   │   ├── management/commands/migrar_imagenes_cloudinary.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── filters.py
│   │   ├── imagenes.py
│   │   ├── views.py
│   │   └── tests/
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

## Decisiones técnicas relevantes

- **Usuario custom por email**: `Usuario` redefine `USERNAME_FIELD = "email"`,
  usa un manager propio y crea el `PerfilUsuario` automáticamente por signal.
  SimpleJWT toma el email como credencial.
- **`estilo` string slug + `estilo_detalle`**: `estilo` es siempre un string
  (`"ipa"`) tanto en list como en detalle, para que el catálogo del front no
  se rompa. En list se agrega `estilo_detalle` con el objeto completo para
  cumplir el requisito de datos anidados sin duplicar la lógica de escritura.
- **Total calculado**: `Pedido.total` se recalcula desde los detalles
  (`recalcular_total`) al crear, editar o borrar una línea. En la API es de
  solo lectura para no aceptar totales inconsistentes.
- **Imágenes de cerveza**: en desarrollo se suben a `media/` y se guarda la
  ruta relativa en `imagen_archivo`. En producción, con
  `USE_CLOUDINARY=True`, se suben a Cloudinary y se guarda la `secure_url` en
  `imagen`. El endpoint `POST /api/cervezas/imagenes/` mantiene el contrato
  `{ ruta, url }` en ambos modos.
- **`precio_unitario` opcional**: si no se envía al crear un detalle, el
  modelo toma `cerveza.precio`; el subtotal se calcula solo.
- **Consultas optimizadas**: `select_related` y `prefetch_related` en los
  viewsets, más `annotate` para contadores (`resenas_count`,
  `cervezas_count`, `ingredientes_count`, `pedidos_count`,
  `detalles_count`).
- **Permisos**: catálogo público de solo lectura con
  `IsAuthenticatedOrReadOnly`; el resto requiere `IsAuthenticated`.
- **Schema limpio**: `ENUM_NAME_OVERRIDES` evita colisiones entre los enums
  `estado` y `tipo`; las actions y `MeView` están documentadas con
  `@extend_schema`.
- **Seed idempotente**: `update_or_create`/`get_or_create` y `--reset` seguro
  para datos de dominio, sin tocar usuarios.


