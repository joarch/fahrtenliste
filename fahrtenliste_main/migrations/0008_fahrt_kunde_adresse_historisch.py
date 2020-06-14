# Generated by Django 3.0.6 on 2020-06-14 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fahrtenliste_main', '0007_kunde_adresse_historisch'),
    ]

    operations = [
        migrations.AddField(
            model_name='fahrt',
            name='adresse_historisch',
            field=models.TextField(blank=True, help_text='Die ursprüngliche Adresse, falls die Adresse später gelöscht wird.', null=True, verbose_name='Adresse Historie'),
        ),
        migrations.AddField(
            model_name='fahrt',
            name='kunde_historisch',
            field=models.TextField(blank=True, help_text='Der ursprüngliche Kunde, falls der Kunde später gelöscht wird.', null=True, verbose_name='Kunde Historie'),
        ),
    ]
