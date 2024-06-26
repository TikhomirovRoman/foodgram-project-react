# Generated by Django 4.2.3 on 2023-10-28 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_alter_recipe_author'),
        ('users', '0004_user_shopping_cart_alter_user_favorite_recipes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='shopping_cart',
            field=models.ManyToManyField(related_name='shopping_carts', to='recipes.ingredient'),
        ),
    ]
