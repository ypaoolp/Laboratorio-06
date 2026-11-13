# ClassroomHub - Plataforma de Recursos Didácticos

**ClassroomHub** es una aplicación web interactiva orientada al intercambio y consulta de material educativo y proyectos académicos. La plataforma está implementada bajo el framework **Django (v6.1.3)** sobre un motor relacional **MySQL / MariaDB**, siguiendo rigurosamente el patrón de diseño **Modelo-Plantilla-Vista (MTV)**.

El proyecto integra control de acceso basado en roles (RBAC), sesiones persistentes, formularios de validación con `ModelForm`, vistas genéricas basadas en clases (CBV) para operaciones CRUD y un set exhaustivo de 55 pruebas automatizadas.

---


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
