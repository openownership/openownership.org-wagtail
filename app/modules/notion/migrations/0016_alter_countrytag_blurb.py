# Generated by Django 3.2.12 on 2022-03-22 14:33

from django.db import migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('notion', '0015_disclosureregime_threshold'),
    ]

    operations = [
        migrations.AlterField(
            model_name='countrytag',
            name='blurb',
            field=wagtail.core.fields.RichTextField(blank=True, null=True),
        ),
    ]