# Generated by Django 3.1.3 on 2020-12-03 09:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='rank',
        ),
    ]
