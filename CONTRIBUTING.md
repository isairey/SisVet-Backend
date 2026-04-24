# Guía de Contribución - Veterinary Clinic Backend

## Organización del Equipo

Este proyecto se desarrolla de forma colaborativa usando **Git, GitHub y Jira**, bajo prácticas profesionales de ingeniería de software.

El backend está construido con **Django REST Framework** y una arquitectura modular basada en **apps independientes**.

---

## Estrategia de Ramas

### Rama Principal
- `main`: Contiene la versión estable, validada y lista para despliegue.
- `develop`: Rama base de integración. Todo nuevo desarrollo parte de aquí.

### Ramas de Funcionalidad

Cada desarrollador debe trabajar en una rama específica según la historia de usuario o módulo asignado.

```

feature/HU-005-registro-usuarios         - Registro y autenticación de usuarios
feature/HU-009-crud-mascotas             - CRUD de mascotas
feature/HU-012-agendar-cita              - Agendamiento de citas
feature/HU-015-registrar-consulta        - Registro de consultas
feature/HU-018-inventario-productos      - Módulo de inventario
feature/HU-020-facturacion               - Facturación y pagos
feature/HU-022-notificaciones            - Recordatorios y alertas

```

También se pueden crear ramas de mantenimiento:

```

hotfix/fix-login-error                   - Corrección urgente en login
chore/update-requirements                - Actualización de dependencias
refactor/optimize-queries                - Mejoras internas de código

````

---

## Flujo de Trabajo Git

### 1. Clonar el Repositorio

```bash
git clone https://github.com/isairey/SisVet-Backend.git
cd SisVet-Backend
````

### 2. Crear una Rama de Trabajo

```bash
# Cambiar a develop y actualizar
git checkout develop
git pull origin develop

# Crear rama de trabajo
git checkout -b feature/HU-005-registro-usuarios
```

### 3. Desarrollar tu Funcionalidad

Haz tus cambios, prueba localmente y confirma el progreso:

```bash
git add .
git commit -m "feat(auth): agregar endpoint de registro con roles"
```

### 4. Subir la Rama y Crear PR

```bash
git push -u origin feature/HU-005-registro-usuarios
```

Luego:

1. Crea un **Pull Request** hacia `develop`.
2. Explica el objetivo, cambios realizados y criterios de aceptación.
3. Asigna revisores.

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
│   ├── users/                     # Gestión de usuarios, roles y autenticación JWT
│   ├── pets/                      # Módulo de mascotas, razas y propietarios
│   ├── appointments/              # Agendamiento y gestión de citas veterinarias
│   ├── consultations/             # Consultas, diagnósticos e historias clínicas
│   ├── inventory/                 # Control de medicamentos e insumos
│   ├── billing/                   # Facturación, pagos y comprobantes
│   ├── notifications/             # Recordatorios automáticos y alertas
│   └── shared/                    # Utilidades comunes, mixins, helpers
│
├── requirements.txt               # Dependencias del proyecto
├── .env.example                   # Variables de entorno ejemplo
├── manage.py
├── README.md
└── CONTRIBUITING.md
```

---

## Convenciones de Commits

Usamos el estándar **Conventional Commits**:

```
feat: Nueva funcionalidad
fix: Corrección de bug
docs: Actualización de documentación
style: Cambios de formato
refactor: Mejora interna sin alterar funcionalidad
test: Agregar o modificar pruebas
chore: Mantenimiento o tareas menores
```

### Ejemplos:

```bash
git commit -m "feat(users): agregar registro con validaciones OCL"
git commit -m "fix(auth): corregir expiración de tokens JWT"
git commit -m "docs: actualizar instrucciones de instalación en README"
```

---

## Estándares de Código

* Seguir **PEP8**.
* Usar nombres descriptivos en variables y métodos.
* Mantener la lógica desacoplada y modular en cada app.
* Cada módulo debe incluir:

  * `models.py`
  * `serializers.py`
  * `views.py`
  * `urls.py`
  * `tests.py`

Ejemplo de estructura mínima de una app:

```
apps/users/
├── models.py
├── serializers.py
├── views.py
├── urls.py
└── tests.py
```

---

## Checklist Antes de Crear un Pull Request

* [ ] El código compila y pasa pruebas (`python manage.py test`)
* [ ] Cumple criterios de aceptación definidos en Jira
* [ ] Incluye documentación o docstrings relevantes
* [ ] Mantiene coherencia en nombres y estilo
* [ ] No rompe funcionalidades existentes
* [ ] README o documentación actualizada si aplica
* [ ] Commit y PR con mensaje descriptivo y limpio

---

## Pruebas

Ejecuta las pruebas locales:

```bash
python manage.py test
```

Si usas `pytest`:

```bash
pytest -v --cov=apps
```

---

## Resolución de Conflictos

```bash
# Actualiza rama develop
git checkout develop
git pull origin develop

