# Generated by Django 2.1.2 on 2018-12-24 10:30

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('CSDNCrawler', '0005_userid_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Follows',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crawledDate', models.DateTimeField(default=django.utils.timezone.now, verbose_name='follows crawled date')),
                ('follow_id', models.CharField(max_length=64)),
                ('follow_name', models.CharField(default='', max_length=64)),
                ('current_total_follows_num', models.IntegerField(default=-1)),
            ],
        ),
        migrations.AlterField(
            model_name='userid',
            name='register_date',
            field=models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc), verbose_name='user register date'),
        ),
        migrations.AddField(
            model_name='follows',
            name='followed_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CSDNCrawler.UserID'),
        ),
    ]
