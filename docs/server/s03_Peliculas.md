# S03 Películas y géneros

## C01 Presentación

En esta unidad crearemos la segunda app del proyecto, encargada de manejar las películas y sus géneros. También veremos cómo proteger las vistas haciéndolas privadas y os facilitaré una base de datos con docenas de películas ya creadas.

## C02 App Films

Creamos la app:

```bash
cd server
pipenv run startapp films
```

La activamos:

#### **`server/settings.py`**

```python
INSTALLED_APPS = [
    # Django custom apps
    'authentication',
    'films',
]
```

Vamos a crear dos modelos, uno para las películas y otro para sus géneros. Cada película podrá tener varios géneros, por lo que usaremos un modelo dentro de otro:

#### **`films/models.py`**

```python
import uuid
from django.db import models
from django.utils.text import slugify


class Film(models.Model):

    id = models.UUIDField(  # uuid en lugar de id clásica autoincremental
        primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        max_length=150, verbose_name="Título")
    year = models.PositiveIntegerField(
        default=2000, verbose_name="Año")
    review_short = models.TextField(
        null=True, blank=True, verbose_name="Argumento (corto)")
    review_large = models.TextField(
        null=True, blank=True, verbose_name="Historia (largo)")
    trailer_url = models.URLField(
        max_length=150, null=True, blank=True, verbose_name="URL youtube")
    genres = models.ManyToManyField(
        'FilmGenre', related_name="film_genres", verbose_name="Géneros")

    class Meta:
        verbose_name = "Película"
        ordering = ['title']

    def __str__(self):
        return f'{self.title} ({self.year})'


class FilmGenre(models.Model):
    name = models.CharField(
        max_length=50, verbose_name="Nombre", unique=True)
    slug = models.SlugField(
        unique=True)

    class Meta:
        verbose_name = "género"
        ordering = ['name']

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(FilmGenre, self).save(*args, **kwargs)
```

Damos de alta los modelos en el panel de administrador para gestionarlos:

#### **`films/admin.py`**

```python
from django.contrib import admin
from .models import Film, FilmGenre


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    pass


@admin.register(FilmGenre)
class FilmGenreAdmin(admin.ModelAdmin):
    readonly_fields = ["slug"]
```

Hacemos las migraciones y migramos la app:

```bash
cd server
pipenv run makemigrations films
pipenv run migrate films
```

Con esto ya tenemos los modelos preparados, sin embargo en la siguiente lección nos tomaremos un rato para añadir un par de campos para almacenar unas imágenes en nuestras películas.

## C03 Miniaturas y wallpapers

En esta lección vamos a añadir dos imágenes a las películas, una miniatura con la carátula y otra con un fondo de pantalla. Quedarán genial en el cliente web, ya veréis.

Si queremos almacenar ficheros en los modelos tenemos que configurar los ficheros **media**:

#### **`server/settings.py`**

```python
import os

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # path al directorio local
MEDIA_URL = 'http://localhost:8000/media/'    # url para el desarrollo
```

Según nuestra configuración los ficheros **media** se almacenarán en un directorio con ese mismo nombre, ubicado en la raiz del proyecto de Django. Lo creamos:

```bash
cd server
mkdir media
```

A continuación tenemos que hacer que el servidor de **Django** sirva los ficheros del directorio **media** o no podremos ver las imágenes:

#### **`server/urls.py`**

```python
from django.conf import settings
from django.conf.urls.static import static

# ...

# Serve static files in development server
if settings.DEBUG:
    urlpatterns += static('/media/', document_root=settings.MEDIA_ROOT)
```

Esta configuración es sólo para la fase de desarrollo, en producción los ficheros los servirá un servidor especializado como **Nginx** o **Apache**.

Ya estamos listos para añadir nuestros dos campos de imágenes:

#### **`films/models.py`**

```python
image_thumbnail = models.ImageField(
    upload_to='films/', null=True, blank=True, verbose_name="Miniatura")
image_wallpaper = models.ImageField(
    upload_to='films/', null=True, blank=True, verbose_name="Wallpaper")
```

Sin embargo de esta forma todas las imágenes de las películas se guardarán en el mismo directorio y eso no es muy eficiente.

Una mejor aproximación es crear una carpeta para cada modelo usando algún campo. En nuestro caso podríamos usar el identificador de la película:

