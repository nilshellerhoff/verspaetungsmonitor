# Generated by Django 4.2.5 on 2023-09-24 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_departure_canceled_alter_departure_actual_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watcher',
            name='url',
            field=models.URLField(max_length=4096),
        ),
    ]
