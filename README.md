# Sistema de Gestión Veterinaria — Backend (Django REST Framework)

## Descripción del Proyecto

El **Sistema de Gestión Veterinaria (SGV)** es una plataforma integral diseñada para automatizar los procesos clínicos, administrativos y operativos de una clínica veterinaria moderna.
El backend del sistema está desarrollado en **Django REST Framework (DRF)** sobre **PostgreSQL**, aplicando principios de arquitectura limpia, buenas prácticas de ingeniería y modularidad escalable.

Este sistema provee servicios API seguros y estructurados que permiten la gestión de usuarios, mascotas, citas, historias clínicas, inventario, facturación y notificaciones automáticas.

---

## Arquitectura y Diseño del Sistema

El diseño del backend se basa en una **arquitectura modular y desacoplada**, compuesta por aplicaciones específicas (apps) dentro del dominio veterinario.
Cada módulo implementa su propia lógica de negocio, modelos y endpoints REST, siguiendo los principios **SOLID** y el patrón **MVC extendido** (Models, Views, Serializers, URLs, Services).

### Componentes Principales

| Módulo                             | Descripción                                                                                                                |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Usuarios y Roles**               | Autenticación JWT, control de acceso y permisos por rol (Administrador, Veterinario, Recepcionista, Cliente, Practicante). |
| **Gestión de Mascotas**            | CRUD de mascotas, historial de vacunas, y vínculo con propietario.                                                         |
| **Citas**                          | Agendamiento, reprogramación y cancelación de citas, validación de disponibilidad veterinaria.                             |
| **Consultas e Historias Clínicas** | Registro de consultas, diagnósticos, recetas y generación de historia clínica consolidada.                                 |
| **Inventario**                     | Administración de medicamentos y productos veterinarios, control de stock y alertas automáticas.                           |
| **Facturación y Pagos**            | Creación de facturas, cálculo de impuestos, registro de pagos y generación de comprobantes.                                |
| **Notificaciones**                 | Envío automático de recordatorios y alertas mediante un sistema interno de notificaciones.                                 |

---

## Tecnologías y Herramientas

