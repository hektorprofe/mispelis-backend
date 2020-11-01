# S05 Perfil del usuario

## C01 Presentación

En esta unidad vamos a extender el modelo de usuario agregándole un campo para guardar la imagen de su **avatar**. También implementaremos una nueva `APIView` para gestionar el perfil y permitir al usuario modificar el nick y el avatar.

## C02 Campo avatar

Añadimos el avatar al modelo:

#### **`authentication/models.py`**

```python
def path_to_avatar(instance, filename):                   # new
    return f'avatars/{instance.id}/{filename}'            # new


class CustomUser(AbstractUser):
    # ...
    avatar = models.ImageField(                           # new
        upload_to=path_to_avatar, null=True, blank=True)  # new
```

Migramos la app:

```bash
cd server
pipenv run makemigrations authentication
pipenv run migrate authentication
```

Añadimos el campo al serializador:

#### **`authentication/serializers.py`**

```python
class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True)
    username = serializers.CharField(
        required=True)
    password = serializers.CharField(
        min_length=8, write_only=True)
    avatar = serializers.ImageField(    # new
        required=False)                 # new

    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'password', 'avatar')  # edited
```

Con esto ya tenemos el campo **avatar**. Si vamos a la interfaz web de la API y registramos un nuevo usuario veréis que podemos adjuntar una imagen. Probad a registrar un usuario con un avatar:

```
Email: avatar@avatar.com
Username: avatar
Password: 12345678
Avatar: Imagen que queramos
```

Veréis que funciona bien, el usuario se crea y la imagen se guarda. Pero hay algo interesante, y es que si comprobamos la ruta donde se almacena la imagen, en lugar del **id** tenemos **None**. Esto sucede porque el **id** del usuario no existe en el momento que se registra el usuario. Este escenario se menciona explícitamente en la [documentación](https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.FileField.upload_to) del parámetro **upload_to**, que por cierto os la dejo en los recursos:

```
In most cases, this object will not have been saved to the database yet, so if it uses the default AutoField, it might not yet have a value for its primary key field.
```

Como la clase **User** utiliza efectivamente el **AutoField** incremental para almacenar el **id**, éste no existe. Esto explicaría también porque en el modelo película este error no sucede, pues allí utilizamos un **UUIDField** en lugar del **AutoField** por defecto.

En cualquier caso en la práctica no es algo que deba preocuparnos, porque cuando el usuario quiera modificar su avatar deberá haberse registrado antes.

## C03 Vista de perfil

Para gestionar nuestro perfil debemos proporcionar dos funcionalidades nueva, la de consulta de la información y la de actualización.

