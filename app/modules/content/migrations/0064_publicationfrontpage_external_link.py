# Generated by Django 3.2.12 on 2022-06-23 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0063_alter_sectionpage_body'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicationfrontpage',
            name='external_link',
            field=models.URLField(blank=True, help_text='Use document download OR external link', null=True),
        ),
    ]