# Generated by Django 3.1.7 on 2023-01-22 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0003_auto_20230121_1420'),
    ]

    operations = [
        migrations.RenameField(
            model_name='financeiro',
            old_name='pagante',
            new_name='membro',
        ),
        migrations.AddField(
            model_name='financeiro',
            name='valor',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
    ]
