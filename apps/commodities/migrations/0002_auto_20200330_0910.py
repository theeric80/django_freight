# Generated by Django 3.0.3 on 2020-03-30 09:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commodities', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='commodity',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='inventory',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='tradepartner',
            options={'ordering': ['id']},
        ),
    ]
