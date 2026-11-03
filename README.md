# ClassroomHub

**ClassroomHub** es un portal web didáctico para recursos de aprendizaje y proyectos, desarrollado como parte del Laboratorio 6 (Fundamentos de Django y primera aplicación web). Su objetivo es demostrar y afianzar la arquitectura **MTV** (Model-Template-View) y el flujo de trabajo de Django: **URL → vista → plantilla → respuesta**.

---

## 📋 Requisitos Funcionales (RF01 – RF07)

| Código | Requisito | Comprobación | Implementación |
|---|---|---|---|
| **RF01** | Abrir la página principal | `GET /` muestra encabezado y bienvenida | `pages/views.py` (`home`), `pages/templates/pages/home.html` |
| **RF02** | Consultar los recursos | `GET /resources/` muestra la lista de recursos | `pages/views.py` (`resources`), `pages/templates/pages/resources.html` |
| **RF03** | Consultar información del sitio | `GET /about/` muestra el propósito | `pages/views.py` (`about`), `pages/templates/pages/about.html` |
| **RF04** | Navegar entre páginas | Los enlaces funcionan desde cualquier página | Barra `<nav>` común en `pages/templates/pages/base.html` con etiquetas `{% url %}` |
| **RF05** | Reutilizar el diseño | Las tres páginas heredan de `base.html` | `{% extends "pages/base.html" %}` en `home.html`, `resources.html` y `about.html` |
| **RF06** | Distinguir disponibilidad | Cada recurso muestra su estado | Bloque `{% if resource.available %}` en `pages/templates/pages/resources.html` |
| **RF07** | Responder a rutas inexistentes | Una dirección desconocida produce `404` | Enrutador de Django devuelve HTTP `404 Not Found` en rutas no declaradas |

---

## 🛠️ Tecnologías y Versiones

- **Python**: 3.12, 3.13, 3.14 o 3.15
- **Django**: 6.1.3
- **Otras dependencias**: `asgiref`, `sqlparse`, `tzdata` (registradas en `requirements.txt`)

---

## 🚀 Instalación y Puesta en Marcha

### 1. Clonar el repositorio y acceder a la carpeta
```bash
cd classroom-hub
```

### 2. Crear y activar el entorno virtual

- **En Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
  *(O ejecutar directamente usando `.\.venv\Scripts\python.exe`)*

- **En Linux / macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Instalar dependencias
```bash
python -m pip install -r requirements.txt
```

### 4. Verificar la configuración del proyecto
```bash
python manage.py check
```

---

## 🧪 Ejecución de Pruebas Automatizadas

El proyecto incluye pruebas automatizadas con `SimpleTestCase` para verificar los códigos de respuesta HTTP, las plantillas utilizadas, el contenido renderizado y los enlaces de navegación:

```bash
python manage.py test pages
```

---

## 💻 Ejecutar el Servidor de Desarrollo

Inicia el servidor local de Django con:

```bash
python manage.py runserver
```

Abre tu navegador en [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## 🌐 Rutas Públicas Disponibles

| Dirección URL | Vista | Descripción |
|---|---|---|
| `/` | `home` | Página principal de bienvenida |
| `/resources/` | `resources` | Catálogo de recursos didácticos de aprendizaje |
| `/about/` | `about` | Información acerca del propósito del proyecto |

Cualquier dirección no registrada (por ejemplo `/not-found/`) devolverá una respuesta HTTP `404 Not Found`.

---

## 📁 Estructura del Proyecto

```text
classroom-hub/
├── .gitignore
├── README.md
├── requirements.txt
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── pages/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── migrations/
    │   └── __init__.py
    ├── models.py
    ├── tests.py
    ├── urls.py
    ├── views.py
    └── templates/
        └── pages/
            ├── base.html
            ├── home.html
            ├── resources.html
            └── about.html
```

---

## ⚠️ Funcionalidades que aún no incluye

Este laboratorio se enfoca exclusivamente en rutas, vistas y plantillas:
- **No incluye base de datos propia ni modelos ORM** (los datos de recursos son listas de diccionarios en memoria dentro de `views.py`).
- **No incluye formularios ni procesamiento de solicitudes POST**.
- **No incluye autenticación ni sesiones de usuario**.
- **No incluye operaciones CRUD**.

Estas características se abordarán en los siguientes laboratorios (a partir del Laboratorio 7).
