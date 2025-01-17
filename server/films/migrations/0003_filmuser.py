# Generated by Django 3.1.7 on 2021-03-19 17:09

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('films', '0002_auto_20201024_2335'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilmUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.PositiveSmallIntegerField(choices=[(0, 'Sin estado'), (1, 'Vista'), (2, 'Quiero verla')], default=0)),
                ('favorite', models.BooleanField(default=False)),
                ('note', models.PositiveSmallIntegerField(null=True, validators=[django.core.validators.MaxValueValidator(10)])),
                ('review', models.TextField(null=True)),
                ('film', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='films.film')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['film__title'],
                'unique_together': {('film', 'user')},
            },
        ),
    ]
