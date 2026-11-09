# ClassroomHub

**ClassroomHub** es un portal web didáctico para recursos de aprendizaje y proyectos, desarrollado sobre **Django 6.1.3** y conectado a **MySQL/MariaDB**. Demuestra la arquitectura **MTV** (Model-Template-View), autenticación de usuarios, gestión de sesiones del lado del servidor, grupos, permisos del framework y un **CRUD completo** con vistas basadas en clases (CBV) y `ModelForm`.

---

## 📋 Requisitos Funcionales (Laboratorios 06, 07, 08 y 09)

| Código | Requisito | Comprobación | Implementación |
|---|---|---|---|
| **RF01** | Catálogo público | `/resources/` accesible sin requerir sesión | `pages:resources` |
| **RF02** | Detalle de recurso | Consulta pública de un recurso y su categoría | `pages:resource-detail` (`DetailView`) |
| **RF03** | Formulario `ModelForm` | Validación y sanitización del título (`clean_title`) | `ResourceForm` (`pages/forms.py`) |
| **RF04** | Creación de recursos | Alta de recursos protegida con `pages.add_resource` | `pages:resource-create` (`CreateView`) |
| **RF05** | Edición de recursos | Modificación sin duplicar PK ni crear registros nuevos | `pages:resource-edit` (`UpdateView`) |
| **RF06** | Eliminación de recursos | Confirmación previa por GET y eliminación por POST | `pages:resource-delete` (`DeleteView`) |
| **RF07** | Registro y autenticación | Registro de usuarios comunes sin privilegios y Login/Logout | `UserCreationForm`, `LoginView`, `LogoutView` |
| **RF08** | Panel privado | `/dashboard/` con contador de visitas en sesión | `pages:dashboard` (`@login_required`) |
| **RF09** | Grupo Revisor | `Catalog reviewers` con permiso `pages.view_resource` | `django.contrib.auth.models.Group` |
| **RF10** | Grupo Editor | `Catalog editors` con permisos completos de CRUD | `add_resource`, `change_resource`, `delete_resource` |
| **RF11** | Control de acceso en servidor | Anónimos redirigidos a login (302), no autorizados reciben 403 | `EditorAccessMixin` + decoradores |
| **RF12** | Manejo de registros inexistentes | Solicitudes a recursos que no existen responden HTTP 404 | Manejador 404 de Django |
| **RF13** | Pruebas aisladas | Suite de 55 pruebas ejecutadas en base descartable | `test_classroom_hub` |

---

## 🌐 Mapa de Rutas de la Aplicación

| Dirección URL | Nombre de Ruta | Permiso / Acceso Requerido | Vista / Tipo | Descripción |
|---|---|---|---|---|
| `/` | `pages:home` | Público | `views.home` (FBV) | Página principal de bienvenida |
| `/resources/` | `pages:resources` | Público | `views.resources` (FBV) | Catálogo general de recursos didácticos |
| `/resources/<int:pk>/` | `pages:resource-detail` | Público | `ResourceDetailView` (CBV) | Vista de detalle de un recurso |
| `/resources/new/` | `pages:resource-create` | Autenticado + `add_resource` | `ResourceCreateView` (CBV) | Formulario de creación de recurso |
| `/resources/<int:pk>/edit/` | `pages:resource-edit` | Autenticado + `change_resource` | `ResourceUpdateView` (CBV) | Formulario de edición de recurso |
| `/resources/<int:pk>/delete/` | `pages:resource-delete` | Autenticado + `delete_resource` | `ResourceDeleteView` (CBV) | Confirmación y eliminación de recurso |
| `/resources/review/` | `pages:resource-review` | Autenticado + `view_resource` | `views.resource_review` (FBV) | Revisión de catálogo para revisores |
| `/about/` | `pages:about` | Público | `views.about` (FBV) | Información del proyecto |
| `/accounts/signup/` | `pages:signup` | Anónimo | `views.signup` (FBV) | Registro de nuevas cuentas |
| `/accounts/login/` | `pages:login` | Anónimo | `LoginView` (CBV) | Inicio de sesión con CSRF |
| `/accounts/logout/` | `pages:logout` | Autenticado (POST) | `LogoutView` (CBV) | Cierre de sesión seguro |
| `/dashboard/` | `pages:dashboard` | Autenticado | `views.dashboard` (FBV) | Panel privado con contador de sesión |
| `/dashboard/summary/` | `pages:dashboard-summary` | Autenticado | `views.dashboard_summary` (FBV) | Métricas agregadas con ORM |
| `/admin/` | `admin:index` | `is_staff=True` | Django Admin | Administración general de modelos |

