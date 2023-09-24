# Generated by Django 4.2.5 on 2023-09-22 17:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Line',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('line', models.CharField(max_length=255)),
                ('direction', models.CharField(max_length=255)),
                ('icon', models.URLField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Watcher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(max_length=255)),
                ('url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Departure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('planned', models.DateTimeField(max_length=255)),
                ('actual', models.DateTimeField(max_length=255)),
                ('in_time', models.BooleanField(max_length=255)),
                ('line', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='myapp.line')),
                ('station', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='myapp.station')),
            ],
        ),
        migrations.CreateModel(
            name='ApiRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('status', models.CharField(max_length=255)),
                ('watcher', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='myapp.watcher')),
            ],
        ),
    ]
