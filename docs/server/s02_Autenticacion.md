# S02 Autenticación

## C01 Presentación

En esta unidad vamos a implementar todo el sistema de autenticación de usuarios de nuestra API, el cuál controlará diferentes aspectos como:

- El registro
- El login y logout
- La recuperación de contraseña

Toda nuestra API gira alrededor de este sistema, por eso nos tomaremos el tiempo necesario para explicar cuidadosamente cada paso de su desarrollo. Podéis estar seguros de que lo aprendido aquí os servirá en prácticamente todas vuestras futuras APIs creadas con DRF.

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

Ya estamos listos para empezar con las vistas de la API, pero antes tenemos que tomar una decisión muy importante.

## C05 Sistemas de autenticación

Las APIs REST como la que vamos a crear permiten implementar diferentes protocolos de autenticación. Vamos a repasar brevemente los más famosos:

- **Básica**: Es el método más sencillo pero inseguro, ya que se basa en enviar el usuario y su contraseña codificadas en **Base64** en las cabeceras de cada petición. Tened en cuenta que la codificiación en Base64 es una formalidad y es tan sencillo descodificar una cadena en este formato como pasar el valor a una función de cualquier lenguaje de programación.

```bash
Authorization: Basic base64(username:password)
```

- **API Keys**: Otro sistema bastante utilizado es enviar una **key** facilitada por la API que sustituye las credenciales de un usuario. Muchas APIs públicas ofrecen este sistema porque es fácil añadirle un límite de peticiones diarias, pero en la práctica es sustituir la cadena de autenticación por la clave que se provee a cliente.

```
Authorization: Apikey <key>
```

- **Bearer**: También conocida como _Token Authentication_ se basa en proveer al cliente de un "código" después de identificarse por primera vez. En lugar de enviar todo el rato el usuario y su contraseña, el cliente envía ese código generado por el backend en la cabecera de las peticiones. Es igual de inseguro que la autenticación básica, pero como mínimo no se mandan las credenciales en cada petición.

```
Authorization: Bearer <token>
```

- **JSON Web Tokens**: Los JWT son un estándar abierto de la industria para representar peticiones de forma "segura" entre dos partes. Este sistema añade una capa extra de seguridad en los tokens, con mecanismos de decodificación, verificación y renovación de los mismos.

```
Authorization: Bearer <JWT token>
```

- **OAuth2**: Este sistema de autenticación permite compartir información entre sitios sin compartir las credenciales del usuario. En lugar de generar el token en nuestro backend se delega este proceso una plataforma de terceros, de manera que no necesitamos almacenar el usuario y la contraseña en la base de datos. Oauth2 es muy cómodo, pero si tenemos interés en almacenar información del usuario en nuestra base de datos igualmente necesitaremos implementar un sistema de usuarios y pedirle la información a esas plataformas de terceros. Casi nunca se utiliza como sistema único de autenticación, sino como apoyo de nuestro propio sistema.

```
Authorization: Bearer <Oauth2 token>
```

Con esto hemos cubierto prácticamente todos los sistemas de autenticación. ¿Cuál vamos a utilizar? Pues... ninguno de ellos.

Veréis, la gracia de las APIs es que permiten separar la lógica del servidor y la del cliente. Sin embargo esto tiene un problema inherente y es que los clientes deben almacenar las credenciales de acceso en la memoria para poder enviarlas en las peticiones.

Que la información se encuentre almacenada en el cliente implica un defecto de facto en un cliente web y es que esas credenciales SIEMPRE son accesibles a través de JavaScript y por tanto son vulnerables a ser accedidas utilizando ataques XSS (Cross-site Scripting).

Por tanto el problema radica en la propia naturaleza de JavaScript... ¿Cómo lo solucionamos? Pues haciendo inaccesibles las credenciales en el cliente.

Espera espera Héctor... ¿Eso se puede hacer? ¿Cómo va a enviar las credenciales el cliente si no tiene acceso a ellas? La respuesta está en las **cookies**.

Ya sé lo que estáis pensando algunos... las cookies también son accesibles desde Javascript y por tanto vulnerables a ataques XSS, así que no vamos a solucionar nada. Por suerte para nosotros existe una cláusula en las cookies llamada **HttpOnly**. Esta opción hace que las cookies sean inaccesibles desde JavaScript y el navegador las recibe y envía automáticamente al servidor.

Mezclando el sistema de autenticación clásico de Django basado en cookies de sesión, junto con la cláusula **HttpOnly** y sus tokens **CSRF**, lograremos un sistema robusto, seguro y lo mejor de todo... muy fácil de implementar.

## C06 Login y logout

