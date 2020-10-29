# S04 Búsqueda, filtrado y paginación

## C01 Presentación

A lo largo de esta sección extenderemos nuestro `FilmViewSet` para ofrecer cuatro nuevas funcionalidades a las películas:

- **Búsqueda**: Usando un texto y buscando coincidencias.
- **Ordenación**: Ascendente o descendente a partir de varios campos.
- **Filtrado**: En base a a partir de varios campos.
- **Paginación**: Para limitar los registros por página.

## C02 Sistema de búsqueda

En esta lección añadiremos de una forma muy sencilla la opción de realizar búsquedas en varios campos del `ViewSet`.

El objetivo es dar cobertura a la típica funcionalidad de un buscador en tiempo real, dónde a partir de un texto se buscan coincidencias en la API y se devuelve la lista resultante.

Implementar esta funcionalidad en un `ViewSet` es facilísimo porque ya viene implementada y sólo hay que configurarla:

#### **`films/views.py`**

```python
from rest_framework import viewsets, filters  # edited

class FilmViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer

    # Sistema de filtros
    filter_backends = [filters.SearchFilter]

    search_fields = ['title', 'year']
```

Sólo con este cambio podemos probar cómo funciona el sistema de búsquedas en el `ViewSet` utilizando el cliente gráfico de pruebas enel nuevo apartado **Filtros** que nos aparecerá en el menú superior.

Fijaros que podemos enviar tanto el título como el año, que según la estructura de las peticiones debe pasarse en un parámetro **GET** llamado **search**.

Otra cosa interesante es que podemos hacer referencia a un campo de un modelo relacionado, por ejemplo si queremos filtrar por el nombre de un género podemos hacerlo así:

```python
search_fields = ['title', 'year', 'genres__name']  # edited
```

