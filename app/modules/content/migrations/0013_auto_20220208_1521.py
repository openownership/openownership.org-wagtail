# Generated by Django 3.1.14 on 2022-02-08 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_auto_20220208_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobpage',
            name='application_deadline',
            field=models.DateField(blank=True, null=True),
        ),
    ]
