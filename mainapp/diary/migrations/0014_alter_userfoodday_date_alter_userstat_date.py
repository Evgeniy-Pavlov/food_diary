# Generated by Django 4.2.9 on 2024-02-25 08:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0013_alter_userfoodday_date_alter_userstat_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userfoodday',
            name='date',
            field=models.DateField(default=datetime.date(2024, 2, 25)),
        ),
        migrations.AlterField(
            model_name='userstat',
            name='date',
            field=models.DateField(default=datetime.date(2024, 2, 25)),
        ),
    ]
