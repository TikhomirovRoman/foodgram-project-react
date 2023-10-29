# Generated by Django 4.2.3 on 2023-10-28 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_alter_recipe_author'),
        ('users', '0003_user_favorite_recipes'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='shopping_cart',
            field=models.ManyToManyField(related_name='shopping_carts', to='recipes.recipe'),
        ),
        migrations.AlterField(
            model_name='user',
            name='favorite_recipes',
            field=models.ManyToManyField(related_name='favored_by', to='recipes.recipe'),
        ),
    ]