Para conseguirlo implementaremos un método que devuelva el path final al campo **upload_to**. El truco está en que se envían implícitamente la instancia y el nombre del fichero para que podamos generar la estructura que deseemos:

#### **`films/models.py`**

```python
class Film(models.Model):

    def path_to_film(self, instance, filename):
        return f'films/{instance.id}/{filename}'

    # ...

    image_thumbnail = models.ImageField(
        upload_to=path_to_film, null=True, blank=True, verbose_name="Miniatura")
    image_wallpaper = models.ImageField(
        upload_to=path_to_film, null=True, blank=True, verbose_name="Wallpaper")
```

Una vez actualizado el modelo creamos de nuevo las migraciones:

```bash
cd server
pipenv run makemigrations films
pipenv run migrate films
```

Nos saltará un error:

```
Cannot use ImageField because Pillow is not installed.
```

Django necesita el módulo **Pillow** para manipular imágenes, así que vamos a instalarlo (puede tardar un poco). Luego migramos de nuevo:

```bash
cd server
pipenv install Pillow==8.0.1
pipenv run makemigrations films
pipenv run migrate films
pipenv run server
```

Si todo ha funcionado correctamente ya deberíamos crear correctamente películas con imágenes y acceder a ellas en el servidor de pruebas.

## C04 ViewSets y Serializers

En esta lección vamos a programar el endpoint para consultar las películas de nuestra API.

En Django generalmente necesitamos dos vistas para gestionar un modelo: una **ListView** para listar múltiples instancias y una **DetailView** para gestionar una única instancia del modelo.