Vamos a empezar creando unas vistas básicas de **login** y **login** sobre una **APIView** básica de DRF. La forma de implementar la lógica es exactamente igual que con Django clásico, os dejo el enlace a la [documentación oficial](https://docs.djangoproject.com/en/3.1/topics/auth/default/#how-to-log-a-user-in) por si queréis profundizar:

#### **`authentication/views.py`**

```python
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class LoginView(APIView):
    def post(self, request):
        # Recuperamos las credenciales y autenticamos al usuario
        email = request.data.get('email', None)
        password = request.data.get('password', None)
        user = authenticate(email=email, password=password)

        # Si es correcto añadimos a la request la información de sesión
        if user:
            login(request, user)
            return Response(
                status=status.HTTP_200_OK)

        # Si no es correcto devolvemos un error en la petición
        return Response(
            status=status.HTTP_404_NOT_FOUND)


class LogoutView(APIView):
    def post(self, request):
        # Borramos de la request la información de sesión
        logout(request)

        # Devolvemos la respuesta al cliente
        return Response(status=status.HTTP_200_OK)
```

Configuramos las dos URL en la app:

#### **`authentication/urls.py`**

```python
from django.urls import path, include
from .views import LoginView, LogoutView

urlpatterns = [
    # Auth views
    path('auth/login/',
         LoginView.as_view(), name='auth_login'),

    path('auth/logout/',
         LogoutView.as_view(), name='auth_logout'),
]
```

Y configuramos las URL de la app en el proyecto:

#### **`server/urls.py`**

```python
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

# Api router
router = routers.DefaultRouter()

urlpatterns = [
    # Admin routes
    path('admin/', admin.site.urls),

    # Api routes
    path('api/', include('authentication.urls')),
    path('api/', include(router.urls)),
]
```

Con esta estructura tenemos dos endpoints:

- `/api/auth/login/`
- `/api/auth/logout/`

En la siguiente lección probaremos si funcionan correctamente.

## C07 Probando la autenticación

Ha llegado la hora de probar la API, la forma más fácil es desde la interfaz que nos provee DRF.

Acceded a la URL de **login** http://localhost:8000/api/auth/login/ y escribid las credenciales en crudo como si fuera un objeto JSON:

```json
{ "email": "admin@admin.com", "password": "1234" }
```

Si todo funciona correctamente al enviar el formulario veréis la respuesta de la API y saldrá vuestro email arriba a la derecha indicando que efectivamente estamos identificados:

```json
{ "login": "success" }
```

Para probar el **logout**, estando identificados, accedemos a la URL pertinente http://localhost:8000/api/auth/logout/ y al enviar el formulario vacío debería hacernos lo propio:

```json
{ "logout": "success" }
```

Si nos logeamos ahora nos devolverá la información que hemos establecido en el serializador:

```json
{
  "email": "admin@admin.com",
  "username": "admin",
  "password": "pbkdf2_sha...."
}
```

Como el campo password no nos interesa serializado vamos a establecer una clásula de sólo escritura, para que Django sólo lo tenga en cuenta al crear o modificar, pero nunca al hacer una lectura:

```python
password = serializers.CharField(
    min_length=8, write_only=True)
```

## C08 Serializando el usuario

Uno de los requisitos del frontend es que justo después de identificarnos la API debe enviar información básica del usuario para utilizarla en la aplicación, como por ejemplo el nombre, el email o más adelante el avatar.

Cuando nos autenticamos conseguimos un objeto **user** con toda esa información, pero no podemos enviarlo al cliente y ya está, necesitamos transformarlo a un objeto JSON. Ese proceso de transformar el objeto de un formato a otro, Python a Javascript en nuestro caso, se conoce como seralización.

DRF permite crear serializadores de modelos para automatizar esta tarea, así que vamos a crear nuestro propio serializador de usuarios:

#### **`authentication/serializers.py`**

```python
from rest_framework import serializers
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True)
    username = serializers.CharField(
        required=True)
    password = serializers.CharField(
        min_length=8)

    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'password')
```

Este serializador básico, a parte de controlar los campos que queremos serializar de Python a JSON, también nos servirá más adelante para configurar métodos como la creación de usuarios durante el registro y la validación personalizada de campos.

Sea como sea vamos a serializar el objeto **user** y a enviarlo como respuesta de la petición de login:

#### **`authentication/views.py`**

```python
from .serializers import UserSerializer

# ...

return Response(
    UserSerializer(user).data,
    status=status.HTTP_200_OK)
```

## C09 Signup

## C10 Reset password

## C11 Portada básica

Hacer que el proyecto sea accesible desde el cliente (tipico cors-headers, podría aparecer Hektor por ahi cuando falla durante el frontend y nos salta el fallo)

**TO DO: Subir al repo con `<tag>` en esta versión**