Os dejo la [documentación](https://www.django-rest-framework.org/api-guide/filtering/#searchfilter) sobre los filtros de búsqueda en los recursos.

## C03 Sistema de ordenación

Al igual que el filtro de búsqueda, el filtro de ordenación viene implementado y sólo hay que activarlo:

#### **`films/views.py`**

```python
class FilmViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer

    # Sistema de filtros
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]  # edited

    search_fields = ['title', 'year', 'genres__name']
    ordering_fields = ['title', 'year']  # new
```

En esta ocasión debemos pasar un parámetro **GET** llamado **ordering**. Lo interesante es que por defecto el orden es descendiente, eso es de la A a la Z en textos y de menos a más en números, pero se puede negar a ascendiente añadiendo un **-** delante del campo.

Además igual que antes podemos hacer referencia a un campo de un modelo relacionado, por ejemplo para ordenar a partir del nombre los géneros pondremos:

```python
ordering_fields = ['title', 'year', 'genres__name']  # edited
```

Es interesante que funcione incluso con campos `ManyToMany` sin hacer ninguna configuración extra.

Os dejo [documentación](https://www.django-rest-framework.org/api-guide/filtering/#orderingfilter) por si queréis aprender más sobre los filtros de ordenamiento.

## C04 Sistema de filtros de campo

En las anteriores lecciones de esta unidad hemos configurado filtros genéricos de búsqueda y ordenamiento que ya se encuentran implementados en DRF. ¿Pero cómo podemos filtrar los resultados a partir de un género o año explícito?

Para conseguir este comportamiento debemos utilizar la librería `DjangoFilterBackend` de DRF que nos permite crear nuestros propios filtros. Ésta requiere instalar y configurar una app externa llamada **django-filter** tal como explican en la [documentación oficial](https://www.django-rest-framework.org/api-guide/filtering/#djangofilterbackend) de DRF, adjunto enlace en los recursos:

```bash
cd server
pipenv install django-filter==2.4.0
```

Luego tenemos que activarla:

#### **`server/settings.py`**

```python
INSTALLED_APPS = [
    # Django external apps
    'corsheaders',
    'rest_framework',
    'django_rest_passwordreset',
    'django_filters',  # new
]
```

Ahora importamos `DjangoFilterBackend` y lo añadimos en la lista `filter_backends` de nuestra `ListView`:

#### **`films/views.py`**

```python
from django_filters.rest_framework import DjangoFilterBackend  # new

class FilmViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer

    # Sistema de filtros
    filter_backends = [DjangoFilterBackend,  # edited
                       filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['title', 'year', 'genres__name']
    ordering_fields = ['title', 'year', 'genres__name']
```

Con este **backend** activo ya podemos configurar filtros de campo con operadores relacionales y otras funcionaliadades:

```python
filterset_fields = {
    'year': ['lte', 'gte'],  # Año menor o igual, mayor o igual que
    'genres': ['exact']      # Género exacto
}
```

Si vamos a la interfaz de la API podremos probar nuestro sistema de filtros de campo y analizar la estructura de las peticiones, que en este caso tendríamos **year\_\_lte**, **year\_\_gte** y múltiples **genres**. Lo mejor de todo es que estos filtros son acumulativos, de manera que que al final podríamos realizar consultas avanzadas en una sola petición, por ejemplo:

- Año mayor que 1980: `year__gte=1980`
- Año menor que 2000: `year__lte=2000`
- Género Fantasía: `genres=3`
- Género Crimen: `genres=12`
- Ordenadas por año: `ordering=year`

Que en una sola query quedaría así:

```json
?year__lte=2000&year__gte=1980&genres=3&genres=12&ordering=title
```

Como véis en conjunto hemos implementado un potente sistema de búsquedas y filtros con muy poco código... Si es que DRF es una maravilla.

## C05 Sistema de paginación

La guinda del pastel de la `FilmViewSet` la pondremos con un sistema de paginación, el cuál se utiliza para limitar los registros devueltos a las peticiones de los clientes, evitando de esa forma saturar al servidor con consultas inmensas.

Según la [documentación](https://www.django-rest-framework.org/api-guide/pagination/) que os dejo en los recursus, podemos activar la paginación por defecto en todas las vistas o configurarla manualmente donde queramos. Nosotros vamos a hacerlo de la segunda forma porque no me interesa paginar los géneros automáticamente.

Sólo tenemos que importar la clase del paginador genérico y asignarla al `ViewSet`:

#### **`films/views.py`**

```python
from rest_framework.pagination import PageNumberPagination  # new

class FilmViewSet(viewsets.ReadOnlyModelViewSet):
    # ...

    # Sistema de paginación
    pagination_class = PageNumberPagination
    pagination_class.page_size = 8  # películas por página
```

Como veremos en la interfaz de la API ahora por defecto tenemos limitados los registros y podemos navegar entre las diferentes páginas que nos aparecen en la parte superior.

Fijaros que ahora las películas nos aparecen dentro del campo **results** de un objeto que contiene información del paginador, como por ejemplo **count** con el número total de registros, **next** y **previous** con los enlaces a la siguiente y anterior página. Además la nevagación como tal se gestiona con un parámetro de tipo **GET** llamado **page** que indica la página actual.

Lo genial de este paginador es que funciona automáticamente incluso con los filtros activos, por ejemplo si buscamos las películas del año 1990 en adelante y ordenadas por año:

```json
?ordering=year&year__gte=1990
```

Simplemente genial.

## C05 Paginación personalizada

En la última lección de la unidad os voy a enseñar a personalizar la paginación de la API para cubrir todas las necesidades que un cliente pueda tener.

Para personalizar la paginación, la [documentación](https://www.django-rest-framework.org/api-guide/pagination/#custom-pagination-styles) nos explica que debemos crear nuestra propia clase a partir de `PageNumberPagination` y extender su método `get_paginated_response`:

#### **`films/views.py`**

```python
from rest_framework.response import Response  # new

class ExtendedPagination(PageNumberPagination):
    page_size = 8

    def get_paginated_response(self, data):

        return Response({
            'count': self.page.paginator.count,
            'num_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'page_size': self.page_size,
            'next_link': self.get_next_link(),
            'previous_link': self.get_previous_link(),
            'results': data
        })


class FilmViewSet(viewsets.ReadOnlyModelViewSet):
    # ...

    # Sistema de paginación
    pagination_class = ExtendedPagination  # edited
```

Usando nuestro propio paginador estamos proveyendo de mucha más información al cliente:

- `count`: El número de registros
- `num_pages`: El número de páginas
- `page_number`: El número de página actual
- `page_size`: El número de página actual
- `next_link`: El enlace a la siguiente página
- `previous_link`: El enlace a la anterior página

Otra cosa que podemos hacer, y de hecho vamos a hacer por petición de Dani, es modificar estos campos a voluntad, concretamente los enlaces para navegar en la paginación.

Dani me ha pedido si era posible dejar sólo los parámetros de la consulta, ya que el plugin de React que va a utilizar los requiere de esta forma, así que vamos a hacerlo:

#### **`films/views.py`**

```python
class ExtendedPagination(PageNumberPagination):
    page_size = 8

    def get_paginated_response(self, data):

        # Recuperamos los valores por defecto
        next_link = self.get_next_link()
        previous_link = self.get_previous_link()

        # Hacemos un split en la primera '/' dejando sólo los parámetros
        if next_link:
            next_link = next_link.split('/')[-1]

        if previous_link:
            previous_link = previous_link.split('/')[-1]

        # Modificamos los valores devueltos
        return Response({
            'count': self.page.paginator.count,
            'num_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'page_size': self.page_size,
            'next_link': next_link,           # edited
            'previous_link': previous_link,   # edited
            'results': data
        })
```

Y con este cambio acabamos la unidad.
