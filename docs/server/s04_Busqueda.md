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

## C04 Sistema de filtros

TO-DO: genero/año/

Como siempre dejo el enlace a la [documentación](https://www.django-rest-framework.org/api-guide/filtering/#djangofilterbackend) en los recursos.

## C05 Sistema de paginación

TO-DO: básica de django 8 items

## C05 Paginación personalizada

En esta lección os voy a enseñar a personalizar la paginación para cubrir todas las necesidades que un cliente puede tener, ya que por defecto es bastante limitada en cuanto a la información que provee y es posible que los clientes de la API requieran que enviemos algunos campos extra como por ejemplo:

- El número de páginas que tiene la paginación.
- El número de la página actual donde se encuentra.
- Un contador de elementos en la página actual.

Además también modificaremos los enlaces de la página anterir y siguiente a petición de Dani, ya que necesita que los enlaces le lleguen sin el dominio, lo cuál nos permitirá aprender sobre cómo modificar y extender los campos de la paginación.

TO-DO
