# Generated by Django 3.2 on 2021-04-27 14:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0010_auto_20210426_2004'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subject',
            name='avg_score',
        ),
    ]
