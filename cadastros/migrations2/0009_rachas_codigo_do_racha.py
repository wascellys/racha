# Generated by Django 3.1.7 on 2021-09-11 20:18

import cadastros.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0008_remove_rachas_codigo'),
    ]

    operations = [
        migrations.AddField(
            model_name='rachas',
            name='codigo_do_racha',
            field=models.CharField(blank=True, default=cadastros.models.create_if_hash, max_length=5, null=True, unique=True),
        ),
    ]
