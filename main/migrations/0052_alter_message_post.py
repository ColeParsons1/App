# Generated by Django 4.1.2 on 2023-02-10 18:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0051_alter_profile_messages_alter_profile_notifications'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='DMsPost', to='main.job'),
        ),
    ]