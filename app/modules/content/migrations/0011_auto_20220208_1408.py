# Generated by Django 3.1.14 on 2022-02-08 14:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_jobpage_jobsindexpage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobsindexpage',
            name='headline',
        ),
        migrations.RemoveField(
            model_name='searchpage',
            name='headline',
        ),
        migrations.RemoveField(
            model_name='searchpage',
            name='hero_image',
        ),
        migrations.RemoveField(
            model_name='utilitypage',
            name='headline',
        ),
    ]
