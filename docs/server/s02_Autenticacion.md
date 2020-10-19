# S02 Autenticación

## C01 Presentación

## C02 Entorno y proyecto

Con la carpeta del proyecto **tuspelisdb/** en VSC abrimos una terminal **CMD** en VSC:

```bash
# Instalamos Pipenv
pip install pipenv
```

A continuación:

```bash
# Creamos un entorno instalando Django 3.1.2
pipenv install django==3.1.2
```

Creamos el proyecto:

```bash
# Le llamaremos "server"
pipenv run django-admin startproject server
```

Ahora configuraremos el entorno virtual en VSC abriendo el fichero **manage.py**.

Al abrirlo nos aparecerá en la parte inferior de VSC el intérprete activo, hacemos clic, buscamos uno llamado **server** y lo activamos.

Veremos como a partir de ahora nos aparece **server-XXXXXX** abajo, eso significa que todos los ficheros Python del proyecto se están ejecutando con el intérprete de nuestro entorno virtual.

Inmediatamente después de configurar el entorno, nos pedirá instalar **pylint** en las dependencias, lo hacemos, ya que nos señalará posibles fallos en el código.

Bien, vamos a comprobar si funciona nuestro proyecto:

```bash
cd server
pipenv run python manage.py runserver
```

Si todo funciona podremos acceder a http://127.0.0.1:8000/. Podemos cambiar el idioma del proyecto:

#### **`tuspelisdb/server/settings.py`**

```python
LANGUAGE_CODE = 'es'
```

Justo después de guardar el primer fichero python del proyecto VSC nos pedirá instalar la extensión **autopep8**, la instalamos. Este paquete nos formateará el código automáticamente cumpliendo las pautas definidas en el pep8.

Si todo ha ido bien deberíamos tener **django** ya funcionando en español.

Por último en esta lección vamos a crear unos scripts en nuestro entorno para manejar más fácilmente **django**.

#### **`tuspelisdb/Pipfile`**

```python
[scripts]
server          = "python manage.py runserver"
migrate         = "python manage.py migrate"
startapp        = "python manage.py startapp"
makemigrations  = "python manage.py makemigrations"
createsuperuser = "python manage.py createsuperuser"
```

Cerramos el servicio y testeamos:

```bash
pipenv run server
```

Con esto es suficiente para empezar a programar nuestra API.

## C03 App de autenticación

Vamos a empezar nuestro desarrollo con una **app** que maneje la autenticación, la parte de la API que manejará las funcionalidades de:

- Registrar una cuenta
- Iniciar y cerrar sesión
- Restaurar contraseña

Empezamos por aquí porque la API que vamos a desarrollar es privada, accesible sólo a usuarios registrados e identificados. Nos os preocupéis por esto, ya que eventualmente también veremos cómo librerar una vista y hacerla accesible sin autenticación.

Dicho lo cuál, vamos crear la app de autenticación:

```bash
pipenv run startapp authentication
```

Podéis ponerle cualquier nombre menos **auth** a secas, ya que ese nombre es el de una app interna **django.contrib.auth** y no debemos sobreescribirlo.

La activamos debajo de las **apps** por defecto de Django:

#### **`server/settings.py`**

```python
INSTALLED_APPS = [

    # Django internal apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Django custom apps
    'authentication',
]
```

Antes de ponernos con las vistas vamos a dejar instalado y configurado **Django Rest Framework**, la app que nos permite transformar Django en un servidor de APIs:

```bash
cd server
pipenv install djangorestframework==3.12.1
```

La activamos:

#### **`server/settings.py`**

```python
INSTALLED_APPS = [

    # Django internal apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Django external apps
    'rest_framework',

    # Django custom apps
    'authentication',
]
```

Muy bien, en la siguiente lección vamos a crear el modelo para los usuarios de nuestra aplicación.

## C04 Custom User

El modelo de usuario que trae Django es algo limitado y nosotros necesitamos añadir algunos campos nuevos. Una forma de hacerlo es crear un modelo **Profile** enlazado a cada usuario con los campos que queremos, sin embargo en este curso vamos a hacerlo de una forma más profesional: **personalizar el usuario base**.

**IMPORTANTE**: Antes de continuar es clave no haber creado ningún usuario en la base de datos. Si lo habéis hecho, borrad la base de datos **db.sqlite3** y todos los ficheros del directorio **migrations** excepto los llamados `__init__.py`.

Para extender el modelo de usuario, vamos a crear un **CustomUser** en nuestra app. La diferencia más importante respecto a un usuario "clásico" es que, si bien Django maneja como campo identificador el **username**, nosotros lo identificaremos con el **email**.

#### **`authentication/models.py`**

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(
        max_length=150, unique=True)
```

Según la [documentación](https://docs.djangoproject.com/en/3.1/topics/auth/customizing/#django.contrib.auth.models.CustomUser.USERNAME_FIELD), que os la adjuntaré siempre en los recursos de la lección, para establecer el campo identificador único del **User** tenemos que definir lo siguiente:

#### **`authentication/models.py`**

```python
    USERNAME_FIELD = 'email'  # new
```

Con estos cambios los usuarios podrán iniciar sesión con el correo en lugar de usar su username.

En este punto repasemos los campos obligatorios del formulario de registro:

- Email: que debe ser único y se utilizará como identificador para acceder.
- Username: que también debe ser único y se mostrará en el perfil.
- Password: para la contraseña del usuario.

Según la [documentación](https://docs.djangoproject.com/en/3.1/topics/auth/customizing/#django.contrib.auth.models.CustomUser.REQUIRED_FIELDS), para obligar al usuario a introducir un campo debemos indicarlo en una lista:

#### **`authentication/models.py`**

```python
    REQUIRED_FIELDS = ['username', 'password']  # new
```

Fijaros que hacemos referencia a **username** y **password** pero nunca los definimos. Eso es porque se heredan del **AbstractUser**. De hecho el propio **email** también se hereda, pero como por defecto no es obligatorio ni único, tenemos que cambiar su configuración tal como hemos hecho.

Ahora vamos a decirle a Django que utilice el **CustomUser** en lugar de su modelo genérico:

#### **`server/settings.py`**

```python
# Custom user model
AUTH_USER_MODEL = "authentication.CustomUser"
```

Hacemos la migración inicial junto con nuestra app:

```bash
cd server
pipenv run makemigrations
pipenv run migrate
```

Vamos a crear un usuario admin para acceder a nuestra administración. Si todo va bien debería pedirnos el email como identificador, a parte de un username:

```bash
cd server
pipenv run createsuperuser

> Email: admin@admin.com
> Nombre de usuario: admin
> Contraseña: 1234
> Superuser created successfully.
```

Perfecto, si ponemos en marcha el servidor deberíamos ser capaces de acceder al panel de administración: http://127.0.0.1:8000/admin/

Al hacerlo notaremos no podemos gestionar usuarios automáticamente. Algo entendible al haber creado nuestro propio modelo.

Para tener de el admin hay que configurarlo manualmente como un modelo cualquiera, la ventaja es que podemos heredar el del usuario por defecto.

No entraremos en detalle porque asumo que la mayoría tenéis conocimientos básicos sobre el panel de administrador. Si no es el caso os recomiendo mi otro curso de introducción a Django.

#### **`authentication/admin.py`**

```python
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin


@admin.register(get_user_model())
class CustomUserAdmin(UserAdmin):
    pass
```

En cualquier caso ya deberíamos tener acceso a nuestro modelo para crear, editar y borar usuarios desde el administrador. Y si queréis incluso podemos desactivar los grupos porque no los vamos a utilizar:

#### **`authentication/admin.py`**

```python
from django.contrib.auth.models import Group  # new

admin.site.unregister(Group)  # new
```

Ya estamos listos para empezar con las vistas de la API.

## C05 Login y logout

## C06 Signup

## C07 Reset password

## C08 Portada básica

Hacer que el proyecto sea accesible desde el cliente (tipico cors-headers, podría aparecer Hektor por ahi cuando falla durante el frontend y nos salta el fallo)

**TO DO: Subir al repo con `<tag>` en esta versión**
