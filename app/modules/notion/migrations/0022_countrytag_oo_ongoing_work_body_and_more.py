# Generated by Django 4.1.7 on 2023-06-29 10:18

from django.db import migrations, models
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('notion', '0021_alter_countrytag_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='countrytag',
            name='oo_ongoing_work_body',
            field=wagtail.fields.RichTextField(blank=True, null=True, verbose_name='Open Ownership Ongoing Work Body'),
        ),
        migrations.AddField(
            model_name='countrytag',
            name='oo_ongoing_work_title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Open Ownership Ongoing Work Title'),
        ),
    ]