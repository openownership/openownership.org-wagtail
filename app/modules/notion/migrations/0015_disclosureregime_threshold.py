# Generated by Django 3.2.12 on 2022-03-21 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notion', '0014_alter_countrytag_body'),
    ]

    operations = [
        migrations.AddField(
            model_name='disclosureregime',
            name='threshold',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Threshold'),
        ),
    ]
