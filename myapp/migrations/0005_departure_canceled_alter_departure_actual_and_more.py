# Generated by Django 4.2.5 on 2023-09-23 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_apirun_error'),
    ]

    operations = [
        migrations.AddField(
            model_name='departure',
            name='canceled',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='departure',
            name='actual',
            field=models.DateTimeField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='departure',
            name='in_time',
            field=models.BooleanField(),
        ),
    ]