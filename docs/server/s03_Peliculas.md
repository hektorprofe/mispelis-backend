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

## C05 ViewSet de géneros

## C06 Lista de pelis sin filtros

Vista de peli sin interacción de los usuarios

## C07 Vistas privadas

## C08 Base de datos preparada

## C09 Mejorar portada: Slideshow random
