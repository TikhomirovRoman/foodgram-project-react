# Generated by Django 4.2.3 on 2023-07-16 21:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_ingredient_name_and_measure_uniq'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='ingredient',
            name='name_and_measure_uniq',
        ),
        migrations.RenameField(
            model_name='ingredient',
            old_name='measurement_init',
            new_name='measurement_unit',
        ),
        migrations.AlterUniqueTogether(
            name='ingredient',
            unique_together={('name', 'measurement_unit')},
        ),
    ]
