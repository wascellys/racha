# Generated by Django 2.1.5 on 2020-10-10 19:30

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cadastros', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jogadores',
            options={'ordering': ['nome']},
        ),
        migrations.AlterModelOptions(
            name='jogadoresracha',
            options={'ordering': ['jogador']},
        ),
        migrations.AlterUniqueTogether(
            name='jogadores',
            unique_together={('nome', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='jogadoresracha',
            unique_together={('jogador', 'racha')},
        ),
    ]
