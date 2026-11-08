# ClassroomHub

**ClassroomHub** es un portal web didáctico para recursos de aprendizaje y proyectos, desarrollado sobre **Django 6.1.3** y conectado a **MySQL/MariaDB**. Demuestra la arquitectura **MTV** (Model-Template-View), autenticación de usuarios, gestión de sesiones del lado del servidor, grupos y autorización basada en permisos del framework.

---

## 📋 Requisitos Funcionales (Laboratorio 8)

| Código | Requisito | Comprobación | Implementación |
|---|---|---|---|
| **RF01** | Registro público de cuentas normales | El usuario se crea sin privilegios (`is_staff=False`, `is_superuser=False`) | `pages:signup` (`UserCreationForm`) |
| **RF02** | Validación del formulario de registro | Rechazo de contraseñas no coincidentes o nombres repetidos | Validadores integrados de Django |
| **RF03** | Login con herramientas Django | Credenciales válidas crean sesión del lado del servidor | `pages:login` (`LoginView`) |
| **RF04** | Logout mediante POST | Cierre de sesión seguro con protección CSRF | `pages:logout` (`LogoutView`) |
| **RF05** | Catálogo público | `/resources/` es accesible sin requerir autenticación | `pages:resources` (público) |
| **RF06** | Panel privado | `/dashboard/` exige autenticación obligatoria | `pages:dashboard` (`@login_required`) |
| **RF07** | Sesión en funcionamiento | Contador de visitas persistente durante la sesión | `request.session['dashboard_visits']` |
| **RF08** | Grupo de revisión | Grupo `Catalog reviewers` con permiso `pages.view_resource` | `django.contrib.auth.models.Group` |
| **RF09** | Control de acceso en servidor | Usuario sin permiso recibe HTTP 403 en `/resources/review/` | `@permission_required(..., raise_exception=True)` |
| **RF10** | Compatibilidad con MySQL/MariaDB | Base de datos persistente en producción/desarrollo | `django.db.backends.mysql` |
| **RF11** | Pruebas aisladas | Suite de pruebas ejecutada en base descartable | `test_classroom_hub` |

---

## 🌐 Mapa de Rutas de la Aplicación

| Dirección URL | Nombre de Ruta | Acceso Requerido | Descripción |
|---|---|---|---|
| `/` | `pages:home` | Público | Página principal de bienvenida |
| `/resources/` | `pages:resources` | Público | Catálogo general de recursos didácticos |
| `/about/` | `pages:about` | Público | Información sobre el propósito del proyecto |
| `/accounts/signup/` | `pages:signup` | Anónimo | Registro público mediante `UserCreationForm` |
| `/accounts/login/` | `pages:login` | Anónimo | Inicio de sesión mediante `LoginView` (POST con CSRF) |
| `/accounts/logout/` | `pages:logout` | Autenticado | Cierre de sesión seguro (`LogoutView`, solo POST) |
| `/dashboard/` | `pages:dashboard` | Autenticado | Panel privado con contador de sesión (`@login_required`) |
| `/dashboard/summary/` | `pages:dashboard-summary` | Autenticado | Resumen métrico de recursos vía ORM |
| `/resources/review/` | `pages:resource-review` | Autenticado + `pages.view_resource` | Vista restringida de revisión de catálogo (403 para usuarios sin permiso) |
| `/admin/` | `admin:index` | `is_staff=True` | Panel administrativo oficial de Django |

---

## 🔐 Autenticación vs. Autorización

1. **Usuario SQL (`classroomhub_user`):** Utilizado internamente por Django en `settings.py` para conectarse a la base de datos MySQL/MariaDB. Los usuarios del sitio nunca se autentican con este usuario.
2. **Usuario Django (`auth_user`):** Cuentas registradas de visitantes. Las contraseñas se almacenan procesadas con algoritmos seguros de hashing (PBKDF2/SHA256), nunca en texto plano.
3. **Sesión (`django_session` / `sessionid`):** Al autenticarse, Django guarda la sesión en el servidor y entrega una cookie `sessionid` segura al navegador.
4. **Grupo y Permisos (`Catalog reviewers`):** Permite autorizar funciones específicas (como `pages.view_resource`) en el servidor sin otorgar privilegios de administración (`is_staff`).

---

## 👥 Preparación del Grupo de Revisores

### Opción 1: Mediante Django Shell
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from pages.models import Resource
from django.contrib.auth import get_user_model

# 1. Obtener el permiso
content_type = ContentType.objects.get_for_model(Resource)
view_permission = Permission.objects.get(content_type=content_type, codename="view_resource")

# 2. Crear grupo y asociar permiso
reviewers, _ = Group.objects.get_or_create(name="Catalog reviewers")
reviewers.permissions.add(view_permission)

# 3. Asignar un usuario al grupo
User = get_user_model()
user = User.objects.get(username="tu_usuario")
user.groups.add(reviewers)
```

### Opción 2: Mediante Django Admin
1. Ingresa a `http://127.0.0.1:8000/admin/`.
2. Dirígete a **Authentication and Authorization → Groups → Add group**.
3. Nombra el grupo como **Catalog reviewers**.
4. En la lista de permisos disponibles, selecciona **pages | resource | Can view resource** (`view_resource`) y guarda.
5. Edita el usuario deseado y en la sección **Groups** agrégalo a **Catalog reviewers**.

---

## 🛡️ Variables de Entorno y Seguridad

El archivo `.env` almacena las credenciales de la base de datos y la configuración sensible local. Este archivo está protegido en `.gitignore` para no ser incluido en Git:

```env
DB_NAME=classroomhub_db
DB_USER=classroomhub_user
DB_PASSWORD=TuPasswordSeguro
DB_HOST=127.0.0.1
DB_PORT=3306
```

---

## 🧪 Ejecución de Pruebas Automatizadas

La suite incluye **28 pruebas** automatizadas que cubren vistas públicas, modelos, relaciones protegidas, registro con validaciones, login, logout seguro por POST, sesiones y control de acceso 403:

```bash
python manage.py test pages
```

Las pruebas se ejecutan contra la base de datos descartable `test_classroom_hub`, aislando los datos de desarrollo.
