# Generated by Django 2.0.1 on 2019-01-20 05:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CSDNCrawler', '0009_auto_20190119_2245'),
    ]

    operations = [
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=128)),
                ('name', models.CharField(default='', max_length=512)),
                ('crawledDate', models.DateField(auto_now=True, verbose_name='follow crawled date')),
                ('current_total_follow_num', models.IntegerField(default=-1)),
                ('followed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follow_set', to='CSDNCrawler.UserID')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]