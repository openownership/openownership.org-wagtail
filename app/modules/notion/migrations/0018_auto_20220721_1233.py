# Generated by Django 3.2.12 on 2022-07-21 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notion', '0017_commitment_all_sectors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disclosureregime',
            name='coverage_legislation_url',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='Coverage: Legislation URL'),
        ),
        migrations.AlterField(
            model_name='disclosureregime',
            name='definition_legislation_url',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='Definition: Legislation URL'),
        ),
    ]
