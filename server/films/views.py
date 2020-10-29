from rest_framework import viewsets, filters
from .models import Film, FilmGenre
from .serializers import FilmSerializer, FilmGenreSerializer


class FilmViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer

    # Sistema de filtros
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'year', 'genres__name']
    ordering_fields = ['title', 'year', 'genres__name']


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FilmGenre.objects.all()
    serializer_class = FilmGenreSerializer
    lookup_field = 'slug'  # identificaremos los géneros usando su slug
