# Generated by Django 2.0.1 on 2018-10-18 16:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('CSDNCrawler', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visualdata',
            name='crawlerDate',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='data crowler date'),
        ),
    ]