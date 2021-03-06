# Generated by Django 2.1.2 on 2018-11-05 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CSDNCrawler', '0003_auto_20181022_2148'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='url_id',
            new_name='articleid',
        ),
        migrations.RenameField(
            model_name='article',
            old_name='userid',
            new_name='user_id',
        ),
        migrations.AddField(
            model_name='article',
            name='comments_num',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='article',
            name='originality',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='article',
            name='read_num',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='article',
            name='title',
            field=models.CharField(default='None', max_length=128),
        ),
    ]
