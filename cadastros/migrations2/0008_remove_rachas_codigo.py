# Generated by Django 3.1.7 on 2021-09-11 20:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0007_auto_20210911_1713'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rachas',
            name='codigo',
        ),
    ]
