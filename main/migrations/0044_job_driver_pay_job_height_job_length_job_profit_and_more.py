# Generated by Django 4.1.2 on 2023-01-17 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0043_job_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='Driver_Pay',
            field=models.FloatField(default=0.0, max_length=10),
        ),
        migrations.AddField(
            model_name='job',
            name='Height',
            field=models.FloatField(default=0.0, max_length=10),
        ),
        migrations.AddField(
            model_name='job',
            name='Length',
            field=models.FloatField(default=0.0, max_length=10),
        ),
        migrations.AddField(
            model_name='job',
            name='Profit',
            field=models.FloatField(default=0.0, max_length=10),
        ),
        migrations.AddField(
            model_name='job',
            name='Width',
            field=models.FloatField(default=0.0, max_length=10),
        ),
        migrations.AddField(
            model_name='profile',
            name='Balance',
            field=models.FloatField(default=0.0, max_length=10),
        ),
    ]