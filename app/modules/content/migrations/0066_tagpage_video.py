# Generated by Django 3.2.12 on 2022-08-08 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0065_auto_20220627_1643'),
    ]

    operations = [
        migrations.AddField(
            model_name='tagpage',
            name='video',
            field=models.URLField(blank=True, null=True),
        ),
    ]