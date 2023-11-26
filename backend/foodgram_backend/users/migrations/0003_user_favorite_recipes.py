# Generated by Django 4.2.3 on 2023-10-22 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_alter_recipe_author'),
        ('users', '0002_user_subscriptions'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='favorite_recipes',
            field=models.ManyToManyField(to='recipes.recipe'),
        ),
    ]