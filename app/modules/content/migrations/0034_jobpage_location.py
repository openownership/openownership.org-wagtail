# Generated by Django 3.2.12 on 2022-02-24 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0033_alter_sectionpage_body'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobpage',
            name='location',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