---

## 👥 Configuración de Grupos y Permisos

### 1. `Catalog reviewers` (Solo lectura de revisión)
- Permisos: `pages.view_resource`.
- Capacidad: Acceder a `/resources/review/`. No puede crear, editar ni eliminar recursos.

### 2. `Catalog editors` (Gestión completa del catálogo)
- Permisos:
  - `pages.view_resource`
  - `pages.add_resource`
  - `pages.change_resource`
  - `pages.delete_resource`
- Capacidad: Crear (`/resources/new/`), editar (`/resources/<pk>/edit/`) y eliminar (`/resources/<pk>/delete/`).

### Configuración desde Django Shell:
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from pages.models import Resource
from django.contrib.auth import get_user_model

content_type = ContentType.objects.get_for_model(Resource)
p_view = Permission.objects.get(content_type=content_type, codename="view_resource")
p_add = Permission.objects.get(content_type=content_type, codename="add_resource")
p_change = Permission.objects.get(content_type=content_type, codename="change_resource")
p_delete = Permission.objects.get(content_type=content_type, codename="delete_resource")

# Grupo Revisores
reviewers, _ = Group.objects.get_or_create(name="Catalog reviewers")
reviewers.permissions.set([p_view])

# Grupo Editores
editors, _ = Group.objects.get_or_create(name="Catalog editors")
editors.permissions.set([p_view, p_add, p_change, p_delete])

# Asignar a un usuario
User = get_user_model()
editor_user = User.objects.get(username="tu_usuario")
editor_user.groups.add(editors)
```

---

## 🛠️ Entorno y Conexión a Base de Datos

ClassroomHub utiliza **MySQL / MariaDB** configurado mediante variables de entorno en `.env`:

```env
DB_NAME=classroomhub_db
DB_USER=classroomhub_user
DB_PASSWORD=TuPasswordSeguro
DB_HOST=127.0.0.1
DB_PORT=3306
```

---

## 🧪 Ejecución de la Suite de Pruebas

ClassroomHub cuenta con **55 pruebas automatizadas**:
- **10 pruebas** del Laboratorio 07 (Modelos, relaciones `PROTECT`, representaciones y vistas).
- **12 pruebas** de Autenticación y Sesiones (Registro, validación, login, logout POST, CSRF).
- **6 pruebas** de Permisos y Revisión de Catálogo (HTTP 403, grupos).
- **6 pruebas** de `ResourceForm` (Validación de título, longitud mínima, espacios en blanco, categorías).
- **4 pruebas** de `ResourceDetailView` (Consulta pública, contenido, 404 para inexistentes).
- **6 pruebas** de `ResourceCreateView` (Redirección anónima, 403 para usuarios sin permiso, alta exitosa y errores).
- **6 pruebas** de `ResourceUpdateView` (Protección 403, persistencia sin duplicar PK, 404 en edición).
- **5 pruebas** de `ResourceDeleteView` (Protección 403, GET no elimina, POST elimina y redirige).

Para ejecutar las 55 pruebas en la base descartable `test_classroom_hub`:

```bash
cd classroom-hub
.\.venv\Scripts\Activate.ps1
python manage.py test pages
```

**Resultado esperado:**
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

## 💻 Ejecución del Servidor Local

```bash
python manage.py runserver
```

Abre en tu navegador: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
