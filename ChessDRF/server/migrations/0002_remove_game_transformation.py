# Generated by Django 3.0.3 on 2020-10-22 09:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='transformation',
        ),
    ]
