# ClassroomHub - Plataforma de Recursos Didácticos

**ClassroomHub** es una aplicación web interactiva orientada al intercambio y consulta de material educativo y proyectos académicos. La plataforma está implementada bajo el framework **Django (v6.1.3)** sobre un motor relacional **MySQL / MariaDB**, siguiendo rigurosamente el patrón de diseño **Modelo-Plantilla-Vista (MTV)**.

El proyecto integra control de acceso basado en roles (RBAC), sesiones persistentes, formularios de validación con `ModelForm`, vistas genéricas basadas en clases (CBV) para operaciones CRUD y un set exhaustivo de 55 pruebas automatizadas.

---

## 📌 Resumen de Capacidades y Objetivos (Labs 06 al 09)

| ID | Capacidad | Comportamiento del Sistema | Componente Asociado |
|:---:|---|---|---|
| **RF01** | Catálogo Abierto | Acceso irrestricto al listado de recursos sin necesidad de inicio de sesión | `pages:resources` |
| **RF02** | Ficha Informativa | Visualización en detalle de un recurso específico y su clasificación | `pages:resource-detail` (`DetailView`) |
| **RF03** | Validación de Entradas | Sanitización de datos y validaciones de negocio en el título vía formulario | `ResourceForm` (`forms.py`) |
| **RF04** | Registro de Material | Creación segura de recursos disponible solo con permiso `pages.add_resource` | `pages:resource-create` (`CreateView`) |
| **RF05** | Actualización de Registros | Modificación de recursos existentes manteniendo la integridad de la clave primaria | `pages:resource-edit` (`UpdateView`) |
| **RF06** | Baja de Recursos | Flujo de borrado en dos etapas: confirmación por GET y ejecución vía POST | `pages:resource-delete` (`DeleteView`) |
| **RF07** | Gestión de Identidad | Registro público de usuarios estándar, autenticación y cierre de sesión seguro | `UserCreationForm`, `LoginView`, `LogoutView` |
| **RF08** | Tablero Personal | Zona privada `/dashboard/` con tracking de visitas mediante variables de sesión | `pages:dashboard` |
| **RF09** | Perfil Revisor | Grupo `Catalog reviewers` con atribuciones de inspección (`pages.view_resource`) | Grupos nativos de Django |
| **RF10** | Perfil Editor | Grupo `Catalog editors` con control total de mantenimiento del catálogo | Permisos CRUD (`add`, `change`, `delete`) |
| **RF11** | Seguridad por Capas | Filtros automáticos: anónimos van a login (302) y no autorizados reciben 403 | `EditorAccessMixin` y decoradores |
| **RF12** | Manejo de Excepciones | Respuestas limpias con código HTTP 404 ante solicitudes de IDs inexistentes | Django 404 Handler |
| **RF13** | Garantía de Calidad | Batería de 55 pruebas ejecutadas en un entorno de pruebas aislado y descartable | `test_classroom_hub` |

---

## 🗺️ Estructura de Rutas y Endpoints

| Ruta URL | Identificador de Ruta | Nivel de Seguridad | Tipo de Vista | Función Principal |
|---|---|---|---|---|
| `/` | `pages:home` | Libre | Función (FBV) | Portal de inicio y bienvenida |
| `/resources/` | `pages:resources` | Libre | Función (FBV) | Listado general de recursos didácticos |
| `/resources/<int:pk>/` | `pages:resource-detail` | Libre | Clase (`DetailView`) | Detalle individual del recurso seleccionado |
| `/resources/new/` | `pages:resource-create` | Usuario con `add_resource` | Clase (`CreateView`) | Formulario para dar de alta nuevo material |
| `/resources/<int:pk>/edit/` | `pages:resource-edit` | Usuario con `change_resource` | Clase (`UpdateView`) | Formulario de edición del material existente |
| `/resources/<int:pk>/delete/` | `pages:resource-delete` | Usuario con `delete_resource` | Clase (`DeleteView`) | Pantalla de confirmación y eliminación |
| `/resources/review/` | `pages:resource-review` | Usuario con `view_resource` | Función (FBV) | Vista especializada para revisión interna |
| `/about/` | `pages:about` | Libre | Función (FBV) | Información general y créditos de la plataforma |
| `/accounts/signup/` | `pages:signup` | Solo anónimos | Función (FBV) | Registro de nuevos usuarios en el sistema |
| `/accounts/login/` | `pages:login` | Solo anónimos | Clase (`LoginView`) | Formulario de autenticación con protección CSRF |
| `/accounts/logout/` | `pages:logout` | Sesión activa (POST) | Clase (`LogoutView`) | Desconexión segura de la cuenta |
| `/dashboard/` | `pages:dashboard` | Requiere login | Función (FBV) | Panel del usuario con contador de actividad |
| `/dashboard/summary/` | `pages:dashboard-summary` | Requiere login | Función (FBV) | Reporte analítico con agregaciones del ORM |
| `/admin/` | `admin:index` | Administrador (`is_staff`) | Interfaz Django Admin | Panel administrativo centralizado |

