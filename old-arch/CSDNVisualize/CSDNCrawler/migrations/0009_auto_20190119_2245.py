# Generated by Django 2.0.1 on 2019-01-19 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CSDNCrawler', '0008_auto_20190119_1731'),
    ]

    operations = [
        migrations.AddField(
            model_name='visualdata',
            name='follow',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='visualdata',
            name='reprint',
            field=models.IntegerField(default=-1),
        ),
        migrations.AlterField(
            model_name='visualdata',
            name='crawlerDate',
            field=models.DateTimeField(auto_now=True, verbose_name='data crowler date'),
        ),
    ]