# Funde cambios en tu rama
git checkout feature/HU-005-registro-usuarios
git merge develop

# Resuelve conflictos y commitea
git add .
git commit -m "fix: resolver conflictos con develop"
git push
```

---

## Buenas Prácticas

### Commits Frecuentes

* Realiza commits pequeños, temáticos y con propósito claro.

### Código Limpio

```python
# ✅ Bien: Claro y autoexplicativo
def calculate_total(invoice_items):
    return sum(item.price for item in invoice_items)

# ❌ Mal: Críptico y sin contexto
def calc(x):
    return sum(y.p for y in x)
```

### Documentación

Usar docstrings en métodos y clases principales:

```python
class AppointmentService:
    """
    Servicio de gestión de citas veterinarias.
    Permite crear, reprogramar y cancelar citas.
    """
```

---

## Roles y Responsabilidades

| Rol               | Responsabilidad Principal                     |
| ----------------- | --------------------------------------------- |
| Backend Developer | Implementar endpoints, modelos y validaciones |
| QA Engineer       | Pruebas unitarias, integración y e2e          |
| Scrum Master      | Seguimiento en Jira, gestión de sprints       |
| DB Specialist     | Estructura y optimización de base de datos    |
| Fullstack Dev     | Integración backend-frontend y despliegue     |

---

## Criterios de Aceptación

Un PR se aprueba cuando:

1. Implementa correctamente la funcionalidad.
2. Cumple con los estándares de código y estilo.
3. Está documentado y probado.
4. No introduce errores ni vulnerabilidades.
5. Fue revisado y aprobado por otro miembro del equipo.

---

## Recursos Adicionales

* [Django Official Docs](https://docs.djangoproject.com/)
* [Django REST Framework](https://www.django-rest-framework.org/)
* [Conventional Commits](https://www.conventionalcommits.org/)
* [Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials)
* [PEP8 Style Guide](https://peps.python.org/pep-0008/)

---

## Comunicación

### Canales Recomendados

* **GitHub Issues** → Reportar errores o proponer mejoras
* **Pull Requests** → Revisar y aprobar código
* **Jira Board** → Seguimiento de tareas e historias
* **Slack / Discord** → Comunicación interna rápida

### Plantilla de Issue

```markdown
**Título**: [HU-XXX] Breve descripción

**Descripción**:
Explica el propósito o problema identificado.

**Archivos afectados**:
- apps/users/views.py
- apps/users/serializers.py

**Pasos para reproducir (si aplica)**:
1. ...
2. ...

**Resultado esperado**:
...

**Resultado actual**:
...
```

---

## Mejores Prácticas de Equipo

* Revisar PRs en máximo 24 horas.
* Participar activamente en la planificación de sprint.
* Mantener `develop` estable y funcional.
* Usar `.env.example` actualizado con cada cambio de configuración.
* Documentar dependencias nuevas en `requirements.txt`.

---



