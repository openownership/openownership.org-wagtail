# Generated by Django 3.2.12 on 2022-03-02 15:58

from django.db import migrations, models
import django_extensions.db.fields
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('notion', '0007_merge_20220302_1159'),
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', django_extensions.db.fields.AutoSlugField(blank=True, editable=False, populate_from='name')),
            ],
            options={
                'verbose_name': 'Region',
                'verbose_name_plural': 'Regions',
            },
        ),
        migrations.AddField(
            model_name='countrytag',
            name='regions',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, related_name='countries', to='notion.Region'),
        ),
    ]