# Generated by Django 4.2.3 on 2023-10-05 13:55

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='subscriptions',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