| Categoría                    | Tecnología / Herramienta                 |
| ---------------------------- | ---------------------------------------- |
| **Framework Backend**        | Django 5 + Django REST Framework         |
| **Base de Datos**            | PostgreSQL                               |
| **Autenticación**            | JWT (SimpleJWT)                          |
| **Configuración de entorno** | python-dotenv                            |
| **Seguridad CORS**           | django-cors-headers                      |
| **Testing**                  | pytest + pytest-django                   |
| **Control de versiones**     | Git (main, develop, feature/*, hotfix/*) |
| **Entorno opcional**         | Docker y docker-compose                  |
| **Linter / Formato**         | black + isort                            |

---

## Estructura del Proyecto

```
veterinary-clinic-backend/
├── core/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── apps.py                # Centraliza apps Django, terceros y locales
│   │   ├── base.py                # Configuración base del proyecto
│   │   ├── local.py               # Configuración local de desarrollo
│   ├── urls.py                    # Rutas principales y endpoints base
│   ├── wsgi.py                    # Configuración WSGI
│   ├── asgi.py                    # Configuración ASGI
│
├── apps/
│   ├── usuarios/                     # Gestión de usuarios, roles y autenticación JWT
│   ├── mascotas/                      # Módulo de mascotas, razas y propietarios
│   ├── citas/              # Agendamiento y gestión de citas veterinarias
│   ├── consultas/             # Consultas, diagnósticos e historias clínicas
│   ├── inventario/                 # Control de medicamentos, productos e insumos
│   ├── facturacion/                   # Facturación, pagos y reportes financieros
│   ├── notificaciones/             # Sistema de notificaciones y recordatorios
│   └── shared/                    # Utilidades comunes, servicios y modelos base
│
├── manage.py
├── requirements.txt               # Dependencias del entorno
├── .env                   # Variables de entorno ejemplo
├── .gitignore
├── README.md
└── CONTRIBUITING.md
```

---

## Configuración del Entorno

### 1- Clonar el repositorio

```bash
git clone https://github.com/isairey/SisVet-Backend.git
cd SisVet-Backend
```

### 2️- Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```

### 3- Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4️- Configurar variables de entorno

```bash
cp .env.example .env
```

Completa el archivo `.env` con tus credenciales locales:

```
DB_NAME=sgv
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

> ⚠️ El archivo `.env` **no debe subirse al repositorio**.

---

## Base de Datos (PostgreSQL)

Si no tienes una instancia local activa, puedes crear una con Docker:

```bash
docker run --name postgres-sgv \
  -e POSTGRES_DB=sgv \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=admin123 \
  -p 5432:5432 -d postgres
```

---

## Migraciones iniciales

```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## Ejecución del servidor

```bash
python manage.py runserver
```

Luego abre el navegador y visita:

> **[http://127.0.0.1:8000/api/health/](http://127.0.0.1:8000/api/health/)**

Respuesta esperada:

```json
{"status": "ok"}
```

---

## Endpoints Base (Configurados por defecto)

| Endpoint              | Descripción                     |
| --------------------- | ------------------------------- |
| `/admin/`             | Panel administrativo de Django  |
| `/api/health/`        | Verifica el estado del servidor |
| `/api/token/`         | Obtiene un token JWT            |
| `/api/token/refresh/` | Refresca el token JWT           |

---

## Estrategia de Ramas (Branching Strategy)

| Rama         | Descripción                                       |
| ------------ | ------------------------------------------------- |
| **main**     | Contiene la versión estable lista para producción |
| **develop**  | Integración continua del desarrollo               |
| **feature/** | Ramas individuales para funcionalidades           |
| **hotfix/**  | Correcciones rápidas en producción                |

Ejemplo de flujo:

```bash
git checkout develop
git checkout -b feature/gestion-usuarios
# Desarrollar...
git add .
git commit -m "feat: agregar endpoints de registro de usuarios"
git push origin feature/gestion-usuarios
# Crear Pull Request → merge a develop
```

---

## Configuración Modular

El proyecto utiliza un esquema de configuración **modular**, ideal para entornos escalables:

| Archivo    | Función                                                         |
| ---------- | --------------------------------------------------------------- |
| `apps.py`  | Centraliza todas las aplicaciones (Django, terceros y locales). |
| `base.py`  | Configuración general (DB, JWT, Logging, REST Framework).       |
| `local.py` | Ajustes de entorno de desarrollo.                               |

Esto permite definir fácilmente entornos `production.py` o `staging.py` si se requieren más adelante.

---

## Dependencias Clave

| Paquete                    | Descripción                               |
| -------------------------- | ----------------------------------------- |
| **Django**                 | Framework principal del backend           |
| **Django REST Framework**  | Serialización, vistas API y autenticación |
| **SimpleJWT**              | Tokens de autenticación seguros           |
| **python-dotenv**          | Gestión de variables de entorno           |
| **django-cors-headers**    | Permite comunicación con frontend         |
| **psycopg2-binary**        | Conector PostgreSQL                       |
| **pytest / pytest-django** | Testing automatizado                      |
| **black / isort**          | Formateo y ordenamiento de código         |

---

## Pruebas Unitarias

Ejecutar todas las pruebas:

```bash
pytest
```

Ejecutar pruebas específicas:

```bash
pytest apps/users/tests/test_models.py::TestUserModel
```

---

## Buenas Prácticas

* Cumplir con **PEP8** y principios **SOLID**.
* Mantener commits pequeños y descriptivos (`feat:`, `fix:`, `refactor:`).
* Incluir **docstrings** y comentarios relevantes.
* Evitar código sin uso o comentado.
* Asegurar la correcta documentación de cada módulo.

---

## Estado Actual del Proyecto

| Elemento                   | Estado | Descripción                                            |
| -------------------------- | ------ | ------------------------------------------------------ |
| Configuración del entorno  | ✅      | Base funcional con conexión PostgreSQL                 |
| Modularización de settings | ✅      | Implementada (apps/base/local)                         |
| JWT y endpoints base       | ✅      | Funcionando                                            |
| Apps del dominio           | ⏳      | Pendiente de implementación (usuarios, mascotas, etc.) |
| Dockerización              | ⏳      | Planificada                                            |
| Testing y documentación    | 🔄     | En desarrollo                                          |

---

© 2025 — Sistema de Gestión Veterinaria (SGV)
Desarrollo backend con Django REST Framework
Proyecto académico profesional con enfoque en arquitectura limpia, escalabilidad y calidad de software.
