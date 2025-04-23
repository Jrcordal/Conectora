# CV App Django

Esta es una aplicación web desarrollada con Django que permite a los usuarios crear y gestionar sus perfiles profesionales y generar un currículum vitae (CV) en formato PDF. Los administradores tienen la capacidad de ver y descargar los CV de todos los usuarios.

## Características

*   **Registro y Autenticación de Usuarios:** Los usuarios pueden crear cuentas, iniciar y cerrar sesión.
*   **Gestión de Perfiles:** Los usuarios pueden completar y actualizar su perfil con información personal, académica, experiencia laboral, habilidades y proyectos.
*   **Generación de CV en PDF:** Los usuarios pueden descargar su perfil como un CV en formato PDF.
*   **Vista de Administrador:** Los usuarios administradores (staff/superuser) pueden ver una lista de todos los perfiles y descargar el CV de cualquier usuario.
*   **Subida de Imágenes:** Los usuarios pueden subir una foto de perfil.

## Estructura del Proyecto

```
.
├── .venv/                  # Entorno virtual de Python
├── db/                     # Carpeta principal del proyecto Django
│   ├── db/                 # Carpeta de configuración del proyecto
│   │   ├── __init__.py
│   │   ├── settings.py     # Configuración principal de Django
│   │   ├── urls.py         # URLs principales del proyecto
│   │   ├── wsgi.py         # Configuración WSGI
│   │   ├── asgi.py         # Configuración ASGI
│   │   └── .env            # Archivo para variables de entorno (ej. SECRET_KEY)
│   ├── users/              # App de Django para usuarios y perfiles
│   │   ├── __init__.py
│   │   ├── admin.py        # Configuración del panel de admin para modelos de 'users'
│   │   ├── apps.py         # Configuración de la app 'users'
│   │   ├── forms.py        # Formularios (Registro, Perfil)
│   │   ├── migrations/     # Migraciones de la base de datos para 'users'
│   │   ├── models.py       # Modelos de datos (Profile)
│   │   ├── signals.py      # Señales (ej. crear perfil al registrar usuario)
│   │   ├── static/         # Archivos estáticos (CSS, JS, imágenes)
│   │   ├── templates/      # Plantillas HTML para la app 'users'
│   │   │   └── users/
│   │   │       ├── base.html
│   │   │       ├── cv.html
│   │   │       ├── cv_clean.html   # Plantilla para generar el PDF
│   │   │       ├── cv_generator.html # Formulario para editar perfil
│   │   │       ├── list.html       # Lista de perfiles (admin)
│   │   │       ├── login.html
│   │   │       ├── logout.html
│   │   │       └── register.html
│   │   └── views.py        # Vistas (lógica de la aplicación)
│   ├── pictures/           # Carpeta para guardar las imágenes de perfil subidas (MEDIA_ROOT)
│   ├── db.sqlite3          # Base de datos SQLite (desarrollo)
│   └── manage.py           # Utilidad de línea de comandos de Django
├── .git/                   # Carpeta de Git (si se usa control de versiones)
├── requirements.txt        # Dependencias de Python
└── README.md               # Este archivo
```

## Instalación y Ejecución

1.  **Clonar el repositorio (si aplica):**
    ```bash
    git clone <url-del-repositorio>
    cd <nombre-del-directorio>
    ```
2.  **Crear y activar un entorno virtual:**
    ```bash
    python -m venv .venv
    # Windows (PowerShell)
    .\.venv\Scripts\Activate.ps1
    # macOS/Linux
    source .venv/bin/activate
    ```
3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Instalar wkhtmltopdf:** Esta aplicación requiere `wkhtmltopdf` para generar los PDFs. Descárgalo e instálalo desde [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html). Asegúrate de que el ejecutable esté en tu PATH del sistema o actualiza la ruta en `db/users/views.py` (en la función `cv_pdf`).
    ```python
    # Ejemplo en db/users/views.py (ajusta la ruta si es necesario)
    config = pdfkit.configuration(wkhtmltopdf = r'C:\\wkhtmltox\\bin\\wkhtmltopdf.exe')
    ```
5.  **Configurar variables de entorno (opcional):** Si planeas usar el archivo `.env` para `SECRET_KEY` o `DEBUG` en producción, asegúrate de crearlo en `db/db/.env`. Para desarrollo, los valores por defecto en `settings.py` pueden ser suficientes.
6.  **Aplicar migraciones:**
    ```bash
    cd db
    python manage.py migrate
    ```
7.  **Crear un superusuario (administrador):**
    ```bash
    python manage.py createsuperuser
    ```
    Sigue las instrucciones para crear tu cuenta de administrador.
8.  **Ejecutar el servidor de desarrollo:**
    ```bash
    python manage.py runserver
    ```
9.  Abre tu navegador y ve a `http://127.0.0.1:8000/`.

## Configuración Clave (`db/db/settings.py`)

*   **`SECRET_KEY`:** Clave secreta de Django. Para desarrollo se usa una insegura, pero debe configurarse de forma segura (preferiblemente con variables de entorno) para producción.
*   **`DEBUG`:** Activado (`True`) para desarrollo, muestra errores detallados. Debe ser `False` en producción.
*   **`ALLOWED_HOSTS`:** Lista de hosts/dominios permitidos para servir la aplicación. Actualmente configurado para `localhost` y `127.0.0.1`.
*   **`INSTALLED_APPS`:** Lista de aplicaciones Django instaladas. Incluye las apps por defecto de Django y la app `users`.
*   **`DATABASES`:** Configuración de la base de datos. Por defecto utiliza SQLite (`db.sqlite3`).
*   **`STATIC_URL`:** URL base para los archivos estáticos (`/static/`).
*   **`MEDIA_ROOT`:** Ruta del sistema de archivos donde se guardan los archivos subidos por los usuarios (imágenes de perfil). Apunta a la carpeta `db/pictures/`.
*   **`MEDIA_URL`:** URL base para servir los archivos de `MEDIA_ROOT` (`/pictures/`).
*   **`LOGIN_REDIRECT_URL`:** URL a la que se redirige al usuario después de iniciar sesión correctamente (redirige a la vista del CV del usuario).
*   **`LOGIN_URL`:** URL de la página de inicio de sesión (`/login/`).

## Dependencias Clave

*   **Django:** Framework web.
*   **Pillow:** Para manejo de imágenes (fotos de perfil).
*   **pdfkit:** Wrapper para `wkhtmltopdf` para generar PDFs desde HTML.
*   **python-dotenv:** Para cargar variables de entorno desde un archivo `.env`.
*   **beautifulsoup4 (bs4):** Probablemente usada para procesar HTML (aunque no se ve su uso explícito en el código proporcionado recientemente).
*   **phonenumbers:** Librería para validar números de teléfono (actualmente comentada en el código).

## Notas

*   El proyecto utiliza SQLite como base de datos por defecto, ideal para desarrollo. Para producción, considera cambiar a PostgreSQL, MySQL u otra base de datos más robusta en `db/db/settings.py`.
*   La generación de perfiles está automatizada para usuarios normales (no superusuarios) mediante señales en `db/users/signals.py`.
*   La autorización se maneja con decoradores `@login_required` y comprobaciones `request.user.is_staff`. 