---

## 🔐 Esquema de Seguridad y Roles de Usuario

El sistema delega la gestión de accesos en el subsistema `django.contrib.auth`:

### Perfiles de Acceso:
1. **Revisores (`Catalog reviewers`)**:
   - Permiso asignado: `pages.view_resource`.
   - Alcance: Pueden consultar la vista protegida de revisión (`/resources/review/`). No poseen facultades para alterar datos.

2. **Editores (`Catalog editors`)**:
   - Permisos asignados: `pages.view_resource`, `pages.add_resource`, `pages.change_resource`, `pages.delete_resource`.
   - Alcance: Tienen acceso irrestricto a los formularios de creación, actualización y baja de registros.

### Inicialización de Grupos en Consola Django:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from pages.models import Resource

# Obtención de permisos del modelo Resource
tipo_contenido = ContentType.objects.get_for_model(Resource)
perm_ver = Permission.objects.get(content_type=tipo_contenido, codename="view_resource")
perm_crear = Permission.objects.get(content_type=tipo_contenido, codename="add_resource")
perm_editar = Permission.objects.get(content_type=tipo_contenido, codename="change_resource")
perm_borrar = Permission.objects.get(content_type=tipo_contenido, codename="delete_resource")

# Creación de grupo Revisores
grupo_revisores, _ = Group.objects.get_or_create(name="Catalog reviewers")
grupo_revisores.permissions.set([perm_ver])

# Creación de grupo Editores
grupo_editores, _ = Group.objects.get_or_create(name="Catalog editors")
grupo_editores.permissions.set([perm_ver, perm_crear, perm_editar, perm_borrar])

# Asignar un usuario al rol de Editor
Usuario = get_user_model()
cuenta_usuario = Usuario.objects.get(username="nombre_de_usuario")
cuenta_usuario.groups.add(grupo_editores)
```

---

## ⚙️ Conectividad y Variables de Entorno

La conexión a la base de datos MySQL/MariaDB se administra mediante desacoplamiento en el archivo `.env`:

```env
DB_NAME=classroomhub_db
DB_USER=classroomhub_user
DB_PASSWORD=TuPasswordSeguro
DB_HOST=127.0.0.1
DB_PORT=3306
```

---

## 🔬 Suite de Pruebas Automatizadas

El proyecto cuenta con **55 casos de prueba unitarios y de integración** que validan la robustez de la lógica de negocio:

- **10 pruebas de Modelos y Relaciones** (Integridad referencial `PROTECT`, representaciones `__str__` y consultas básicas).
- **12 pruebas de Autenticación y Ciclo de Vida de Sesiones** (Altas, inicio de sesión, desconexión por POST, tokens CSRF).
- **6 pruebas de Control de Acceso y Permisos** (Validación de respuestas HTTP 403 y pertenencia a grupos).
- **6 pruebas de Formulario (`ResourceForm`)** (Validaciones estrictas de título, espacios, longitudes y categorías).
- **4 pruebas de Detalle (`ResourceDetailView`)** (Disponibilidad pública y tratamiento de claves inexistentes con 404).
- **6 pruebas de Creación (`ResourceCreateView`)** (Redirección para anónimos, rechazo 403 y altas exitosas).
- **6 pruebas de Edición (`ResourceUpdateView`)** (Blindaje contra modificaciones no autorizadas, preservación de ID y 404).
- **5 pruebas de Eliminación (`ResourceDeleteView`)** (Invariabilidad del modelo bajo peticiones GET, supresión efectiva por POST).

### Instrucciones para Correr la Suite:

```bash
cd classroom-hub
.\.venv\Scripts\Activate.ps1
python manage.py test pages
```

**Salida de éxito esperada:**
```text
Creating test database for alias 'default'...
.......................................................
----------------------------------------------------------------------
Ran 55 tests in ~240s

OK
Destroying test database for alias 'default'...
Found 55 test(s).
```

---

## 🚀 Despliegue Local

Para levantar el servidor de desarrollo local:

```bash
python manage.py runserver
```

Acceso disponible en: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
