# Generated by Django 4.1.2 on 2022-11-17 18:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0035_profile_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='username',
        ),
    ]