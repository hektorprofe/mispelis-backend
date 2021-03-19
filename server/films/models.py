import uuid
from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db.models import Sum
from django.db.models.signals import post_save


class Film(models.Model):

    def path_to_film(instance, filename):
        return f'films/{instance.id}/{filename}'

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
    image_thumbnail = models.ImageField(
        upload_to=path_to_film, null=True, blank=True, verbose_name="Miniatura")
    image_wallpaper = models.ImageField(
        upload_to=path_to_film, null=True, blank=True, verbose_name="Wallpaper")

    favorites = models.IntegerField(
        default=0, verbose_name="favoritos")
    average_note = models.FloatField(
        default=0.0, verbose_name="nota media",
        validators=[MaxValueValidator(10.0)])

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


class FilmUser(models.Model):

    STATUS_CHOICES = (
        (0, "Sin estado"),
        (1, "Vista"),
        (2, "Quiero verla"))

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    state = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES, default=0)  # Al crearse sin estado se borra
    favorite = models.BooleanField(
        default=False)
    note = models.PositiveSmallIntegerField(
        null=True, validators=[MaxValueValidator(10)])
    review = models.TextField(null=True)

    class Meta:
        unique_together = ['film', 'user']
        ordering = ['film__title']


def update_film_stats(sender, instance, **kwargs):
    count_favorites = FilmUser.objects.filter(
        film=instance.film, favorite=True).count()
    instance.film.favorites = count_favorites
    notes = FilmUser.objects.filter(
        film=instance.film).exclude(note__isnull=True)
    count_notes = notes.count()
    sum_notes = notes.aggregate(Sum('note')).get('note__sum')
    try:
        instance.film.average_note = round(sum_notes/count_notes, 2)
    except:
        pass
    instance.film.save()


post_save.connect(update_film_stats, sender=FilmUser)