Pues DRF permite combinar la lógica de ambas vistas en lo que ellos denominan un **ViewSet** o literalmente conjunto de vistas, os dejaré [documentación](https://www.django-rest-framework.org/api-guide/viewsets/) en los recursos.

Un **ViewSet** gira entorno a un modelo y su serializador, así que vamos a empezar creando unos serializadorres básicos para las película y los géneros:

#### **`films/serializers.py`**

```python
from rest_framework import serializers
from .models import Film, FilmGenre


class FilmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = '__all__'


class FilmGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilmGenre
        fields = '__all__'
```

Como véis son muy simples, les pasamos el modelo y les indicamos devuelvan todos los campos con `__all__` en los fields.

Con esto podemos crear unos **viewsets** básicos:

#### **`films/views.py`**

```python
from rest_framework import viewsets
from .models import Film, FilmGenre
from .serializers import FilmSerializer, FilmGenreSerializer


class FilmViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FilmGenre.objects.all()
    serializer_class = FilmGenreSerializer
    lookup_field = 'slug'  # identificaremos los géneros usando su slug
```

Como véis estamos utilizando unos **viewsets** de tipo `ReadOnlyModelViewset`, cuya particularidad como podéis suponer, es que ofrecen acciones de lectura. Eso es porque no necesitamos que nuestros clientes puedan crear, editar o borrar películas y géneros, ya que son acciones protegidas sólo disponibles a los administradores de la API. Os dejaré [documentación](https://www.django-rest-framework.org/api-guide/viewsets/#readonlymodelviewset) sobre este tipo de **viewset** en los recursos.

Sea como sea sólo falta dar de alta los viewsets en el **router**:

#### **`server/urls.py`**

```python
from films import views as film_views

# Api router
router = routers.DefaultRouter()
router.register('films', film_views.FilmViewSet, basename='Film')
router.register('genres', film_views.GenreViewSet, basename='FilmGenre')
```

Y ya podremos navegar por los viewsets de nuestra API:

- http://127.0.0.1:8000/api/
- http://127.0.0.1:8000/api/films/
- http://127.0.0.1:8000/api/films/:id/
- http://127.0.0.1:8000/api/genres/:slug/

En la siguiente lección puliremos los serializadores para ofrecer más información.

## C05 Serializadores anidados

Hay algunas cosas mejorables en nuestra API.

La primera es que cuando trabajamos con relaciones en los modelos, DRF automáticamente las serializa utilizando sus campos **ids**.

En este caso los géneros de una película forman parte de una relación **ManyToMany** y serializa los **ids** en una lista numérica:

```json
"genres": [
    1
]
```

Lo ideal es proporcionar más de información y para conseguirlo podemos utilizar un sistema de serialización anidada:

#### **`films/serializers.py`**

```python
from rest_framework import serializers
from .models import Film, FilmGenre


class FilmGenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = FilmGenre
        fields = '__all__'


class FilmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Film
        fields = '__all__'

    genres = FilmGenreSerializer(many=True)  # new
```

El parámetro `many=True` indica que se tiene que serializar una lista de instancias, algo evidente teniendo en cuenta que `genres` es una relación **ManyToMany**. Además hay que cambiar el orden de los serializadores, ya que no se puede hacer referencia a una clase antes de declararla

Si consultamos la API veremos que ahora las películas contienen la información anidada de los géneros en forma de lista de objetos:

```json
"genres": [
    {
        "id": 1,
        "name": "Prueba",
        "slug": "prueba"
    }
],
```

Otra cosa que podemos hacer es mostrar una lista de las películas que tiene cada género.

Para conseguir esta funcionalidad hay que ser un poco más creativos, ya que por defecto nuestros géneros no contienen las películas, sino que son las películas las que contienen las referencias a los géneros.

Por suerte Django permite hacer consultas inversas en las relaciones, algo que podemos usar a nuestro favor para crear nuestro propios campo **films** en el serializador de géneros:

#### **`films/serializers.py`**

```python
class FilmGenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = FilmGenre
        fields = '__all__'

    films = FilmSerializer(many=True, source="film_genres") # query reversa
```

Sin embargo hay un error en esta lógica: no podemos hacer referencia a la clase `FilmSerializer` porque se encuentra debajo de `FilmGenreSerializer`.

Para solucionar este error podemos definir un serializador anidado de películas dentro de él mismo:

#### **`films/serializers.py`**

```python
class FilmGenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = FilmGenre
        fields = '__all__'

    class NestedFilmSerializer(serializers.ModelSerializer):

        class Meta:
            model = Film
            fields = '__all__'

    films = NestedFilmSerializer(
        many=True, read_only=True)
```

Esta estructura nos lleva nuevamente a hacer referencia a `FilmGenreSerializer`, pero como se encuentra abajo del todo no podemos acceder... así que vamos a crear una vez más otro serializador anidado dentro del serializador anidado, lo cuál generará una estructura de subclases muy interesante a la par que confusa:

#### **`films/serializers.py`**

```python
from rest_framework import serializers
from .models import Film, FilmGenre


class FilmGenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = FilmGenre
        fields = '__all__'

    class NestedFilmSerializer(serializers.ModelSerializer):

        class Meta:
            model = Film
            fields = '__all__'

        class NestedFilmGenreSerializer(serializers.ModelSerializer):

            class Meta:
                model = FilmGenre
                fields = '__all__'

        genres = NestedFilmGenreSerializer(many=True)

    films = NestedFilmSerializer(
        many=True, source="film_genres")  # query reversa
```

Es un poco complejo de entender pero os aseguro que gracias a la serialización anidada se pueden hacer maravillas con muy poco código.

En cualquier caso podemos consultar la API y notar como los géneros nos devuelven un campo **films** con una lista de películas y toda su información:

```json
[
  {
    "id": 1,
    "name": "Prueba",
    "slug": "prueba",
    "films": [
      {
        "id": "xxx",
        "genres": [
          {
            "id": 1,
            "name": "Prueba",
            "slug": "prueba"
          }
        ],
        "title": "Prueba de pelicula",
        "year": 2000,
        "review_short": "",
        "review_large": "",
        "trailer_url": null,
        "image_thumbnail": "http://localhost:8000/media/films/xxx/yyy.png",
        "image_wallpaper": "http://localhost:8000/media/films/xxx/zzz.jpg"
      }
    ]
  }
]
```

La gracia ahora es adaptar los serializadores para devolver la información que consideremos necesaria.

Por ejemplo no hace falta devolver todos los campos de la película en los géneros, por ahora será suficiente con el **id, el título, la miniatura y los géneros**:

#### **`films/serializers.py`**

```python
class NestedFilmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Film
        fields = ['id', 'title', 'image_thumbnail', 'genres']

        class NestedFilmGenreSerializer(serializers.ModelSerializer):

            class Meta:
                model = FilmGenre
                fields = '__all__'

        genres = NestedFilmGenreSerializer(many=True)
```

De hecho vamos a quitar los géneros de las películas en los géneros, es demasiado redundante y en el fondo sólo quería liaros un poco para que vieses una muestra del potencial de anidar serializadores:

#### **`films/serializers.py`**

```python
class NestedFilmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Film
        fields = ['id', 'title', 'image_thumbnail']  # edited

        # BORRAMOS LO SIGUIENTE ========>

        # class NestedFilmGenreSerializer(serializers.ModelSerializer):

        #     class Meta:
        #         model = FilmGenre
        #         fields = '__all__'

        # genres = NestedFilmGenreSerializer(many=True)
```

Conseguiremos así una serialización mucho más simple:

```json
[
  {
    "id": 1,
    "films": [
      {
        "id": "42569494-d623-446e-8d14-3686860c5277",
        "title": "Prueba de pelicula",
        "image_thumbnail": "http://localhost:8000/media/films/xxx/yyy.png"
      }
    ],
    "name": "Prueba",
    "slug": "prueba"
  }
]
```

Sin embargo hacer todo ha desembocado en un último problemilla...

Si consultamos una película en la API veremos que nos está mostrando los géneros con las películas dentro de las películas... todo un lío:

```json
[
  {
    "id": "42569494-d623-446e-8d14-3686860c5277",
    "genres": [
      {
        "id": 1,
        "films": [
          {
            "id": "42569494-d623-446e-8d14-3686860c5277",
            "title": "Prueba de pelicula",
            "image_thumbnail": "http://localhost:8000/media/films/xxx/yyy.png"
          }
        ],
        "name": "Prueba",
        "slug": "prueba"
      }
    ],
    "title": "Prueba de pelicula",
    "year": 2000,
    "review_short": "",
    "review_large": "",
    "trailer_url": null,
    "image_thumbnail": "http://localhost:8000/media/films/xxx/yyy.png",
    "image_wallpaper": "http://localhost:8000/media/films/xxx/zzz.jpg"
  }
]
```

Vamos a usar la misma lógica de los serializadores anidados para simplificar el serializador de géneros de las películas y que no incluya las películas:

#### **`films/serializers.py`**

```python
class FilmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Film
        fields = '__all__'

    class NestedFilmGenreSerializer(serializers.ModelSerializer):

        class Meta:
            model = FilmGenre
            fields = '__all__'

    genres = NestedFilmGenreSerializer(many=True)
```

Si probamos ahora con la nueva lógica...

```json
[
  {
    "id": "42569494-d623-446e-8d14-3686860c5277",
    "genres": [
      {
        "id": 1,
        "name": "Prueba",
        "slug": "prueba"
      }
    ],
    "title": "Prueba de pelicula",
    "year": 2000,
    "review_short": "",
    "review_large": "",
    "trailer_url": null,
    "image_thumbnail": "http://localhost:8000/media/films/xxx/yyy.png",
    "image_wallpaper": "http://localhost:8000/media/films/xxx/zzz.jpg"
  }
]
```

¡Solucionado! ¿Qué bien quedan nuestras clases anidadas verdad?

Por ahora os dejo [documentación](https://www.django-rest-framework.org/api-guide/serializers/) sobre los serializadores en los recursos, sólo por si queréis aprender un poco más por vuestra cuenta...

## C06 Base de datos preparada

Para acabar la unidad vamos a "instalar" la base de datos que he preparado para vosotros con mucho cariño. Un montón de buenas películas con la información e imágenes para hacer nuestros experimentos de la mejor forma posible.

Simplemente tendréis que descargar el fichero `db_preparada.zip` en los recursos de esta lección y hacer lo que os enseño a continuación:

1. Parar el servidor si lo tenéis en marcha.
2. Borrar o renombrar el fichero **db.sqlite3** de la raiz.
3. Borrar o renombrar los directorios **migrations** de las apps **authentication** y **films**.
4. Extraer el contenido del fichero `db_preparada.zip` en la raíz del proyecto `server`y substutir si os lo pide.

Al final deberéis tener de nuevo la base de datos **db.sqlite3** en la raíz, así como los nuevos directorios **migrations** en las apps y un montón de carpetas en el directorio **media/films**.

Tened en cuenta que vuestros usuarios se habrán borrado, pero tendréis a vuestra disposición:

- admin@admin.com : 1234
- test@test.com : 12345678

Siempre podéis crear nuevos administradores o editaros estos usuarios desde el panel de administrador.

En cualquier caso ya deberíais poder acceder a esta versión preparada de la base de datos con un montón de películas y géneros.

Buen provecho.

# TO DO: preparar base de datos...
