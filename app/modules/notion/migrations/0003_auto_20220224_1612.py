# Generated by Django 3.2.12 on 2022-02-24 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notion', '0002_auto_20220224_1556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commitment',
            name='link',
            field=models.URLField(blank=True, max_length=1000, null=True, verbose_name='Link'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='coverage_legislation_url',
            field=models.URLField(blank=True, max_length=1000, null=True, verbose_name='Coverage: Legislation URL'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='definition_legislation_url',
            field=models.URLField(blank=True, max_length=1000, null=True, verbose_name='Definition: Legislation URL'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='legislation_url',
            field=models.URLField(blank=True, max_length=1000, null=True, verbose_name='Legislation URL'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='public_access_register_url',
            field=models.URLField(blank=True, max_length=1000, null=True, verbose_name='Public Access Register URL'),
        ),
    ]
