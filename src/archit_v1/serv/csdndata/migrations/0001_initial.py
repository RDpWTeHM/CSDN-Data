# Generated by Django 2.1.5 on 2019-04-02 13:44

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserID',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=64)),
                ('register_date', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='user register date')),
                ('name', models.CharField(default='', max_length=64)),
                ('visit', models.IntegerField(default=-1)),
                ('rank', models.IntegerField(default=-1)),
            ],
        ),
    ]
