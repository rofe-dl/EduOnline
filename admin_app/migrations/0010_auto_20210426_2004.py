# Generated by Django 3.2 on 2021-04-26 14:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0009_reportcard_is_ongoing'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submittedquestion',
            name='question',
        ),
        migrations.RemoveField(
            model_name='submittedquestion',
            name='user',
        ),
        migrations.DeleteModel(
            name='ReportCard',
        ),
        migrations.DeleteModel(
            name='SubmittedQuestion',
        ),
    ]