DRF cuenta con una vista llamada `RetrieveUpdateAPIView` pensada para tareas de lectura y actualización, os dejo el enlace a la [documentación](https://www.django-rest-framework.org/api-guide/generic-views/#retrieveupdateapiview). Ahí veremos que la vista implementa tres métodos: **GET, POST y PATCH**. Según la documentación de [Mozilla](https://developer.mozilla.org/es/docs/Web/HTTP/Methods) sobre los métodos de las peticiones HTTP:

- El método `GET` solicita una representación de un recurso específico. Las peticiones que usan el método GET sólo deben recuperar datos.
- El método `POST` se utiliza para enviar una entidad a un recurso en específico, causando a menudo un cambio en el estado o efectos secundarios en el servidor.
- El método `PATCH` es utilizado para aplicar modificaciones parciales a un recurso.

Así que vamos a utilizar **GET** para devolver la información de lectura y **PATCH** para manejar la actualización parcial del usuario.

Empezamos creando la vista, asignando el serializador y los métodos que queremos permitir, en nuestro caso manejaremos el usuario así que pasaremos `UserSerializer` y los métodos `GET` y `PATCH`:

#### **`authentication/views.py`**

```python
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    http_method_names = ['get', 'patch']
```

Añadimos la vista a las URL:

#### **`authentication/urls.py`**

```python
from .views import LoginView, LogoutView, SignupView, ProfileView  # edited

urlpatterns = [

    # ...

    # Profile views
    path('user/profile/',
         ProfileView.as_view(), name='user_profile'),
]
```

Si nos identificamos http://localhost:8000/api/auth/login/ y accdemos acceder al perfil http://localhost:8000/api/user/profile/ obtendremos un error:

```
'ProfileView' should either include a `queryset` attribute, or override the `get_queryset()` method.
```

Esto sucede porque la vista no sabe con qué información rellenar el serializador.

Nosotros queremos rellenarlo con la información del usuario, así que podemos hacer uso del método `get_object`, la versión para un único objeto del `get_queryset` y que tome el usuario de la propia petición:

#### **`authentication/views.py`**

```python
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    http_method_names = ['get', 'patch']

    def get_object(self):
        if self.request.user.is_authenticated:
            return self.request.user
```

Si intentamos ahora acceder al perfil ya veremos la información del usuario, sin embargo al modificar algún dato y presionar **PATCH** nos devolverá un error:

```
"avatar": [ "Este campo no puede ser nulo."]
```

Al parecer que `required=False` no es suficiente para quee el avatar puede ser nulo y tenemos que especificarlo manualmente así:

#### **`authentication/serializers.py`**

```python
avatar = serializers.ImageField(
    required=False, allow_null=True)  # edited
```

Ahora sí deberíamos ser capaces de editar los campos del perfil http://localhost:8000/api/user/profile/.

```json
{
  "email": "test@test.com",
  "username": "test",
  "avatar": null
}
```

Pero no vamos a dejarlo así, hay varias cosas que debemos arreglar.

## C04 Puliendo el serializador

Como os decía debemos arreglar algunas cosas, empezando por el hecho de que podemos editar el email y eso no entra en mis planes. En esta API por ahora sólo quiero dar la opción de editar el nombre de usuario, que debe ser único, y el avatar.

Una forma simple de bloquear la edición de un campo es sobreescribir el método **update** del serializador y borrarlo del diccionario de campos validados:

```python
def update(self, instance, validated_data):
    validated_data.pop('email', None)               # prevenimos el borrado
    return super().update(instance, validated_data)  # seguimos la ejecución
```

Como dato el método **create** de un serializador se ejecuta una única vez durante la creación de la instancia, mientras que el **update** se ejecuta siempre que actualizamos algo.

En cualquier caso siguamos mejorando nuestra API, por ejemplo editando el nombre de usuario y poniendo uno de un usuario que ya exista:

```
UNIQUE constraint failed: authentication_customuser.username
```

Como vemos se devuelve un error muy feo. Si el **DEBUG** estubiera desactivado se devolvería un código 500 indicando un error interno del servidor.

Podemos añadir nuestro propio validador para el campo **username** y devolver un error en condiciones sin que explote el servidor por el camino:

#### **`authentication/serializers.py`**

```python
# ...

def validate_password(self, value):
    return make_password(value)

def validate_username(self, value):
    value = value.replace(" ", "")  # Ya que estamos borramos los espacios
    try:
        user = get_user_model().objects.get(username=value)
        # Si es el mismo usuario mandando su mismo username le dejamos
        if user == self.instance:
            return value
    except get_user_model().DoesNotExist:
        return value
    raise serializers.ValidationError("Nombre de usuario en uso")
```

Con esta validación mucho más elegante el servidor devolverá un código **400 Bad Request** con información detallada del error:

```json
"username": ["Nombre de usuario en uso"]
```

En este punto no perdemos nada por agregar otra validación al email, ya que durante el registro si se utiliza un email en uso sucede lo mismo que antes y explota devolviendo un código 500 sin nada de información:

#### **`authentication/serializers.py`**

```python
def validate_email(self, value):
    # Hay un usuario con este email ya registrado?
    try:
        user = get_user_model().objects.get(email=value)
    except get_user_model().DoesNotExist:
        return value
    # En cualquier otro caso la validación fallará
    raise serializers.ValidationError("Email en uso")
```

Con esto ya tenemos nuestro serializador está perfectamente validado y acabamos la unidad.
