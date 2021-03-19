from rest_framework import serializers
from .models import Film, FilmGenre, FilmUser


class FilmGenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = FilmGenre
        fields = '__all__'

    class NestedFilmSerializer(serializers.ModelSerializer):

        class Meta:
            model = Film
            fields = ['id', 'title', 'image_thumbnail']

    films = NestedFilmSerializer(
        many=True, source="film_genres")  # query reversa


class FilmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Film
        fields = '__all__'

    class NestedFilmGenreSerializer(serializers.ModelSerializer):

        class Meta:
            model = FilmGenre
            fields = '__all__'

    genres = NestedFilmGenreSerializer(many=True)


class FilmUserSerializer(serializers.ModelSerializer):

    film = FilmSerializer(read_only=True)

    class Meta:
        model = FilmUser
        fields = ['film', 'favorite', 'note', 'state', 'review']
