# Generated by Django 4.2.5 on 2023-09-26 06:05

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_alter_watcher_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='departure',
            name='last_update',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='departure',
            name='watcher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='myapp.watcher'),
        ),
    ]