# Generated by Django 3.1.14 on 2022-02-16 18:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sitesettings',
            name='body',
        ),
        migrations.RemoveField(
            model_name='sitesettings',
            name='limit_to_pages',
        ),
        migrations.RemoveField(
            model_name='sitesettings',
            name='link_label',
        ),
        migrations.RemoveField(
            model_name='sitesettings',
            name='link_page',
        ),
        migrations.RemoveField(
            model_name='sitesettings',
            name='live',
        ),
        migrations.RemoveField(
            model_name='sitesettings',
            name='show_on_all_pages',
        ),
    ]
