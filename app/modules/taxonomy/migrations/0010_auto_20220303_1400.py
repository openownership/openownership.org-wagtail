# Generated by Django 3.2.12 on 2022-03-03 14:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0009_auto_20220301_1824'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='focusareatag',
            name='body',
        ),
        migrations.RemoveField(
            model_name='publicationtype',
            name='body',
        ),
        migrations.RemoveField(
            model_name='sectortag',
            name='body',
        ),
    ]
