# Generated by Django 4.2.9 on 2024-02-07 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0007_recipefood'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipefood',
            name='gram',
            field=models.IntegerField(default=0),
        ),
    ]
