# Generated by Django 4.2.9 on 2024-02-25 08:17

from django.db import migrations, models
import django.db.models.functions.datetime


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0012_userbase_recommended_calories'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userfoodday',
            name='date',
            field=models.DateField(default=django.db.models.functions.datetime.Now()),
        ),
        migrations.AlterField(
            model_name='userstat',
            name='date',
            field=models.DateField(default=django.db.models.functions.datetime.Now()),
        ),
    ]
